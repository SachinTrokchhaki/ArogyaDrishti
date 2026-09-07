import React from 'react';

export default function Navbar() {
  return (
    <header className="header">
      <div className="container header-inner">
        <a href="/" className="logo">
          <span className="logo-mark">♥</span>
          <span>
            <span className="logo-name">ArogyaDrishti</span>
            <br />
            <span className="logo-sub">REPORT ANALYSIS</span>
          </span>
        </a>

        <nav className="nav">
          <a href="#features">Features</a>
          <a href="#how">How it works</a>
          <a href="#privacy">Privacy</a>
        </nav>

        <div className="header-actions">
          <button className="btn btn-outline">Get Started</button>
          <a href="/analyze">
            <button className="btn btn-primary">Analyze a Report</button>
          </a>
        </div>
      </div>
    </header>
  );
}