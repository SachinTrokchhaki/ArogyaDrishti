import React from 'react';
import "./App.css";
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';

const features = [
  { icon: "🔍", title: "OCR & Text Extraction", body: "Scanned pages and photographs are converted into clean, searchable report text." },
  { icon: "🗂️", title: "Medical Report Classification", body: "CBC, biochemistry, imaging, ECG, prescriptions and discharge summaries are recognised automatically." },
  { icon: "⚠️", title: "Abnormal Value Detection", body: "Each value is compared with the reference range printed on your own report." },
  { icon: "✨", title: "AI-Assisted Explanation", body: "A plain-language summary that explains what the report says, without medical jargon." },
];

const steps = [
  { icon: "⬆️", title: "Upload Report", body: "Add a PDF or image of your medical report." },
  { icon: "📄", title: "Extract Information", body: "Text and structured fields are pulled from the file." },
  { icon: "✅", title: "Validate Results", body: "Values are checked against the report's reference ranges." },
  { icon: "💬", title: "Get Simple Explanation", body: "Read a patient-friendly summary of the findings." },
];

const privacy = [
  { icon: "🔒", title: "Encrypted transfer", body: "Files move over secure connections only." },
  { icon: "🙈", title: "No public sharing", body: "Reports are never shown to other users." },
  { icon: "🛡️", title: "You stay in control", body: "Delete a report from your history anytime." },
];

export default function App() {
  return (
    <>
      {/* ===== NAVBAR ===== */}
      <Navbar />

      {/* ===== HERO SECTION ===== */}
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-content">
            <span className="badge">✅ Report analysis, not diagnosis</span>
            <h1>Understand Your Medical Reports in Simple Language</h1>
            <p className="lead">
              Upload a medical report and get structured results, abnormal-value detection, and
              easy-to-understand explanations.
            </p>
            <div className="hero-actions">
              <a href="/analyze">
                <button className="btn btn-primary btn-lg">Analyze a Report →</button>
              </a>
              <button className="btn btn-outline btn-lg">Get Started</button>
            </div>
            <div className="hero-notes">
              <span>✅ PDF, PNG, JPG supported</span>
              <span>✅ Reference-range validation</span>
            </div>
          </div>

          <div className="hero-preview">
            <div className="preview">
              <div className="preview-bar">
                <span className="dot" style={{ background: "#e57373" }}></span>
                <span className="dot" style={{ background: "#ffb74d" }}></span>
                <span className="dot" style={{ background: "#66bb6a" }}></span>
                <span className="preview-title">Blood Test Report — Analysis Complete</span>
              </div>
              <div className="preview-body">
                <div className="preview-placeholder">
                  <span className="placeholder-icon">📋</span>
                  <p>Click "Analyze a Report" to upload your medical document</p>
                  <p className="placeholder-sub">Supports PDF, PNG, JPG up to 10MB</p>
                </div>
                <div className="preview-features">
                  <div className="preview-feature">
                    <span>🔍</span>
                    <span>OCR Extraction</span>
                  </div>
                  <div className="preview-feature">
                    <span>📊</span>
                    <span>Value Validation</span>
                  </div>
                  <div className="preview-feature">
                    <span>🤖</span>
                    <span>AI Explanation</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== FEATURES SECTION ===== */}
      <section className="section" id="features">
        <div className="container">
          <h2>Built for real medical reports</h2>
          <p className="sub">
            Every stage of the analysis pipeline is designed around what is actually printed on your report.
          </p>
          <div className="cards">
            {features.map((f) => (
              <article className="card" key={f.title}>
                <span className="icon">{f.icon}</span>
                <h3>{f.title}</h3>
                <p>{f.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ===== HOW IT WORKS SECTION ===== */}
      <section className="section alt" id="how">
        <div className="container">
          <h2>How ArogyaDrishti Works</h2>
          <p className="sub">Four clear steps between uploading a document and understanding it.</p>
          <div className="cards">
            {steps.map((s, i) => (
              <article className="card" key={s.title}>
                <div className="card-top">
                  <span className="icon">{s.icon}</span>
                  <span className="step-num">{String(i + 1).padStart(2, "0")}</span>
                </div>
                <h3>{s.title}</h3>
                <p>{s.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ===== PRIVACY SECTION ===== */}
      <section className="section" id="privacy">
        <div className="container privacy-grid">
          <div>
            <h2>Your report stays your report</h2>
            <p className="sub" style={{ maxWidth: 420, lineHeight: 1.7 }}>
              Medical documents are sensitive. ArogyaDrishti is built so that reports are handled
              carefully at every step of processing.
            </p>
          </div>
          <div className="privacy-cards">
            {privacy.map((p) => (
              <article className="card" key={p.title}>
                <span style={{ fontSize: 16 }}>{p.icon}</span>
                <h3>{p.title}</h3>
                <p>{p.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* ===== CTA SECTION ===== */}
      <div className="container">
        <div className="cta">
          <div>
            <h3>Ready to read your report clearly?</h3>
            <p>Upload a report and see structured results in under a minute.</p>
          </div>
          <a href="/analyze">
            <button className="btn btn-accent btn-lg">Analyze a Report →</button>
          </a>
        </div>
      </div>

      {/* ===== FOOTER ===== */}
      <Footer />
    </>
  );
}