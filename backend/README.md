# Backend - Enterprise Document Intelligence API

FastAPI-based backend for RAG (Retrieval-Augmented Generation) document intelligence system.

## 🏗️ Architecture

### System Architecture

```
┌─────────────┐
│   Client    │
│  (Frontend) │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌──────────────────────────────┐  │
│  │      API Routes              │  │
│  │  - /api/upload               │  │
│  │  - /api/query                │  │
│  │  - /api/decision-mode        │  │
│  │  - /api/documents            │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │    Service Layer              │  │
│  │  - Document Processor         │  │
│  │  - Embedding Service          │  │
│  │  - Vector DB Service         │  │
│  │  - RAG Service                │  │
│  │  - LLM Service                │  │
│  │  - Decision Mode Service     │  │
│  └──────────┬───────────────────┘  │
└─────────────┼───────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌─────────┐      ┌──────────────┐
│ ChromaDB │      │  Groq API    │
│ (Vector)│      │  (LLM)       │
└─────────┘      └──────────────┘
```

### Request Flow

1. **Document Upload**:
   ```
   Client → /api/upload → Document Processor → Embedding Service → Vector DB
   ```

2. **Query Processing**:
   ```
   Client → /api/query → RAG Service → Vector DB (retrieve) → LLM Service → Response
   ```

3. **Decision Mode**:
   ```
   Client → /api/decision-mode → Decision Mode Service → RAG Service → LLM Service → Structured Response
   ```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── routes.py           # All API endpoints
│   │
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   └── config.py           # Settings and environment variables
│   │
│   └── services/               # Business logic services
│       ├── __init__.py
│       ├── document_processor.py    # PDF/DOCX/TXT parsing
│       ├── embedding_service.py     # Embedding generation
│       ├── vector_db_service.py     # ChromaDB operations
│       ├── llm_service.py           # LLM API calls
│       ├── rag_service.py           # RAG pipeline orchestration
│       └── decision_mode_service.py # Decision Mode logic
│
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (create this)
├── uploads/                   # Uploaded documents (auto-created)
└── chroma_db/                 # Vector database (auto-created)
```

## 🔧 Setup Instructions

### Step 1: Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Ensure venv is activated (you should see (venv) in prompt)
pip install -r requirements.txt
```

### Step 3: Environment Configuration

Create `.env` file in `backend/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=local
```

**Getting API Keys:**
- **Groq**: https://console.groq.com/ (Free tier available)
- **Gemini**: https://makersuite.google.com/app/apikey (Optional)

### Step 4: Run Backend Server

```bash
# Make sure venv is activated
uvicorn app.main:app --reload
```

Server will start on: `http://localhost:8000`

## 📡 API Endpoints

### 1. Upload Document
```http
POST /api/upload?user_id=default
Content-Type: multipart/form-data

Body: file (PDF/DOCX/TXT)
```

**Response:**
```json
{
  "message": "Document processed successfully",
  "filename": "document.pdf",
  "chunks_created": 285,
  "user_id": "default"
}
```

### 2. Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "question": "What is this document about?",
  "user_id": "default"
}
```

**Response:**
```json
{
  "answer": "Answer text...",
  "sources": [
    {
      "source_id": 1,
      "filename": "document.pdf",
      "chunk_id": 32,
      "text_preview": "Preview...",
      "relevance_score": 0.85
    }
  ],
  "metadata": {
    "chunks_retrieved": 8,
    "question": "What is this document about?"
  }
}
```

### 3. Decision Mode
```http
POST /api/decision-mode
Content-Type: application/json

