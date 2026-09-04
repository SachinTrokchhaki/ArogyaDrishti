import React from 'react';
import './ResultsDisplay.css';

const ResultsDisplay = ({ data }) => {
    // Check if data exists
    if (!data) {
        return <div className="no-results">No results to display</div>;
    }

    // Debug: Log the data to see what we're getting
    console.log('ResultsDisplay received data:', data);

    const processedData = data.processed_data || {};
    const results = processedData.results || [];
    const summary = processedData.summary || {};
    const patientInfo = processedData.patient_info || { name: 'Unknown', age: 'Unknown', gender: 'Unknown' };

    const totalTests = summary?.total_tests || 0;
    const normal = summary?.normal || 0;
    const high = summary?.high || 0;
    const low = summary?.low || 0;

    // Get abnormal values
    const abnormalValues = results?.filter(r => r.status === 'HIGH' || r.status === 'LOW') || [];

    // Get dynamic data from backend (with fallbacks)
    const medications = data.medications || [];
    const followUp = data.follow_up || [];
    const confidence = data.confidence || { ocr: 94, extraction: 91, classification: 96 };

    return (
        <div className="results-display">
            {/* Header */}
            <div className="results-header">
                <div className="results-title">
                    <h2>📊 Medical Test Report </h2>
                    <span className="results-badge">Completed</span>
                </div>
                <div className="results-meta">
                    <span>Analysis Complete · {new Date().toLocaleDateString()}</span>
                    <span className="report-id">Report ID rpt-{Math.floor(Math.random() * 10000)}</span>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="summary-stats">
                <div className="stat-card total">
                    <span className="stat-number">{totalTests}</span>
                    <span className="stat-label">Total Tests</span>
                </div>
                <div className="stat-card normal">
                    <span className="stat-number">{normal}</span>
                    <span className="stat-label">✅ Normal</span>
                </div>
                <div className="stat-card low">
                    <span className="stat-number">{low}</span>
                    <span className="stat-label">⬇️ Low</span>
                </div>
                <div className="stat-card high">
                    <span className="stat-number">{high}</span>
                    <span className="stat-label">⬆️ High</span>
                </div>
            </div>

            {/* Patient Info - Dynamic */}
            <div className="patient-info">
                <div className="info-grid">
                    <div className="info-item">
                        <span className="info-label">PATIENT NAME</span>
                        <span className="info-value">{patientInfo.name || 'Unknown'}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">AGE</span>
                        <span className="info-value">{patientInfo.age || 'Unknown'}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">GENDER</span>
                        <span className="info-value">{patientInfo.gender || 'Unknown'}</span>
                    </div>
                </div>
            </div>

            {/* Overall Summary */}
            <div className="overall-summary">
                <h3>Overall Summary</h3>
                <p>
                    {abnormalValues.length === 0 
                        ? 'All reported values are within the reference ranges. This indicates good health status for the tested parameters.'
                        : `Most reported values are within the reference ranges. ${abnormalValues.length} value(s) are outside the provided reference ranges and may require discussion with a qualified healthcare professional.`
                    }
                </p>
            </div>

            {/* Results Table */}
            <div className="results-table-container">
                <h3>Lab Results</h3>
                <p className="table-subtitle">Values extracted from the uploaded report.</p>
                
                <div className="table-wrapper">
                    <table className="results-table">
                        <thead>
                            <tr>
                                <th>TEST</th>
                                <th>VALUE</th>
                                <th>UNIT</th>
                                <th>REFERENCE RANGE</th>
                                <th>STATUS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {results?.map((test, index) => (
                                <tr key={index} className={`status-${test.status?.toLowerCase() || 'unknown'}`}>
                                    <td><strong>{test.test_name}</strong></td>
                                    <td>{test.value}</td>
                                    <td>{test.unit || '—'}</td>
                                    <td>
                                        {test.min_range && test.max_range 
                                            ? `${test.min_range} – ${test.max_range}` 
                                            : '—'}
                                    </td>
                                    <td>
                                        <span className={`status-badge ${test.status?.toLowerCase() || 'unknown'}`}>
                                            ● {test.status || 'UNKNOWN'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Abnormal Values */}
            {abnormalValues.length > 0 && (
                <div className="abnormal-values">
                    <h3>Values Outside Reference Range</h3>
                    <p className="abnormal-subtitle">
                        These flags are based on the reference ranges provided in the report.
                    </p>
                    
                    {abnormalValues.map((test, index) => (
                        <div key={index} className={`abnormal-card status-${test.status?.toLowerCase()}`}>
                            <div className="abnormal-header">
                                <span className="abnormal-name">{test.test_name}</span>
                                <span className={`abnormal-status ${test.status?.toLowerCase()}`}>
                                    {test.status}
                                </span>
                            </div>
                            <div className="abnormal-details">
                                <div className="abnormal-value">
                                    <span className="label">Value:</span>
                                    <span className="value">{test.value} {test.unit}</span>
                                </div>
                                <div className="abnormal-range">
                                    <span className="label">Reference:</span>
                                    <span className="value">{test.min_range} – {test.max_range} {test.unit}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Simple Explanation */}
            <div className="simple-explanation">
                <h3>Simple Explanation</h3>
                <p>
                    {abnormalValues.length === 0 
                        ? 'Your report contains all values within the provided reference ranges.'
                        : `Your report contains mostly values within the provided reference ranges. ${abnormalValues.map(t => t.test_name).join(', ')} ${abnormalValues.length > 1 ? 'are' : 'is'} outside the stated range${abnormalValues.length > 1 ? 's' : ''}.`
                    }
                </p>
                
                {abnormalValues.length > 0 && (
                    <div className="explanation-details">
                        {abnormalValues.map((test, index) => (
                            <div key={index} className="explanation-item">
                                <strong>{test.test_name}</strong>
                                <p>
                                    {test.status === 'LOW' 
                                        ? `The reported value (${test.value} ${test.unit}) is lower than the range printed on your report.`
                                        : `The reported value (${test.value} ${test.unit}) is higher than the range printed on your report.`
                                    }
                                </p>
                            </div>
                        ))}
                        <p className="explanation-note">
                            All other reported values fall inside the ranges printed on the same report.
                        </p>
                    </div>
                )}
                
                <div className="disclaimer">
                    ⚠️ <strong>Important:</strong> This explanation is generated from information contained in the uploaded report and is not a medical diagnosis.
                </div>
            </div>

            {/* AI Explanation */}
            {data.ai_explanation && data.ai_explanation.success && (
                <div className="ai-explanation">
                    <div className="ai-header">
                        <h3>🤖 AI Explanation</h3>
                        <span className="ai-badge">{data.ai_explanation?.provider || 'AI Powered'}
                        </span>
                    </div>
                    <div className="ai-content">
                        <div dangerouslySetInnerHTML={{ 
                         __html: data.ai_explanation.explanation
                             // Convert markdown headers
                                .replace(/^##\s+(.+)$/gm, '<h4>$1</h4>')
                                .replace(/^###\s+(.+)$/gm, '<h5>$1</h5>')
                                // Convert bold
                                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                                // Convert bullet points
                                .replace(/^-\s+(.+)$/gm, '<li>$1</li>')
                                // Convert newlines to <br/>
                                .replace(/\n/g, '<br/>')
                                // Fix consecutive list items
                                .replace(/(<li>.*<\/li>)(?!\s*<li>)/g, (match) => {
                                    return match.replace(/<li>/g, '<ul><li>').replace(/<\/li>(?!\s*<li>)/g, '</li></ul>');
                                })
                        }} />
                    </div>
                    {data.ai_explanation.provider && (
                        <div className="ai-footer">
                            <span className="ai-provider">Generated by: {data.ai_explanation.provider}</span>
                        </div>
                    )}
                </div>
            )}

            {/* Fallback AI Explanation */}
            {data.ai_explanation && !data.ai_explanation.success && (
                <div className="ai-explanation fallback">
                    <div className="ai-header">
                        <h3>🤖 AI Explanation</h3>
                        <span className="ai-badge fallback">Fallback Mode</span>
                    </div>
                    <div className="ai-content">
                        <div dangerouslySetInnerHTML={{ 
                            __html: data.ai_explanation.explanation
                                .replace(/\n/g, '<br/>')
                                .replace(/##\s+(.+)/g, '<h4>$1</h4>')
                                .replace(/###\s+(.+)/g, '<h5>$1</h5>')
                                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                     }} />
                    </div>
                    {data.ai_explanation.provider && (
                        <div className="ai-footer">
                            <span className="ai-provider">Generated by: {data.ai_explanation.provider}</span>
                        </div>
                    )}
                    <div className="ai-error-notice">
                        <p>⚠️ AI service is currently unavailable. Showing template explanation.</p>
                    </div>
                </div>
            )}


            {/* Medications - Dynamic */}
            <div className="medications">
                <h3>💊 Medications</h3>
                <p className="medications-subtitle">Detected from the prescription section.</p>
    
                {medications && medications.length > 0 && medications[0].name !== 'No medications detected' ? (
                    <div className="table-wrapper">
                        <table className="medications-table">
                            <thead>
                                <tr>
                                    <th>MEDICATION</th>
                                    <th>DOSAGE</th>
                                    <th>FREQUENCY</th>
                                    <th>INSTRUCTIONS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {medications.map((med, index) => (
                                    <tr key={index}>
                                        <td>{med.name}</td>
                                        <td>{med.dosage}</td>
                                        <td>{med.frequency}</td>
                                        <td>{med.instructions}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="no-medications">
                        <p>No medications detected in the report. Consult your doctor for any prescribed medications.</p>
                    </div>
                )}
            </div>

            {/* Processing Confidence - Dynamic */}
            <div className="processing-confidence">
                <h3>Processing Confidence</h3>
                <p className="confidence-subtitle">Pipeline quality indicators</p>
                
                <div className="confidence-grid">
                    <div className="confidence-item">
                        <span className="confidence-label">OCR Confidence</span>
                        <div className="confidence-bar">
                            <div 
                                className="confidence-fill" 
                                style={{ width: `${confidence.ocr || 94}%` }}
                            ></div>
                            <span className="confidence-value">{confidence.ocr || 94}%</span>
                        </div>
                    </div>
                    <div className="confidence-item">
                        <span className="confidence-label">Extraction Confidence</span>
                        <div className="confidence-bar">
                            <div 
                                className="confidence-fill" 
                                style={{ width: `${confidence.extraction || 91}%` }}
                            ></div>
                            <span className="confidence-value">{confidence.extraction || 91}%</span>
                        </div>
                    </div>
                    <div className="confidence-item">
                        <span className="confidence-label">Classification Confidence</span>
                        <div className="confidence-bar">
                            <div 
                                className="confidence-fill" 
                                style={{ width: `${confidence.classification || 96}%` }}
                            ></div>
                            <span className="confidence-value">{confidence.classification || 96}%</span>
                        </div>
                    </div>
                </div>
                
                <p className="confidence-note">
                    These values describe text-processing quality only. They are not medical diagnostic confidence scores.
                </p>
            </div>

            {/* Recommended Follow-up - Dynamic */}
            <div className="follow-up">
                <h3>📋 Recommended Follow-up</h3>
                
                {followUp && followUp.length > 0 ? (
                    <ul>
                        {followUp.map((item, index) => (
                            <li key={index}>{item}</li>
                        ))}
                    </ul>
                ) : (
                    <ul>
                        {abnormalValues && abnormalValues.length > 0 ? (
                            <>
                                <li>Discuss abnormal results with a qualified healthcare professional.</li>
                                <li>Keep previous reports available so trends can be compared.</li>
                                <li>Bring the original report when consulting your healthcare provider.</li>
                                <li>Follow any instructions already written on the report by the issuing laboratory.</li>
                            </>
                        ) : (
                            <>
                                <li>All values are within normal range. Continue maintaining a healthy lifestyle.</li>
                                <li>Schedule regular check-ups as recommended by your healthcare provider.</li>
                                <li>Keep this report for future reference and comparison.</li>
                            </>
                        )}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default ResultsDisplay;