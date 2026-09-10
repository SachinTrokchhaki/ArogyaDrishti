import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "./App.css";
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import { useAuth } from './context/AuthContext';
import doctorIllustration from './assets/doctor-illustration.jpg';
import prescriptionIcon from './assets/prescription-icon.png';
import heartRateIcon from './assets/heart-rate-icon.png';
import bloodPanelIcon from './assets/blood-panel-icon.png';
import bloodTestIcon from './assets/blood-test.png';

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
const faqs = [
  {
    question: "Is my medical data secure?",
    answer:
      "Your medical documents are handled carefully during processing. Reports are not publicly shared with other users."
  },
  {
    question: "Can it replace a real doctor?",
    answer:
      "No. ArogyaDrishti is designed to explain medical reports in simple language and is not a replacement for a qualified healthcare professional."
  },
  {
    question: "What types of reports can I upload?",
    answer:
      "You can upload supported medical reports such as blood tests, prescriptions, imaging reports, and other clinical documents in PDF, PNG, or JPG format."
  },
  {
    question: "How does abnormal-value detection work?",
    answer:
      "ArogyaDrishti compares values in your report with the reference ranges provided on the same report."
  },
  {
    question: "Does ArogyaDrishti provide a diagnosis?",
    answer:
      "No. It provides explanations and identifies information from the report. It does not diagnose medical conditions."
  }
];

const privacy = [
  { icon: "🔒", title: "Encrypted transfer", body: "Files move over secure connections only." },
  { icon: "🙈", title: "No public sharing", body: "Reports are never shown to other users." },
  { icon: "🛡️", title: "You stay in control", body: "Delete a report from your history anytime." },
];

export default function App() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [openFaq, setOpenFaq] = useState(null);

  const handleAnalyzeClick = () => {
    if (isAuthenticated) {
      navigate('/analyze');
    } else {
      navigate('/login');
    }
  };

  const handleGetStartedClick = () => {
    navigate('/login');
  };

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
              <button
                className="btn btn-primary btn-lg"
                onClick={handleAnalyzeClick}
              >
                Analyze a Report →
              </button>
              {!isAuthenticated && (
                <button
                  className="btn btn-outline btn-lg"
                  onClick={handleGetStartedClick}
                >
                  Get Started
                </button>
              )}
            </div>
            <div className="hero-notes">
              <span>✅ PDF, PNG, JPG supported</span>
              <span>✅ Reference-range validation</span>
            </div>
          </div>

          <div className="hero-visual">
            <div className="report-window">
              <div className="report-window-bar" aria-hidden="true">
                <span className="illustration-dot illustration-dot-red" />
                <span className="illustration-dot illustration-dot-yellow" />
                <span className="illustration-dot illustration-dot-green" />
              </div>
              <div className="report-window-body">
                <img
                  className="doctor-image"
                  src={doctorIllustration}
                  alt="Medical report analysis"
                />
              </div>
            </div>

            <div className="floating-card prescription">
              <b>PRESCRIPTION</b>
              <span>
                <img src={prescriptionIcon} alt="" />
                Amoxicillin 500mg
              </span>
            </div>

            <div className="floating-card heart-rate">
              <b>HEART RATE</b>
              <span>
                <img src={heartRateIcon} alt="" />
                72 BPM (Normal)
              </span>
            </div>

            <div className="floating-card blood-panel">
              <b>BLOOD PANEL</b>
              <span>
                <img src={bloodPanelIcon} alt="" />
                CBC <small>Analyzed</small>
              </span>
            </div>

            <div className="floating-card blood-test">
              <b>BLOOD TEST</b>
              <span>
                <img src={bloodTestIcon} alt="" />
                CBC Analyzed
              </span>
            </div>

            <div className="insights-card">✦ AI Insights Generated</div>
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

      {/* ===== FAQ SECTION ===== */}
<section className="section faq-section" id="faq">
  <div className="container">
    <h2>Frequently Asked Questions</h2>

    <div className="faq-list">
      {faqs.map((faq, index) => (
        <div
          className={`faq-item ${openFaq === index ? "open" : ""}`}
          key={faq.question}
        >
          <button
            className="faq-question"
            onClick={() =>
              setOpenFaq(openFaq === index ? null : index)
            }
          >
            <span>{faq.question}</span>
            <span className="faq-arrow">
              {openFaq === index ? "⌃" : "⌄"}
            </span>
          </button>

          {openFaq === index && (
            <div className="faq-answer">
              <p>{faq.answer}</p>
            </div>
          )}
        </div>
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
          <button
            className="btn btn-accent btn-lg"
            onClick={handleAnalyzeClick}
          >
            Analyze a Report →
          </button>
        </div>
      </div>

      {/* ===== FOOTER ===== */}
      <Footer />
    </>
  );
}