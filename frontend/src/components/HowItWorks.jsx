import React from 'react';

const steps = [
  {
    number: 1,
    title: 'Upload Report',
    description: 'Add a PDF or image of your medical report.',
    icon: '📤'
  },
  {
    number: 2,
    title: 'Extract Information',
    description: 'Text and structured fields are pulled from the file.',
    icon: '📝'
  },
  {
    number: 3,
    title: 'Validate Results',
    description: "Values are checked against the report's reference ranges.",
    icon: '✅'
  },
  {
    number: 4,
    title: 'Get Simple Explanation',
    description: 'Read a patient-friendly summary of the findings.',
    icon: '💬'
  }
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="how-it-works">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">How ArogyaDrishti Works</h2>
          <p className="section-subtitle">
            Four clear steps between uploading a document and understanding it.
          </p>
        </div>
        <div className="steps-container">
          {steps.map((step, index) => (
            <div key={index} className="step-wrapper">
              <div className="step-card">
                <div className="step-number">{step.number}</div>
                <span className="step-icon">{step.icon}</span>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-description">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="step-connector">→</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;