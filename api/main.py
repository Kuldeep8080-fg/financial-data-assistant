# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from services.embedding_service import model
from services.vector_search_service import search
import numpy as np
import faiss
import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY", "")

app = FastAPI()

class Query(BaseModel):
    query: str
    top_k: int = 5
    userId: str = None
    month: str = None
    initial_fetch: int = 200  # Make configurable

@app.post("/search")
def semantic_search(q: Query):
    # Validate inputs
    if q.top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be positive")
    if q.month and not (1 <= int(q.month.zfill(2)) <= 12):
        raise HTTPException(status_code=400, detail="month must be 1-12")
    # embed query locally
    emb = model.encode([q.query], convert_to_numpy=True)
    faiss.normalize_L2(emb)
    results, distances = search(emb, top_k=q.initial_fetch)

    filtered_results = []
     
    for i, result in enumerate(results):
        # Filter by userId
        if q.userId and result.get("userId") != q.userId:
            continue
        
        # Filter by month - FIX: handle the date format properly
        if q.month:
            # Extract month from date (format: "2024-02-XX")
            date_str = result.get("date", "")
            if date_str:
                # Get the month part from "2024-02-XX"
                try:
                    result_month = date_str.split("-")[1]  # Gets "02" from "2024-02-05"
                    # Normalize input month (handle both "2" and "02")
                    query_month = q.month.zfill(2) if len(q.month) <= 2 else q.month.split("-")[1]
                    if result_month != query_month:
                        continue
                except (IndexError, AttributeError):
                    continue
        
        filtered_results.append({
            **result,
            "score": float(distances[i])
        })
    
    # Sort by amount (descending) for expense queries
    if "expense" in q.query.lower() or "top" in q.query.lower():
        filtered_results.sort(key=lambda x: x["amount"], reverse=True)
    
    # Return only top_k results
    final_results = filtered_results[:q.top_k]
    
    return {
        "query": q.query,
        "userId": q.userId,
        "month": q.month,
        "results": final_results,
        "count": len(final_results),
        "total_before_limit": len(filtered_results)
    }

   
@app.post("/summarize")
def summarize(results: dict):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    # results should be list of txn dicts; we'll create a prompt
    txns = results.get("results", [])[:10]
    if not txns:
        return {"summary": "No transactions to summarize"}
    prompt = "Summarize these transactions: " + "\n".join([f"{t['date']} {t['description']} ₹{t['amount']} {t['category']}" for t in txns])
    try:
        # call OpenAI chat (example)
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role":"user","content": prompt}],
            max_tokens=200
        )
        return {"summary": resp["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)