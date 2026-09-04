import React from 'react';

const Landing = () => {
  return (
    <section id="top" className="landing">
      <div className="container landing-container">
        <div className="landing-content">
          <h1 className="landing-title">
            Understand Your Medical Reports <br />
            <span className="highlight">in Simple Language</span>
          </h1>
          <p className="landing-description">
            Upload a medical report and get structured results, abnormal-value detection,
            and easy-to-understand explanations.
          </p>
          <div className="landing-buttons">
            <button className="btn btn-primary btn-large">
              Analyze a Report
            </button>
            <button className="btn btn-secondary btn-large">
              View Demo
            </button>
          </div>
          <div className="landing-badges">
            <span className="badge">📄 PDF, PNG, JPG supported</span>
            <span className="badge">📊 Reference-range validation</span>
          </div>
        </div>
        <div className="landing-image">
          <div className="landing-illustration">
            <span className="floating-icon">📋</span>
            <span className="floating-icon">🔬</span>
            <span className="floating-icon">🧠</span>
            <div className="landing-card">
              <div className="card-header">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
              <div className="report-line"></div>
              <div className="report-line"></div>
              <div className="report-line"></div>
              <div className="report-line"></div>
              <div className="report-line"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Landing;