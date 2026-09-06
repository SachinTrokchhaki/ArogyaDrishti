import "../styles/auth.css";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Lock, Mail, Loader2 } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError("Please enter both your email and password.");
      return;
    }

    setLoading(true);
    try {
      // TODO: replace with Django API call
      // await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/login/`, {...})
      await new Promise((r) => setTimeout(r, 700));
      localStorage.setItem("ad_user", JSON.stringify({ email }));
      navigate("/dashboard");
    } catch {
      setError("We couldn't sign you in. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen bg-gradient-to-br from-teal-50 via-white to-emerald-50">
      <div className="mx-auto flex w-full max-w-md flex-col justify-center px-4 py-12">
        <div className="mb-8 text-center">
          <h2 className="text-2xl font-bold tracking-tight text-teal-700">ArogyaDrishti</h2>
          <p className="mt-1 text-sm text-slate-500">Understand Your Health Reports, Simply.</p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl shadow-teal-900/5 sm:p-8">
          <h1 className="text-2xl font-semibold text-slate-900">Welcome back</h1>
          <p className="mt-1 text-sm text-slate-500">Log in to view your report analyses.</p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-slate-700">
                Email
              </label>
              <div className="relative">
                <Mail className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white py-2 pr-3 pl-9 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-slate-700">
                Password
              </label>
              <div className="relative">
                <Lock className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white py-2 pr-3 pl-9 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-teal-600 focus:ring-2 focus:ring-teal-600/20"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm text-slate-600">
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 rounded border-slate-300 text-teal-600 focus:ring-teal-600/30"
                />
                Remember me
              </label>
              <button
                type="button"
                onClick={() => alert("Password reset will be handled by the backend.")}
                className="text-sm font-medium text-teal-700 hover:underline"
              >
                Forgot password?
              </button>
            </div>

            {error ? (
              <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
                {error}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-teal-700 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-teal-800 disabled:opacity-60"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {loading ? "Signing in…" : "Log in"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            New to ArogyaDrishti?{" "}
            <Link to="/register" className="font-medium text-teal-700 hover:underline">
              Create an account
            </Link>
          </p>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          Demo build — any email and password will sign you in.
        </p>
      </div>
    </main>
  );
}
