import streamlit as st
from database.db import get_connection
from google import genai
from models.ml_model import predict_depression
from datetime import datetime

# Gemini Setup
client = genai.Client(api_key="AIzaSyD0x6UECZaycr3Gz2PJWFDs4RQ-d4i_seY")
MODEL = "gemini-2.5-flash"

def generate_notifications(user, pregnancy, mental, cursor):

    if not pregnancy:
        return

    month = pregnancy["month"]
    hb = pregnancy["hb"]
    sugar = pregnancy["sugar"]
    risk = pregnancy["risk_level"]
    mental_prob = mental["probability"] if mental else 0

    notifications = []

    # Trimester alerts
    if month >= 7:
        notifications.append(("Prepare for Delivery",
                              "You are in 3rd trimester. Keep hospital bag ready.",
                              "Medium"))

    # Hb alert
    if hb < 10:
        notifications.append(("Low Hemoglobin",
                              "Iron levels are low. Increase iron intake immediately.",
                              "High"))

    # Sugar alert
    if sugar > 140:
        notifications.append(("High Blood Sugar",
                              "Monitor glucose levels and adjust diet.",
                              "High"))

    # Risk alert
    if risk == "High":
        notifications.append(("High Risk Pregnancy",
                              "Strict monitoring required. Avoid travel.",
                              "High"))

    # Mental alert
    if mental_prob > 0.6:
        notifications.append(("Mental Health Alert",
                              "High stress detected. Consider counseling.",
                              "Medium"))

    # Insert notifications (avoid duplicates same day)
    for title, message, level in notifications:
        cursor.execute("""
            INSERT INTO notifications (woman_id, title, message, level)
            SELECT ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM notifications
                WHERE woman_id=? AND title=? AND DATE(created_at)=DATE('now')
            )
        """, (user["id"], title, message, level,
              user["id"], title))

