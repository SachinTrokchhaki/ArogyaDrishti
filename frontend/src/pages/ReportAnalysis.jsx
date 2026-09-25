import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import FileUpload from '../components/FileUpload';
import ProcessingPipeline from '../components/ProcessingPipeline';
import ResultsDisplay from './ResultsDisplay';
import api from '../services/api';
import './ReportAnalysis.css';

const ReportAnalysis = () => {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(true);
  const [showPipeline, setShowPipeline] = useState(false);
  const [result, setResult] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUploaded = async (file) => {
    setUploadedFile(file);
    setShowUpload(false);
    setShowPipeline(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setShowPipeline(false);
      setResult(response.data);
      
    } catch (error) {
      console.error('Upload error:', error);
      setShowPipeline(false);
      setShowUpload(true);
      
      if (error.response?.status === 401) {
        setError('Please login to upload reports.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setError(error.response?.data?.error || 'Failed to process report. Please try again.');
      }
    }
  };

  const handlePipelineComplete = () => {
    setShowPipeline(false);
  };

  const handleReset = () => {
    setResult(null);
    setShowUpload(true);
    setShowPipeline(false);
    setUploadedFile(null);
    setError(null);
  };

  // ✅ Navigate to full report view in dashboard
  const handleViewFullReport = () => {
    if (result?.id) {
      navigate(`/dashboard/reports`);
    }
  };

  return (
    <>
      {/* ===== NAVBAR ===== */}
      <Navbar />

      <div className="report-analysis-page">
        <div className="analysis-main">
          <div className="analysis-hero">
            <h1>📊 Medical Report Analysis</h1>
            <p>Upload your medical report and get instant analysis with AI-powered insights</p>
          </div>

          <div className="analysis-container">
            {error && (
              <div className="error-message" style={{ marginBottom: '20px' }}>
                ⚠️ {error}
              </div>
            )}

            {showUpload && (
              <FileUpload 
                onFileUploaded={handleFileUploaded}
              />
            )}

            {showPipeline && (
              <ProcessingPipeline onComplete={handlePipelineComplete} />
            )}

            {result && (
              <>
                <ResultsDisplay data={result} />
                
                {/* ✅ Action buttons after analysis */}
                <div className="re-upload-section">
                  <button 
                    className="btn btn-outline" 
                    onClick={handleReset}
                  >
                    📤 Upload Another Report
                  </button>
                  
                  {result.id && (
                    <button 
                      className="btn btn-primary"
                      onClick={handleViewFullReport}
                    >
                      📊 View My Reports →
                    </button>
                  )}
                </div>
              </>
            )}
          </div>

          {showUpload && !result && (
            <div className="analysis-info">
              <div className="info-grid">
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
            </div>
          )}

          <div className="analysis-disclaimer">
            <p>⚠️ <strong>Disclaimer:</strong> This tool provides analysis and explanations for educational purposes only. 
            Always consult a qualified healthcare professional for medical advice.</p>
          </div>
        </div>
      </div>

      {/* ===== FOOTER ===== */}
      <Footer />
    </>
  );
};

export default ReportAnalysis;