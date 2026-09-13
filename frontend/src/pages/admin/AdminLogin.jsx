import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAdminAuth } from '../../context/AdminAuthContext';
import './AdminLogin.css';

export default function AdminLogin() {
  const navigate = useNavigate();
  const { adminLogin, isAdminAuthenticated, error: ctxError } = useAdminAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isAdminAuthenticated) {
      navigate('/admin', { replace: true });
    }
  }, [isAdminAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    try {
      const result = await adminLogin(email, password);
      if (result.success) {
        navigate('/admin', { replace: true });
      } else {
        setError(result.error || 'Login failed');
      }
    } catch {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-page">
      <div className="admin-login-container">
        <div className="admin-login-header">
          <div className="admin-login-logo">
            <span className="admin-login-logo-mark">♥</span>
            <span className="admin-login-logo-name">
              <span style={{ color: '#ffffff' }}>Arogya</span>
              <span style={{ color: '#5eead4' }}>Drishti</span>
            </span>
          </div>
          <span className="admin-login-badge">ADMIN ACCESS</span>
          <p className="admin-login-subtitle">
            Restricted area. Administrator credentials required.
          </p>
        </div>

        <div className="admin-login-card">
          <h1 className="admin-login-title">Admin Login</h1>
          <p className="admin-login-desc">
            Only staff accounts can access this panel.
          </p>

          <form onSubmit={handleSubmit} className="admin-login-form" noValidate>
            <div className="admin-login-field">
              <label htmlFor="admin-email">Email</label>
              <input
                id="admin-email"
                type="email"
                autoComplete="off"
                placeholder="admin@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="admin-login-input"
                required
              />
            </div>

            <div className="admin-login-field">
              <label htmlFor="admin-password">Password</label>
              <input
                id="admin-password"
                type="password"
                autoComplete="off"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="admin-login-input"
                required
              />
            </div>

            {(error || ctxError) && (
              <div className="admin-login-error">{error || ctxError}</div>
            )}

            <button
              type="submit"
              className="admin-login-btn"
              disabled={loading}
            >
              {loading ? 'Verifying...' : 'Access Admin Panel'}
            </button>
          </form>

          <p className="admin-login-note">
            🔒 This page is separate from user login.
          </p>
        </div>

        <p className="admin-login-footer">
          Not an admin?{' '}
          <a href="/login">Go to user login</a>
        </p>
      </div>
    </div>
  );
}