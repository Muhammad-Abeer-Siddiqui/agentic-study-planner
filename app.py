import streamlit as st
import requests
import datetime
import json

# 🔑 Put your OpenRouter key here
OPENROUTER_KEY = st.secrets["OPENROUTER_KEY"]

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json"
}

def ask_ai(prompt):
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    data = response.json()
    return data["choices"][0]["message"]["content"]

st.set_page_config(page_title="Agentic Study Planner", layout="wide")
st.title("🎓 Agentic AI Study Planner (100% FREE CLOUD)")

# Memory
if "history" not in st.session_state:
    st.session_state.history = ""

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "completed" not in st.session_state:
    st.session_state.completed = []

today = datetime.date.today()

user_input = st.text_input("Enter your study goal")

if st.button("Run Agent") and user_input:

    planner_prompt = f"""
You are a Study Planning AI Agent.
Today's date: {today}
Break goals into tasks and create a daily study schedule.

Conversation history:
{st.session_state.history}

User: {user_input}
"""

    plan = ask_ai(planner_prompt)

    st.write("## 📋 Study Plan")
    st.write(plan)

    st.session_state.history += f"\nUser:{user_input}\nAI:{plan}"
    st.session_state.tasks.append(plan)

# Task tracker
st.write("## ✅ Task Tracker")
for i, task in enumerate(st.session_state.tasks):
    done = st.checkbox(task, key=i)
    if done and task not in st.session_state.completed:
        st.session_state.completed.append(task)

# Progress bar
if st.session_state.tasks:
    progress = len(st.session_state.completed)/len(st.session_state.tasks)
    st.progress(progress)

# Save plan
if st.button("Save Plan"):
    with open("study_plan.json","w") as f:
        json.dump(st.session_state.tasks,f)
    st.success("Saved!")