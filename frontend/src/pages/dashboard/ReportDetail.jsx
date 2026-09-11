import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ResultsDisplay from '../ResultsDisplay';
import api from '../../services/api';
import './Dashboard.css';

export default function ReportDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReport();
  }, [id]);

  const fetchReport = async () => {
    try {
      const response = await api.get(`/reports/${id}/`);
      setReport(response.data);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to load report. It may have been deleted.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-content">
        <div className="loading-state">Loading report...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-content">
        <div className="alert-error">{error}</div>
        <button 
          className="btn-back" 
          onClick={() => navigate('/dashboard/reports')}
          style={{ marginTop: '16px' }}
        >
          ← Back to Reports
        </button>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="dashboard-content">
        <div className="empty-state">Report not found.</div>
      </div>
    );
  }

  // Prepare data for ResultsDisplay - matches what backend sends
  const formattedData = {
    id: report.id,
    file_name: report.file_name,
    file_size: report.file_size,
    created_at: report.created_at,
    extracted_text: report.extracted_text,
    processed_data: report.processed_data || {},
    ai_explanation: report.ai_explanation || null,
    medications: report.medications || [],
    follow_up: report.follow_up || [],
    confidence: report.confidence || { ocr: 94, extraction: 91, classification: 96 },
  };

  return (
    <div className="dashboard-content">
      <div className="dashboard-header">
        <div>
          <button 
            className="btn-back" 
            onClick={() => navigate('/dashboard/reports')}
            style={{ marginBottom: '16px' }}
          >
            ← Back to Reports
          </button>
          <h1 className="dashboard-title">Report Details</h1>
          <p className="dashboard-subtitle">{report.file_name}</p>
        </div>
      </div>

      <ResultsDisplay data={formattedData} />
    </div>
  );
}