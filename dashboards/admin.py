import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database.db import get_connection


def admin_dashboard(user):

    st.title("🏛 Government Admin Intelligence Dashboard")

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # DISTRICT FILTER
    # =====================================================

    districts = cursor.execute(
        "SELECT DISTINCT district FROM users WHERE district IS NOT NULL"
    ).fetchall()

    district_list = ["All"] + [d[0] for d in districts if d[0]]
    selected_district = st.selectbox("Select District", district_list)

    params = []
    district_filter = ""

    if selected_district != "All":
        district_filter = " AND u.district=? "
        params.append(selected_district)

    # =====================================================
    # CORE METRICS (FILTERED)
    # =====================================================

    total = cursor.execute(f"""
        SELECT COUNT(*) 
        FROM pregnancies p
        JOIN users u ON p.woman_id=u.id
        WHERE 1=1 {district_filter}
    """, params).fetchone()[0]

    high = cursor.execute(f"""
        SELECT COUNT(*) 
        FROM pregnancies p
        JOIN users u ON p.woman_id=u.id
        WHERE p.risk_level='High' {district_filter}
    """, params).fetchone()[0]

    medium = cursor.execute(f"""
        SELECT COUNT(*) 
        FROM pregnancies p
        JOIN users u ON p.woman_id=u.id
        WHERE p.risk_level='Medium' {district_filter}
    """, params).fetchone()[0]

    low = cursor.execute(f"""
        SELECT COUNT(*) 
        FROM pregnancies p
        JOIN users u ON p.woman_id=u.id
        WHERE p.risk_level='Low' {district_filter}
    """, params).fetchone()[0]

    avg_risk_score = cursor.execute(f"""
        SELECT AVG(risk_score)
        FROM pregnancies p
        JOIN users u ON p.woman_id=u.id
        WHERE 1=1 {district_filter}
    """, params).fetchone()[0]

    # =====================================================
    # DISTRICT RISK DISTRIBUTION (NOW FILTERED)
    # =====================================================

    district_risk = cursor.execute(f"""
        SELECT u.district,
               SUM(CASE WHEN p.risk_level='High' THEN 1 ELSE 0 END) as high,
               SUM(CASE WHEN p.risk_level='Medium' THEN 1 ELSE 0 END) as medium,
               SUM(CASE WHEN p.risk_level='Low' THEN 1 ELSE 0 END) as low
        FROM pregnancies p
        JOIN users u ON p.woman_id=u.id
        WHERE 1=1 {district_filter}
        GROUP BY u.district
    """, params).fetchall()

    district_compare = cursor.execute(f"""
        SELECT u.district, COUNT(p.id)
        FROM pregnancies p
        JOIN users u ON p.woman_id=u.id
        WHERE 1=1 {district_filter}
        GROUP BY u.district
    """, params).fetchall()

    conn.close()

    # =====================================================
    # STYLED KPI CARDS
    # =====================================================

    st.markdown("### 📊 Key Indicators")

    col1, col2, col3, col4 = st.columns(4)

    def kpi_box(title, value, color):
        return f"""
        <div style="
            background-color:{color};
            padding:20px;
            border-radius:15px;
            text-align:center;
            color:white;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        ">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
        """

    col1.markdown(kpi_box("Total Cases", total, "#2563EB"),
                  unsafe_allow_html=True)
    col2.markdown(kpi_box("High Risk", high, "#DC2626"),
                  unsafe_allow_html=True)
    col3.markdown(kpi_box("Medium Risk", medium, "#F59E0B"),
                  unsafe_allow_html=True)
    col4.markdown(kpi_box("Low Risk", low, "#16A34A"),
                  unsafe_allow_html=True)

    # =====================================================
    # DISTRICT RISK + COMPARISON (SIDE BY SIDE)
    # =====================================================

    st.markdown("---")
    st.subheader("District Risk Overview")

    colA, colB = st.columns(2)

    with colA:
        if district_risk:

            df = pd.DataFrame(
                district_risk,
                columns=["District", "High", "Medium", "Low"]
            )

            fig, ax = plt.subplots(figsize=(4, 3))

            ax.bar(df["District"], df["High"],
                   label="High", color="#DC2626")

            ax.bar(df["District"], df["Medium"],
                   bottom=df["High"],
                   label="Medium", color="#FBBF24")

            bottom = df["High"] + df["Medium"]

            ax.bar(df["District"], df["Low"],
                   bottom=bottom,
                   label="Low", color="#16A34A")

            ax.set_title("Risk Distribution")
            ax.legend(fontsize=8)
            plt.xticks(rotation=45)
            plt.tight_layout()

            st.pyplot(fig)

        else:
            st.info("No data available")

    with colB:
        if district_compare:

            df2 = pd.DataFrame(
                district_compare,
                columns=["District", "Cases"]
            )

            fig2, ax2 = plt.subplots(figsize=(4, 3))

            ax2.bar(df2["District"],
                    df2["Cases"],
                    color="#2563EB")

            ax2.set_title("Total Cases")
            plt.xticks(rotation=45)
            plt.tight_layout()

            st.pyplot(fig2)

        else:
            st.info("No data available")

    # =====================================================
    # SEVERITY METRICS
    # =====================================================

    st.markdown("---")
    st.subheader("Severity Metrics")

    colX, colY = st.columns(2)

    colX.metric(
        "Average Risk Score",
        round(avg_risk_score, 2) if avg_risk_score else "N/A"
    )

    high_ratio = round((high / total) * 100, 2) if total else 0
    colY.metric("High Risk Ratio (%)", f"{high_ratio}%")

           # =====================================================
    # SMART DOWNLOAD REPORT (AUTO BASED ON FILTER)
    # =====================================================

    import os
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import TableStyle

    st.markdown("---")
    st.subheader("📄 Download Analytics Report")

    if st.button("Download Report"):

        # Dynamic filename
        if selected_district == "All":
            file_name = "maternal_report_all_districts.pdf"
            report_title = "Maternal Health Overall Report"
            district_label = "All Districts"
        else:
            file_name = f"maternal_report_{selected_district}.pdf"
            report_title = f"Maternal Health Report - {selected_district}"
            district_label = selected_district

        doc = SimpleDocTemplate(file_name)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(report_title, styles['Heading1']))
        elements.append(Spacer(1, 0.3 * inch))

        report_data = [
            ["District", district_label],
            ["Total Cases", total],
            ["High Risk Cases", high],
            ["Medium Risk Cases", medium],
            ["Low Risk Cases", low],
            ["Average Risk Score", round(avg_risk_score, 2) if avg_risk_score else "N/A"],
            ["High Risk Ratio (%)", f"{round((high/total)*100,2) if total else 0}%"]
        ]

        table = Table(report_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 10)
        ]))

        elements.append(table)
        doc.build(elements)

        with open(file_name, "rb") as f:
            st.download_button(
                label="Click to Download",
                data=f,
                file_name=file_name,
                mime="application/pdf"
            )

        os.remove(file_name)