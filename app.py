import streamlit as st
import requests
import datetime
import json

st.set_page_config(
    page_title="Agentic Study Planner",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
.main { background-color: #0E1117; }
.block-container { padding-top: 2rem; }
.stTextInput input { border-radius: 10px; }
.stButton button { 
    border-radius: 12px;
    height: 3em;
    font-weight: bold;
}
.big-title {
    font-size:40px !important;
    font-weight:700;
}
.subtitle {
    color: #9aa0a6;
    margin-bottom:30px;
}
.stTextInput input:focus {
    border: 2px solid #4CAF50 !important;
    box-shadow: none !important;
}

/* Make normal border subtle */
.stTextInput input {
    border: 1px solid #444 !important;
}
/* ADD THESE 👇 */
[data-testid="stForm"] {
    border: 1px solid #222 !important;
}

[data-testid="stForm"] div:focus-within {
    border: none !important;
    box-shadow: none !important;
}

*:focus {
    outline: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# 🔑 Put your OpenRouter key here
OPENROUTER_KEY = st.secrets["OPENROUTER_KEY"]

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://agentic-study-planner.streamlit.app",
    "X-Title": "Agentic Study Planner"
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

    # If API returned an error, show it instead of crashing
    if "error" in data:
        return "API Error: " + str(data["error"])

    # Normal successful response
    if "choices" in data:
        return data["choices"][0]["message"]["content"]

    return str(data)

st.markdown(
    """
    <div style="text-align:center;">
        <p class="big-title">Study Planner</p>
        <p class="subtitle">AI that plans your study schedule and tracks progress</p>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

    
# Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history (now safe)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

today = datetime.date.today()

user_prompt = st.chat_input("Ask me to plan your study schedule...")

if user_prompt:
    # Show user message
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    planner_prompt = f"""
You are a Study Planning AI Agent.
Today's date: {today}
Break goals into tasks and create a daily study schedule.

Conversation history:
{st.session_state.messages}

User: {user_prompt}
"""

    # Assistant reply WITH spinner (now correctly inside the if)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = ask_ai(planner_prompt)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# Save plan
if st.button("💾 Save Plan", use_container_width=True):
    with open("study_plan.json","w") as f:
        json.dump(st.session_state.tasks,f)
    st.success("Saved!")