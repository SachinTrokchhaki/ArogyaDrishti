import React, { createContext, useState, useContext, useEffect } from 'react';
import adminApi from '../services/adminApi';

const AdminAuthContext = createContext();

export const useAdminAuth = () => useContext(AdminAuthContext);

export const AdminAuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('admin_access_token');
    const cachedAdmin = localStorage.getItem('admin_user');

    if (token && cachedAdmin) {
      try {
        setAdmin(JSON.parse(cachedAdmin));
        adminApi.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      } catch {
        localStorage.removeItem('admin_access_token');
        localStorage.removeItem('admin_refresh_token');
        localStorage.removeItem('admin_user');
      }
    }
    setLoading(false);
  }, []);

  const adminLogin = async (email, password) => {
    try {
      setError(null);
      const res = await adminApi.post('/admin/login/', { email, password });
      const { access, refresh, user } = res.data;

      localStorage.setItem('admin_access_token', access);
      localStorage.setItem('admin_refresh_token', refresh);
      localStorage.setItem('admin_user', JSON.stringify(user));

      adminApi.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      setAdmin(user);

      return { success: true, user };
    } catch (err) {
      const msg = err.response?.data?.error || 'Login failed. Please try again.';
      setError(msg);
      return { success: false, error: msg };
    }
  };

  const adminLogout = () => {
    localStorage.removeItem('admin_access_token');
    localStorage.removeItem('admin_refresh_token');
    localStorage.removeItem('admin_user');
    delete adminApi.defaults.headers.common['Authorization'];
    setAdmin(null);
  };

  // ✅ Fetch fresh admin profile from backend
  const refreshAdmin = async () => {
    try {
      const res = await adminApi.get('/admin/profile/');
      setAdmin(res.data);
      localStorage.setItem('admin_user', JSON.stringify(res.data));
      return res.data;
    } catch (err) {
      console.error('refreshAdmin failed:', err);
      return null;
    }
  };

  // ✅ Safe updater that also persists to localStorage
  const updateAdmin = (patchOrFn) => {
    setAdmin((prev) => {
      const next =
        typeof patchOrFn === 'function'
          ? patchOrFn(prev)
          : { ...(prev || {}), ...patchOrFn };
      try {
        localStorage.setItem('admin_user', JSON.stringify(next));
      } catch {}
      return next;
    });
  };

  return (
    <AdminAuthContext.Provider
      value={{
        admin,
        loading,
        error,
        adminLogin,
        adminLogout,
        refreshAdmin,
        setAdmin: updateAdmin,
        isAdminAuthenticated: !!admin,
      }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
};