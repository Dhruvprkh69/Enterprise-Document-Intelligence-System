# Frontend - Enterprise Document Intelligence UI

Next.js 14 frontend for the Enterprise Document Intelligence System with a clean, professional interface.

## 🏗️ Architecture

### Frontend Architecture

```
┌─────────────────────────────────────┐
│         Next.js 14 App              │
│  ┌──────────────────────────────┐  │
│  │      App Router              │  │
│  │  - app/page.tsx (Main UI)   │  │
│  │  - app/layout.tsx            │  │
│  │  - app/globals.css           │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │      Components              │  │
│  │  - Document Upload           │  │
│  │  - Query Input               │  │
│  │  - Decision Mode Selector    │  │
│  │  - Response Display          │  │
│  │  - Markdown Renderer         │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│  ┌──────────▼───────────────────┐  │
│  │      API Client              │  │
│  │  - lib/api.ts                │  │
│  └──────────┬───────────────────┘  │
└─────────────┼───────────────────────┘
              │ HTTP/REST
              ▼
┌─────────────────────────────────────┐
│      FastAPI Backend                 │
│      (localhost:8000)                │
└─────────────────────────────────────┘
```

### Component Structure

```
app/
├── page.tsx              # Main application page
│   ├── Document Upload Section
│   ├── Query Section
│   │   ├── Mode Toggle (Regular/Decision)
│   │   ├── Decision Mode Selector
│   │   └── Query Input with Auto-fill
│   └── Response Display
│       ├── Markdown Rendering
│       ├── Source Citations
│       └── Copy Button
│
├── layout.tsx            # Root layout
├── globals.css           # Global styles + Markdown CSS
│
lib/
└── api.ts                # API client functions
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main UI component
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Tailwind + Markdown styles
│   └── favicon.ico           # Favicon
│
├── lib/
│   └── api.ts                # API client (fetch functions)
│
├── public/                   # Static assets
│
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── next.config.ts            # Next.js config
└── tailwind.config.js        # Tailwind config
```

## 🚀 Setup Instructions

### Step 1: Navigate to Frontend

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install:
- Next.js 14
- React 19
- TypeScript
- Tailwind CSS
- react-markdown

### Step 3: Start Development Server

```bash
npm run dev
```

Frontend will run on: `http://localhost:3000`

### Step 4: Access Application

Open browser: `http://localhost:3000`

**Note:** Ensure backend is running on `http://localhost:8000`

## 🎨 Features

### 1. Document Upload
- Drag & drop or file picker
- Support for PDF, DOCX, TXT
- Upload progress indicator
- Success/error messages

### 2. Query Interface

**Regular Query Mode:**
- Simple text input
- Enter key to submit
- Real-time processing indicator

**Decision Mode:**
- Mode selector dropdown:
  - Executive Summary
  - Risk Analysis
  - Revenue Analysis
  - Clause Extraction
- Auto-fill queries (editable)
- Mode-specific action buttons:
  - "Generate Summary"
  - "Analyze Risks"
  - "Analyze Revenue"
  - "Extract Clauses"

### 3. Response Display
- **Markdown Rendering**: 
  - Bold text, headings, lists
  - Code blocks, blockquotes
  - Professional formatting
- **Source Citations**:
  - Source ID, filename
  - Relevance score (percentage)
  - Text preview
- **Copy Button**:
  - Top-right corner
  - Copies full response + sources
  - Success feedback (green checkmark)

### 4. UI/UX Features
- Clean white background
- Professional design
- Responsive layout
- Loading states
- Error handling
- Smooth transitions

## 🛠️ Key Components

### Main Page (`app/page.tsx`)

**State Management:**
- `file`: Selected file for upload
- `question`: Query text
- `mode`: Query mode (regular/decision)
- `decisionModeType`: Selected decision mode
- `response`: API response
- `loading`: Loading state
- `error`: Error messages

**Key Functions:**
- `handleUpload()`: Upload document
- `handleQuery()`: Process query
- `handleCopy()`: Copy response
- `handleModeChange()`: Switch modes
- `handleDecisionModeChange()`: Change decision mode

### API Client (`lib/api.ts`)