def woman_dashboard(user):

    

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # Fetch Latest Records
    # -----------------------------------------------------

    pregnancy = cursor.execute("""
        SELECT * FROM pregnancies
        WHERE woman_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user["id"],)).fetchone()

    mental = cursor.execute("""
        SELECT * FROM mental_health
        WHERE woman_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user["id"],)).fetchone()

    # Generate smart notifications automatically
    generate_notifications(user, pregnancy, mental, cursor)
    conn.commit()

    # -----------------------------------------------------
    # Sidebar Features
    # -----------------------------------------------------

    features = [
        "Chatbot Assistant",
        "Complete Health Overview",
        "Mental Health Tracker",
        "Smart Reminders",
        "Nutrition Plan",
        "Exercise Guide",
        "Nearby Hospitals"
    ]

    if "selected_feature" not in st.session_state:
        st.session_state.selected_feature = features[0]

    selected_feature = st.sidebar.radio(
        "Choose Feature",
        features,
        index=features.index(st.session_state.selected_feature)
    )

    st.session_state.selected_feature = selected_feature

    st.title(selected_feature)

    # =====================================================
    # 1️⃣ CHATBOT (FULL PREVIOUS VERSION RESTORED)
    # =====================================================

    if selected_feature == "Chatbot Assistant":

        st.subheader("AI Pregnancy Assistant")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        def pregnancy_bot(message):
            prompt = f"""
            You are Nurture, a calm and responsible maternal health assistant designed for rural and semi-urban pregnant women.

            Your communication rules:
            - Use very simple, easy-to-understand language.
            - Respond in 3 to 4 short bullet points only.
            - Do NOT write long paragraphs.
            - Be supportive and reassuring.
            - Avoid medical jargon.

            Safety Rules:
            If the question contains emergency or severe symptoms such as:
            - heavy bleeding
            - severe abdominal pain
            - unconsciousness
            - no baby movement
            - high fever
            - seizures
            - chest pain
            - difficulty breathing
            - suicide thoughts
            - extreme depression

            Then:
            - Immediately advise contacting the ASHA worker or visiting the nearest hospital.
            - Clearly say: "Please contact your ASHA worker immediately or visit the nearest hospital."
            - Do NOT provide detailed medical instructions in such cases.

            Context Information:
            Pregnancy Risk Level: {pregnancy['risk_level'] if pregnancy else 'Unknown'}
            Mental Health Risk Level: {mental['risk_level'] if mental else 'Unknown'}

            Question from Pregnant Woman:
            {message}

            Now generate the response following all rules strictly.
            """
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )
            return response.text

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask your pregnancy question")
            submitted = st.form_submit_button("Send")

        if submitted and user_input:
            reply = pregnancy_bot(user_input)

            # Store in session (for woman view)
            st.session_state.chat_history.append({
                "question": user_input,
                "answer": reply,
                "time": datetime.now()
            })

            # Store in database (for ASHA/Admin view)
            cursor.execute("""
                INSERT INTO chat_history (woman_id, question, response)
                VALUES (?, ?, ?)
            """, (user["id"], user_input, reply))

            conn.commit()
        # Display chat history
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"**Assistant:** {chat['answer']}")
            st.markdown("---")
            
            

    # =====================================================
    # 2️⃣ COMPLETE HEALTH OVERVIEW
    # =====================================================

    elif selected_feature == "Complete Health Overview":

        if not pregnancy:
            st.warning("No pregnancy record found.")
        else:

            risk_score = pregnancy["risk_score"]
            hb = pregnancy["hb"]
            sugar = pregnancy["sugar"]
            mental_prob = mental["probability"] if mental else 0

            health_score = max(0, min(100,
                (40 - risk_score*5) +
                hb*2 +
                (20 - (sugar-90)*0.2) +
                (20 - mental_prob*20)
            ))

            col1, col2, col3 = st.columns(3)

            col1.metric("Health Score", f"{round(health_score,1)}/100")
            col2.metric("Pregnancy Risk", pregnancy["risk_level"])
            col3.metric("Mental Risk", mental["risk_level"] if mental else "Not Assessed")

            st.markdown("### Clinical Indicators")
            st.write(f"Hemoglobin: {hb}")
            st.write(f"Blood Sugar: {sugar}")

            if health_score < 50:
                st.error("High overall risk. Immediate monitoring required.")
            elif health_score < 75:
                st.warning("Moderate risk. Follow recommendations carefully.")
            else:
                st.success("Health condition stable.")

    # =====================================================
    # 3️⃣ MENTAL HEALTH TRACKER (FULL TRACKER RESTORED)
    # =====================================================

    elif selected_feature == "Mental Health Tracker":

        st.subheader("Perinatal Mental Health Screening")

        mood = st.slider("Mood Level (1=Very Low, 5=Very Good)", 1, 5)
        stress = st.slider("Stress Level (1=Low, 5=Very High)", 1, 5)
        sleep = st.slider("Sleep Quality (1=Poor, 5=Excellent)", 1, 5)

        if st.button("Analyze Mental Health"):

            probability = predict_depression(mood, stress, sleep)

            if probability >= 0.6:
                level = "High Risk"
            elif probability >= 0.35:
                level = "Moderate Risk"
            else:
                level = "Low Risk"

            cursor.execute("""
                INSERT INTO mental_health
                (woman_id, mood, stress, sleep, probability, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user["id"], mood, stress, sleep, probability, level
            ))

            conn.commit()

            st.metric("Depression Risk Probability", f"{round(probability*100,2)}%")

            if level == "High Risk":
                st.error("Counseling recommended.")
            elif level == "Moderate Risk":
                st.warning("Monitor stress levels.")
            else:
                st.success("Mental health stable.")

    # =====================================================
    # 4️⃣ SMART REMINDERS
    # =====================================================

    elif selected_feature == "Smart Reminders":

        st.markdown("## Personalized Daily Care Plan")

        if not pregnancy:
            st.warning("Pregnancy data required for personalized reminders.")
        else:

            month = pregnancy["month"]
            hb = pregnancy["hb"]
            sugar = pregnancy["sugar"]
            risk = pregnancy["risk_level"]

            mental_prob = mental["probability"] if mental else 0

            # -------------------------------------------------
            # DOCTOR VISIT REMINDER
            # -------------------------------------------------

            st.markdown("### Doctor Visit Guidance")

            if month >= 7:
                st.error("Third Trimester: Weekly ANC visit required.")
                st.write("• Keep hospital bag ready")
                st.write("• Confirm delivery hospital")
                st.write("• Keep emergency numbers accessible")

            elif month >= 4:
                st.warning("Second Trimester: Monthly ANC visit required.")
                st.write("• Complete anomaly scan")
                st.write("• Monitor blood pressure")

            else:
                st.info("First Trimester: Early registration essential.")
                st.write("• Take folic acid daily")
                st.write("• Report severe vomiting")

            # -------------------------------------------------
            # WATER INTAKE REMINDER
            # -------------------------------------------------

            st.markdown("### Hydration Reminder")

            st.success("Target: 2.5 – 3 Liters per day (8–10 glasses)")

            if month >= 7:
                st.write("• Increased hydration supports amniotic fluid levels.")
            else:
                st.write("• Maintain steady hydration for circulation.")

            # -------------------------------------------------
            # FOOD INTAKE REMINDER
            # -------------------------------------------------

            st.markdown("### Nutrition Monitoring")

            if hb < 10:
                st.error("Low Hemoglobin Detected")
                st.write("• Include spinach, lentils, jaggery")
                st.write("• Take iron tablets regularly")
                st.write("• Repeat Hb test next visit")

            elif sugar > 140:
                st.error("High Blood Sugar Detected")
                st.write("• Avoid sugary drinks")
                st.write("• Prefer millets over white rice")
                st.write("• Walk 20-30 minutes daily")

            else:
                st.success("Balanced Nutritional Status")
                st.write("• 3 balanced meals + 2 healthy snacks")
                st.write("• Include protein in each meal")

            # -------------------------------------------------
            # TABLET INTAKE REMINDER
            # -------------------------------------------------

            st.markdown("### Supplement & Tablet Intake")

            st.warning("Daily Supplements Required:")
            st.write("• Iron & Folic Acid")
            st.write("• Calcium")
            st.write("• Vitamin D (if prescribed)")

            if hb < 10:
                st.write("• Strict adherence to iron tablets required")

            # -------------------------------------------------
            # MENTAL WELLNESS REMINDER
            # -------------------------------------------------

            st.markdown("### Mental Wellness Check")

            if mental_prob > 0.6:
                st.error("High Stress Level Detected")
                st.write("• Consider counseling")
                st.write("• Practice breathing exercises twice daily")

            elif mental_prob > 0.35:
                st.warning("Moderate Stress Level")
                st.write("• Try 10-minute relaxation session daily")

            else:
                st.success("Mental health stable")
                st.write("• Maintain positive routines")

            # -------------------------------------------------
            # HIGH-RISK ALERT
            # -------------------------------------------------

            if risk == "High":
                st.markdown("### High Risk Monitoring")
                st.error("Avoid heavy physical activity")
                st.error("Avoid long-distance travel")
                st.error("Follow strict medical supervision")


    # =====================================================
    # 5️⃣ NUTRITION PLAN
    # =====================================================

    elif selected_feature == "Nutrition Plan":

        if pregnancy:

            st.subheader("Personalized Nutrition Intelligence")

            month = pregnancy["month"]
            hb = pregnancy["hb"]
            sugar = pregnancy["sugar"]

            # -----------------------------
            # Base Calories by Trimester
            # -----------------------------

            if month <= 3:
                base_calories = 2200
                trimester_note = "1st Trimester: Focus on folic acid & nausea-friendly foods."
            elif month <= 6:
                base_calories = 2500
                trimester_note = "2nd Trimester: Rapid fetal growth phase."
            else:
                base_calories = 2800
                trimester_note = "3rd Trimester: Higher energy & protein demand."

            adjustment_note = ""

            # -----------------------------
            # Personal Adjustments
            # -----------------------------

            if hb < 10:
                base_calories += 200
                adjustment_note += "Increased calories due to low Hemoglobin. "

            if sugar > 140:
                carb_ratio = 0.40
                adjustment_note += "Reduced carbohydrate ratio due to high sugar. "
            else:
                carb_ratio = 0.50

            protein_ratio = 0.20
            fat_ratio = 1 - carb_ratio - protein_ratio

            protein = round(base_calories * protein_ratio / 4)
            carbs = round(base_calories * carb_ratio / 4)
            fats = round(base_calories * fat_ratio / 9)

            # -----------------------------
            # Display Core Metrics
            # -----------------------------

            col1, col2 = st.columns(2)

            col1.metric("Daily Calorie Goal", f"{base_calories} kcal")
            col2.metric("Protein Requirement", f"{protein} g")

            st.info(trimester_note)

            if adjustment_note:
                st.warning(adjustment_note)

            # -----------------------------
            # Macro Breakdown
            # -----------------------------

            st.markdown("### Macronutrient Distribution")
            st.write(f"Carbohydrates: {carbs} g")
            st.write(f"Fats: {fats} g")

            # -----------------------------
            # Meal Split Plan
            # -----------------------------

            st.markdown("### Suggested Meal Calorie Split")

            breakfast = round(base_calories * 0.25)
            lunch = round(base_calories * 0.30)
            snack = round(base_calories * 0.15)
            dinner = round(base_calories * 0.30)

            st.write(f"Breakfast: {breakfast} kcal")
            st.write(f"Lunch: {lunch} kcal")
            st.write(f"Evening Snack: {snack} kcal")
            st.write(f"Dinner: {dinner} kcal")

            # -----------------------------
            # Condition-Based Suggestions
            # -----------------------------

            st.markdown("### Targeted Food Recommendations")

            if hb < 10:
                st.error("Low Hemoglobin Detected")
                st.write("✔ Spinach")
                st.write("✔ Dates")
                st.write("✔ Lentils")
                st.write("✔ Jaggery")

            if sugar > 140:
                st.error("High Blood Sugar Detected")
                st.write("✔ Millets instead of white rice")
                st.write("✔ Avoid sugary drinks")
                st.write("✔ Increase fiber intake")

            if hb >= 10 and sugar <= 140:
                st.success("Balanced Nutrition Status")

        else:
            st.warning("Pregnancy record required for personalized nutrition.")    

    # =====================================================
    # 6️⃣ EXERCISE GUIDE
    # =====================================================
    elif selected_feature == "Exercise Guide":

        if not pregnancy:
            st.warning("Pregnancy record required for exercise guidance.")
        else:

            month = pregnancy["month"]
            risk = pregnancy["risk_level"]

            st.markdown("### Personalized Exercise Intelligence")

            # -----------------------------
            # Trimester Classification
            # -----------------------------

            if month <= 3:
                trimester = "First Trimester"
                goal = "Maintain circulation & reduce nausea fatigue."
            elif month <= 6:
                trimester = "Second Trimester"
                goal = "Improve strength & posture stability."
            else:
                trimester = "Third Trimester"
                goal = "Prepare body for labor & improve breathing control."

            st.write(f"Trimester: {trimester}")
            st.info(f"Primary Goal: {goal}")

            # -----------------------------
            # Risk-Based Modification
            # -----------------------------

            if risk == "High":
                st.error("High Risk Pregnancy: Restricted activity recommended.")
                st.write("Allowed:")
                st.write("- 10-15 min slow walking")
                st.write("- Deep breathing exercises")
                st.write("- Gentle ankle rotations")
                st.write("Avoid:")
                st.write("- Squats")
                st.write("- Core workouts")
                st.write("- Heavy lifting")

            elif risk == "Medium":
                st.warning("Moderate Risk: Controlled intensity recommended.")
                st.write("Recommended:")
                st.write("- 20 min walking")
                st.write("- Light prenatal yoga")
                st.write("- Pelvic floor exercises")

            else:
                st.success("Low Risk: Standard prenatal routine allowed.")
                st.write("Recommended:")
                st.write("- 30 min brisk walking")
                st.write("- Prenatal yoga")
                st.write("- Light strength training")
                st.write("- Pelvic floor strengthening")

            # -----------------------------
            # Weekly Structure Plan
            # -----------------------------

            st.markdown("### Suggested Weekly Structure")

            st.write("3-5 days: Walking")
            st.write("2-3 days: Prenatal yoga")
            st.write("Daily: 5 min breathing exercises")

            # -----------------------------
            # Trimester-Specific Focus
            # -----------------------------

            st.markdown("### Trimester Focus")

            if month <= 3:
                st.write("Focus on circulation & nausea control.")
                st.write("Avoid overheating and high intensity.")
            elif month <= 6:
                st.write("Focus on posture correction & back pain prevention.")
            else:
                st.write("Focus on hip flexibility & breathing for labor.")

            # -----------------------------
            # Recommended YouTube Videos
            # -----------------------------

            st.markdown("### Recommended Guided Sessions")

            if month <= 3:
                st.write("Prenatal Yoga First Trimester:")
                st.write("https://www.youtube.com/watch?v=2T5wF9Rr3gA")

            elif month <= 6:
                st.write("Prenatal Yoga Second Trimester:")
                st.write("https://www.youtube.com/watch?v=44fYnoSLL9c")

            else:
                st.write("Prenatal Yoga Third Trimester:")
                st.write("https://www.youtube.com/watch?v=6ZJp6C0qD7E")

            st.write("Breathing Exercises for Pregnancy:")
            st.write("https://www.youtube.com/watch?v=DbDoBzGY3vo")

            # -----------------------------
            # Safety Alert
            # -----------------------------

            st.markdown("---")
            st.markdown("### When to Stop Exercising")

            st.write("- Dizziness")
            st.write("- Vaginal bleeding")
            st.write("- Severe abdominal pain")
            st.write("- Reduced fetal movement")

            st.warning("Always consult ANM or doctor before starting new exercise routine.")

    # =====================================================
    # 7️⃣ NEARBY HOSPITALS
    # =====================================================

    elif selected_feature == "Nearby Hospitals":

        st.subheader("Nearby Hospitals & Emergency Support")

        # -------------------------------------------------
        # Static Hospital Infrastructure Data (Demo Mode)
        # -------------------------------------------------

        hospital_data = {
            "Chennai": [
                {
                    "name": "Government General Hospital",
                    "phone": "044-25305000",
                    "ambulance": "108",
                    "ambulance_count": 12
                },
                {
                    "name": "Apollo Hospital Chennai",
                    "phone": "044-28293333",
                    "ambulance": "1860-500-1066",
                    "ambulance_count": 8
                }
            ],
            "Coimbatore": [
                {
                    "name": "Coimbatore Medical College Hospital",
                    "phone": "0422-2301393",
                    "ambulance": "108",
                    "ambulance_count": 6
                },
                {
                    "name": "Ganga Hospital",
                    "phone": "0422-2485000",
                    "ambulance": "0422-2485001",
                    "ambulance_count": 5
                }
            ],
            "Madurai": [
                {
                    "name": "Government Rajaji Hospital",
                    "phone": "0452-2533430",
                    "ambulance": "108",
                    "ambulance_count": 7
                },
                {
                    "name": "Meenakshi Mission Hospital",
                    "phone": "0452-4263000",
                    "ambulance": "0452-4263010",
                    "ambulance_count": 4
                }
            ],
            "Salem": [
                {
                    "name": "Government Mohan Kumaramangalam Hospital",
                    "phone": "0427-2340150",
                    "ambulance": "108",
                    "ambulance_count": 5
                },
                {
                    "name": "SKS Hospital Salem",
                    "phone": "0427-4033333",
                    "ambulance": "0427-4033344",
                    "ambulance_count": 3
                }
            ]
        }

        district = user["district"]

        if district in hospital_data:

            hospitals = hospital_data[district]

            total_ambulances = 0

            for h in hospitals:

                st.markdown(f"### {h['name']}")
                st.write(f"Emergency Contact: {h['phone']}")
                st.write(f"Ambulance Contact: {h['ambulance']}")
                st.write(f"Ambulances Available: {h['ambulance_count']}")
                st.markdown("---")

                total_ambulances += h["ambulance_count"]

            st.metric("Total Hospitals in District", len(hospitals))
            st.metric("Total Ambulances Available", total_ambulances)

            st.info("For immediate emergency, dial 108.")

        else:
            st.warning("No hospital infrastructure data available for your district.")

    conn.close()