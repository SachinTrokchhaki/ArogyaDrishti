import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import ProcessingPipeline from '../components/ProcessingPipeline';
import ResultsDisplay from './ResultsDisplay';
import './ReportAnalysis.css';

const ReportAnalysis = () => {
    const [showUpload, setShowUpload] = useState(true);
    const [showPipeline, setShowPipeline] = useState(false);
    const [result, setResult] = useState(null);
    const [uploadedFile, setUploadedFile] = useState(null);

    const handleFileUploaded = (file) => {
        setUploadedFile(file);
        setShowUpload(false);
        setShowPipeline(true);
    };

    const handlePipelineComplete = () => {
        setShowPipeline(false);
        // Results are already set by FileUpload via onAnalysisComplete
    };

    const handleAnalysisComplete = (data) => {
        setResult(data);
        setShowUpload(false);
        setShowPipeline(false);
    };

    const handleReset = () => {
        setResult(null);
        setShowUpload(true);
        setShowPipeline(false);
        setUploadedFile(null);
    };

    return (
        <div className="report-analysis-page">
            {/* Header */}
            <header className="analysis-header">
                <div className="container header-inner">
                    <a href="/" className="logo">
                        <span className="logo-mark">♥</span>
                        <span>
                            <span className="logo-name">ArogyaDrishti</span>
                            <br />
                            <span className="logo-sub">REPORT ANALYSIS</span>
                        </span>
                    </a>

                    <div className="header-actions">
                        <button className="btn btn-outline">Get Started</button>
                        <a href="/analyze">
                            <button className="btn btn-primary">Analyze a Report</button>
                        </a>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="analysis-main">
                <div className="analysis-hero">
                    <h1>📊 Medical Report Analysis</h1>
                    <p>Upload your medical report and get instant analysis with AI-powered insights</p>
                </div>

                <div className="analysis-container">
                    {/* Upload Section */}
                    {showUpload && (
                        <FileUpload 
                            onFileUploaded={handleFileUploaded}
                            onAnalysisComplete={handleAnalysisComplete}
                        />
                    )}

                    {/* Processing Pipeline */}
                    {showPipeline && (
                        <ProcessingPipeline onComplete={handlePipelineComplete} />
                    )}

                    {/* Results Section - Shows REAL data from backend */}
                    {result && (
                        <>
                            <ResultsDisplay data={result} />
                            <div className="re-upload-section">
                                <button 
                                    className="btn btn-outline" 
                                    onClick={handleReset}
                                >
                                    📤 Upload Another Report
                                </button>
                            </div>
                        </>
                    )}
                </div>

                {/* Info Cards */}
                {showUpload && !result && (
                    <div className="analysis-info">
                        <div className="info-grid">
                            <div className="info-card">
                                <span className="info-icon">🔒</span>
                                <h3>Secure & Private</h3>
                                <p>Your reports are processed securely and never shared</p>
                            </div>
                            <div className="info-card">
                                <span className="info-icon">⚡</span>
                                <h3>Fast Results</h3>
                                <p>Get structured results in under a minute</p>
                            </div>
                            <div className="info-card">
                                <span className="info-icon">📋</span>
                                <h3>Supported Formats</h3>
                                <p>PDF, PNG, JPG, JPEG - Max 10MB</p>
                            </div>
                            <div className="info-card">
                                <span className="info-icon">🤖</span>
                                <h3>AI-Powered</h3>
                                <p>Advanced AI extracts and explains medical values</p>
                            </div>
                        </div>
                    </div>
                )}

                <div className="analysis-disclaimer">
                    <p>⚠️ <strong>Disclaimer:</strong> This tool provides analysis and explanations for educational purposes only. 
                    Always consult a qualified healthcare professional for medical advice.</p>
                </div>
            </div>

            {/* Footer */}
            <footer className="footer">
                <div className="container footer-inner">
                    <span>© {new Date().getFullYear()} ArogyaDrishti. Report analysis, not diagnosis.</span>
                    <span>Always consult a qualified doctor for medical advice.</span>
                </div>
            </footer>
        </div>
    );
};

export default ReportAnalysis;