{
  "query": "Analyze risks in this document",
  "mode": "risk_analysis",
  "user_id": "default"
}
```

**Modes:**
- `summary`: Executive Summary
- `risk_analysis`: Risk Analysis
- `revenue_analysis`: Revenue Analysis
- `clause_extraction`: Clause Extraction

**Response:**
```json
{
  "mode": "risk_analysis",
  "result": "Structured analysis...",
  "structured_data": {
    "sources": ["document.pdf"],
    "chunks_analyzed": 12
  }
}
```

### 4. List Documents
```http
GET /api/documents?user_id=default
```

**Response:**
```json
{
  "documents": [
    {
      "filename": "document.pdf",
      "upload_date": "2025-02-10",
      "chunks_count": 285
    }
  ]
}
```

## 🔍 Service Details

### Document Processor (`document_processor.py`)

**Responsibilities:**
- Parse PDF files (PyPDF2, pdfplumber)
- Parse DOCX files (python-docx)
- Parse TXT files
- Chunk text into 1000-character chunks with 200-character overlap

**Key Methods:**
- `process_document(file_path, filename)`: Main processing function
- `_chunk_text(text, chunk_size, overlap)`: Text chunking logic

### Embedding Service (`embedding_service.py`)

**Responsibilities:**
- Generate embeddings using Hugging Face Sentence Transformers
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Singleton pattern for model loading (loads once)

**Key Methods:**
- `generate_embeddings(texts)`: Batch embedding generation
- `generate_single_embedding(text)`: Single text embedding

### Vector DB Service (`vector_db_service.py`)

**Responsibilities:**
- Manage ChromaDB operations
- Store document chunks with embeddings
- Search for similar chunks
- User-based filtering (multi-tenancy)

**Key Methods:**
- `store_documents(chunks, embeddings, user_id)`: Store documents
- `search(query, top_k, user_id)`: Search similar chunks

### LLM Service (`llm_service.py`)

**Responsibilities:**
- Interface with Groq API
- Primary model: `llama-3.3-70b-versatile`
- Fallback models: `llama-3.1-8b-instant`, `mixtral-8x7b-32768`
- Error handling and retries

**Key Methods:**
- `generate_response(prompt, temperature, max_tokens)`: Generate LLM response

### RAG Service (`rag_service.py`)

**Responsibilities:**
- Orchestrate RAG pipeline
- Dynamic retrieval (8-12 chunks based on complexity)
- Context building
- Prompt creation with calculation/inference support

**Key Methods:**
- `query(question, user_id, top_k)`: Main RAG query method
- `_is_complex_question(question)`: Detect complex questions
- `_create_rag_prompt(question, context, is_complex)`: Create enhanced prompts

### Decision Mode Service (`decision_mode_service.py`)

**Responsibilities:**
- Handle specialized business intelligence queries
- Mode-specific prompts
- Structured output generation

**Key Methods:**
- `process_decision_query(query, mode, user_id)`: Process decision mode query
- `_get_mode_prompt(mode, query, context)`: Get mode-specific prompt

## ⚙️ Configuration

### Settings (`core/config.py`)

**Key Settings:**
- `CHUNK_SIZE`: 1000 characters
- `CHUNK_OVERLAP`: 200 characters
- `TOP_K_RESULTS`: 8 (default retrieval)
- `TOP_K_COMPLEX`: 12 (complex questions)
- `MAX_FILE_SIZE`: 10MB

**Environment Variables:**
- `GROQ_API_KEY`: Required
- `GEMINI_API_KEY`: Optional
- `ENVIRONMENT`: `local` or `cloud`

## 🚀 Running the Server

### Development Mode (Auto-reload)

```bash
uvicorn app.main:app --reload
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### With Custom Port

```bash
uvicorn app.main:app --port 8001
```

## 🧪 Testing

### Using Swagger UI

Visit: `http://localhost:8000/docs`

- Interactive API documentation
- Test endpoints directly
- See request/response schemas

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Upload document
curl -X POST "http://localhost:8000/api/upload?user_id=default" \
  -F "file=@document.pdf"

# Query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this about?", "user_id": "default"}'
```

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'chromadb'**
```bash
# Solution: Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

**2. API Key Errors**
```bash
# Check .env file exists in backend/ directory
# Verify API keys are correct
```

**3. Port Already in Use**
```bash
# Use different port
uvicorn app.main:app --port 8001
```

**4. ChromaDB Errors**
```bash
# Delete chroma_db folder and restart
rm -rf chroma_db  # Linux/Mac
rmdir /s chroma_db  # Windows
```

## 📊 Performance Optimization

### Current Optimizations

1. **Singleton Embedding Model**: Loads once, reuses
2. **Dynamic TOP_K**: More chunks for complex questions
3. **Smart Prompts**: Task-specific instructions
4. **Context Grouping**: Document-wise organization

### Future Optimizations

- Caching frequently asked questions
- Batch processing for multiple documents
- Async document processing
- Connection pooling for database

## 🔒 Security Considerations

- API key stored in `.env` (not committed)
- User isolation via `user_id`
- File size limits (10MB)
- CORS configured for frontend only
- Input validation via Pydantic

## 📝 Code Style

- Type hints throughout
- Docstrings for all functions
- Pydantic models for validation
- Error handling with try-except
- Logging for debugging

## 🚀 Deployment (Future)

### Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Migrate to Pinecone/Qdrant for vector DB
- [ ] Add authentication (JWT/OAuth)
- [ ] Implement rate limiting
- [ ] Add monitoring and logging
- [ ] Use environment-based config
- [ ] Set up CI/CD pipeline

---

**Backend is production-ready for local development!** 🚀

For questions or issues, check the main README.md or open an issue.
