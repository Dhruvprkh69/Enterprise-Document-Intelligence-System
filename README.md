# Enterprise Document Intelligence System

A production-ready RAG (Retrieval-Augmented Generation) based document intelligence system that enables users to upload documents, ask questions, and get AI-powered answers with citations. Features specialized Decision Modes for business intelligence tasks.

## 🚀 Features

- **Document Upload & Processing**: Support for PDF, DOCX, and TXT files
- **Intelligent Q&A**: Ask questions and get accurate answers with source citations
- **Decision Modes**: 4 specialized analysis modes:
  - **Executive Summary**: Comprehensive document summaries
  - **Risk Analysis**: Identify and analyze risks with mitigation strategies
  - **Revenue Analysis**: Financial performance and trend analysis
  - **Clause Extraction**: Extract legal clauses, obligations, and deadlines
- **Semantic Search**: Vector-based retrieval with relevance scoring
- **Markdown Rendering**: Beautiful formatted responses with lists, headings, and emphasis
- **Copy Functionality**: One-click copy for responses
- **Production-Ready**: Multi-tenant architecture, error handling, environment-based config

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Vector Database**: ChromaDB (local), ready for Pinecone (cloud)
- **LLM**: Groq API (Llama 3.3-70B) with fallback models
- **Embeddings**: Hugging Face Sentence Transformers (all-MiniLM-L6-v2)
- **Document Processing**: PyPDF2, pdfplumber, python-docx
- **Database**: SQLite (local), ready for PostgreSQL (cloud)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Markdown**: react-markdown for formatted responses
- **UI**: Clean, professional white background design

## 📁 Project Structure

```
Rag/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration
│   │   ├── services/       # Business logic
│   │   └── main.py         # Entry point
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment variables
│   └── README.md           # Backend documentation
│
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app directory
│   ├── lib/                # Utilities
│   ├── package.json        # Node dependencies
│   └── README.md           # Frontend documentation
│
├── chroma_db/             # Vector database (auto-created)
└── README.md               # This file
```

## 🚦 Quick Start

### Prerequisites

- **Python 3.9+** (check: `python --version`)
- **Node.js 18+** (check: `node --version`)
- **npm** (comes with Node.js)

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd Rag
```

### Step 2: Backend Setup

```bash
# Navigate to backend
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

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Copy the template and add your API keys
# See backend/README.md for details

# Start backend server
uvicorn app.main:app --reload
```

Backend will run on: `http://localhost:8000`

### Step 3: Frontend Setup

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on: `http://localhost:3000`

### Step 4: Access Application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔑 Environment Variables

Create `backend/.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here (optional)
ENVIRONMENT=local
```

### Getting API Keys

1. **Groq API Key**: 
   - Visit: https://console.groq.com/
   - Sign up and get your API key
   - Free tier available

2. **Gemini API Key** (Optional):
   - Visit: https://makersuite.google.com/app/apikey
   - Get your API key
   - Free tier available

## 📖 Usage

### 1. Upload Document

- Click "Upload Document"
- Select PDF, DOCX, or TXT file
- Wait for processing confirmation

### 2. Ask Questions

**Regular Query Mode:**
- Type your question
- Get answer with source citations
- View relevance scores

**Decision Mode:**
- Select analysis mode (Summary/Risk/Revenue/Clause)
- Query auto-fills (editable)
- Get structured analysis
- Click mode-specific button (e.g., "Generate Summary")

### 3. View Results

- Formatted markdown responses
- Source citations with relevance scores
- Copy button for easy sharing
- Clean, professional UI

## 🏗️ Architecture

### RAG Pipeline

1. **Document Upload** → Parse document (PDF/DOCX/TXT)
2. **Chunking** → Split into 1000-character chunks with 200-character overlap
3. **Embedding** → Generate embeddings using Hugging Face model
4. **Storage** → Store in ChromaDB vector database
5. **Query** → User asks question
6. **Retrieval** → Retrieve top 8-12 relevant chunks (based on complexity)
7. **Generation** → LLM generates answer with context
8. **Response** → Return answer with citations

### Decision Mode Flow

1. User selects mode (Summary/Risk/Revenue/Clause)
2. Query auto-fills with mode-specific template
3. System retrieves 12 chunks for comprehensive analysis
4. Mode-specific prompt generates structured output
5. Formatted response with markdown rendering

## 🎯 Key Features Explained

### Dynamic Retrieval
- Simple questions: 8 chunks
- Complex questions: 12 chunks
- Automatic detection based on keywords

### Smart Prompts
- Calculation questions: Step-by-step instructions
- Inference questions: Multi-source synthesis guidance
- Mode-specific: Tailored prompts for each Decision Mode

### Multi-Tenancy
- User isolation via `user_id`
- Separate document collections per user
- Ready for SaaS deployment

## 📊 Performance

- **Query Accuracy**: 91% (20/22 test questions)
- **Response Time**: < 3 seconds (local)
- **Supported Formats**: PDF, DOCX, TXT
- **Max File Size**: 10MB

## 🔧 Development

### Backend Development

```bash
cd backend
# Activate venv
.\venv\Scripts\Activate.ps1  # Windows
# Run with auto-reload
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
# Run development server
npm run dev
```

### API Testing

Visit: http://localhost:8000/docs (Swagger UI)

## 📚 Documentation

- **Backend**: See [backend/README.md](backend/README.md)
- **Frontend**: See [frontend/README.md](frontend/README.md)

## 🚀 Deployment

### Local Development
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`

### Production (Future)
- Backend: Deploy to AWS/GCP/Azure
- Frontend: Deploy to Vercel/Netlify
- Vector DB: Migrate to Pinecone/Qdrant
- Database: Migrate to PostgreSQL

## 🐛 Troubleshooting

### Backend Issues

**Module not found errors:**
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

**API key errors:**
- Check `.env` file exists in `backend/` folder
- Verify API keys are correct

### Frontend Issues

**Port already in use:**
- Change port: `npm run dev -- -p 3001`

**API connection errors:**
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/main.py`

## 📝 License

This project is open source and available for personal/educational use.

## 👤 Author

Built as a portfolio project demonstrating:
- Full-stack development (Backend + Frontend)
- AI/ML integration (RAG, embeddings, LLMs)
- Production-ready architecture
- Modern tech stack

## 🙏 Acknowledgments

- Groq for LLM API
- Hugging Face for embeddings
- ChromaDB for vector database
- FastAPI and Next.js communities

---

**Ready to use!** Start with backend setup, then frontend, and you're good to go! 🚀
