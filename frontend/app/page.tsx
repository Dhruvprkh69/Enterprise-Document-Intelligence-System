'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useGoogleLogin } from '@react-oauth/google';
import ReactMarkdown from 'react-markdown';
import { uploadDocument, queryDocuments, decisionMode, verifyAuth, QueryResponse, DecisionResponse, AuthResponse } from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | DecisionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'query' | 'decision'>('query');
  const [decisionModeType, setDecisionModeType] = useState<'risk_analysis' | 'revenue_analysis' | 'clause_extraction' | 'summary'>('summary');
  const [user, setUser] = useState<AuthResponse | null>(null);
  const [googleToken, setGoogleToken] = useState<string | null>(null);


  // Mode-specific auto-fill queries
  const modeQueries = {
    summary: 'Provide a comprehensive executive summary of the uploaded documents',
    risk_analysis: 'Identify all risks, liabilities, and potential issues in this document',
    revenue_analysis: 'Analyze revenue trends, financial performance, and business metrics',
    clause_extraction: 'Extract all legal clauses, obligations, and important terms'
  };

  // Mode-specific button labels
  const modeButtonLabels = {
    summary: 'Generate Summary',
    risk_analysis: 'Analyze Risks',
    revenue_analysis: 'Analyze Revenue',
    clause_extraction: 'Extract Clauses'
  };

  // Google OAuth Login
  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        // Verify token with backend
        const userInfo = await verifyAuth(tokenResponse.access_token);
        setUser(userInfo);
        setGoogleToken(tokenResponse.access_token);
        localStorage.setItem('google_token', tokenResponse.access_token);
        localStorage.setItem('user_info', JSON.stringify(userInfo));
      } catch (err: any) {
        setError(err.message || 'Failed to authenticate');
      }
    },
    onError: () => {
      setError('Google authentication failed');
    },
  });

  // Check for authentication on mount
  useEffect(() => {
    const isAuthenticated = localStorage.getItem('is_authenticated');
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const savedToken = localStorage.getItem('google_token');
    const savedUser = localStorage.getItem('user_info');
    if (savedToken && savedUser) {
      setGoogleToken(savedToken);
      setUser(JSON.parse(savedUser));
    } else if (savedUser) {
      // Email/password login
      setUser(JSON.parse(savedUser));
    }
  }, [router]);

  const handleLogout = () => {
    setUser(null);
    setGoogleToken(null);
    localStorage.removeItem('google_token');
    localStorage.removeItem('user_info');
    localStorage.removeItem('is_authenticated');
    localStorage.removeItem('auth_type');
    router.push('/login');
  };

  const handleModeChange = (newMode: 'query' | 'decision') => {
    setMode(newMode);
    if (newMode === 'decision') {
      // Auto-fill query when switching to decision mode
      setQuestion(modeQueries[decisionModeType]);
    } else {
      // Clear query when switching to regular mode
      setQuestion('');
    }
  };

  const handleDecisionModeChange = (newMode: 'risk_analysis' | 'revenue_analysis' | 'clause_extraction' | 'summary') => {
    setDecisionModeType(newMode);
    // Auto-fill query when mode changes
    setQuestion(modeQueries[newMode]);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const userId = user?.user_id || 'default';
      const result = await uploadDocument(file, userId, googleToken || undefined);
      setUploadSuccess(true);
      setFile(null);
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (err: any) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const userId = user?.user_id || 'default';
      const token = googleToken || undefined;
      
      if (mode === 'query') {
        const result = await queryDocuments({ question, user_id: userId, token });
        setResponse(result);
      } else {
        const result = await decisionMode({
          query: question,
          mode: decisionModeType,
          user_id: userId,
          token,
        });
        setResponse(result);
      }
      setQuestion('');
    } catch (err: any) {
      setError(err.message || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!response) return;
    
    let textToCopy = '';
    
    if ('answer' in response) {
      // Regular Query Response
      textToCopy = response.answer;
      if (response.sources && response.sources.length > 0) {
        textToCopy += '\n\n--- Sources ---\n';
        response.sources.forEach((source, index) => {
          textToCopy += `\n${index + 1}. ${source.filename} (${source.relevance_score ? (source.relevance_score * 100).toFixed(1) + '% match' : 'N/A'})\n`;
          textToCopy += source.text_preview + '\n';
        });
      }
    } else {
      // Decision Mode Response
      textToCopy = response.result;
      if (response.structured_data) {
        textToCopy += `\n\nSources: ${response.structured_data.sources.join(', ')}`;
        textToCopy += `\nChunks analyzed: ${response.structured_data.chunks_analyzed}`;
      }
    }
    
    navigator.clipboard.writeText(textToCopy).then(() => {
      // Show temporary success message
      const button = document.getElementById('copy-button');
      if (button) {
        const originalHTML = button.innerHTML;
        button.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg> Copied!';
        button.classList.remove('bg-gray-100', 'text-gray-700', 'hover:bg-gray-200');
        button.classList.add('bg-green-600', 'text-white');
        setTimeout(() => {
          button.innerHTML = originalHTML;
          button.classList.remove('bg-green-600', 'text-white');
          button.classList.add('bg-gray-100', 'text-gray-700', 'hover:bg-gray-200');
        }, 2000);
      }
    }).catch(err => {
      console.error('Failed to copy:', err);
    });
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Enterprise Document Intelligence
              </h1>
              <p className="text-gray-600">
                Upload documents and ask questions with AI-powered RAG system
              </p>
            </div>
            <div className="flex items-center gap-4">
              {user ? (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user.name}</p>
                <p className="text-xs text-gray-500">{user.email}</p>
              </div>
              {user.picture ? (
                <img
                  src={user.picture}
                  alt={user.name}
                  className="w-10 h-10 rounded-full"
                />
              ) : (
                <div 
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                  style={{
                    backgroundColor: `hsl(${user.name.charCodeAt(0) * 137.508 % 360}, 70%, 50%)`
                  }}
                >
                  {user.name.charAt(0).toUpperCase()}
                </div>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 font-medium"
              >
                Logout
              </button>
            </div>
              ) : (
                <button
                  onClick={() => login()}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium flex items-center gap-2"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  Sign in with Google
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Upload Section */}
        <section className="bg-gray-50 rounded-lg p-6 mb-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Document</h2>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label
                htmlFor="file-input"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Select PDF, DOCX, or TXT file
              </label>
              <input
                id="file-input"
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
          {uploadSuccess && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md text-green-800">
              ✓ Document uploaded successfully!
            </div>
          )}
        </section>

        {/* Query Section */}
        <section className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Ask Questions</h2>
          
          {/* Mode Toggle */}
          <div className="flex gap-4 mb-4">
            <button
              onClick={() => handleModeChange('query')}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                mode === 'query'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Regular Query
            </button>
            <button
              onClick={() => handleModeChange('decision')}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                mode === 'decision'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Decision Mode
            </button>
          </div>

          {/* Decision Mode Selector */}
          {mode === 'decision' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Analysis Mode:
              </label>
              <select
                value={decisionModeType}
                onChange={(e) => handleDecisionModeChange(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
                <option value="summary">Executive Summary</option>
                <option value="risk_analysis">Risk Analysis</option>
                <option value="revenue_analysis">Revenue Analysis</option>
                <option value="clause_extraction">Clause Extraction</option>
              </select>
              <p className="mt-2 text-sm text-gray-500">
                Query will auto-fill based on selected mode. You can customize it below.
          </p>
        </div>
          )}

          {/* Query Input */}
          <div className="flex gap-4">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
              placeholder={
                mode === 'query'
                  ? 'Ask a question about your documents...'
                  : 'Query will auto-fill based on selected mode (editable)'
              }
              className="flex-1 px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleQuery}
              disabled={!question.trim() || loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading 
                ? 'Processing...' 
                : mode === 'decision' 
                  ? modeButtonLabels[decisionModeType]
                  : 'Ask'
              }
            </button>
          </div>
        </section>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md text-red-800">
            Error: {error}
          </div>
        )}

        {/* Response Display */}
        {response && (
          <section className="bg-white rounded-lg p-6 border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Response</h2>
              <button
                id="copy-button"
                onClick={handleCopy}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 font-medium text-sm transition-colors flex items-center gap-2"
                title="Copy response"
          >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </button>
            </div>
            
            {'answer' in response ? (
              // Regular Query Response
              <div>
                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
                  <h3 className="font-semibold text-gray-900 mb-2">Answer:</h3>
                  <div className="text-gray-700 prose prose-sm max-w-none markdown-content">
                    <ReactMarkdown>{response.answer}</ReactMarkdown>
                  </div>
                </div>
                
                {response.sources && response.sources.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Sources:</h3>
                    <div className="space-y-2">
                      {response.sources.map((source) => (
                        <div
                          key={source.source_id}
                          className="p-3 bg-gray-50 border border-gray-200 rounded-md"
                        >
                          <div className="flex justify-between items-start mb-1">
                            <span className="font-medium text-gray-900">
                              Source {source.source_id}: {source.filename}
                            </span>
                            {source.relevance_score && (
                              <span className="text-sm text-gray-500">
                                {(source.relevance_score * 100).toFixed(1)}% match
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {source.text_preview}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              // Decision Mode Response
              <div>
                <div className="mb-4">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {response.mode.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                  <div className="text-gray-700 prose prose-sm max-w-none markdown-content">
                    <ReactMarkdown>{response.result}</ReactMarkdown>
                  </div>
                </div>
                {response.structured_data && (
                  <div className="mt-4 text-sm text-gray-600">
                    <p>Sources: {response.structured_data.sources.join(', ')}</p>
                    <p>Chunks analyzed: {response.structured_data.chunks_analyzed}</p>
                  </div>
                )}
              </div>
            )}
          </section>
        )}
        </div>
    </div>
  );
}
