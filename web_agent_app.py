import streamlit as st
import requests
import datetime
import json
import google.generativeai as genai

# ------------ SETUP API KEYS AND LOAD LOCAL RULES ---------------
TRACXN_API_TOKEN = "a3797606-a2ba-43b0-b270-a579116a3637"
GEMINI_API_KEY = "a3797606-a2ba-43b0-b270-a579116a3637"
genai.configure(api_key=GEMINI_API_KEY)


try:
    with open("combined_traffic_rules.txt", "r", encoding="utf-8") as f:
        rules = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    st.error("combined_traffic_rules.txt not found in this folder!")
    rules = []

# ---------- GEMINI MEMORY FUNCTIONS (copy these) ----------
def save_gemini_answer(question, answer, path="gemini_qa.jsonl"):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"question": question, "answer": answer}) + "\n")

def load_gemini_qa(path="gemini_qa.jsonl"):
    pairs = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                pairs.append(json.loads(line))
    except FileNotFoundError:
        pass
    return pairs

def search_gemini_local_db(user_question, qa_pairs, max_results=3):
    user_q_lower = user_question.lower()
    results = []
    for qa in qa_pairs:
        if any(word in qa["question"].lower() for word in user_q_lower.split()):
            results.append(qa)
    return results[:max_results]

# ----- LOAD GEMINI MEMORY ON APP START -----
qa_pairs = load_gemini_qa()

# ---------- YOUR USUAL HELPER FUNCTIONS ----------
def local_search(question):
    matches = []
    q_words = [w.lower() for w in question.split()]
    for rule in rules:
        rule_lower = rule.lower()
        if any(qw in rule_lower for qw in q_words):
            matches.append(rule)
    return matches[:3]

def gemini_answer(question):
    model = genai.GenerativeModel("gemini-1.5-flash")  # or gemini-1.5-pro or gemini-1.0-pro
    response = model.generate_content(question)
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

# ---------------- STREAMLIT UI CODE -----------------
st.title("AI Traffic Rules & Company Agent 🚦🤖")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_q = st.text_input("Ask your traffic/business/AI question:")

if st.button("Submit") and user_q:
    # 1. First, check memory for Gemini answer:
    offline_results = search_gemini_local_db(user_q, qa_pairs)
    if offline_results:
        gemini_result = offline_results[0]["answer"]
        st.info("Answer provided by: Boi")

    else:
        gemini_result = gemini_answer(user_q)
        save_gemini_answer(user_q, gemini_result)  # save for future
        qa_pairs.append({"question": user_q, "answer": gemini_result})

    # Normal output for all three sources
    local_results = local_search(user_q)
    tracxn_result = tracxn_search(user_q)

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

    # Save to chat history & log
    st.session_state['chat_history'].append((user_q, gemini_result))
    log_interaction(user_q, gemini_result)

if st.session_state['chat_history']:
    st.write("---")
    st.write("### Chat History")
    for idx, pair in enumerate(st.session_state['chat_history']):
        st.markdown(f"**You:** {pair[0]}")
        st.markdown(f"**Agent:** {pair[1]}")
        st.write(" ")

