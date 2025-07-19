# Simple keyword search agent for traffic rules
rules = []

# Read in the text from your extracted rules
with open("combined_traffic_rules.txt", "r", encoding="utf-8") as f:
    for line in f:
        rules.append(line.strip())

print("Welcome to the Indian Traffic Rules Agent!")
question = input("Type your question about traffic rules: ").lower()

# Try to find a rule that matches a keyword in your question
found = False
for rule in rules:
    if any(word in rule.lower() for word in question.split()):
        print("Answer:", rule)
        found = True

if not found:
    print("Sorry, I don’t know this one yet!")

