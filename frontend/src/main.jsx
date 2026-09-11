import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import App from './App';
import ReportAnalysis from './pages/ReportAnalysis';
import Login from './pages/login';
import Register from './pages/register';
import DashboardLayout from './pages/dashboard/DashboardLayout';
import DashboardHome from './pages/dashboard/DashboardHome';
import MyReports from './pages/dashboard/MyReports';
import UploadReport from './pages/dashboard/UploadReport';
import ReportDetail from './pages/dashboard/ReportDetail';
import Profile from './pages/dashboard/Profile';
import './index.css';
import './styles/auth.css';

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/analyze" element={<ReportAnalysis />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Dashboard Routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }>
            <Route index element={<DashboardHome />} />
            <Route path="upload" element={<UploadReport />} />
            <Route path="reports" element={<MyReports />} />
            <Route path="reports/:id" element={<ReportDetail />} />
            <Route path="profile" element={<Profile />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);