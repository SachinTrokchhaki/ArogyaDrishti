import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import adminApi from '../../services/adminApi';
import './Admin.css';

export default function AdminHome() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await adminApi.get('/admin/stats/');
      setStats(res.data);
    } catch (err) {
      console.error('Stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="admin-content"><div className="admin-loading">Loading stats...</div></div>;
  }

  if (!stats) {
    return <div className="admin-content"><div className="admin-empty">Failed to load stats.</div></div>;
  }

  return (
    <div className="admin-content">
      <div className="admin-header">
        <div>
          <h1 className="admin-title">Admin Overview</h1>
          <p className="admin-subtitle">System-wide statistics and activity.</p>
        </div>
      </div>

      <div className="admin-stats-grid">
        <div className="admin-stat-card">
          <div className="admin-stat-header">
            <span className="admin-stat-label">Total Users</span>
            <span className="admin-stat-icon icon-teal">👥</span>
          </div>
          <div className="admin-stat-value">{stats.total_users}</div>
          <div className="admin-stat-sub">{stats.active_users} active · {stats.staff_users} staff</div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-header">
            <span className="admin-stat-label">Total Reports</span>
            <span className="admin-stat-icon icon-green">📊</span>
          </div>
          <div className="admin-stat-value">{stats.total_reports}</div>
          <div className="admin-stat-sub">{stats.reports_this_week} this week</div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-header">
            <span className="admin-stat-label">Uploads Today</span>
            <span className="admin-stat-icon icon-yellow">⏱</span>
          </div>
          <div className="admin-stat-value">{stats.reports_today}</div>
          <div className="admin-stat-sub">since midnight</div>
        </div>

        <div className="admin-stat-card">
          <div className="admin-stat-header">
            <span className="admin-stat-label">Abnormal Values</span>
            <span className="admin-stat-icon icon-red">⚠</span>
          </div>
          <div className="admin-stat-value">{stats.total_abnormal_values}</div>
          <div className="admin-stat-sub">across all reports</div>
        </div>
      </div>

      <div className="admin-panel">
        <div className="admin-panel-header">
          <h2 className="admin-panel-title">📈 Upload Activity (Last 14 Days)</h2>
        </div>
        <div className="admin-chart-wrapper">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={stats.daily_activity} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '8px', fontSize: '12px' }}
              />
              <Line type="monotone" dataKey="count" stroke="#0d5c63" strokeWidth={2.5} dot={{ fill: '#0d5c63', r: 3 }} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="admin-quick-actions">
        <button className="admin-quick-card" onClick={() => navigate('/admin/users')}>
          <span className="admin-quick-icon icon-teal">👥</span>
          <span className="admin-quick-title">View All Users</span>
          <span className="admin-quick-desc">Browse, search, and manage user accounts</span>
        </button>
        <button className="admin-quick-card" onClick={() => navigate('/admin/reports')}>
          <span className="admin-quick-icon icon-green">📊</span>
          <span className="admin-quick-title">View All Reports</span>
          <span className="admin-quick-desc">See every uploaded medical report</span>
        </button>
      </div>
    </div>
  );
}