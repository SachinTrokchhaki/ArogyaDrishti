import React from 'react';

const Footer = () => {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-cta">
          <h2 className="footer-title">Ready to read your report clearly?</h2>
          <p className="footer-description">
            Upload a report and see structured results in under a minute.
          </p>
          <button className="btn btn-primary btn-large">
            Upload Report Now
          </button>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 ArogyaDrishti. All rights reserved.</p>
          <div className="footer-links">
            <a onClick={scrollToTop}>Back to Top</a>
            <a>Privacy Policy</a>
            <a>Terms of Service</a>
            <a>Contact</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;