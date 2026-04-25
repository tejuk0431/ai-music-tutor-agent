from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
import json

app = FastAPI(title="AI Personalized Music Tutor Agent")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_FILE = "student_data.json"


@app.get("/")
def home():
    return {
        "message": "AI Personalized Music Tutor Agent is running"
    }
class StudentProfile(BaseModel):
    name: str
    age: int
    level: str
    goal: str
    learning_style: str


class LessonRequest(BaseModel):
    student_name: str


class QuizRequest(BaseModel):
    student_name: str
    topic: str


class ProgressUpdate(BaseModel):
    student_name: str
    completed_lesson: str
    mistakes: str
    confidence_level: int
def load_data():
    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def find_student(name):
    data = load_data()

    for student in data["students"]:
        if student["name"].lower() == name.lower():
            return student

    return None
@app.post("/student-profile")
def create_student_profile(profile: StudentProfile):
    data = load_data()

    existing_student = find_student(profile.name)

    if existing_student:
        raise HTTPException(
            status_code=400,
            detail="Student profile already exists"
        )

    new_student = {
        "name": profile.name,
        "age": profile.age,
        "level": profile.level,
        "goal": profile.goal,
        "learning_style": profile.learning_style,
        "completed_lessons": [],
        "mistakes": [],
        "confidence_history": []
    }

    data["students"].append(new_student)
    save_data(data)

    return {
        "message": "Student profile created successfully",
        "student": new_student
    }
@app.post("/lesson-plan")
def generate_lesson_plan(request: LessonRequest):
    student = find_student(request.student_name)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    prompt = f"""
You are an AI music tutor agent.

Your job:
- Analyze the student
- Decide what they need next
- Generate a structured lesson

Student:
Name: {student["name"]}
Age: {student["age"]}
Level: {student["level"]}
Goal: {student["goal"]}
Learning style: {student["learning_style"]}
Completed lessons: {student["completed_lessons"]}
Mistakes: {student["mistakes"]}

Return response in JSON format:

{{
  "lesson_title": "...",
  "concept_explanation": "...",
  "practice_plan": ["step1", "step2"],
  "common_mistakes": ["..."],
  "homework": "...",
  "next_step": "..."
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a patient beginner music tutor specializing in Carnatic music foundations."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "student": student["name"],
        "lesson_plan": response.choices[0].message.content
    }
@app.post("/quiz")
def generate_quiz(request: QuizRequest):
    student = find_student(request.student_name)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    prompt = f"""
    Create a beginner-friendly quiz for a music student.

    Student:
    Name: {student["name"]}
    Level: {student["level"]}
    Goal: {student["goal"]}

    Topic: {request.topic}

    Create:
    - 5 simple questions
    - Answer key
    - 1 practice activity
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You create simple beginner music quizzes."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "student": student["name"],
        "topic": request.topic,
        "quiz": response.choices[0].message.content
    }
@app.post("/progress")
def update_progress(progress: ProgressUpdate):
    data = load_data()

    for student in data["students"]:
        if student["name"].lower() == progress.student_name.lower():
            student["completed_lessons"].append(progress.completed_lesson)
            student["mistakes"].append(progress.mistakes)
            student["confidence_history"].append(progress.confidence_level)

            save_data(data)

            return {
                "message": "Progress updated successfully",
                "student": student
            }

    raise HTTPException(
        status_code=404,
        detail="Student not found"
    )
@app.post("/recommend-next-step")
def recommend_next_step(request: LessonRequest):
    student = find_student(request.student_name)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    prompt = f"""
    Recommend the next best learning step for this music student.

    Student profile:
    {student}

    Consider:
    - Completed lessons
    - Mistakes
    - Confidence history
    - Learning goal

    Return:
    1. Recommended next topic
    2. Why this topic is next
    3. Practice plan for 3 days
    4. Warning signs to watch for
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an AI learning coach that recommends personalized next steps."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {
        "student": student["name"],
        "recommendation": response.choices[0].message.content
    }
