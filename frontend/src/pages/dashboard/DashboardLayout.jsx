import React from 'react';
import { Link, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

export default function DashboardLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return (user.first_name[0] + user.last_name[0]).toUpperCase();
    }
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

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '▦' },
    { path: '/dashboard/upload', label: 'Upload Report', icon: '⬆' },
    { path: '/dashboard/reports', label: 'My Reports', icon: '📊' },
    { path: '/dashboard/profile', label: 'Profile', icon: '👤' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        <Link to="/" className="sidebar-logo">
          <span className="logo-mark">♥</span>
          <span className="logo-text-group">
            <span className="logo-name">
              <span className="logo-name-dark">Arogya</span>
              <span className="logo-name-teal">Drishti</span>
            </span>
            <span className="logo-sub">REPORT ANALYSIS</span>
          </span>
        </Link>

        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${isActive(item.path) ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">
              {user?.avatar ? (
                <img src={user.avatar} alt={user.username} />
              ) : (
                getInitials()
              )}
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{getDisplayName()}</span>
              <span className="sidebar-user-email">{user?.email}</span>
            </div>
          </div>

          <button className="sidebar-logout" onClick={handleLogout}>
            <span>↪</span> Logout
          </button>
        </div>
      </aside>

      <main className="dashboard-main">
        <Outlet />
      </main>
    </div>
  );
}