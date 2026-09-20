import React from 'react';
import { Link, useNavigate, useLocation, Outlet, Navigate } from 'react-router-dom';
import { useAdminAuth } from '../../context/AdminAuthContext';
import './Admin.css';

export default function AdminLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { admin, adminLogout, isAdminAuthenticated, loading } = useAdminAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        Loading...
      </div>
    );
  }

  if (!isAdminAuthenticated) {
    return <Navigate to="/admin/login" replace />;
  }

  const handleLogout = () => {
    adminLogout();
    navigate('/admin/login');
  };

  const getInitials = () => {
    if (admin?.first_name && admin?.last_name) {
      return (admin.first_name[0] + admin.last_name[0]).toUpperCase();
    }
    if (admin?.username) return admin.username[0].toUpperCase();
    if (admin?.email) return admin.email[0].toUpperCase();
    return '?';
  };

  const getDisplayName = () => {
    if (admin?.first_name && admin?.last_name) {
      return `${admin.first_name} ${admin.last_name}`;
    }
    if (admin?.first_name) return admin.first_name;
    if (admin?.username) return admin.username;
    return 'Admin';
  };

  const menuItems = [
    { path: '/admin', label: 'Overview', icon: '▦', exact: true },
    { path: '/admin/users', label: 'Users', icon: '👥' },
    { path: '/admin/reports', label: 'Reports', icon: '📊' },
  ];

  const isActive = (item) => {
    if (item.exact) return location.pathname === item.path;
    return location.pathname.startsWith(item.path);
  };

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <Link to="/admin" className="admin-sidebar-logo">
          <span className="admin-logo-mark">♥</span>
          <span className="admin-logo-text-group">
            <span className="admin-logo-name">
              <span className="admin-logo-dark">Arogya</span>
              <span className="admin-logo-teal">Drishti</span>
            </span>
            <span className="admin-logo-sub">ADMIN PANEL</span>
          </span>
        </Link>

        <nav className="admin-sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`admin-sidebar-link ${isActive(item) ? 'active' : ''}`}
            >
              <span className="admin-sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="admin-sidebar-footer">
          <div className="admin-sidebar-user">
            <div className="admin-sidebar-avatar">{admin?.avatar ? (<img src={admin.avatar} alt={admin.username} />) : (getInitials())}</div>
            <div
             className="admin-sidebar-user-info">
              <span className="admin-sidebar-user-name">{getDisplayName()}</span>
              <span className="admin-sidebar-user-email">{admin?.email}</span>
            </div>
          </div>

          <button className="admin-sidebar-logout" onClick={handleLogout}>
            <span>↪</span> Logout
          </button>
        </div>
      </aside>

      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
}