# services/embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np
import json
from pathlib import Path

# Load the model
model = SentenceTransformer("all-MiniLM-L6-v2")

def txn_to_text(txn):
    """
    Convert a transaction dict to a single string suitable for embedding
    """
    return f"{txn['type']} of ₹{txn['amount']} on {txn['date']} for {txn['description']} under {txn['category']} category."


def load_transactions(path="data/transactions.json"):
    """
    Load your transactions JSON file
    """
    return json.loads(Path(path).read_text())

def compute_embeddings(transactions):
    """
    Generate embeddings for a list of transaction dicts
    """
    texts = [txn_to_text(t) for t in transactions]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings

def save_embeddings(embeddings, path="embeddings/embeddings.npy"):
    Path("embeddings").mkdir(exist_ok=True)
    np.save(path, embeddings)
    print(f"Saved embeddings at {path}")

if __name__ == "__main__":
    txns = load_transactions()
    embs = compute_embeddings(txns)
    save_embeddings(embs)