import streamlit as st
import requests

API_URL = "https://ai-music-tutor-agent.onrender.com"

st.title("🎵 AI Music Tutor Agent")
st.info("Create a student profile first, then generate a personalized lesson.")

name = st.text_input("Student Name")
age = st.number_input("Age", min_value=3, max_value=100)
level = st.selectbox("Level", ["beginner", "intermediate"])
goal = st.text_input("Goal")
style = st.text_input("Learning Style")


def show_response(res):
    try:
        data = res.json()
    except Exception:
        st.error("Backend did not return JSON.")
        st.write("Status code:", res.status_code)
        st.write("Raw response:", res.text)
        return

    if res.status_code >= 400:
        st.error(data)
    else:
        st.success("Success")
        st.write(data)


if st.button("Create Profile"):
    if not name or not goal or not style:
        st.warning("Please fill all fields.")
    else:
        data = {
            "name": name,
            "age": age,
            "level": level,
            "goal": goal,
            "learning_style": style
        }

        res = requests.post(f"{API_URL}/student-profile", json=data)
        show_response(res)


if st.button("Generate Lesson"):
    if not name:
        st.warning("Enter student name first.")
    else:
        res = requests.post(
            f"{API_URL}/lesson-plan",
            json={"student_name": name}
        )
        show_response(res)