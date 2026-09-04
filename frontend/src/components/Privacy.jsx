import React from 'react';

const securityFeatures = [
  {
    icon: '🔒',
    title: 'Encrypted transfer',
    description: 'Files move over secure connections only.'
  },
  {
    icon: '👁️',
    title: 'No public sharing',
    description: 'Reports are never shown to other users.'
  },
  {
    icon: '🎯',
    title: 'You stay in control',
    description: 'Delete a report from your history anytime.'
  }
];

const Security = () => {
  return (
    <section id="security" className="security">
      <div className="container security-container">
        <div className="security-content">
          <h2 className="section-title">Your report stays your report</h2>
          <p className="security-description">
            Medical documents are sensitive. ArogyaDrishti is built so that reports
            are handled carefully at every step of processing.
          </p>
          <div className="security-features">
            {securityFeatures.map((feature, index) => (
              <div key={index} className="security-item">
                <span className="security-icon">{feature.icon}</span>
                <div>
                  <h4 className="security-item-title">{feature.title}</h4>
                  <p className="security-item-description">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="security-image">
          <div className="security-shield">🛡️</div>
        </div>
      </div>
    </section>
  );
};

export default Security;