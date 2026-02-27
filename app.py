import streamlit as st
import requests
import datetime
import json
import urllib.parse

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

# =========================
# 🧰 AGENT TOOLS
# =========================

import webbrowser

def save_note_tool(text):
    with open("notes.txt", "a") as f:
        f.write(text + "\n")
    return "📝 Note saved successfully."

def open_website_tool(url):
    webbrowser.open(url)
    return f"🌐 Opening {url}"

def get_today_date_tool():
    return f"📅 Today's date is {datetime.date.today()}"

#ask_ai
def ask_ai(prompt):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    data = response.json()

    if "error" in data:
        return "API Error: " + str(data["error"])

    return data["choices"][0]["message"]["content"]

# 🌐 Search engines / platforms
SEARCH_ENGINES = {
    "youtube": "https://www.youtube.com/results?search_query={}",
    "google": "https://www.google.com/search?q={}",
    "twitter": "https://twitter.com/search?q={}",
    "spotify": "https://open.spotify.com/search/{}",
    "wikipedia": "https://en.wikipedia.org/wiki/{}"
}

# =========================
# 🧠 AGENT DECISION LAYER
# =========================

import urllib.parse

def agent_router(user_prompt, planner_prompt):
    text = user_prompt.lower()

    # 📝 Save note tool
    if "save note" in text:
        note = user_prompt.replace("save note", "")
        return save_note_tool(note)

    # 🔎 Universal search tool
    if "search" in text and "on" in text:
        try:
            # extract query and platform
            parts = text.split("search")[1].split("on")
            query = parts[0].strip()
            platform = parts[1].strip()

            if platform in SEARCH_ENGINES:
                encoded_query = urllib.parse.quote(query)
                url = SEARCH_ENGINES[platform].format(encoded_query)
                return open_website_tool(url)

            else:
                return f"❌ I don't know how to search on {platform} yet."

        except:
            return "❌ Try: search calculus on youtube"

    # ▶ Open YouTube homepage
    if "open youtube" in text:
        return open_website_tool("https://youtube.com")

    # 🌐 Open Google
    if "open google" in text:
        return open_website_tool("https://google.com")
    
    # ▶ Open Instagram homepage
    if "open instagram" in text:
        return open_website_tool("https://instagram.com")

    # 📅 Date tool
    if "what is today's date" in text:
        return get_today_date_tool()

    # 🤖 Default → AI thinking
    return ask_ai(planner_prompt)


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
    # show user message
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

    # assistant reply with spinner + typing animation
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = agent_router(user_prompt, planner_prompt)

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# Save plan
if st.button("💾 Save Chat", use_container_width=True):
    with open("chat_history.json", "w") as f:
        json.dump(st.session_state.messages, f, indent=2)
    st.success("Chat saved!")

#Load saved chat
if st.button("📂 Load Saved Chat", use_container_width=True):
    try:
        with open("chat_history.json", "r") as f:
            loaded_messages = json.load(f)

        if len(loaded_messages) > 0:
            st.session_state.messages = loaded_messages
            st.success("Chat loaded!")
            st.rerun()
        else:
            st.warning("Saved chat is empty.")
    except FileNotFoundError:
        st.error("No saved chat found yet.")