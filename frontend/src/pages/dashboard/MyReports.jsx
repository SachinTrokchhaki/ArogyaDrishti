import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './Dashboard.css';

export default function MyReports() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortOrder, setSortOrder] = useState('newest');
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    fetchReports();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [reports, searchTerm, filterType, sortOrder]);

  const fetchReports = async () => {
    try {
      const response = await api.get('/reports/');
      setReports(response.data.reports || []);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let result = [...reports];

    if (searchTerm) {
      result = result.filter(r => 
        r.file_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterType !== 'all') {
      result = result.filter(r => {
        const hasResults = r.processed_data?.results?.length > 0;
        if (filterType === 'analyzed') return hasResults;
        if (filterType === 'processing') return !hasResults;
        return true;
      });
    }

    result.sort((a, b) => {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);
      return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
    });

    setFiltered(result);
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/reports/${id}/delete/`);
      setReports(reports.filter(r => r.id !== id));
      setDeleteConfirm(null);
    } catch (error) {
      console.error('Delete error:', error);
      alert('Failed to delete report');
    }
  };

  const getStatusBadge = (report) => {
    const hasResults = report.processed_data?.results?.length > 0;
    if (hasResults) return { label: 'Analyzed', class: 'status-analyzed' };
    return { label: 'Processing', class: 'status-processing' };
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  };

  return (
    <div className="dashboard-content">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">My reports</h1>
          <p className="dashboard-subtitle">{reports.length} report{reports.length !== 1 ? 's' : ''} in your history.</p>
        </div>
        <button 
          className="btn-upload-primary"
          onClick={() => navigate('/dashboard/upload')}
        >
          ⬆ Upload Report
        </button>
      </div>

      <div className="dashboard-panel">
        {/* Filter Bar */}
        <div className="reports-filter-bar">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>

          <select 
            className="filter-select"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="all">All types</option>
            <option value="analyzed">Analyzed</option>
            <option value="processing">Processing</option>
          </select>

          <select 
            className="filter-select"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </select>
        </div>

        {/* Reports List */}
        {loading ? (
          <div className="loading-state">Loading reports...</div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <p>No reports found.</p>
          </div>
        ) : (
          <div className="reports-list">
            {filtered.map((report) => {
              const badge = getStatusBadge(report);
              const abnormalCount = (report.processed_data?.results || [])
                .filter(r => r.status === 'HIGH' || r.status === 'LOW').length;

              return (
                <div key={report.id} className="report-list-item">
                  <div className="report-list-info">
                    <span className="report-list-name">{report.file_name}</span>
                    <span className="report-list-meta">
                      {formatDate(report.created_at)} · {abnormalCount} abnormal value{abnormalCount !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <div className="report-list-actions">
                    <span className={`status-badge ${badge.class}`}>{badge.label}</span>
                    <button 
                      className="btn-view-small"
                      onClick={() => navigate(`/dashboard/reports/${report.id}`)}
                    >
                      View Report
                    </button>
                    <button 
                      className="btn-icon-delete"
                      onClick={() => setDeleteConfirm(report.id)}
                      title="Delete"
                    >
                      🗑
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Delete Modal */}
      {deleteConfirm && (
        <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Delete Report?</h3>
            <p>This action cannot be undone.</p>
            <div className="modal-actions">
              <button className="btn-cancel" onClick={() => setDeleteConfirm(null)}>
                Cancel
              </button>
              <button className="btn-delete-confirm" onClick={() => handleDelete(deleteConfirm)}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}