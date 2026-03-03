import streamlit as st
from database.schema import create_tables
from services.auth_service import authenticate_user, create_user
from database.db import get_connection

# Import dashboards
from dashboards.woman import woman_dashboard
from dashboards.asha import asha_dashboard
from dashboards.anm import anm_dashboard
from dashboards.admin import admin_dashboard

st.set_page_config(page_title="Nurture - Maternal Care System", layout="wide")

# Ensure DB tables exist
create_tables()

# -----------------------------
# SESSION STATE
# -----------------------------

if "user" not in st.session_state:
    st.session_state.user = None


# -----------------------------
# LOGIN PAGE
# -----------------------------

def login_page():
    st.title("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        user = authenticate_user(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid credentials")


# -----------------------------
# SIGNUP PAGE
# -----------------------------

def signup_page():
    st.title("Create User")

    name = st.text_input("Name", key="signup_name")
    username = st.text_input("Username", key="signup_username")
    password = st.text_input("Password", type="password", key="signup_password")

    # Role selection (display uppercase, store lowercase)
    role_display = st.selectbox(
        "Role",
        ["Woman", "ASHA", "ANM", "Admin"],
        key="signup_role"
    )

    district = st.selectbox(
        "Select District",
        ["Chennai", "Coimbatore", "Madurai", "Salem"],
        key="signup_district"
    )

    if st.button("Create User", key="signup_button"):

        create_user(
            name=name,
            username=username,
            password=password,
            role=role_display.lower(),   # 🔥 enforce lowercase
            district=district
        )

        st.success("User created successfully")


# -----------------------------
# MAIN ROUTING
# -----------------------------

if st.session_state.user is None:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        login_page()

    with tab2:
        signup_page()

else:

    user = st.session_state.user
    role = user["role"].lower()

    # -----------------------------------
    # SIDEBAR PROFILE SECTION (NEW)
    # -----------------------------------

    with st.sidebar.expander(f"👤 Logged in as: {user['name']}", expanded=False):

        conn = get_connection()
        cursor = conn.cursor()

        st.write("### Profile Details")
        st.write(f"Name: {user['name']}")
        st.write(f"Username: {user['username']}")
        st.write(f"Role: {role.capitalize()}")
        st.write(f"District: {user['district']}")

        # Extra details for Woman
        if role == "woman":

            # Assigned ASHA
            if user["asha_id"]:
                asha = cursor.execute("""
                    SELECT name FROM users WHERE id=?
                """, (user["asha_id"],)).fetchone()

                if asha:
                    st.write(f"Assigned ASHA: {asha['name']}")
                else:
                    st.write("Assigned ASHA: Not Assigned")
            else:
                st.write("Assigned ASHA: Not Assigned")

            # Latest pregnancy risk
            pregnancy = cursor.execute("""
                SELECT risk_level FROM pregnancies
                WHERE woman_id=?
                ORDER BY created_at DESC
                LIMIT 1
            """, (user["id"],)).fetchone()

            if pregnancy:
                st.write(f"Current Risk Level: {pregnancy['risk_level']}")
            else:
                st.write("Current Risk Level: Not Recorded")

        conn.close()

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    # -----------------------------
    # DASHBOARD ROUTING
    # -----------------------------

    if role == "woman":
        woman_dashboard(user)

    elif role == "asha":
        asha_dashboard(user)

    elif role == "anm":
        anm_dashboard(user)

    elif role == "admin":
        admin_dashboard(user)