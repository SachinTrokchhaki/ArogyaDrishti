import React from 'react';

const features = [
  {
    icon: '🔍',
    title: 'OCR & Text Extraction',
    description: 'Scanned pages and photographs are converted into clean, searchable report text.'
  },
  {
    icon: '📊',
    title: 'Medical Report Classification',
    description: 'CBC, biochemistry, imaging, ECG, prescriptions and discharge summaries are recognised automatically.'
  },
  {
    icon: '⚠️',
    title: 'Abnormal Value Detection',
    description: 'Each value is compared with the reference range printed on your own report.'
  },
  {
    icon: '💡',
    title: 'AI-Assisted Explanation',
    description: 'A plain-language summary that explains what the report says, without medical jargon.'
  }
];

const Features = () => {
  return (
    <section id="features" className="features">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Built for Real Medical Reports</h2>
          <p className="section-subtitle">
            Every stage of the analysis pipeline is designed around what is actually printed on your report.
          </p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <span className="feature-icon">{feature.icon}</span>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;