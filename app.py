import streamlit as st
import requests
import json

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
        return None

    if res.status_code >= 400:
        st.error(data)
        return None

    return data


# ------------------ CREATE PROFILE ------------------

if st.button("Create Profile"):
    if not name or not goal or not style:
        st.warning("Please fill all fields.")
    else:
        payload = {
            "name": name,
            "age": age,
            "level": level,
            "goal": goal,
            "learning_style": style
        }

        res = requests.post(f"{API_URL}/student-profile", json=payload)
        data = show_response(res)

        if data:
            st.success("Profile created successfully")
            st.subheader("Student Profile")
            st.json(data)


# ------------------ GENERATE LESSON ------------------

if st.button("Generate Lesson"):
    if not name:
        st.warning("Enter student name first.")
    else:
        res = requests.post(
            f"{API_URL}/lesson-plan",
            json={"student_name": name}
        )

        data = show_response(res)

        if data:
            st.success("Lesson generated successfully")

            st.subheader("Student")
            st.write(data.get("student"))

            st.subheader("Lesson Plan")

            lesson_plan_raw = data.get("lesson_plan", "{}")

            try:
                lesson_plan = json.loads(lesson_plan_raw)

                st.markdown(f"### 🎼 {lesson_plan.get('lesson_title', 'Lesson')}")

                st.markdown("### 📘 Concept Explanation")
                st.write(lesson_plan.get("concept_explanation", ""))

                st.markdown("### 🎯 Practice Plan")
                for step in lesson_plan.get("practice_plan", []):
                    st.write(f"- {step}")

                st.markdown("### ⚠️ Common Mistakes")
                for mistake in lesson_plan.get("common_mistakes", []):
                    st.write(f"- {mistake}")

                st.markdown("### 📝 Homework")
                st.write(lesson_plan.get("homework", ""))

                st.markdown("### 🚀 Next Step")
                st.write(lesson_plan.get("next_step", ""))

            except Exception:
                # fallback if parsing fails
                st.write(lesson_plan_raw)