import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return (user.first_name[0] + user.last_name[0]).toUpperCase();
    }
    if (user?.first_name) return user.first_name[0].toUpperCase();
    if (user?.username) return user.username[0].toUpperCase();
    if (user?.email) return user.email[0].toUpperCase();
    return '?';
  };

  const getDisplayName = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    if (user?.first_name) return user.first_name;
    if (user?.username) return user.username;
    return 'User';
  };

  const handleAnalyzeClick = () => {
    if (isAuthenticated) {
      navigate('/analyze');
    } else {
      navigate('/login');
    }
  };

  const handleNavClick = (e, sectionId) => {
    e.preventDefault();
    if (window.location.pathname !== '/') {
      navigate('/');
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } else {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <header className="header">
      <div className="container header-inner">
        <Link to="/" className="logo">
          <span className="logo-mark">♥</span>
          <span>
            <span className="logo-name">
              <span className="logo-arogya">Arogya</span><span className="logo-drishti">Drishti</span>
            </span>
            <br />
            <span className="logo-sub">REPORT ANALYSIS</span>
          </span>
        </Link>

        <nav className="nav">
          <a href="#features" onClick={(e) => handleNavClick(e, 'features')}>
            Features
          </a>
          <a href="#how" onClick={(e) => handleNavClick(e, 'how')}>
            How it works
          </a>
          <a href="#privacy" onClick={(e) => handleNavClick(e, 'privacy')}>
            Privacy
          </a>
        </nav>

        <div className="header-actions">
          {isAuthenticated ? (
            <div className="user-profile">
              {/* Clickable user info block */}
              <button
                className="navbar-user-info"
                onClick={() => navigate('/dashboard')}
                title="Go to dashboard"
              >
                <div className="navbar-user-avatar">
                  {user?.avatar ? (
                    <img
                      src={user.avatar}
                      alt={getDisplayName()}
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.style.display = 'none';
                        e.target.parentNode.textContent = getInitials();
                      }}
                    />
                  ) : (
                    getInitials()
                  )}
                </div>
                <div className="navbar-user-details">
                  <span className="navbar-user-name">{getDisplayName()}</span>
                  <span className="navbar-user-email">{user?.email}</span>
                </div>
              </button>

              <button
                className="btn btn-outline btn-sm"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          ) : (
            <>
              <Link to="/login">
                <button className="btn btn-outline">Get Started</button>
              </Link>
              <button
                className="btn btn-primary"
                onClick={handleAnalyzeClick}
              >
                Analyze a Report
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}