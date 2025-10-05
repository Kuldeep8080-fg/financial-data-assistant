import requests

url = "http://127.0.0.1:8000/search"  # FastAPI server must be running
payload = {
    "query": "Top 5 expenses in August for user_1",
    "top_k": 5,
    "userId": "user_1"
}

resp = requests.post(url, json=payload)
print(resp.json())