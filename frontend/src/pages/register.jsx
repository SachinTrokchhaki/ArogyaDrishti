import "../styles/auth.css";
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import Footer from "../components/common/Footer";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();
  
  const [form, setForm] = useState({ 
    username: "", 
    email: "", 
    password: "", 
    password2: "" 
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [passwordRequirements, setPasswordRequirements] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false,
    special: false
  });

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    
    // Real-time password validation
    if (field === 'password') {
      setPasswordRequirements({
        length: value.length >= 8,
        uppercase: /[A-Z]/.test(value),
        lowercase: /[a-z]/.test(value),
        number: /\d/.test(value),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(value)
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    if (!form.username || !form.email || !form.password || !form.password2) {
      setError("Please fill in all the fields.");
      return;
    }

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (form.password !== form.password2) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const result = await register({
        username: form.username,
        email: form.email,
        password: form.password,
        password2: form.password2,
        first_name: form.username.split(' ')[0] || form.username,
        last_name: form.username.split(' ').slice(1).join(' ') || '',
      });

      if (result.success) {
        navigate("/");
      } else {
        if (result.errors) {
          setFieldErrors(result.errors);
        }
        setError(result.errors?.email?.[0] || "Registration failed. Please try again.");
      }
    } catch (err) {
      setError("Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-header">
  <div className="auth-logo">
    <span className="auth-logo-mark">♥</span>

    <div>
      <div className="auth-logo-name">
        <span className="logo-arogya">Arogya</span>
        <span className="logo-drishti">Drishti</span>
      </div>

      <div className="auth-logo-sub">
        REPORT ANALYSIS
      </div>
    </div>
  </div>

  <p className="auth-brand-tagline">
    Understand Your Health Reports, Simply.
  </p>
</div>

          <div className="auth-card">
            <h1 className="auth-title">Create your account</h1>
            <p className="auth-subtitle">It takes less than a minute to get started.</p>

            <form onSubmit={handleSubmit} className="auth-form" noValidate>
              <div className="form-group">
                <label htmlFor="username" className="form-label">Username</label>
                <input
                  id="username"
                  autoComplete="username"
                  placeholder="john_doe"
                  value={form.username}
                  onChange={(e) => update("username", e.target.value)}
                  className="form-input form-input-no-icon"
                  required
                />
                {fieldErrors.username && (
                  <span className="field-error">{fieldErrors.username[0]}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="email" className="form-label">Email</label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={(e) => update("email", e.target.value)}
                  className="form-input form-input-no-icon"
                  required
                />
                {fieldErrors.email && (
                  <span className="field-error">{fieldErrors.email[0]}</span>
                )}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="password" className="form-label">Password</label>
                  <input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    placeholder="••••••••"
                    value={form.password}
                    onChange={(e) => update("password", e.target.value)}
                    className="form-input form-input-no-icon"
                    required
                  />
                  {fieldErrors.password && (
                    <span className="field-error">{fieldErrors.password[0]}</span>
                  )}
                </div>
                <div className="form-group">
                  <label htmlFor="password2" className="form-label">Confirm password</label>
                  <input
                    id="password2"
                    type="password"
                    autoComplete="new-password"
                    placeholder="••••••••"
                    value={form.password2}
                    onChange={(e) => update("password2", e.target.value)}
                    className="form-input form-input-no-icon"
                    required
                  />
                  {fieldErrors.password2 && (
                    <span className="field-error">{fieldErrors.password2[0]}</span>
                  )}
                </div>
              </div>

              {/* Password Requirements */}
              {form.password && (
                <div className="password-requirements">
                  <p className="requirements-title">Password must contain:</p>
                  <ul>
                    <li className={passwordRequirements.length ? 'met' : ''}>
                      {passwordRequirements.length ? '✅' : '❌'} At least 8 characters
                    </li>
                    <li className={passwordRequirements.uppercase ? 'met' : ''}>
                      {passwordRequirements.uppercase ? '✅' : '❌'} One uppercase letter
                    </li>
                    <li className={passwordRequirements.lowercase ? 'met' : ''}>
                      {passwordRequirements.lowercase ? '✅' : '❌'} One lowercase letter
                    </li>
                    <li className={passwordRequirements.number ? 'met' : ''}>
                      {passwordRequirements.number ? '✅' : '❌'} One number
                    </li>
                    <li className={passwordRequirements.special ? 'met' : ''}>
                      {passwordRequirements.special ? '✅' : '❌'} One special character
                    </li>
                  </ul>
                </div>
              )}

              {error && (
                <div className="error-message">{error}</div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="submit-button"
              >
                {loading && <span className="spinner">⟳</span>}
                {loading ? "Creating account…" : "Register"}
              </button>
            </form>

            <p className="auth-footer-text">
              Already have an account?{" "}
              <Link to="/login" className="auth-link">
                Log in
              </Link>
            </p>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}