/**
 * API client for backend communication
 */

// Get API URL - simple localhost for now
const getApiBaseUrl = () => {
  // Always use localhost for now - simple and works
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

// Debug: Log API URL
if (typeof window !== 'undefined') {
  console.log('🔍 API Base URL:', API_BASE_URL);
}

export interface AuthRequest {
  token: string;
}

export interface AuthResponse {
  user_id: string;
  email: string;
  name: string;
  picture?: string;
}

export interface QueryRequest {
  question: string;
  user_id?: string;
  token?: string;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    source_id: number;
    filename: string;
    chunk_id: number;
    text_preview: string;
    relevance_score: number | null;
  }>;
  metadata: {
    chunks_retrieved: number;
    question: string;
  };
}

export interface DecisionRequest {
  query: string;
  mode: 'risk_analysis' | 'revenue_analysis' | 'clause_extraction' | 'summary';
  user_id?: string;
  token?: string;
}

export interface DecisionResponse {
  mode: string;
  result: string;
  structured_data: {
    sources: string[];
    chunks_analyzed: number;
  } | null;
  metadata: {
    mode: string;
    sources_count: number;
  };
}

export interface UploadResponse {
  message: string;
  filename: string;
  chunks_created: number;
  user_id: string;
}

/**
 * Verify Google OAuth token
 */
export async function verifyAuth(token: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ token }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to verify authentication');
  }

  return response.json();
}

/**
 * Upload a document
 */
export async function uploadDocument(
  file: File,
  userId: string = 'default',
  token?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (token) {
    formData.append('token', token);
  }

  const url = `${API_BASE_URL}/api/upload?user_id=${userId}`;
  console.log('Upload URL:', url);
  console.log('API Base URL:', API_BASE_URL);

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      // Don't set Content-Type header - browser will set it with boundary for FormData
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
      throw new Error(error.detail || 'Failed to upload document');
    }

    return response.json();
  } catch (error: any) {
    console.error('Upload error:', error);
    if (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED')) {
      throw new Error(`Cannot connect to backend at ${API_BASE_URL}. Please check if the backend is running and accessible.`);
    }
    throw error;
  }
}

/**
 * Query documents using RAG
 */
export async function queryDocuments(
  request: QueryRequest
): Promise<QueryResponse> {
  // Get token from localStorage if not provided
  const token = request.token || localStorage.getItem('google_token') || undefined;
  const payload = { ...request, token };
  
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to query documents');
  }

  return response.json();
}

/**
 * Process decision mode query
 */
export async function decisionMode(
  request: DecisionRequest
): Promise<DecisionResponse> {
  // Get token from localStorage if not provided
  const token = request.token || localStorage.getItem('google_token') || undefined;
  const payload = { ...request, token };
  
  const response = await fetch(`${API_BASE_URL}/api/decision-mode`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to process decision query');
  }

  return response.json();
}
