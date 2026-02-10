/**
 * API client for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface QueryRequest {
  question: string;
  user_id?: string;
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
 * Upload a document
 */
export async function uploadDocument(
  file: File,
  userId: string = 'default'
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/upload?user_id=${userId}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload document');
  }

  return response.json();
}

/**
 * Query documents using RAG
 */
export async function queryDocuments(
  request: QueryRequest
): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
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
  const response = await fetch(`${API_BASE_URL}/api/decision-mode`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to process decision query');
  }

  return response.json();
}
