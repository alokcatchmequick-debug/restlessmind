from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# 1. Load your rules
rules = []
with open("combined_traffic_rules.txt", "r", encoding="utf-8") as f:
    for line in f:
        rule = line.strip()
        if rule:
            rules.append(rule)

# 2. Prepare ChromaDB (persistent)
chroma_client = chromadb.Client(Settings(
    persist_directory="traffic_chroma_db",
    anonymized_telemetry=False
))

# 3. Use embedding model
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = chroma_client.create_collection(
    name="traffic_rules",
    embedding_function=ef
)

# 4. Add rules to the vector DB
BATCH_SIZE = 5000
for i in range(0, len(rules), BATCH_SIZE):
    batch_rules = rules[i:i+BATCH_SIZE]
    batch_ids = [f"rule_{j}" for j in range(i, i+len(batch_rules))]
    collection.add(
        documents=batch_rules,
        ids=batch_ids
    )

print("Welcome to the Smarter Indian Traffic Rules Agent!")
print("Type 'exit' to quit.")

while True:
    question = input("\nAsk your question: ").strip()
    if question.lower() == "exit":
        break
    # 5. Query: Do semantic search!
    result = collection.query(
        query_texts=[question],
        n_results=3,  # Top 3 most relevant results
    )
    found = result['documents'][0]
    if found:
        print("\nMost relevant answers:")
        for rule in found:
            print("-", rule)
    else:
        print("Sorry, could not find a relevant rule.")
