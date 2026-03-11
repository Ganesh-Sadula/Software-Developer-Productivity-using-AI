import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import numpy as np
import joblib

# =================================================
# PAGE CONFIG (MUST BE FIRST)
# =================================================
st.set_page_config(
    page_title="Task Success Predictor",
    layout="centered"
)

# =================================================
# DATABASE & AUTH FUNCTIONS
# =================================================
def get_db():
    return sqlite3.connect("users.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    # Default admin creation
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "admin")
        )

    conn.commit()
    conn.close()

def register_user(username, password):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), "user")
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT username, role FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    user = cur.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    conn.close()
    return users

# =================================================
# INIT DATABASE
# =================================================
init_db()

# =================================================
# SESSION STATE
# =================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =================================================
# 🔐 AUTH SECTION
# =================================================
if not st.session_state.logged_in:

    st.title("🔐 Login / Registration")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # -------- LOGIN --------
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[1]
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # -------- REGISTER --------
    with tab2:
        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")

        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")

# =================================================
# 🚀 MAIN APP (AFTER LOGIN)
# =================================================
else:

    # ---------------- SIDEBAR ----------------
    st.sidebar.success(f"👤 {st.session_state.username}")
    st.sidebar.write(f"Role: **{st.session_state.role}**")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- ADMIN PANEL ----------------
    if st.session_state.role == "admin":
        st.sidebar.markdown("### 👑 Admin Panel")

        if st.sidebar.button("View Registered Users"):
            users = get_all_users()
            df = pd.DataFrame(users, columns=["ID", "Username", "Role"])
            st.subheader("📋 Registered Users")
            st.dataframe(df)

    # =================================================
    # 🚀 TASK SUCCESS PREDICTOR
    # =================================================
    model = joblib.load('task_success_regression.pkl')

    st.title("🚀 Task Success Predictor")
    st.markdown("Enter the following details to predict your task success score:")

    hours_coding = st.number_input("Hours Coding", min_value=0.0, step=0.1)
    coffee_intake = st.number_input("Coffee Intake (mg)", min_value=0)
    distractions = st.number_input("Distractions", min_value=0)
    sleep_hours = st.number_input("Sleep Hours", min_value=0.0, step=0.1)
    commits = st.number_input("Commits", min_value=0)
    bugs_reported = st.number_input("Bugs Reported", min_value=0)
    ai_usage_hours = st.number_input("AI Usage Hours", min_value=0.0, step=0.1)
    cognitive_load = st.slider("Cognitive Load (0 to 10)", 0.0, 10.0, step=0.1)

    if st.button("Predict Task Success"):
        try:
            features = np.array([[hours_coding, coffee_intake, distractions,
                                  sleep_hours, commits, bugs_reported,
                                  ai_usage_hours, cognitive_load]])

            prediction = model.predict(features)[0]
            st.success(f"🎯 Predicted Task Success Score: {round(prediction, 2)}")

        except Exception as e:
            st.error(f"Prediction failed: {e}")