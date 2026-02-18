# Google OAuth Setup Guide

## Overview
This project uses Google OAuth for authentication. Users can sign in with their Google account or use email/password.

---

## Step 1: Create Google OAuth Credentials

### 1.1 Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable **Google+ API** (if not already enabled)

### 1.2 Create OAuth 2.0 Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure OAuth consent screen:
   - **User Type**: Select "External" (for testing) or "Internal" (for organization)
   - **App name**: "Enterprise Document Intelligence" (or your app name)
   - **User support email**: Your email
   - **Developer contact**: Your email
   - Click **Save and Continue**
   - Add scopes: `email`, `profile`, `openid`
   - Add test users (if External)
   - Click **Save and Continue**

4. Create OAuth Client ID:
   - **Application type**: Web application
   - **Name**: "RAG Frontend Client"
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (for local development)
     - `https://yourdomain.com` (for production)
   - **Authorized redirect URIs**:
     - `http://localhost:3000` (for local development)
     - `https://yourdomain.com` (for production)
   - Click **Create**

5. **Copy the Client ID** (you'll need this)

---

## Step 2: Frontend Setup

### 2.1 Add Environment Variable
Create/update `frontend/.env.local`:

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here
```

**Example:**
```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
```

### 2.2 Verify Frontend Code
The frontend is already configured in:
- `frontend/app/layout.tsx` - GoogleOAuthProvider setup
- `frontend/app/login/page.tsx` - Login page with Google button
- `frontend/app/page.tsx` - Main page with Google auth

**No code changes needed** - just add the environment variable!

---

## Step 3: Backend Setup

### 3.1 Backend is Already Configured
The backend automatically handles both:
- **ID tokens** (from Google Sign-In)
- **Access tokens** (from OAuth flow)

**No backend configuration needed!**

The backend service (`backend/app/services/auth_service.py`) handles token verification automatically.

---

## Step 4: Testing

### 4.1 Start Backend
```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
uvicorn app.main:app --reload
```

### 4.2 Start Frontend
```bash
cd frontend
npm run dev
```

### 4.3 Test Google OAuth
1. Open: http://localhost:3000/login
2. Click **"Continue with Google"**
3. Select your Google account
4. Grant permissions
5. You should be redirected to the main app

---

## How It Works

### Flow:
1. **User clicks "Continue with Google"**
2. **Frontend** (`@react-oauth/google`) opens Google OAuth popup
3. **User authenticates** with Google
4. **Google returns access token**
5. **Frontend sends token** to backend `/api/auth/verify`
6. **Backend verifies token** with Google API
7. **Backend returns user info** (email, name, user_id)
8. **Frontend stores** user info in localStorage
9. **User is logged in** ✅

### Token Types Supported:
- **ID Token**: Direct user info (email, name, picture)
- **Access Token**: Fetches user info from Google API

---

## Troubleshooting

### Issue: "Invalid Google token"
**Solution**: 
- Check if `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is set correctly
- Verify OAuth credentials in Google Console
- Check authorized origins match your URL

### Issue: "Redirect URI mismatch"
**Solution**:
- Add your exact URL to "Authorized redirect URIs" in Google Console
- Include both `http://localhost:3000` and production URL

### Issue: "Access blocked"
**Solution**:
- If using "External" user type, add yourself as a test user
- Or change to "Internal" if within organization

### Issue: Token verification fails
**Solution**:
- Backend automatically tries both ID token and access token
- Check backend logs for specific error
- Verify Google API is enabled in Google Cloud Console

---

## Production Deployment

### For AWS/Production:
1. Update **Authorized JavaScript origins** in Google Console:
   - `https://yourdomain.com`
   - `https://www.yourdomain.com` (if using www)

2. Update **Authorized redirect URIs**:
   - `https://yourdomain.com`
   - `https://yourdomain.com/login`

3. Set environment variable on server:
   ```bash
   export NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id
   ```

4. Or in `.env` file on production server

---

## Security Notes

- ✅ Tokens are verified server-side
- ✅ User data is isolated per user_id
- ✅ No sensitive data stored in frontend
- ⚠️ For production, add rate limiting
- ⚠️ Consider adding refresh token handling for long sessions

---

## Multi-User Support

The system automatically:
- Creates unique `user_id` from email (email prefix)
- Isolates documents per user
- Supports multiple users simultaneously

**Example:**
- `dhruv@company.com` → `user_id: "dhruv"`
- `john@company.com` → `user_id: "john"`

Each user's documents are stored separately in the vector database.

---

## Quick Checklist

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] OAuth client ID created
- [ ] Authorized origins added (localhost + production)
- [ ] `NEXT_PUBLIC_GOOGLE_CLIENT_ID` set in frontend/.env.local
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Test login successful

---

**That's it! Google OAuth is now configured.** 🎉
