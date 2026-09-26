import React, { useState, useEffect, useRef } from 'react';
import { useAdminAuth } from '../../context/AdminAuthContext';
import adminApi from '../../services/adminApi';
import './Admin.css';

export default function AdminProfile() {
  const { admin, setAdmin, refreshAdmin } = useAdminAuth();
  const fileInputRef = useRef(null);

  const [accountForm, setAccountForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    bio: '',
  });

  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });

  const [avatarPreview, setAvatarPreview] = useState(null);
  const [avatarFile, setAvatarFile] = useState(null);
  const [savingAccount, setSavingAccount] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (admin) {
      setAccountForm({
        first_name: admin.first_name || '',
        last_name: admin.last_name || '',
        email: admin.email || '',
        phone: admin.phone || '',
        bio: admin.bio || '',
      });
      setAvatarPreview(admin.avatar || null);
    }
  }, [admin]);

  const getInitials = () => {
    if (admin?.first_name && admin?.last_name) {
      return (admin.first_name[0] + admin.last_name[0]).toUpperCase();
    }
    if (admin?.username) return admin.username[0].toUpperCase();
    if (admin?.email) return admin.email[0].toUpperCase();
    return 'A';
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

    const reader = new FileReader();
    reader.onload = (ev) => setAvatarPreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  const handleAccountSave = async (e) => {
    e.preventDefault();
    setSavingAccount(true);
    setMessage({ type: '', text: '' });

    try {
      // 1. Upload new avatar if selected
      if (avatarFile) {
        const formData = new FormData();
        formData.append('avatar', avatarFile);

        // ✅ No Content-Type header — axios sets multipart boundary
        const uploadRes = await adminApi.post('/admin/profile/upload-avatar/', formData);

        if (uploadRes.data?.avatar_url) {
          setAvatarPreview(`${uploadRes.data.avatar_url}?t=${Date.now()}`);
        }

        setAvatarFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }

      // 2. Update name/phone/bio
      const res = await adminApi.put('/admin/profile/update/', {
        first_name: accountForm.first_name,
        last_name: accountForm.last_name,
        phone: accountForm.phone,
        bio: accountForm.bio,
      });

      // 3. Refresh admin in context so sidebar updates
      if (refreshAdmin) {
        await refreshAdmin();
      } else if (setAdmin) {
        setAdmin((prev) => ({ ...prev, ...res.data }));
      }

      if (res.data.avatar) {
        setAvatarPreview(`${res.data.avatar}?t=${Date.now()}`);
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
      await adminApi.post('/admin/profile/change-password/', passwordForm);
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      const errs = error.response?.data || {};
      const first =
        errs.error ||
        errs.password?.[0] ||
        errs.old_password?.[0] ||
        errs.password2?.[0] ||
        'Failed to change password';
      setMessage({ type: 'error', text: first });
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <div className="admin-content">
      <div className="admin-header">
        <div>
          <h1 className="admin-title">My Profile</h1>
          <p className="admin-subtitle">Manage your admin account details.</p>
        </div>
      </div>

      {message.text && (
        <div className={`alert-${message.type}`}>{message.text}</div>
      )}

      <div className="admin-profile-header-card">
        <div className="admin-profile-avatar-wrapper">
          <div
            className="admin-profile-avatar-large"
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
            <div className="admin-avatar-overlay"><span>📷</span></div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
            onChange={handleAvatarChange}
            style={{ display: 'none' }}
          />

          {avatarFile && (
            <span className="admin-avatar-hint">New photo ready — click Save</span>
          )}
        </div>

        <div className="admin-profile-header-info">
          <h2>
            {accountForm.first_name && accountForm.last_name
              ? `${accountForm.first_name} ${accountForm.last_name}`
              : admin?.username || 'Admin'}
          </h2>
          <p className="admin-profile-email">{admin?.email}</p>
          <p className="admin-profile-role">
            {admin?.is_superuser ? '👑 Superuser' : '🛡 Administrator'}
          </p>
        </div>
      </div>

      <div className="admin-profile-two-col">
        <div className="admin-panel">
          <h2 className="admin-panel-title">Account information</h2>
          <form onSubmit={handleAccountSave} className="admin-profile-form">
            <div className="admin-form-group">
              <label>First name</label>
              <input
                type="text"
                value={accountForm.first_name}
                onChange={(e) => setAccountForm({ ...accountForm, first_name: e.target.value })}
                placeholder="First name"
              />
            </div>
            <div className="admin-form-group">
              <label>Last name</label>
              <input
                type="text"
                value={accountForm.last_name}
                onChange={(e) => setAccountForm({ ...accountForm, last_name: e.target.value })}
                placeholder="Last name"
              />
            </div>
            <div className="admin-form-group">
              <label>Email (read-only)</label>
              <input
                type="email"
                value={accountForm.email}
                disabled
                readOnly
                className="admin-input-disabled"
              />
              <span className="admin-field-hint">Email cannot be changed.</span>
            </div>
            <div className="admin-form-group">
              <label>Phone</label>
              <input
                type="text"
                value={accountForm.phone}
                onChange={(e) => setAccountForm({ ...accountForm, phone: e.target.value })}
                placeholder="+977 98XXXXXXXX"
              />
            </div>
            <div className="admin-form-group">
              <label>Bio</label>
              <textarea
                rows={3}
                value={accountForm.bio}
                onChange={(e) => setAccountForm({ ...accountForm, bio: e.target.value })}
                placeholder="A short note about you..."
              />
            </div>

            <button type="submit" className="admin-btn-primary" disabled={savingAccount}>
              {savingAccount ? 'Saving...' : 'Save changes'}
            </button>
          </form>
        </div>

        <div className="admin-panel">
          <h2 className="admin-panel-title">Change password</h2>
          <form onSubmit={handlePasswordChange} className="admin-profile-form">
            <div className="admin-form-group">
              <label>Current password</label>
              <input
                type="password"
                value={passwordForm.old_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })}
                placeholder="••••••••"
                required
              />
            </div>
            <div className="admin-form-group">
              <label>New password</label>
              <input
                type="password"
                value={passwordForm.new_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })}
                placeholder="••••••••"
                required
                minLength={8}
              />
            </div>
            <div className="admin-form-group">
              <label>Confirm new password</label>
              <input
                type="password"
                value={passwordForm.confirm_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                placeholder="••••••••"
                required
              />
            </div>
            <button type="submit" className="admin-btn-outline" disabled={savingPassword}>
              {savingPassword ? 'Updating...' : 'Update password'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}