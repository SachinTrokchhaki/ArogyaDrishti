import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUpload from '../../components/FileUpload';
import ProcessingPipeline from '../../components/ProcessingPipeline';
import ResultsDisplay from '../ResultsDisplay';
import api from '../../services/api';
import './Dashboard.css';

export default function UploadReport() {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(true);
  const [showPipeline, setShowPipeline] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUploaded = async (file) => {
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

      // Small delay to show pipeline animation
      setTimeout(() => {
        setShowPipeline(false);
        setResult(response.data);
      }, 1500);

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

  const handleReset = () => {
    setResult(null);
    setShowUpload(true);
    setShowPipeline(false);
    setError(null);
  };

  return (
    <div className="dashboard-content">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Upload report</h1>
          <p className="dashboard-subtitle">
            Add a lab report and we will explain the values in simple language.
          </p>
        </div>
      </div>

      {error && (
        <div className="alert-error" style={{ marginBottom: '20px' }}>
          ⚠️ {error}
        </div>
      )}

      {showUpload && (
        <FileUpload onFileUploaded={handleFileUploaded} />
      )}

      {showPipeline && (
        <ProcessingPipeline onComplete={() => {}} />
      )}

      {result && (
        <>
          <ResultsDisplay data={result} />

          <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
            <button 
              className="btn-upload-primary"
              onClick={handleReset}
            >
              📤 Upload Another Report
            </button>
            <button 
              className="btn-back"
              onClick={() => navigate('/dashboard/reports')}
            >
              View My Reports
            </button>
          </div>
        </>
      )}

      {showUpload && !result && (
        <div className="dashboard-disclaimer">
          <span className="disclaimer-icon">⚠</span>
          <span>
            <strong>Disclaimer:</strong> This system provides educational information and is not a medical 
            diagnosis or a substitute for professional medical advice.
          </span>
        </div>
      )}
    </div>
  );
}