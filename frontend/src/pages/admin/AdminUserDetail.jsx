import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import adminApi from '../../services/adminApi';
import './Admin.css';

export default function AdminUserDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUser();
  }, [id]);

  const fetchUser = async () => {
    try {
      const res = await adminApi.get(`/admin/users/${id}/`);
      setUser(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load user');
    } finally {
      setLoading(false);
    }
  };

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return (user.first_name[0] + user.last_name[0]).toUpperCase();
    }
    if (user?.username) return user.username[0].toUpperCase();
    return '?';
  };

  const formatDate = (str) => {
    if (!str) return '—';
    return new Date(str).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  };

  if (loading) return <div className="admin-content"><div className="admin-loading">Loading...</div></div>;
  if (error) return <div className="admin-content"><div className="admin-alert-error">{error}</div></div>;
  if (!user) return <div className="admin-content"><div className="admin-empty">User not found.</div></div>;

  return (
    <div className="admin-content">
      <div className="admin-header">
        <div>
          <button className="admin-btn-back" onClick={() => navigate('/admin/users')}>
            ← Back to Users
          </button>
          <h1 className="admin-title" style={{ marginTop: '16px' }}>User Details</h1>
          <p className="admin-subtitle">Full profile and report history.</p>
        </div>
      </div>

      <div className="admin-user-card">
        <div className="admin-user-avatar-large">
          {user.avatar ? (
            <img src={user.avatar} alt={user.username} />
          ) : (
            getInitials()
          )}
        </div>
        <div className="admin-user-card-info">
          <h2>
            {user.first_name || user.last_name
              ? `${user.first_name} ${user.last_name}`.trim()
              : user.username}
            {user.is_staff && <span className="admin-badge-staff" style={{ marginLeft: '8px' }}>STAFF</span>}
          </h2>
          <p className="admin-user-card-email">{user.email}</p>
          <div className="admin-user-card-meta">
            <span>@{user.username}</span>
            <span>·</span>
            <span className={`admin-badge ${user.is_active ? 'badge-active' : 'badge-inactive'}`}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      <div className="admin-stats-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <div className="admin-stat-card">
          <div className="admin-stat-header">
            <span className="admin-stat-label">Reports</span>
            <span className="admin-stat-icon icon-teal">📊</span>
          </div>
          <div className="admin-stat-value">{user.report_count}</div>
        </div>
        <div className="admin-stat-card">
          <div className="admin-stat-header">
            <span className="admin-stat-label">Joined</span>
            <span className="admin-stat-icon icon-green">📅</span>
          </div>
          <div className="admin-stat-value" style={{ fontSize: '20px' }}>{formatDate(user.date_joined)}</div>
        </div>
        <div className="admin-stat-card">
          <div className="admin-stat-header">
            <span className="admin-stat-label">Last Login</span>
            <span className="admin-stat-icon icon-yellow">⏱</span>
          </div>
          <div className="admin-stat-value" style={{ fontSize: '20px' }}>{formatDate(user.last_login)}</div>
        </div>
      </div>

      <div className="admin-panel">
        <h2 className="admin-panel-title">📊 Reports ({user.report_count})</h2>
        {user.reports.length === 0 ? (
          <div className="admin-empty">This user has no reports yet.</div>
        ) : (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Tests</th>
                  <th>Abnormal</th>
                  <th>Uploaded</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {user.reports.map((r) => (
                  <tr key={r.id}>
                    <td><strong>{r.file_name}</strong></td>
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
                      <button
                        className="admin-btn-small"
                        onClick={() => navigate(`/admin/reports/${r.id}`)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}