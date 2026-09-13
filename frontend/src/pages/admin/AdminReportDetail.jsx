import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ResultsDisplay from '../ResultsDisplay';
import adminApi from '../../services/adminApi';
import './Admin.css';

export default function AdminReportDetail() {
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
      const res = await adminApi.get(`/admin/reports/${id}/`);
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="admin-content"><div className="admin-loading">Loading...</div></div>;
  if (error) return <div className="admin-content"><div className="admin-alert-error">{error}</div></div>;
  if (!report) return <div className="admin-content"><div className="admin-empty">Report not found.</div></div>;

  return (
    <div className="admin-content">
      <div className="admin-header">
        <div>
          <button className="admin-btn-back" onClick={() => navigate('/admin/reports')}>
            ← Back to Reports
          </button>
          <h1 className="admin-title" style={{ marginTop: '16px' }}>Report View (Admin)</h1>
          <p className="admin-subtitle">{report.file_name}</p>
        </div>
      </div>

      <ResultsDisplay data={report} />
    </div>
  );
}