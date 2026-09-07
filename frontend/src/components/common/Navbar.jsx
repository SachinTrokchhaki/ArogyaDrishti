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

  const getInitials = (name) => {
    if (!name) return '?';
    return name.charAt(0).toUpperCase();
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
            <span className="logo-name">ArogyaDrishti</span>
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
              <button 
                className="user-avatar"
                onClick={() => navigate('/profile')}
                title={user?.username || user?.email}
              >
                {getInitials(user?.username || user?.email)}
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