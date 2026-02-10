# Setup Guide - Step by Step

Yeh guide aapko project setup karne mein help karega. Har step ke baad output share karein, main next steps bataunga.

## Prerequisites Check

Pehle check karein aapke system mein yeh installed hai:

### Step 1: Python Check
```bash
python --version
```
**Expected Output:** Python 3.9 ya higher (e.g., `Python 3.11.5`)

### Step 2: Node.js Check
```bash
node --version
```
**Expected Output:** Node.js 18 ya higher (e.g., `v18.17.0`)

### Step 3: npm Check
```bash
npm --version
```
**Expected Output:** npm version (e.g., `9.6.7`)

---

## Backend Setup

### Step 4: Navigate to Backend Directory
```bash
cd backend
```

### Step 5: Create Virtual Environment
**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### Step 6: Activate Virtual Environment
**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Expected Output:** Terminal prompt mein `(venv)` dikhna chahiye

### Step 7: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected Output:** Sab packages install hote hue dikhenge. Kuch minutes lag sakte hain.

**Note:** Agar koi error aaye (especially `sqlite3` related), ignore karein - wo built-in hai Python mein.

### Step 8: Create .env File
Backend folder mein `.env` file create karein:

**Windows (PowerShell):**
```bash
New-Item -Path .env -ItemType File
```

**Linux/Mac:**
```bash
touch .env
```

Phir `.env` file mein yeh content add karein:
```
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=local
```

**Important:** Apni actual API keys add karein (GitHub pe commit mat karein!)

**Note:** Agar Gemini API key hai to add karein, warna empty rakh sakte hain.

### Step 9: Test Backend Setup
```bash
python -c "from app.core.config import settings; print('Config loaded:', settings.ENVIRONMENT)"
```

**Expected Output:** `Config loaded: local`

### Step 10: Start Backend Server
```bash
uvicorn app.main:app --reload
```

**Expected Output:** 
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 11: Test API (New Terminal)
Naya terminal open karein (pehla terminal running rakhna hai):

**Windows (PowerShell):**
```bash
curl http://localhost:8000/
```

**Ya browser mein open karein:**
```
http://localhost:8000/docs
```

**Expected Output:** Swagger UI page dikhna chahiye (API documentation)

---

## Frontend Setup (Next Step)

Backend successfully run ho raha hai to frontend setup karenge. Pehle backend test karein, phir frontend setup karenge.

---

## Troubleshooting

### Error: "Module not found"
- Virtual environment activate kiya hai?
- `pip install -r requirements.txt` run kiya?

### Error: "Port already in use"
- Port 8000 already use ho raha hai
- Ya to wo process stop karein, ya port change karein:
  ```bash
  uvicorn app.main:app --reload --port 8001
  ```

### Error: "GROQ_API_KEY not found"
- `.env` file backend folder mein hai?
- `.env` file mein `GROQ_API_KEY` correctly set hai?

---

## Next Steps

Backend successfully run ho gaya to:
1. Frontend setup karenge (Next.js)
2. Integration test karenge
3. Document upload test karenge
4. Query test karenge

Har step ke baad output share karein! 🚀
