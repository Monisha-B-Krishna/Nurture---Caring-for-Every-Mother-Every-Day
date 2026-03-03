import streamlit as st
from database.db import get_connection

# -----------------------------
# ANM DASHBOARD
# -----------------------------

def anm_dashboard(user):

    st.title("ANM Clinical Dashboard")

    conn = get_connection()
    cursor = conn.cursor()

    features = [
        "Enter Pregnancy Details",
        "Find Risk",
        "ASHA Compliance"
    ]

    selected_feature = st.sidebar.radio("ANM Panel", features)

    # =====================================================
    # 1️⃣ ENTER PREGNANCY DETAILS
    # =====================================================

    if selected_feature == "Enter Pregnancy Details":

        st.subheader("Register / Update Pregnancy Details")

        # ✅ FIXED ROLE (lowercase)
        women_rows = cursor.execute("""
            SELECT id, name FROM users WHERE role='woman'
        """).fetchall()

        if not women_rows:
            st.warning("No women users found.")
        else:
            women_list = [(w["id"], w["name"]) for w in women_rows]
            woman_names = [w[1] for w in women_list]

            selected_name = st.selectbox("Select Woman", woman_names)
            selected_woman_id = next(
                w[0] for w in women_list if w[1] == selected_name
            )

            month = st.number_input("Pregnancy Month", 1, 9)
            week = st.number_input("Pregnancy Week", 1, 40)
            weight = st.number_input("Weight (kg)", 30.0, 120.0)
            hb = st.number_input("Hemoglobin (Hb)", 5.0, 15.0)
            sugar = st.number_input("Blood Sugar", 60.0, 250.0)
            bp = st.text_input("Blood Pressure (e.g., 120/80)")

            if st.button("Save Record"):

                risk_score = 0

                if hb < 10:
                    risk_score += 2

                if sugar > 140:
                    risk_score += 2

                if month >= 7:
                    risk_score += 1

                if risk_score >= 4:
                    risk_level = "High"
                elif risk_score >= 2:
                    risk_level = "Medium"
                else:
                    risk_level = "Low"

                cursor.execute("""
                    INSERT INTO pregnancies
                    (woman_id, month, week, weight, hb, bp, sugar, risk_score, risk_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    selected_woman_id,
                    month,
                    week,
                    weight,
                    hb,
                    bp,
                    sugar,
                    risk_score,
                    risk_level
                ))

                conn.commit()

                st.success("Pregnancy record saved successfully.")
                st.info(f"Calculated Risk Level: {risk_level}")

    # =====================================================
    # 2️⃣ FIND RISK
    # =====================================================

    elif selected_feature == "Find Risk":

        st.subheader("Risk Analysis")

        records = cursor.execute("""
            SELECT u.name, p.month, p.hb, p.sugar, p.risk_level
            FROM pregnancies p
            JOIN users u ON p.woman_id = u.id
            ORDER BY p.created_at DESC
        """).fetchall()

        total = len(records)
        high = sum(1 for r in records if r["risk_level"] == "High")
        medium = sum(1 for r in records if r["risk_level"] == "Medium")
        low = sum(1 for r in records if r["risk_level"] == "Low")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Records", total)
        col2.metric("High Risk", high)
        col3.metric("Medium Risk", medium)

        st.metric("Low Risk", low)

        st.markdown("### High Risk Cases")

        for r in records:
            if r["risk_level"] == "High":
                st.error(
                    f"{r['name']} - Month {r['month']} | Hb: {r['hb']} | Sugar: {r['sugar']}"
                )

    # =====================================================
    # 3️⃣ ASHA COMPLIANCE
    # =====================================================

    elif selected_feature == "ASHA Compliance":

        st.subheader("ASHA Visit Compliance")

        # ✅ FIXED ROLE (lowercase)
        compliance = cursor.execute("""
            SELECT u.name, COUNT(p.id) as visit_count
            FROM users u
            LEFT JOIN pregnancies p ON u.id = p.woman_id
            WHERE u.role='woman'
            GROUP BY u.name
        """).fetchall()

        st.metric("Total Women Registered", len(compliance))

        for c in compliance:
            st.write(f"{c['name']} - Total Visits Logged: {c['visit_count']}")

    conn.close()