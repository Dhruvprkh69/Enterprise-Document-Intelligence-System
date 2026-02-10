# Backend - Enterprise RAG System

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── services/
│   │   ├── document_processor.py    # Document processing
│   │   ├── embedding_service.py     # Embedding generation
│   │   ├── vector_db_service.py     # Vector database
│   │   ├── llm_service.py           # LLM API calls
│   │   ├── rag_service.py           # RAG pipeline
│   │   └── decision_mode_service.py # Decision Mode
│   └── main.py                # FastAPI app
├── uploads/                   # Uploaded documents (created automatically)
├── chroma_db/                 # Vector database (created automatically)
├── requirements.txt
└── .env                       # Environment variables
```

## How It Works

### 1. Document Upload Flow
```
User uploads file → DocumentProcessor extracts text → 
Chunks created → Embeddings generated → Stored in Vector DB
```

### 2. Query Flow (RAG)
```
User query → Generate query embedding → Search Vector DB → 
Retrieve top chunks → Build context → LLM generates answer → 
Return answer with citations
```

### 3. Decision Mode Flow
```
User query + mode → Retrieve relevant chunks → 
Mode-specific prompt → LLM generates structured output → 
Format and return
```

## API Endpoints

### POST `/api/upload`
Upload and process a document.

**Request:**
- `file`: PDF, DOCX, or TXT file
- `user_id`: (optional) User identifier

**Response:**
```json
{
  "message": "Document processed successfully",
  "filename": "document.pdf",
  "chunks_created": 15,
  "user_id": "default"
}
```

### POST `/api/query`
Query documents using RAG.

**Request:**
```json
{
  "question": "What are the main risks?",
  "user_id": "default"
}
```

**Response:**
```json
{
  "answer": "Based on the documents...",
  "sources": [
    {
      "source_id": 1,
      "filename": "document.pdf",
      "text_preview": "...",
      "relevance_score": 0.95
    }
  ],
  "metadata": {
    "chunks_retrieved": 5
  }
}
```

### POST `/api/decision-mode`
Process decision mode queries.

**Request:**
```json
{
  "query": "Analyze risks in this contract",
  "mode": "risk_analysis",
  "user_id": "default"
}
```

**Modes:**
- `risk_analysis`: Identify risks and liabilities
- `revenue_analysis`: Analyze revenue trends
- `clause_extraction`: Extract legal clauses
- `summary`: Executive summary

## Configuration

Edit `.env` file:
```
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here (optional)
ENVIRONMENT=local
```

## Running the Server

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run server
uvicorn app.main:app --reload
```

Server will run on: http://localhost:8000

API Docs: http://localhost:8000/docs
