# AI-Powered Financial Data Assistant

An intelligent financial data assistant that uses semantic similarity and vector embeddings to query and retrieve insights from financial transaction data.

## Features

- **AI-Based Dummy Data Generation**: Generates synthetic financial transactions using Faker.
- **Embedding Generation**: Uses Sentence Transformers (HuggingFace) for text embeddings.
- **Semantic Search API**: Accepts natural language queries and returns relevant transactions using FAISS vector search.
- **Summarization**: (Optional) Summarizes retrieved transactions using OpenAI GPT-4.

## Project Structure

```
financial-data-assistant/
│
├── data/
│   └── transactions.json           # AI-generated dummy financial data
│
├── embeddings/
│   └── faiss_index.faiss           # Stored FAISS vector index
│   └── metadata.json               # Transaction metadata mapping
│
├── api/
│   └── main.py                     # Main FastAPI application
│
├── services/
│   ├── data_generator.py           # AI-based dummy data generator
│   ├── embedding_service.py        # Embedding generation service
│   ├── vector_search_service.py    # FAISS vector DB operations
│   └── __init__.py
│
└── README.md
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <your-github-repo-url>
   cd financial-data-assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn faiss-cpu sentence-transformers faker openai
   ```

4. Set up OpenAI API key (for summarization):
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

## How to Generate Dummy Data

Run the data generator to create synthetic transactions:

```bash
python services/data_generator.py
```

This generates 200 transactions per user for 3 users (user_1, user_2, user_3) and saves to `data/transactions.json`.

## Building Embeddings and Vector Index

After generating data, build the FAISS index:

```bash
python -m services.vector_search_service
```

This creates embeddings using Sentence Transformers and stores the FAISS index in `embeddings/`.

## Running the API

Start the FastAPI server:

```bash
uvicorn api.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### POST /search

Performs semantic search on transactions.

**Request Body:**
```json
{
  "query": "string",      // Natural language query
  "top_k": 5,             // Number of results (default: 5)
  "userId": "string",     // Optional: Filter by user
  "month": "string",      // Optional: Filter by month (MM format)
  "initial_fetch": 200    // Optional: Initial search size (default: 200)
}
```

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/search" \
-H "Content-Type: application/json" \
-d '{
  "query": "top 5 expenses last month",
  "top_k": 5,
  "month": "09"
}'
```

**Response:**
```json
{
  "query": "top 5 expenses last month",
  "userId": null,
  "month": "09",
  "results": [
    {
      "id": "txn_user_1_45",
      "userId": "user_1",
      "date": "2024-09-01",
      "description": "Debit transaction",
      "amount": 5000,
      "type": "Debit",
      "category": "Shopping",
      "balance": 10000,
      "score": 0.85
    }
  ],
  "count": 5,
  "total_before_limit": 50
}
```

### POST /summarize

Summarizes a list of transactions using OpenAI GPT-4.

**Request Body:**
```json
{
  "results": [...]  // Array of transaction objects from /search
}
```

**Example Request:**
```bash
curl -X POST "http://127.0.0.1:8000/summarize" \
-H "Content-Type: application/json" \
-d '{
  "results": [
    {
      "date": "2024-09-01",
      "description": "Swiggy payment",
      "amount": 1200,
      "category": "Food"
    }
  ]
}'
```

**Response:**
```json
{
  "summary": "You spent ₹1,200 on food through Swiggy in September."
}
```

## Model & DB Configuration

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace)
- **Vector Database**: FAISS (IndexFlatIP for cosine similarity)
- **LLM**: OpenAI GPT-4 (for summarization)
- **Data Storage**: JSON files

## Example Queries and Outputs

### Query: "Show all UPI transactions above ₹1000"
```json
{
  "query": "Show all UPI transactions above ₹1000",
  "results": [
    {
      "id": "txn_user_1_10",
      "description": "UPI payment to Amazon",
      "amount": 2500,
      "category": "Shopping",
      "score": 0.92
    }
  ]
}
```

### Query: "What’s my biggest expense in August?"
```json
{
  "query": "What’s my biggest expense in August?",
  "userId": "user_1",
  "month": "08",
  "results": [
    {
      "amount": 5000,
      "category": "Travel",
      "score": 0.88
    }
  ]
}
```

### Query: "How much did I spend on food last month?"
```json
{
  "query": "How much did I spend on food last month?",
  "month": "09",
  "results": [...],
  "summary": "You spent ₹12,300 on food in September, mostly through Swiggy and Zomato."
}
```
