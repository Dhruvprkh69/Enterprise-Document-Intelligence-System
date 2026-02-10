# Enterprise Document Intelligence System (RAG-based)

## Project Overview
An end-to-end RAG (Retrieval-Augmented Generation) system for enterprise document intelligence with Decision Mode capabilities.

## Features
- 📄 Document Upload & Processing (PDF, DOCX, TXT)
- 🔍 Semantic Search with Citations
- 🤖 Decision Mode (Risk Analysis, Revenue Analysis, Clause Extraction)
- 🎯 Production-ready Architecture (Local → Cloud migration ready)

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js 14 (TypeScript)
- **Vector DB**: Chroma (Local) → Pinecone (Cloud)
- **LLM**: Groq API (Llama 3.1) + Gemini API
- **Embeddings**: Gemini Embeddings / Hugging Face
- **Database**: SQLite (Local) → PostgreSQL (Cloud)

## Project Structure
```
enterprise-rag/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── uploads/          # Document storage (local)
└── chroma_db/        # Vector database (local)
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables
Create `.env` file in `backend/`:
```
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key (optional)
ENVIRONMENT=local
```

## API Documentation
Once backend is running, visit: http://localhost:8000/docs

## Development Roadmap
- [x] Project structure
- [ ] Backend setup
- [ ] Document processing
- [ ] RAG pipeline
- [ ] Decision Mode
- [ ] Frontend UI
- [ ] Deployment
