import requests
from google import genai

# Set up your API keys/tokens
TRACXN_API_TOKEN = "a3797606-a2ba-43b0-b270-a579116a3637"
GEMINI_API_KEY = "AIzaSyCvulPIv89YIEaF5-5T3Ne8u5CS6zPHO94"
client = genai.Client(api_key=GEMINI_API_KEY)

# Load local rules
with open("combined_traffic_rules.txt", "r", encoding="utf-8") as f:
    rules = [line.strip() for line in f if line.strip()]

def local_search(question):
    matches = [rule for rule in rules if any(word in rule.lower() for word in question.lower().split())]
    return matches[:3]

def gemini_answer(question):
    response = client.models.generate_content(model="gemini-2.5-flash", contents=question)
    return response.text

def tracxn_search(question):
    url = "https://platform.tracxn.com/api/2.2/playground/search_companies"
    headers = {"Authorization": f"Bearer {TRACXN_API_TOKEN}"}
    params = {"query": question}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

while True:
    question = input("\nAsk your question (or type 'exit'): ")
    if question.lower().strip() == 'exit': break

    # 1. Local results
    local_results = local_search(question)
    # 2. Gemini answer
    gemini_result = gemini_answer(question)
    # 3. Tracxn data
    tracxn_result = tracxn_search(question)

    print("\n--- Local Database Results ---")
    if local_results:
        for rule in local_results:
            print("-", rule)
    else:
        print("No match in local rules.")

    print("\n--- Gemini AI Answer ---")
    print(gemini_result)

    print("\n--- Tracxn API Data ---")
    print(tracxn_result)

