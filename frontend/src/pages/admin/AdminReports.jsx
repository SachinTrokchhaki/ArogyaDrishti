import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import adminApi from '../../services/adminApi';
import './Admin.css';

export default function AdminReports() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [message, setMessage] = useState({ type: '', text: '' });
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    fetchReports();
  }, [search, filter]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (filter !== 'all') params.append('filter', filter);
      const res = await adminApi.get(`/admin/reports/?${params.toString()}`);
      setReports(res.data.reports || []);
    } catch (err) {
      console.error('Reports error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (reportId) => {
    try {
      await adminApi.delete(`/admin/reports/${reportId}/delete/`);
      setMessage({ type: 'success', text: 'Report deleted successfully!' });
      setDeleteConfirm(null);
      fetchReports();
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.error || 'Failed to delete report',
      });
    }
  };

  const formatDate = (str) => {
    if (!str) return '—';
    return new Date(str).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  };

  const formatSize = (bytes) => {
    if (!bytes) return '—';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  return (
    <div className="admin-content">
      <div className="admin-header">
        <div>
          <h1 className="admin-title">Reports</h1>
          <p className="admin-subtitle">{reports.length} report{reports.length !== 1 ? 's' : ''} found.</p>
        </div>
      </div>

      {message.text && (
        <div className={`admin-alert-${message.type}`}>{message.text}</div>
      )}

      <div className="admin-panel">
        <div className="admin-filter-bar">
          <div className="admin-search-box">
            <span className="admin-search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search by file name, user, or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="admin-search-input"
            />
          </div>
          <select
            className="admin-filter-select"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All reports</option>
            <option value="analyzed">Analyzed</option>
            <option value="processing">Processing</option>
          </select>
        </div>

        {loading ? (
          <div className="admin-loading">Loading...</div>
        ) : reports.length === 0 ? (
          <div className="admin-empty">No reports found.</div>
        ) : (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>User</th>
                  <th>Size</th>
                  <th>Tests</th>
                  <th>Abnormal</th>
                  <th>Uploaded</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => (
                  <tr key={r.id}>
                    <td><strong>{r.file_name}</strong></td>
                    <td>
                      <div className="admin-user-cell-compact">
                        <span className="admin-user-name-sm">@{r.username}</span>
                        <span className="admin-user-email-sm">{r.user_email}</span>
                      </div>
                    </td>
                    <td>{formatSize(r.file_size)}</td>
                    <td>{r.total_tests}</td>
                    <td>
                      {r.abnormal_count > 0 ? (
                        <span className="admin-badge badge-warning">{r.abnormal_count}</span>
                      ) : (
                        <span className="admin-badge badge-active">0</span>
                      )}
                    </td>
                    <td>{formatDate(r.created_at)}</td>
                    <td>
                      <span className={`admin-badge ${r.status === 'analyzed' ? 'badge-active' : 'badge-processing'}`}>
                        {r.status}
                      </span>
                    </td>
                    <td>
                        <div className="admin-actions-cell">
                            <button
                                className="admin-btn-small"
                                onClick={() => navigate(`/admin/reports/${r.id}`)}
                            >
                            View
                            </button>
                            <button
                                className="admin-btn-small btn-danger"
                                onClick={() => setDeleteConfirm(r.id)}
                            >
                            Delete
                            </button>
                        </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {deleteConfirm && (
        <div className="admin-modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Delete Report?</h3>
            <p>This action cannot be undone.</p>
            <div className="admin-modal-actions">
              <button className="admin-btn-cancel" onClick={() => setDeleteConfirm(null)}>
                Cancel
              </button>
              <button className="admin-btn-danger" onClick={() => handleDelete(deleteConfirm)}>
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}