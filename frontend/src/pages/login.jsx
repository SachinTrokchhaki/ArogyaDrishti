import "../styles/auth.css";
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/common/Navbar";
import Footer from "../components/common/Footer";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated, error: authError } = useAuth();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);
    try {
      const result = await login(email, password);
      if (result.success) {
        navigate("/");
      } else {
        setError(result.error || "Invalid email or password.");
      }
    } catch (err) {
      setError("Login failed. Please try again.");
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
            <h2>♥ ArogyaDrishti</h2>
            <p>Understand Your Health Reports, Simply.</p>
          </div>

          <div className="auth-card">
            <h1 className="auth-title">Welcome back</h1>
            <p className="auth-subtitle">Log in to view your report analyses.</p>

            <form onSubmit={handleSubmit} className="auth-form" noValidate>
              <div className="form-group">
                <label htmlFor="email" className="form-label">Email</label>
                <div className="input-wrapper">
                  <span className="input-icon">✉️</span>
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password" className="form-label">Password</label>
                <div className="input-wrapper">
                  <span className="input-icon">🔒</span>
                  <input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="form-input"
                    required
                  />
                </div>
              </div>

              <div className="form-options">
                <label className="checkbox-label">
                  <input type="checkbox" defaultChecked className="form-checkbox" />
                  Remember me
                </label>
                <button
                  type="button"
                  onClick={() => alert("Password reset will be handled by the backend.")}
                  className="link-button"
                >
                  Forgot password?
                </button>
              </div>

              {(error || authError) && (
                <div className="error-message">{error || authError}</div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="submit-button"
              >
                {loading && <span className="spinner">⟳</span>}
                {loading ? "Signing in…" : "Log in"}
              </button>
            </form>

            <p className="auth-footer-text">
              New to ArogyaDrishti?{" "}
              <Link to="/register" className="auth-link">
                Create an account
              </Link>
            </p>
          </div>

          <p className="auth-demo-note">
            Demo build — any email and password will sign you in.
          </p>
        </div>
      </div>
      <Footer />
    </>
  );
}