import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import './SharedReport.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export default function SharedReport() {
  const { token } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchReport() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_URL}/reports/share/${token}/`);
        if (!res.ok) {
          if (res.status === 404) throw new Error('Report not found or link expired.');
          throw new Error(`Failed to load report (${res.status})`);
        }
        const data = await res.json();
        if (!cancelled) setReport(data);
      } catch (err) {
        if (!cancelled) setError(err.message || 'Something went wrong.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchReport();
    return () => { cancelled = true; };
  }, [token]);

  if (loading) {
    return (
      <div className="sr-page">
        <div className="sr-loading">
          <div className="sr-spinner" />
          <p>Loading your report…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sr-page">
        <div className="sr-error-card">
          <div className="sr-error-icon">⚠️</div>
          <h1>Report unavailable</h1>
          <p>{error}</p>
          <Link to="/" className="sr-btn-primary">Go to ArogyaDrishti</Link>
        </div>
      </div>
    );
  }

  const processed = report.processed_data || {};
  const results = processed.results || [];
  const summary = processed.summary || {};
  const patient = processed.patient_info || {};
  const aiExp = report.ai_explanation || {};
  const medications = report.medications || [];
  const followUp = report.follow_up || [];

  const analyzedDate = new Date(report.created_at).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });

  return (
    <div className="sr-page">
      <header className="sr-header">
        <div className="sr-header-inner">
          <Link to="/" className="sr-brand">
            <span className="sr-brand-icon">♥</span>
            <span className="sr-brand-text">
              Arogya<span className="sr-brand-accent">Drishti</span>
            </span>
          </Link>
          <span className="sr-header-tag">SHARED REPORT</span>
        </div>
      </header>

      <main className="sr-main">
        <div className="sr-title-card">
          <p className="sr-eyebrow">📄 Report</p>
          <h1 className="sr-title">{report.file_name}</h1>
          <p className="sr-meta">🕐 Analyzed on {analyzedDate}</p>
        </div>

        <section className="sr-section">
          <h2 className="sr-section-title">📊 Summary</h2>
          <div className="sr-summary-grid">
            <div className="sr-summary-card">
              <span className="sr-summary-num">{summary.total_tests || 0}</span>
              <span className="sr-summary-label">Total Tests</span>
            </div>
            <div className="sr-summary-card sr-summary-normal">
              <span className="sr-summary-num">{summary.normal || 0}</span>
              <span className="sr-summary-label">Normal</span>
            </div>
            <div className="sr-summary-card sr-summary-low">
              <span className="sr-summary-num">{summary.low || 0}</span>
              <span className="sr-summary-label">Low</span>
            </div>
            <div className="sr-summary-card sr-summary-high">
              <span className="sr-summary-num">{summary.high || 0}</span>
              <span className="sr-summary-label">High</span>
            </div>
          </div>
        </section>

        {(patient.name || patient.age || patient.gender) && (
          <section className="sr-section">
            <h2 className="sr-section-title">👤 Patient Info</h2>
            <div className="sr-patient-card">
              <div><span>Name</span><strong>{patient.name || '—'}</strong></div>
              <div><span>Age</span><strong>{patient.age || '—'}</strong></div>
              <div><span>Gender</span><strong>{patient.gender || '—'}</strong></div>
            </div>
          </section>
        )}

        {results.length > 0 && (
          <section className="sr-section">
            <h2 className="sr-section-title">🧪 Lab Results</h2>
            <div className="sr-table-wrap">
              <table className="sr-table">
                <thead>
                  <tr>
                    <th>Test</th>
                    <th>Value</th>
                    <th>Unit</th>
                    <th>Reference</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, i) => {
                    const status = (r.status || '').toUpperCase();
                    const ref =
                      r.min_range != null && r.max_range != null
                        ? `${r.min_range} – ${r.max_range}`
                        : '—';
                    return (
                      <tr key={i} className={`sr-row-${status.toLowerCase()}`}>
                        <td>{r.test_name}</td>
                        <td>{r.value}</td>
                        <td>{r.unit || '—'}</td>
                        <td>{ref}</td>
                        <td>
                          <span className={`sr-badge sr-badge-${status.toLowerCase()}`}>
                            {status || '—'}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {aiExp.explanation && (
          <section className="sr-section">
            <h2 className="sr-section-title">🤖 AI Explanation</h2>
            <div className="sr-prose">
              {aiExp.explanation
                .replace(/^## /gm, '')
                .split('\n')
                .filter(Boolean)
                .map((line, i) => (
                  <p key={i}>{line.replace(/\*\*/g, '')}</p>
                ))}
            </div>
          </section>
        )}

        {medications.length > 0 &&
          medications[0].name !== 'No medications detected' && (
            <section className="sr-section">
              <h2 className="sr-section-title">💊 Medications</h2>
              <div className="sr-table-wrap">
                <table className="sr-table">
                  <thead>
                    <tr>
                      <th>Medication</th>
                      <th>Dosage</th>
                      <th>Frequency</th>
                      <th>Instructions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {medications.map((m, i) => (
                      <tr key={i}>
                        <td><strong>{m.name}</strong></td>
                        <td>{m.dosage}</td>
                        <td>{m.frequency}</td>
                        <td>{m.instructions}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

        {followUp.length > 0 && (
          <section className="sr-section">
            <h2 className="sr-section-title">📋 Recommended Follow-up</h2>
            <ul className="sr-list">
              {followUp.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </section>
        )}

        <div className="sr-disclaimer">
          ⚠️ <strong>Disclaimer:</strong> This is educational information, not a
          medical diagnosis. Always consult a qualified doctor for medical advice.
        </div>
      </main>

      <footer className="sr-footer">
        © {new Date().getFullYear()} ArogyaDrishti · Report Analysis
      </footer>
    </div>
  );
}