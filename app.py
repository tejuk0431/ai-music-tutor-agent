import streamlit as st
import requests

API_URL = "https://ai-music-tutor-agent.onrender.com"

st.title("🎵 AI Music Tutor Agent")

name = st.text_input("Student Name")
age = st.number_input("Age", min_value=3, max_value=100)
level = st.selectbox("Level", ["beginner", "intermediate"])
goal = st.text_input("Goal")
style = st.text_input("Learning Style")

if st.button("Create Profile"):
    data = {
        "name": name,
        "age": age,
        "level": level,
        "goal": goal,
        "learning_style": style
    }
    res = requests.post(f"{API_URL}/student-profile", json=data)
    st.write(res.json())

if st.button("Generate Lesson"):
    res = requests.post(
        f"{API_URL}/lesson-plan",
        json={"student_name": name}
    )
    st.write(res.json())