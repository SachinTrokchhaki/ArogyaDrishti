import React, { useState } from 'react';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <div className="navbar-brand" onClick={() => scrollToSection('top')}>
          <span className="brand-icon">🏥</span>
          <span className="brand-text">ArogyaDrishti</span>
        </div>

        <button 
          className="mobile-menu-btn"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Toggle menu"
        >
          <span className="hamburger"></span>
        </button>

        <ul className={`navbar-links ${isMenuOpen ? 'active' : ''}`}>
          <li><a onClick={() => scrollToSection('features')}>Features</a></li>
          <li><a onClick={() => scrollToSection('how-it-works')}>How It Works</a></li>
          <li><a onClick={() => scrollToSection('security')}>Privacy</a></li>
          <li>
            <button className="btn btn-primary">Upload Report</button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;