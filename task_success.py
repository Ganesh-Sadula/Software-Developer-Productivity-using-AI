
import streamlit as st
import joblib
import numpy as np

# Load the saved regression model
model = joblib.load('task_success_regression.pkl')

st.title("Task Success Predictor")
st.markdown("Enter the following details to predict your task success score:")

# Input fields
hours_coding = st.number_input("Hours Coding", min_value=0.0, step=0.1)
coffee_intake = st.number_input("Coffee Intake (mg)", min_value=0)
distractions = st.number_input("Distractions", min_value=0)
sleep_hours = st.number_input("Sleep Hours", min_value=0.0, step=0.1)
commits = st.number_input("Commits", min_value=0)
bugs_reported = st.number_input("Bugs Reported", min_value=0)
ai_usage_hours = st.number_input("AI Usage Hours", min_value=0.0, step=0.1)
cognitive_load = st.slider("Cognitive Load (0 to 10)", 0.0, 10.0, step=0.1)

# Predict button
if st.button("Predict Task Success"):
    try:
        features = np.array([[hours_coding, coffee_intake, distractions, sleep_hours,
                              commits, bugs_reported, ai_usage_hours, cognitive_load]])
        prediction = model.predict(features)[0]
        st.success(f"Predicted Task Success: {round(prediction, 2)}")
    except Exception as e:
        st.error(f"Prediction failed: {e}")
