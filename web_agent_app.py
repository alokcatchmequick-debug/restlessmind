import streamlit as st
import requests
import datetime
from google import genai

#-------------- Set Up APIs and Load Rules --------------
TRACXN_API_TOKEN = "a3797606-a2ba-43b0-b270-a579116a3637"
GEMINI_API_KEY = "AIzaSyCvulPIv89YIEaF5-5T3Ne8u5CS6zPHO94"
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    with open("combined_traffic_rules.txt", "r", encoding="utf-8") as f:
        rules = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    st.error("combined_traffic_rules.txt not found in this folder!")
    rules = []

#-------------- Utility Functions --------------

def local_search(question):
    matches = []
    q_words = [w.lower() for w in question.split()]
    for rule in rules:
        rule_lower = rule.lower()
        if any(qw in rule_lower for qw in q_words):
            matches.append(rule)
    return matches[:3]

def gemini_answer(question):
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=question)
        return response.text
    except Exception as e:
        return f"Gemini error: {e}"

def tracxn_search(question):
    url = "https://platform.tracxn.com/api/2.2/playground/search_companies"
    headers = {"Authorization": f"Bearer {TRACXN_API_TOKEN}"}
    params = {"query": question}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return f"Tracxn error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Tracxn error: {e}"

def log_interaction(question, answer, logfile="chat_log.txt"):
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - Q: {question}\n")
        f.write(f"A: {answer}\n\n")

#-------------- Streamlit App UI and Logic --------------

st.title("AI Traffic Rules & Company Agent 🚦🤖")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_q = st.text_input("Ask your traffic/business/AI question:")

if st.button("Submit") and user_q:
    local_results = local_search(user_q)
    gemini_result = gemini_answer(user_q)
    tracxn_result = tracxn_search(user_q)

    # Display answers
    st.subheader("Local Database Answer 🗂️")
    if local_results:
        for r in local_results:
            st.write("-", r)
    else:
        st.write("No match in local rules.")

    st.subheader("Gemini AI Answer 🤖")
    st.write(gemini_result)

    st.subheader("Tracxn API Data 💼")
    st.write(tracxn_result)

    # Save to chat history (shows in app)
    st.session_state['chat_history'].append((user_q, gemini_result))

    # Save to log file
    log_interaction(user_q, gemini_result)

# Show chat history
if st.session_state['chat_history']:
    st.write("---")
    st.write("### Chat History")
    for idx, pair in enumerate(st.session_state['chat_history']):
        st.markdown(f"**You:** {pair[0]}")
        st.markdown(f"**Agent:** {pair[1]}")
        st.write(" ")
