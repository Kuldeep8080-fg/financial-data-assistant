# services/vector_search_service.py
import faiss
import numpy as np
import json
from pathlib import Path
from .embedding_service import compute_embeddings, load_transactions

INDEX_PATH = "embeddings/faiss_index.faiss"
META_PATH = "embeddings/metadata.json"

# Cache metadata in memory
_cached_meta = None

def build_faiss_index():
    txns = load_transactions()
    embs = compute_embeddings(txns)
    # normalize for cosine similarity with inner-product search
    faiss.normalize_L2(embs)
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner-product, works with normalized vectors for cosine
    index.add(embs.astype('float32'))
    Path("embeddings").mkdir(exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    # store metadata mapping by vector index -> txn JSON
    with open(META_PATH, "w") as f:
        json.dump(txns, f, indent=2)
    print("Saved FAISS index and metadata")

def search(query_embedding, top_k=5):
    try:
        index = faiss.read_index(INDEX_PATH)
    except Exception as e:
        raise FileNotFoundError(f"FAISS index not found at {INDEX_PATH}. Run build_faiss_index() first. Error: {e}")
    # normalize query
    faiss.normalize_L2(query_embedding)
    D, I = index.search(query_embedding.astype('float32'), top_k)
    # load metadata (use cache if available)
    global _cached_meta
    if _cached_meta is None:
        try:
            with open(META_PATH) as f:
                _cached_meta = json.load(f)
        except Exception as e:
            raise FileNotFoundError(f"Metadata not found at {META_PATH}. Run build_faiss_index() first. Error: {e}")
    results = [_cached_meta[i] for i in I[0]]
    return results, D[0]

if __name__ == "__main__":
    build_faiss_index()