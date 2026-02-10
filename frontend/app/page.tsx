'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { uploadDocument, queryDocuments, decisionMode, QueryResponse, DecisionResponse } from '@/lib/api';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | DecisionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'query' | 'decision'>('query');
  const [decisionModeType, setDecisionModeType] = useState<'risk_analysis' | 'revenue_analysis' | 'clause_extraction' | 'summary'>('summary');

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
      const result = await uploadDocument(file);
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
      if (mode === 'query') {
        const result = await queryDocuments({ question, user_id: 'default' });
        setResponse(result);
      } else {
        const result = await decisionMode({
          query: question,
          mode: decisionModeType,
          user_id: 'default',
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Enterprise Document Intelligence
          </h1>
          <p className="text-gray-600">
            Upload documents and ask questions with AI-powered RAG system
          </p>
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
