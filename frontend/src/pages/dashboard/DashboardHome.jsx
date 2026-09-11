import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import './Dashboard.css';

export default function DashboardHome() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [trendData, setTrendData] = useState([]);
  const [trendTest, setTrendTest] = useState('hemoglobin');
  const [trendUnit, setTrendUnit] = useState('');
  const [stats, setStats] = useState({
    totalReports: 0,
    analyzed: 0,
    abnormalValues: 0,
    lastUpload: 'N/A',
  });

  useEffect(() => {
    fetchReports();
    fetchTrend('hemoglobin');
  }, []);

  const fetchReports = async () => {
    try {
      const response = await api.get('/reports/');
      const list = response.data.reports || [];
      setReports(list);

      const totalReports = list.length;
      const analyzed = list.filter(r => r.processed_data?.results?.length > 0).length;

      let abnormalCount = 0;
      list.forEach(r => {
        const results = r.processed_data?.results || [];
        abnormalCount += results.filter(x => x.status === 'HIGH' || x.status === 'LOW').length;
      });

      const lastUpload = list.length > 0
        ? new Date(list[0].created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
        : 'N/A';

      setStats({ totalReports, analyzed, abnormalValues: abnormalCount, lastUpload });
    } catch (error) {
      console.error('Fetch reports error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrend = async (testName) => {
    try {
      const response = await api.get(`/reports/trend/?test=${testName}`);
      setTrendData(response.data.data || []);
      setTrendUnit(response.data.unit || '');
    } catch (error) {
      console.error('Trend fetch error:', error);
      setTrendData([]);
    }
  };

  const handleTrendChange = (e) => {
    const value = e.target.value;
    setTrendTest(value);
    fetchTrend(value);
  };

  const getStatusBadge = (report) => {
    const hasResults = report.processed_data?.results?.length > 0;
    return hasResults
      ? { label: 'Analyzed', class: 'status-analyzed' }
      : { label: 'Processing', class: 'status-processing' };
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  };

  const getFirstName = () => {
    if (user?.first_name) return user.first_name;
    if (user?.username) return user.username;
    return 'User';
  };

  return (
    <div className="dashboard-content">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Welcome back, {getFirstName()} 👋</h1>
          <p className="dashboard-subtitle">
            {stats.abnormalValues > 0
              ? `You have ${stats.abnormalValues} abnormal value${stats.abnormalValues !== 1 ? 's' : ''} across ${stats.totalReports} report${stats.totalReports !== 1 ? 's' : ''}.`
              : 'Here is a quick overview of your report analyses.'}
          </p>
        </div>
        <button className="btn-upload-primary" onClick={() => navigate('/dashboard/upload')}>
          ⬆ Upload New Report
        </button>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <button className="quick-action-card" onClick={() => navigate('/dashboard/upload')}>
          <span className="quick-action-icon icon-teal">📤</span>
          <span className="quick-action-title">Upload Report</span>
          <span className="quick-action-desc">Analyze a new medical document</span>
        </button>
        <button className="quick-action-card" onClick={() => navigate('/dashboard/reports')}>
          <span className="quick-action-icon icon-green">📊</span>
          <span className="quick-action-title">My Reports</span>
          <span className="quick-action-desc">View your report history</span>
        </button>
        <button className="quick-action-card" onClick={() => navigate('/dashboard/profile')}>
          <span className="quick-action-icon icon-yellow">👤</span>
          <span className="quick-action-title">Profile</span>
          <span className="quick-action-desc">Manage your account</span>
        </button>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Total Reports</span>
            <span className="stat-card-icon icon-teal">📋</span>
          </div>
          <div className="stat-card-value">{stats.totalReports}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Reports Analysed</span>
            <span className="stat-card-icon icon-green">✓</span>
          </div>
          <div className="stat-card-value">{stats.analyzed}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Abnormal Values Found</span>
            <span className="stat-card-icon icon-red">⚠</span>
          </div>
          <div className="stat-card-value">{stats.abnormalValues}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-label">Last Upload</span>
            <span className="stat-card-icon icon-yellow">⏱</span>
          </div>
          <div className="stat-card-value stat-card-date">{stats.lastUpload}</div>
        </div>
      </div>

      {/* Two Column: Recent Reports + Chart */}
      <div className="dashboard-two-col">
        {/* Recent Reports */}
        <div className="dashboard-panel">
          <div className="panel-header">
            <h2 className="panel-title">Recent reports</h2>
            <button className="panel-link" onClick={() => navigate('/dashboard/reports')}>
              View all →
            </button>
          </div>

          {loading ? (
            <div className="loading-state">Loading reports...</div>
          ) : reports.length === 0 ? (
            <div className="empty-state">
              <p>No reports yet. Upload your first report to get started.</p>
              <button className="btn-upload-primary" onClick={() => navigate('/dashboard/upload')}>
                Upload Report
              </button>
            </div>
          ) : (
            <div className="recent-reports-list">
              {reports.slice(0, 5).map((report) => {
                const badge = getStatusBadge(report);
                const abnormalCount = (report.processed_data?.results || [])
                  .filter(r => r.status === 'HIGH' || r.status === 'LOW').length;

                return (
                  <div key={report.id} className="recent-report-item">
                    <div className="recent-report-info">
                      <span className="recent-report-name">{report.file_name}</span>
                      <span className="recent-report-meta">
                        {formatDate(report.created_at)} · {abnormalCount} abnormal value{abnormalCount !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="recent-report-actions">
                      <span className={`status-badge ${badge.class}`}>{badge.label}</span>
                      <button
                        className="btn-view-small"
                        onClick={() => navigate(`/dashboard/reports/${report.id}`)}
                      >
                        View
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Chart + Insight */}
        <div className="dashboard-right-col">
          <div className="dashboard-panel">
            <div className="panel-header">
              <h2 className="panel-title">📈 {trendTest.charAt(0).toUpperCase() + trendTest.slice(1)} trend</h2>
              <select
                className="trend-select"
                value={trendTest}
                onChange={handleTrendChange}
              >
                <option value="hemoglobin">Hemoglobin</option>
                <option value="cholesterol">Cholesterol</option>
                <option value="glucose">Glucose</option>
                <option value="creatinine">Creatinine</option>
                <option value="platelet">Platelet</option>
              </select>
            </div>

            {trendData.length < 2 ? (
              <div className="chart-empty">
                <p>Upload at least 2 reports with this test to see the trend.</p>
              </div>
            ) : (
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis
                      dataKey="display_date"
                      tick={{ fontSize: 11, fill: '#94a3b8' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: '#94a3b8' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        background: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        fontSize: '12px',
                      }}
                      formatter={(value) => [`${value} ${trendUnit}`, trendTest]}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#0d5c63"
                      strokeWidth={2.5}
                      dot={{ fill: '#0d5c63', r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
                <p className="chart-caption">
                  Values from your last {trendData.length} reports ({trendUnit || 'units'}).
                </p>
              </div>
            )}
          </div>

          {trendData.length >= 2 && (
            <div className="dashboard-panel insight-panel">
              <h2 className="panel-title">💡 Health insight</h2>
              <p className="insight-text">
                {(() => {
                  const first = trendData[0].value;
                  const last = trendData[trendData.length - 1].value;
                  const diff = last - first;
                  const pct = first !== 0 ? ((diff / first) * 100).toFixed(1) : 0;
                  const trend = diff > 0 ? 'increased' : diff < 0 ? 'decreased' : 'stayed stable';

                  return `Your ${trendTest} has ${trend} by ${Math.abs(pct)}% across your recent reports (from ${first} to ${last} ${trendUnit}). ${
                    diff < 0
                      ? 'Consider discussing this trend with a healthcare professional.'
                      : 'Keep maintaining your current routine.'
                  }`;
                })()}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}