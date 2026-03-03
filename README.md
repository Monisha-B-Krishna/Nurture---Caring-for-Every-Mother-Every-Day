#  Nurture  
## A Digital Bridge for Pregnancy Risk Monitoring in Rural & Semi-Urban Areas

---

##  Domain
Women’s Health & Maternal Wellness

---

##  Problem Statement

In rural and semi-urban regions, maternal healthcare delivery during pregnancy involves multiple stakeholders:

- Pregnant Women  
- ASHA Workers  
- ANMs (Auxiliary Nurse Midwives)  

Currently, pregnancy registration and maternal data are entered by ANMs into government systems such as ANMOL (Auxiliary Nurse Midwife Online).

Field-level follow-ups are conducted by ASHA workers under schemes like:

- Janani Suraksha Yojana (JSY)  
- Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)  

Despite these initiatives, the operational workflow suffers from fragmentation and lack of intelligence-driven monitoring.

---

##  Core Operational Gaps

###  Gap Between Visits (No Continuous Monitoring)
- ANC checkups are periodic (monthly or scheduled)
- ASHA visits depend on workload
- Monitoring happens only during physical contact
- No real-time health tracking between visits

---

###  Data is Recorded but Not Interpreted
Maternal data such as:
- Blood Pressure (BP)
- Hemoglobin (Hb)
- Weight
- TT doses

 Current Issues:
- No automated risk scoring
- No trend analysis
- No predictive modelling
- No early warning alerts
- Data is stored only for reporting, not intelligence

---

###  No Structured Perinatal Mental Health Screening
- 22–28% perinatal depression prevalence
- No structured mental health screening
- Emotional well-being remains invisible

---

###  ASHA Workload Without Prioritization
- Covers many households
- No dynamic high-risk priority list
- All pregnancies treated similarly unless manually identified

---

###  No Direct Patient Empowerment
- Woman has no app access
- Fully dependent on health worker communication
- No automated reminders
- No personalized guidance

---

# Proposed Solution

## Nurture – Caring for Every Mother, Every Day

Nurture is a Python-based digital system that acts as a bridge between:

- Pregnant Woman  
- ASHA Worker  
- ANM / Nurse  
- Government Admin  

It transforms passive data storage into active, intelligent monitoring.

---

# System Stakeholders & Roles

---

## Woman Role

Login credentials:
- Created and updated by ANM during hospital visits

Features:
- Pregnancy overview dashboard
- View pregnancy stage:
  - Month
  - Week
  - Body Weight
  - BP
  - Blood Sugar
  - Hemoglobin
- Hospital visit reminders
- Food, water & medicine reminders
- Nutrition recommendations (based on month)
- Nutrition gap analysis
- Mental health screening & guidance
- Exercise recommendations
- Nearest hospital locator

---

## ASHA Worker Role

Capabilities:
- View assigned women list
- Priority-based dashboard:
  - Visit Immediately
  - This Week
  - Routine Follow-Up
- Track appointment compliance
- Monitor chatbot alerts
- Identify high-risk women via system-generated scoring

---

## ANM / Nurse Role

Capabilities:
- Approve pregnancy registrations
- Validate medical data
- View complete maternal history
- Monitor high-risk flagged cases
- Track ASHA visit compliance
- Update medical parameters

---

## Admin Role

Capabilities:
- Manage user roles (ANM, ASHA, Woman)
- District-level operational dashboard
- Pregnancy count monitoring
- Generate summary reports
- View risk distribution analytics

---

# Technical Architecture

This prototype is built entirely using:

- Python  
- Streamlit (Frontend + App Logic)  
- SQLite (Database)  
- Pandas (Data processing)  
- NumPy (Numerical operations)  
- Scikit-learn (Risk prediction model)  
- hashlib / bcrypt (Password security)  

---

# Core Intelligence Features

- Automated Risk Scoring  
- Predictive Early Warning System  
- Trend Analysis of Maternal Parameters  
- Mental Health Screening Integration  
- Risk-Based ASHA Task Allocation  
- Continuous Monitoring Between Visits  

---

# Innovation

Nurture converts:

> "Data Collection System" ➜ into ➜ "Data Intelligence System"

Instead of storing maternal data only for reporting, it uses analytics and machine learning to enable early intervention, prioritization, and proactive care.

---

# Future Scope

- State-wide integration  
- Government health dashboard integration  
- SMS-based rural notifications  
- Postpartum depression monitoring  
- Integration with ANMOL data pipelines  

---

# Prototype Status

Hackathon-ready working prototype  
Built fully in Python using Streamlit  

---

## Developed For
Maternal health monitoring and intelligent risk prediction in rural India.

---

