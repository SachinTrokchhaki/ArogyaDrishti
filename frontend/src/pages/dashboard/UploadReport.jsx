import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../../components/FileUpload';
import ProcessingPipeline from '../../components/ProcessingPipeline';
import ResultsDisplay from '../ResultsDisplay';
import './Dashboard.css';

export default function UploadReport() {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(true);
  const [showPipeline, setShowPipeline] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUploaded = (file) => {
    setShowUpload(false);
    setShowPipeline(true);
    setError(null);
  };

  const handleAnalysisComplete = (data) => {
    setShowPipeline(false);
    setResult(data);
  };

  const handleError = (errorMessage) => {
    setShowPipeline(false);
    setShowUpload(true);
    setError(errorMessage);
  };

  const handleReset = () => {
    setResult(null);
    setShowUpload(true);
    setShowPipeline(false);
    setError(null);
  };

  return (
    <div className="upload-report-page">
      {/* ===== HERO (matches main page) ===== */}
      <div className="upload-report-hero">
        <h1>📊 Medical Report Analysis</h1>
        <p>Upload your medical report and get instant analysis with AI-powered insights</p>
      </div>

      <div className="upload-report-container">
        {error && (
          <div className="alert-error" style={{ marginBottom: '20px' }}>
            ⚠️ {error}
          </div>
        )}

        {showUpload && (
          <FileUpload
            onFileUploaded={handleFileUploaded}
            onAnalysisComplete={handleAnalysisComplete}
            onError={handleError}
          />
        )}

        {showPipeline && (
          <ProcessingPipeline onComplete={() => {}} />
        )}

        {result && (
          <>
            <ResultsDisplay data={result} />

            <div className="re-upload-section">
              <button
                className="btn btn-outline"
                onClick={handleReset}
              >
                📤 Upload Another Report
              </button>
              <button
                className="btn btn-primary"
                onClick={() => navigate('/dashboard/reports')}
              >
                📊 View My Reports →
              </button>
            </div>
          </>
        )}

        {/* ===== INFO CARDS (matches main page) ===== */}
        {showUpload && !result && (
          <div className="upload-info-cards">
            <div className="info-card">
              <span className="info-icon">🔒</span>
              <h3>Secure & Private</h3>
              <p>Your reports are processed securely and never shared</p>
            </div>
            <div className="info-card">
              <span className="info-icon">⚡</span>
              <h3>Fast Results</h3>
              <p>Get structured results in under a minute</p>
            </div>
            <div className="info-card">
              <span className="info-icon">📋</span>
              <h3>Supported Formats</h3>
              <p>PDF, PNG, JPG, JPEG - Max 10MB</p>
            </div>
            <div className="info-card">
              <span className="info-icon">🤖</span>
              <h3>AI-Powered</h3>
              <p>Advanced AI extracts and explains medical values</p>
            </div>
          </div>
        )}

        {/* ===== DISCLAIMER (matches main page) ===== */}
        {showUpload && !result && (
          <div className="analysis-disclaimer">
            <p>
              ⚠️ <strong>Disclaimer:</strong> This tool provides analysis and explanations for
              educational purposes only. Always consult a qualified healthcare professional for
              medical advice.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}