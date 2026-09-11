import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // On mount: fetch fresh profile from backend
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      try {
        const response = await api.get('/auth/profile/');
        setUser(response.data);
        localStorage.setItem('user', JSON.stringify(response.data));
      } catch (e) {
        if (e.response?.status === 401) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          delete api.defaults.headers.common['Authorization'];
        } else {
          const cached = localStorage.getItem('user');
          if (cached) {
            try { setUser(JSON.parse(cached)); } catch {}
          }
        }
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await api.post('/auth/login/', { email, password });
      const { access, refresh } = response.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;

      // Fetch full profile (includes avatar)
      let fullUser = response.data.user;
      try {
        const profileRes = await api.get('/auth/profile/');
        fullUser = profileRes.data;
      } catch {}

      localStorage.setItem('user', JSON.stringify(fullUser));
      setUser(fullUser);

      return { success: true, user: fullUser };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      const response = await api.post('/auth/register/', userData);
      const { access, refresh } = response.data;

      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;

      let fullUser = response.data.user;
      try {
        const profileRes = await api.get('/auth/profile/');
        fullUser = profileRes.data;
      } catch {}

      localStorage.setItem('user', JSON.stringify(fullUser));
      setUser(fullUser);

      return { success: true, user: fullUser };
    } catch (error) {
      const errors = error.response?.data || {};
      setError(errors);
      return { success: false, errors };
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
    }
  };

  const refreshUser = async () => {
    try {
      const response = await api.get('/auth/profile/');
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error('Refresh user failed:', error);
      return null;
    }
  };

  const value = {
    user,
    setUser,
    loading,
    error,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};