import streamlit as st
from database.db import get_connection

def asha_dashboard(user):

    st.title("ASHA Worker Intelligence Dashboard")

    conn = get_connection()
    cursor = conn.cursor()

    features = [
        "Assigned Women",
        "Priority Visit List",
        "Appointment Tracking",
        "Chat Alerts"
    ]

    selected_feature = st.sidebar.radio("ASHA Panel", features)

    # -----------------------------------------------------
    # Get Assigned Women (FIXED ROLE BUG)
    # -----------------------------------------------------

    assigned_women = cursor.execute("""
        SELECT id, name
        FROM users
        WHERE role='woman' AND asha_id=?
    """, (user["id"],)).fetchall()

    woman_ids = [w["id"] for w in assigned_women]

    # =====================================================
    # 1️⃣ ASSIGNED WOMEN
    # =====================================================

    if selected_feature == "Assigned Women":

        st.subheader("Assigned Women Overview")

        total = len(assigned_women)

        if woman_ids:
            placeholders = ",".join("?" * len(woman_ids))

            high_risk = cursor.execute(f"""
                SELECT COUNT(*) FROM pregnancies
                WHERE woman_id IN ({placeholders})
                AND risk_level='High'
            """, woman_ids).fetchone()[0]

            medium_risk = cursor.execute(f"""
                SELECT COUNT(*) FROM pregnancies
                WHERE woman_id IN ({placeholders})
                AND risk_level='Medium'
            """, woman_ids).fetchone()[0]

            low_risk = cursor.execute(f"""
                SELECT COUNT(*) FROM pregnancies
                WHERE woman_id IN ({placeholders})
                AND risk_level='Low'
            """, woman_ids).fetchone()[0]
        else:
            high_risk = medium_risk = low_risk = 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Assigned", total)
        col2.metric("High Risk", high_risk)
        col3.metric("Medium Risk", medium_risk)
        st.metric("Low Risk", low_risk)

        st.markdown("### Woman List")

        if assigned_women:
            for w in assigned_women:
                st.write(w["name"])
        else:
            st.info("No women assigned.")

    # =====================================================
    # 2️⃣ PRIORITY VISIT LIST
    # =====================================================

    elif selected_feature == "Priority Visit List":

        st.subheader("Risk-Based Priority Analysis")

        if not woman_ids:
            st.info("No assigned women.")
        else:
            placeholders = ",".join("?" * len(woman_ids))

            women_data = cursor.execute(f"""
                SELECT u.name, p.risk_level, p.month
                FROM pregnancies p
                JOIN users u ON p.woman_id=u.id
                WHERE p.woman_id IN ({placeholders})
                ORDER BY p.risk_level DESC
            """, woman_ids).fetchall()

            for w in women_data:

                if w["risk_level"] == "High":
                    st.error(f"{w['name']} - High Risk (Month {w['month']})")
                elif w["risk_level"] == "Medium":
                    st.warning(f"{w['name']} - Medium Risk (Month {w['month']})")
                else:
                    st.success(f"{w['name']} - Low Risk (Month {w['month']})")

    # =====================================================
    # 3️⃣ APPOINTMENT TRACKING
    # =====================================================

    elif selected_feature == "Appointment Tracking":

        st.subheader("Upcoming ANC Visits")

        if not woman_ids:
            st.info("No assigned women.")
        else:
            placeholders = ",".join("?" * len(woman_ids))

            visits = cursor.execute(f"""
                SELECT u.name, p.created_at
                FROM pregnancies p
                JOIN users u ON p.woman_id=u.id
                WHERE p.woman_id IN ({placeholders})
                ORDER BY p.created_at DESC
            """, woman_ids).fetchall()

            st.metric("Total Records Logged", len(visits))

            for v in visits[:10]:
                st.write(f"{v['name']} - Last Visit: {v['created_at']}")

    # =====================================================
    # 4️⃣ CHAT ALERTS
    # =====================================================

    elif selected_feature == "Chat Alerts":

        st.subheader("Women Chat Activity")

        if not woman_ids:
            st.info("No assigned women.")
        else:
            placeholders = ",".join("?" * len(woman_ids))

            chats = cursor.execute(f"""
                SELECT u.name, c.question, c.timestamp
                FROM chat_history c
                JOIN users u ON c.woman_id=u.id
                WHERE c.woman_id IN ({placeholders})
                ORDER BY c.timestamp DESC
            """, woman_ids).fetchall()

            st.metric("Total Chat Messages", len(chats))

            high_keyword_count = 0

            for chat in chats:

                if any(word in chat["question"].lower() for word in ["bleeding", "pain", "emergency"]):
                    high_keyword_count += 1
                    st.error(f"⚠ {chat['name']} - Possible Emergency Query")

                st.write(f"{chat['name']}: {chat['question']}")
                st.markdown("---")

            st.metric("Potential Emergency Chats", high_keyword_count)

    conn.close()