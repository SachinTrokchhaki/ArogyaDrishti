import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import adminApi from '../../services/adminApi';
import './Admin.css';

export default function AdminUsers() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchUsers();
  }, [search, filter]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (filter !== 'all') params.append('filter', filter);
      const res = await adminApi.get(`/admin/users/?${params.toString()}`);
      setUsers(res.data.users || []);
    } catch (err) {
      console.error('Users error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (userId) => {
    try {
      const res = await adminApi.post(`/admin/users/${userId}/toggle-active/`);
      setMessage({ type: 'success', text: res.data.message });
      fetchUsers();
    } catch (err) {
      setMessage({
        type: 'error',
        text: err.response?.data?.error || 'Failed to update user',
      });
    }
  };

  const getInitials = (u) => {
    if (u.first_name && u.last_name) {
      return (u.first_name[0] + u.last_name[0]).toUpperCase();
    }
    if (u.username) return u.username[0].toUpperCase();
    if (u.email) return u.email[0].toUpperCase();
    return '?';
  };

  const formatDate = (str) => {
    if (!str) return '—';
    return new Date(str).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  };

  return (
    <div className="admin-content">
      <div className="admin-header">
        <div>
          <h1 className="admin-title">Users</h1>
          <p className="admin-subtitle">{users.length} user{users.length !== 1 ? 's' : ''} found.</p>
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
              placeholder="Search by name, email, or username..."
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
            <option value="all">All users</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="staff">Staff</option>
          </select>
        </div>

        {loading ? (
          <div className="admin-loading">Loading...</div>
        ) : users.length === 0 ? (
          <div className="admin-empty">No users found.</div>
        ) : (
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Reports</th>
                  <th>Joined</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div className="admin-user-cell">
                        <div className="admin-user-avatar">
                          {u.avatar ? (
                            <img src={u.avatar} alt={u.username} />
                          ) : (
                            getInitials(u)
                          )}
                        </div>
                        <div className="admin-user-meta">
                          <span className="admin-user-name">
                            {u.first_name || u.last_name
                              ? `${u.first_name} ${u.last_name}`.trim()
                              : u.username}
                            {u.is_staff && <span className="admin-badge-staff">STAFF</span>}
                          </span>
                          <span className="admin-user-handle">@{u.username}</span>
                        </div>
                      </div>
                    </td>
                    <td>{u.email}</td>
                    <td>
                      <span className="admin-badge-count">{u.report_count}</span>
                    </td>
                    <td>{formatDate(u.date_joined)}</td>
                    <td>
                      <span className={`admin-badge ${u.is_active ? 'badge-active' : 'badge-inactive'}`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <div className="admin-actions-cell">
                        <button
                          className="admin-btn-small"
                          onClick={() => navigate(`/admin/users/${u.id}`)}
                        >
                          View
                        </button>
                        <button
                          className={`admin-btn-small ${u.is_active ? 'btn-danger' : 'btn-success'}`}
                          onClick={() => handleToggle(u.id)}
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
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
    </div>
  );
}