import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import './Dashboard.css';

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const fileInputRef = useRef(null);
  
  const [accountForm, setAccountForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
  });
  
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    highlightBorderline: true,
    keepHistory: true,
  });

  const [avatarPreview, setAvatarPreview] = useState(null);
  const [avatarFile, setAvatarFile] = useState(null);
  const [savingAccount, setSavingAccount] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (user) {
      setAccountForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
      });
      setAvatarPreview(user.avatar || null);
    }
  }, [user]);

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return (user.first_name[0] + user.last_name[0]).toUpperCase();
    }
    if (user?.username) return user.username[0].toUpperCase();
    if (user?.email) return user.email[0].toUpperCase();
    return '?';
  };

  const handleAvatarClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    fileInputRef.current?.click();
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Please select an image file (JPG, PNG, GIF, or WEBP)' });
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'Image must be less than 5MB' });
      return;
    }

    setAvatarFile(file);
    setMessage({ type: '', text: '' });

    // Show instant preview
    const reader = new FileReader();
    reader.onload = (ev) => setAvatarPreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  // ⭐ MAIN SAVE — handles BOTH avatar + name changes
  const handleAccountSave = async (e) => {
    e.preventDefault();
    setSavingAccount(true);
    setMessage({ type: '', text: '' });

    try {
      // 1️⃣ If a new avatar was selected, upload it first
      if (avatarFile) {
        const formData = new FormData();
        formData.append('avatar', avatarFile);

        await api.post('/auth/profile/upload-avatar/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        setAvatarFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }

      // 2️⃣ Save name changes (email is read-only)
      await api.put('/auth/profile/update/', {
        first_name: accountForm.first_name,
        last_name: accountForm.last_name,
      });

      // 3️⃣ Refresh user data — sidebar + avatar both update
      const freshUser = await refreshUser();

      // 4️⃣ Update preview with cache-busted URL
      if (freshUser?.avatar) {
        setAvatarPreview(`${freshUser.avatar}?t=${Date.now()}`);
      }

      setMessage({ type: 'success', text: 'Profile updated successfully!' });
    } catch (error) {
      console.error('Save error:', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to update profile',
      });
    } finally {
      setSavingAccount(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setSavingPassword(true);
    setMessage({ type: '', text: '' });

    try {
      await api.post('/auth/change-password/', passwordForm);
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Failed to change password' });
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <div className="dashboard-content">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Profile</h1>
          <p className="dashboard-subtitle">Manage your account details and preferences.</p>
        </div>
      </div>

      {message.text && (
        <div className={`alert-${message.type}`}>{message.text}</div>
      )}

      {/* Profile header card */}
      <div className="profile-header-card">
        <div className="profile-avatar-wrapper">
          <div
            className="profile-avatar-large"
            onClick={handleAvatarClick}
            title="Click to change photo"
          >
            {avatarPreview ? (
              <img
                src={avatarPreview}
                alt="Avatar"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.style.display = 'none';
                }}
              />
            ) : (
              getInitials()
            )}
            <div className="avatar-overlay"><span>📷</span></div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
            onChange={handleAvatarChange}
            style={{ display: 'none' }}
          />

          {/* Small hint below avatar when a new file is selected */}
          {avatarFile && (
            <span className="avatar-hint">New photo ready — click Save changes</span>
          )}
        </div>

        <div className="profile-header-info">
          <h2>
            {accountForm.first_name && accountForm.last_name
              ? `${accountForm.first_name} ${accountForm.last_name}`
              : user?.username || 'User'}
          </h2>
          <p className="profile-email">{user?.email}</p>
          <p className="profile-since">
            Member since {new Date(user?.date_joined || Date.now()).toLocaleDateString('en-GB', {
              month: 'long', year: 'numeric'
            })}
          </p>
        </div>
      </div>

      <div className="profile-two-col">
        {/* Account Info */}
        <div className="dashboard-panel">
          <h2 className="panel-title">Account information</h2>
          <form onSubmit={handleAccountSave} className="profile-form">
            <div className="form-group">
              <label>First name</label>
              <input
                type="text"
                value={accountForm.first_name}
                onChange={(e) => setAccountForm({ ...accountForm, first_name: e.target.value })}
                placeholder="First name"
              />
            </div>
            <div className="form-group">
              <label>Last name</label>
              <input
                type="text"
                value={accountForm.last_name}
                onChange={(e) => setAccountForm({ ...accountForm, last_name: e.target.value })}
                placeholder="Last name"
              />
            </div>
            <div className="form-group">
              <label>Email (read-only)</label>
              <input
                type="email"
                value={accountForm.email}
                disabled
                readOnly
                className="input-disabled"
                title="Email cannot be changed"
              />
              <span className="field-hint">
                Email cannot be changed. Contact support if you need to update it.
              </span>
            </div>

            <button type="submit" className="btn-save-primary" disabled={savingAccount}>
              {savingAccount ? 'Saving...' : 'Save changes'}
            </button>
          </form>
        </div>

        {/* Change Password */}
        <div className="dashboard-panel">
          <h2 className="panel-title">Change password</h2>
          <form onSubmit={handlePasswordChange} className="profile-form">
            <div className="form-group">
              <label>Current password</label>
              <input
                type="password"
                value={passwordForm.old_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })}
                placeholder="••••••••"
                required
              />
            </div>
            <div className="form-group">
              <label>New password</label>
              <input
                type="password"
                value={passwordForm.new_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                placeholder="••••••••"
                required
              />
            </div>
            <div className="form-group">
              <label>Confirm new password</label>
              <input
                type="password"
                value={passwordForm.confirm_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                placeholder="••••••••"
                required
              />
            </div>
            <button type="submit" className="btn-save-outline" disabled={savingPassword}>
              {savingPassword ? 'Updating...' : 'Update password'}
            </button>
          </form>
        </div>
      </div>

      {/* Preferences */}
      <div className="dashboard-panel">
        <h2 className="panel-title">Preferences</h2>
        <div className="preferences-list">
          <div className="preference-item">
            <div>
              <div className="preference-title">Email me when an analysis is ready</div>
              <div className="preference-desc">Get a short note once your uploaded report has been processed.</div>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={preferences.emailNotifications}
                onChange={(e) => setPreferences({ ...preferences, emailNotifications: e.target.checked })}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          <div className="preference-item">
            <div>
              <div className="preference-title">Highlight borderline values</div>
              <div className="preference-desc">Show borderline results with their own colour in report tables.</div>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={preferences.highlightBorderline}
                onChange={(e) => setPreferences({ ...preferences, highlightBorderline: e.target.checked })}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          <div className="preference-item">
            <div>
              <div className="preference-title">Keep report history</div>
              <div className="preference-desc">Store analysed reports so you can compare values over time.</div>
            </div>
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={preferences.keepHistory}
                onChange={(e) => setPreferences({ ...preferences, keepHistory: e.target.checked })}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}