**Functions:**
- `uploadDocument(file)`: Upload document
- `queryDocuments({question, user_id})`: Regular query
- `decisionMode({query, mode, user_id})`: Decision mode query
- `listDocuments(user_id)`: List uploaded documents

**Configuration:**
- Base URL: `http://localhost:8000`
- Error handling included

### Styling (`app/globals.css`)

**Features:**
- Tailwind CSS setup
- Markdown styling:
  - Headings (h1-h4)
  - Lists (ul, ol) with proper bullets
  - Code blocks
  - Blockquotes
  - Bold/italic text

## 🎯 Usage Guide

### Uploading Documents

1. Click "Select PDF, DOCX, or TXT file"
2. Choose file from file picker
3. Click "Upload" button
4. Wait for "✓ Document uploaded successfully!" message

### Asking Questions

**Regular Query:**
1. Select "Regular Query" mode
2. Type your question
3. Press Enter or click "Ask"
4. View formatted response with sources

**Decision Mode:**
1. Select "Decision Mode"
2. Choose analysis mode (Summary/Risk/Revenue/Clause)
3. Query auto-fills (you can edit it)
4. Click mode-specific button (e.g., "Generate Summary")
5. View structured analysis

### Copying Responses

1. After getting response, click "Copy" button (top-right)
2. Button turns green with "✓ Copied!" message
3. Response copied to clipboard (includes sources)

## 🔧 Development

### Available Scripts

```bash
# Development server (with hot reload)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Customization

**Change API URL:**
Edit `lib/api.ts`:
```typescript
const API_BASE_URL = 'http://your-backend-url:8000';
```

**Modify Styling:**
- Tailwind: Edit `app/globals.css`
- Component styles: Edit `app/page.tsx`

**Add Features:**
- New components: Create in `app/` or `components/`
- New API calls: Add to `lib/api.ts`

## 🎨 UI Components Breakdown

### Document Upload Section
```tsx
- File input (hidden)
- Custom file picker button
- Upload button
- Success message
```

### Query Section
```tsx
- Mode toggle buttons (Regular/Decision)
- Decision mode dropdown (conditional)
- Query input field
- Submit button (mode-specific text)
```

### Response Section
```tsx
- Copy button (top-right)
- Answer/Result display (markdown)
- Sources list
  - Source ID, filename
  - Relevance score
  - Text preview
```

## 📱 Responsive Design

- Desktop: Full-width layout
- Tablet: Responsive columns
- Mobile: Stacked layout

## 🐛 Troubleshooting

### Common Issues

**1. API Connection Errors**
```
Error: Failed to fetch
```
**Solution:**
- Verify backend is running on port 8000
- Check CORS settings in backend
- Verify API_BASE_URL in `lib/api.ts`

**2. Port Already in Use**
```bash
# Use different port
npm run dev -- -p 3001
```

**3. Module Not Found**
```bash
# Reinstall dependencies
rm -rf node_modules
npm install
```

**4. Markdown Not Rendering**
- Check `react-markdown` is installed
- Verify `globals.css` has markdown styles
- Check browser console for errors

## 🚀 Production Build

### Build for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Environment Variables

For production, set:
- `NEXT_PUBLIC_API_URL`: Backend API URL

## 📊 Performance

- **Initial Load**: < 2 seconds
- **Query Response**: < 3 seconds (depends on backend)
- **Markdown Rendering**: Instant
- **Bundle Size**: Optimized with Next.js

## 🎯 Key Features Implementation

### Auto-fill Queries
- Mode-specific default queries
- Editable after auto-fill
- Helper text for guidance

### Markdown Rendering
- Uses `react-markdown` library
- Custom CSS for styling
- Supports all markdown features

### Copy Functionality
- Uses Clipboard API
- Success feedback
- Copies full response + sources

## 🔒 Security

- No sensitive data in frontend
- API keys handled by backend
- CORS configured properly
- Input validation

## 📝 Code Style

- TypeScript for type safety
- Functional components
- Hooks for state management
- Clean component structure

---

**Frontend is ready for development and production!** 🚀

For backend setup, see `../backend/README.md`
For overall project info, see `../README.md`
