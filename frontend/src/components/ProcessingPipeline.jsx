import React, { useState, useEffect } from 'react';
import './ProcessingPipeline.css';

const ProcessingPipeline = ({ onComplete }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [progress, setProgress] = useState(0);
    const [steps, setSteps] = useState([
        { id: 0, label: 'Upload', status: 'completed', icon: '📤' },
        { id: 1, label: 'File Validation', status: 'pending', icon: '✅' },
        { id: 2, label: 'Text Extraction', status: 'pending', icon: '📄' },
        { id: 3, label: 'OCR', status: 'pending', icon: '🔍' },
        { id: 4, label: 'Report Classification', status: 'pending', icon: '🏷️' },
        { id: 5, label: 'Information Extraction', status: 'pending', icon: '📊' },
        { id: 6, label: 'Validation', status: 'pending', icon: '✓' },
        { id: 7, label: 'AI Explanation', status: 'pending', icon: '🤖' },
    ]);

    useEffect(() => {
        const startPipeline = async () => {
            for (let i = 1; i < steps.length; i++) {
                setCurrentStep(i);
                setSteps(prev => prev.map((step, index) => {
                    if (index === i) return { ...step, status: 'processing' };
                    if (index < i) return { ...step, status: 'completed' };
                    return step;
                }));
                setProgress(Math.round((i / (steps.length - 1)) * 100));
                const delay = 800 + Math.random() * 800;
                await new Promise(resolve => setTimeout(resolve, delay));
            }

            setSteps(prev => prev.map(step => ({ ...step, status: 'completed' })));
            setProgress(100);

            setTimeout(() => {
                if (onComplete) onComplete();
            }, 500);
        };

        startPipeline();
    }, []);

    const getStepStatusClass = (status) => {
        switch(status) {
            case 'completed': return 'step-completed';
            case 'processing': return 'step-processing';
            default: return 'step-pending';
        }
    };

    const getStepIcon = (step) => {
        if (step.status === 'completed') return '✓';
        if (step.status === 'processing') return '⏳';
        return step.icon;
    };

    return (
        <div className="pipeline-container">
            <div className="pipeline-header">
                <h3>🔄 Analyzing Your Report</h3>
                <span className="progress-percentage">{progress}% complete</span>
            </div>

            <div className="progress-bar-container">
                <div className="progress-bar" style={{ width: `${progress}%` }}></div>
            </div>

            <div className="pipeline-steps">
                {steps.map((step, index) => (
                    <div 
                        key={step.id} 
                        className={`pipeline-step ${getStepStatusClass(step.status)}`}
                    >
                        <div className="step-indicator">
                            <span className="step-icon">{getStepIcon(step)}</span>
                            {index < steps.length - 1 && (
                                <div className={`step-line ${step.status === 'completed' ? 'line-completed' : ''}`}></div>
                            )}
                        </div>
                        <div className="step-content">
                            <span className="step-label">{step.label}</span>
                            {step.status === 'processing' && (
                                <span className="step-status">Processing...</span>
                            )}
                            {step.status === 'completed' && (
                                <span className="step-status completed">✓ Done</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <div className="pipeline-footer">
                <button 
                    className="btn btn-outline" 
                    onClick={() => window.location.href = '/'}
                >
                    Cancel and return to dashboard
                </button>
            </div>
        </div>
    );
};

export default ProcessingPipeline;