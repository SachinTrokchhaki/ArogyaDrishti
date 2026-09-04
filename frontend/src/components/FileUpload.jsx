import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = ({ onFileUploaded, onAnalysisComplete }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            const validTypes = ['application/pdf', 'image/png', 'image/jpeg'];
            const maxSize = 10 * 1024 * 1024;

            if (!validTypes.includes(selectedFile.type)) {
                setError('Please upload a PDF, PNG, or JPG file');
                return;
            }

            if (selectedFile.size > maxSize) {
                setError('File size must be less than 10MB');
                return;
            }

            setFile(selectedFile);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select a file first');
            return;
        }

        // Notify parent that file is being processed (show pipeline)
        if (onFileUploaded) {
            onFileUploaded(file);
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            
            // Pass the REAL data from backend to parent
            if (onAnalysisComplete) {
                onAnalysisComplete(response.data);
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Upload failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="file-upload-container">
            <div className="upload-area">
                <div className="upload-dropzone">
                    <input
                        type="file"
                        id="fileInput"
                        onChange={handleFileChange}
                        accept=".pdf,.png,.jpg,.jpeg"
                        className="file-input"
                    />
                    <label htmlFor="fileInput" className="file-label">
                        <span className="upload-icon">📄</span>
                        <span className="upload-text">
                            {file ? file.name : 'Click to select or drag & drop a medical report'}
                        </span>
                        {file && (
                            <span className="file-size">
                                ({(file.size / 1024).toFixed(1)} KB)
                            </span>
                        )}
                    </label>
                </div>

                <button 
                    onClick={handleUpload} 
                    disabled={!file || loading}
                    className="upload-btn"
                >
                    {loading ? '⏳ Processing...' : '🔬 Analyze Report'}
                </button>

                {error && (
                    <div className="error-message">
                        ❌ {error}
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;