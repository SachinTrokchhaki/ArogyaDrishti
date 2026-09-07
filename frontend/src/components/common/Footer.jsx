import React from 'react';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <span>© {new Date().getFullYear()} ArogyaDrishti. Report analysis, not diagnosis.</span>
        <span>Always consult a qualified doctor for medical advice.</span>
      </div>
    </footer>
  );
}