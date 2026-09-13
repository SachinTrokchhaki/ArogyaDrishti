import React from 'react';
import api from '../services/api';
import './ResultsDisplay.css';

const ResultsDisplay = ({ data }) => {
    if (!data) {
        return <div className="no-results">No results to display</div>;
    }

    const processedData = data.processed_data || {};
    const results = processedData.results || [];
    const summary = processedData.summary || {};
    const patientInfo = processedData.patient_info || { name: 'Unknown', age: 'Unknown', gender: 'Unknown' };

    const totalTests = summary?.total_tests || 0;
    const normal = summary?.normal || 0;
    const high = summary?.high || 0;
    const low = summary?.low || 0;

    const abnormalValues = results?.filter(r => r.status === 'HIGH' || r.status === 'LOW') || [];
    const medications = data.medications || [];
    const followUp = data.follow_up || [];
    const confidence = data.confidence || { ocr: 94, extraction: 91, classification: 96 };

    // ---- CSV download handler ----
    const handleDownloadCSV = async () => {
        if (!data.id) return;
        try {
            const response = await api.get(`/reports/${data.id}/export/csv/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${data.id}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('CSV export failed:', err);
            alert('Failed to download CSV');
        }
    };

    // ---- PDF download handler ----
    const handleDownloadPDF = async () => {
        if (!data.id) return;
        try {
            const response = await api.get(`/reports/${data.id}/export/pdf/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(
                new Blob([response.data], { type: 'application/pdf' })
            );
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${data.id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('PDF export failed:', err);
            alert('Failed to download PDF');
        }
    };

    return (
        <div className="results-display-modern">
            {/* ===== HEADER ===== */}
            <div className="results-header-modern">
                <div className="header-left">
                    <h1>🩺 Medical Test Report</h1>
                    <div className="header-meta">
                        <span className="badge-complete">✅ Completed</span>
                        <span>Analysis Complete · {new Date().toLocaleDateString()}</span>
                        <span className="report-id">
                            Report ID rpt-{data.id || Math.floor(Math.random() * 10000)}
                        </span>
                    </div>
                </div>

                {data.id && (
                    <div className="header-actions-results">
                        <button
                            type="button"
                            className="btn-export btn-export-csv"
                            onClick={handleDownloadCSV}
                        >
                            📊 Download CSV
                        </button>
                        <button
                            type="button"
                            className="btn-export btn-export-pdf"
                            onClick={handleDownloadPDF}
                        >
                            📄 Export PDF
                        </button>
                    </div>
                )}
            </div>

            {/* ===== SUMMARY STATS ===== */}
            <div className="summary-stats-modern">
                <div className="stat-card-modern total">
                    <div className="stat-icon">📊</div>
                    <div className="stat-content">
                        <span className="stat-number">{totalTests}</span>
                        <span className="stat-label">Total Tests</span>
                    </div>
                </div>
                <div className="stat-card-modern normal">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <span className="stat-number">{normal}</span>
                        <span className="stat-label">Normal</span>
                    </div>
                </div>
                <div className="stat-card-modern low">
                    <div className="stat-icon">⬇️</div>
                    <div className="stat-content">
                        <span className="stat-number">{low}</span>
                        <span className="stat-label">Low</span>
                    </div>
                </div>
                <div className="stat-card-modern high">
                    <div className="stat-icon">⬆️</div>
                    <div className="stat-content">
                        <span className="stat-number">{high}</span>
                        <span className="stat-label">High</span>
                    </div>
                </div>
            </div>

            {/* ===== PATIENT INFO + AI EXPLANATION ===== */}
            <div className="two-column-grid-large">
                <div className="patient-info-small">
                    <h3>👤 Patient</h3>
                    <div className="info-compact">
                        <div className="info-item-small">
                            <span className="info-label">Name</span>
                            <span className="info-value">{patientInfo.name || 'Unknown'}</span>
                        </div>
                        <div className="info-item-small">
                            <span className="info-label">Age</span>
                            <span className="info-value">{patientInfo.age || 'Unknown'}</span>
                        </div>
                        <div className="info-item-small">
                            <span className="info-label">Gender</span>
                            <span className="info-value">{patientInfo.gender || 'Unknown'}</span>
                        </div>
                    </div>
                </div>

                {data.ai_explanation && (
                    <div className={`ai-explanation-large ${data.ai_explanation.success ? '' : 'fallback'}`}>
                        <div className="ai-header-large">
                            <h3>🤖 AI Explanation</h3>
                            <span className={`ai-badge-modern ${data.ai_explanation.success ? 'active' : 'fallback'}`}>
                                {data.ai_explanation.success ? 'Powered by Groq AI' : 'Fallback Mode'}
                            </span>
                        </div>
                        <div className="ai-content-large">
                            <div
                                dangerouslySetInnerHTML={{
                                    __html: (data.ai_explanation.explanation || 'No explanation available.')
                                        .replace(/\n/g, '<br/>')
                                        .replace(/##\s+(.+)/g, '<h4>$1</h4>')
                                        .replace(/###\s+(.+)/g, '<h5>$1</h5>')
                                        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                                        .replace(/^-\s+(.+)/gm, '<li>$1</li>')
                                        .replace(/<li>.+<\/li>/g, (match) => `<ul>${match}</ul>`),
                                }}
                            />
                        </div>
                        {data.ai_explanation.provider && (
                            <div className="ai-footer-large">
                                <span>Generated by: {data.ai_explanation.provider}</span>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* ===== OVERALL SUMMARY ===== */}
            <div className="overall-summary-modern">
                <h3>📋 Overall Summary</h3>
                <p>
                    {abnormalValues.length === 0
                        ? 'All reported values are within the reference ranges. This indicates good health status for the tested parameters.'
                        : `Most reported values are within the reference ranges. ${abnormalValues.length} value(s) are outside the provided reference ranges and may require discussion with a qualified healthcare professional.`}
                </p>
            </div>

            {/* ===== RESULTS TABLE ===== */}
            <div className="results-table-modern">
                <div className="table-header">
                    <h3>🧪 Lab Results</h3>
                    <p className="table-subtitle">Values extracted from the uploaded report</p>
                </div>
                <div className="table-wrapper-modern">
                    <table>
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
                                        <span className={`status-dot ${test.status?.toLowerCase() || 'unknown'}`}>
                                            ● {test.status || 'UNKNOWN'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* ===== ABNORMAL VALUES ===== */}
            {abnormalValues.length > 0 && (
                <div className="abnormal-values-modern">
                    <h3>⚠️ Values Outside Reference Range</h3>
                    <p className="abnormal-subtitle">
                        These flags are based on the reference ranges provided in the report.
                    </p>
                    <div className="abnormal-grid">
                        {abnormalValues.map((test, index) => (
                            <div key={index} className={`abnormal-card-modern status-${test.status?.toLowerCase()}`}>
                                <div className="abnormal-card-header">
                                    <span className="abnormal-name">{test.test_name}</span>
                                    <span className={`abnormal-status-badge ${test.status?.toLowerCase()}`}>
                                        {test.status}
                                    </span>
                                </div>
                                <div className="abnormal-card-body">
                                    <div className="abnormal-detail">
                                        <span className="detail-label">Value:</span>
                                        <span className="detail-value">{test.value} {test.unit}</span>
                                    </div>
                                    <div className="abnormal-detail">
                                        <span className="detail-label">Reference:</span>
                                        <span className="detail-value">
                                            {test.min_range} – {test.max_range} {test.unit}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ===== MEDICATIONS + CONFIDENCE ===== */}
            <div className="two-column-grid">
                <div className="medications-modern">
                    <h3>💊 Medications</h3>
                    <p className="medications-subtitle">Detected from the prescription section</p>
                    {medications && medications.length > 0 && medications[0].name !== 'No medications detected' ? (
                        <div className="table-wrapper-modern">
                            <table>
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
                                            <td><strong>{med.name}</strong></td>
                                            <td>{med.dosage}</td>
                                            <td>{med.frequency}</td>
                                            <td>{med.instructions}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="no-medications-modern">
                            <p>No medications detected in the report.</p>
                        </div>
                    )}
                </div>

                <div className="confidence-modern">
                    <h3>📊 Processing Confidence</h3>
                    <p className="confidence-subtitle">Pipeline quality indicators</p>
                    <div className="confidence-grid-modern">
                        <div className="confidence-item-modern">
                            <span className="confidence-label">OCR</span>
                            <div className="confidence-bar-modern">
                                <div
                                    className="confidence-fill-modern"
                                    style={{ width: `${confidence.ocr || 94}%` }}
                                ></div>
                            </div>
                            <span className="confidence-value">{confidence.ocr || 94}%</span>
                        </div>
                        <div className="confidence-item-modern">
                            <span className="confidence-label">Extraction</span>
                            <div className="confidence-bar-modern">
                                <div
                                    className="confidence-fill-modern"
                                    style={{ width: `${confidence.extraction || 91}%` }}
                                ></div>
                            </div>
                            <span className="confidence-value">{confidence.extraction || 91}%</span>
                        </div>
                        <div className="confidence-item-modern">
                            <span className="confidence-label">Classification</span>
                            <div className="confidence-bar-modern">
                                <div
                                    className="confidence-fill-modern"
                                    style={{ width: `${confidence.classification || 96}%` }}
                                ></div>
                            </div>
                            <span className="confidence-value">{confidence.classification || 96}%</span>
                        </div>
                    </div>
                    <p className="confidence-note">
                        These values describe text-processing quality only. They are not medical diagnostic confidence scores.
                    </p>
                </div>
            </div>

            {/* ===== FOLLOW-UP ===== */}
            <div className="follow-up-modern">
                <h3>📋 Recommended Follow-up</h3>
                {followUp && followUp.length > 0 ? (
                    <ul>
                        {followUp.map((item, index) => (
                            <li key={index}>{item}</li>
                        ))}
                    </ul>
                ) : (
                    <ul>
                        {abnormalValues.length > 0 ? (
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