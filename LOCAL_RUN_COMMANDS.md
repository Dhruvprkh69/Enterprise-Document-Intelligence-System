# Local Development - Run Commands

## Quick Start

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# Install new dependencies (if not already installed)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload
```

**Backend will run on**: `http://localhost:8000`

---

### Step 2: Frontend Setup

```bash
# Open new terminal
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start frontend development server
npm run dev
```

**Frontend will run on**: `http://localhost:3000`

---

## Testing the Improvements

### 1. Upload Test Document

1. Open browser: `http://localhost:3000`
2. Login (Google OAuth or Email/Password)
3. Upload `TEST_DOCUMENT.md` or convert to PDF and upload

### 2. Test Questions

Use questions from `TEST_QUESTIONS.md`:
- Start with simple questions (Q1-Q4)
- Then try explanatory questions (Q5-Q7)
- Test analytical questions (Q8-Q10)
- Test calculations (Q11-Q13)
- Test complex questions (Q14-Q16)
- Test confusion detection (Q17-Q18)
- Test general knowledge (Q19-Q20)

### 3. Check Backend Logs

Watch the terminal where backend is running to see:
- Query analysis results
- Intent detection
- User level detection
- Prompt generation

---

## Troubleshooting

### Backend Issues

**Error: Module not found (spaCy/NLTK/TextBlob)**
```bash
cd backend
pip install -r requirements.txt
```

**Error: Port 8000 already in use**
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill
```

**Error: Virtual environment not found**
```bash
cd backend
python -m venv venv
# Then activate and install dependencies
```

### Frontend Issues

**Error: Port 3000 already in use**
```bash
# Use different port
npm run dev -- -p 3001
```

**Error: Module not found**
```bash
cd frontend
rm -rf node_modules
npm install
```

---

## API Testing (Optional)

### Test Backend Directly

```bash
# Health check
curl http://localhost:8000/health

# Test query (replace with your question)
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is EBITDA?", "user_id": "test_user"}'
```

---

## Expected Behavior

### With Improvements:

1. **Intent Detection**: System should detect if question needs explanation
2. **User Level**: Should adapt language (beginner vs expert)
3. **Layered Answers**: Simple summary → Detailed explanation
4. **Confusion Detection**: Should provide extra clarity for confused users
5. **General Knowledge**: Should explain concepts even if not in document
6. **Better Formatting**: Structured answers with sections, bullets

### Example Good Answer:

```
**Simple Summary:** EBITDA is ₹450 crores, representing 36% margin.

**Detailed Explanation:**
EBITDA stands for Earnings Before Interest, Taxes, Depreciation, and Amortization.
It's a financial metric that measures...

**From Documents:**
According to Source 1, Acme Corporation's EBITDA is ₹450 crores with an EBITDA margin of 36%.

**Why It Matters:**
A 36% EBITDA margin indicates strong operational efficiency...
```

---

## Next Steps After Testing

1. **Share Results**: Paste answers in chat for evaluation
2. **Get Feedback**: I'll provide detailed analysis
3. **Iterate**: Make improvements based on feedback
4. **Phase 2**: Move to Hybrid Search (Vector + BM25)

---

**Ready to test? Start with backend, then frontend, then upload document and ask questions!** 🚀
