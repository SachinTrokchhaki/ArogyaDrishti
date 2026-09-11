// import React, { useState } from 'react';
// import axios from 'axios';

// const FileUpload = ({ onFileUploaded, onAnalysisComplete }) => {
//     const [file, setFile] = useState(null);
//     const [loading, setLoading] = useState(false);
//     const [error, setError] = useState(null);

//     const handleFileChange = (e) => {
//         const selectedFile = e.target.files[0];
//         if (selectedFile) {
//             const validTypes = ['application/pdf', 'image/png', 'image/jpeg'];
//             const maxSize = 10 * 1024 * 1024;

//             if (!validTypes.includes(selectedFile.type)) {
//                 setError('Please upload a PDF, PNG, or JPG file');
//                 return;
//             }

//             if (selectedFile.size > maxSize) {
//                 setError('File size must be less than 10MB');
//                 return;
//             }

//             setFile(selectedFile);
//             setError(null);
//         }
//     };

//     const handleUpload = async () => {
//         if (!file) {
//             setError('Please select a file first');
//             return;
//         }

//         // Notify parent that file is being processed (show pipeline)
//         if (onFileUploaded) {
//             onFileUploaded(file);
//         }

//         setLoading(true);
//         setError(null);

//         const formData = new FormData();
//         formData.append('file', file);

//         try {
//             const response = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
//                 headers: {
//                     'Content-Type': 'multipart/form-data',
//                 },
//             });
            
//             // Pass the REAL data from backend to parent
//             if (onAnalysisComplete) {
//                 onAnalysisComplete(response.data);
//             }
//         } catch (err) {
//             setError(err.response?.data?.error || 'Upload failed. Please try again.');
//         } finally {
//             setLoading(false);
//         }
//     };

//     return (
//         <div className="file-upload-container">
//             <div className="upload-area">
//                 <div className="upload-dropzone">
//                     <input
//                         type="file"
//                         id="fileInput"
//                         onChange={handleFileChange}
//                         accept=".pdf,.png,.jpg,.jpeg"
//                         className="file-input"
//                     />
//                     <label htmlFor="fileInput" className="file-label">
//                         <span className="upload-icon">📄</span>
//                         <span className="upload-text">
//                             {file ? file.name : 'Click to select or drag & drop a medical report'}
//                         </span>
//                         {file && (
//                             <span className="file-size">
//                                 ({(file.size / 1024).toFixed(1)} KB)
//                             </span>
//                         )}
//                     </label>
//                 </div>

//                 <button 
//                     onClick={handleUpload} 
//                     disabled={!file || loading}
//                     className="upload-btn"
//                 >
//                     {loading ? '⏳ Processing...' : '🔬 Analyze Report'}
//                 </button>

//                 {error && (
//                     <div className="error-message">
//                         ❌ {error}
//                     </div>
//                 )}
//             </div>
//         </div>
//     );
// };

// export default FileUpload;

import React, { useState } from 'react';
import api from '../services/api';

const FileUpload = ({ onFileUploaded, onAnalysisComplete }) => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dragging, setDragging] = useState(false);

    const validateFile = (selectedFile) => {
        const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
        const maxSize = 10 * 1024 * 1024;

        if (!validTypes.includes(selectedFile.type)) {
            setError('Please upload a PDF, PNG, or JPG file');
            return false;
        }
        if (selectedFile.size > maxSize) {
            setError('File size must be less than 10MB');
            return false;
        }
        return true;
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && validateFile(selectedFile)) {
            setFile(selectedFile);
            setError(null);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        const droppedFile = e.dataTransfer.files?.[0];
        if (droppedFile && validateFile(droppedFile)) {
            setFile(droppedFile);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select a file first');
            return;
        }

        if (onFileUploaded) {
            onFileUploaded(file);
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/upload/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });

            if (onAnalysisComplete) {
                onAnalysisComplete(response.data);
            }
        } catch (err) {
            if (err.response?.status === 401) {
                setError('Please login to upload reports.');
            } else {
                setError(err.response?.data?.error || 'Upload failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="file-upload-container">
            <div className="upload-area">
                <div 
                    className={`upload-dropzone ${dragging ? 'dragging' : ''}`}
                    onDrop={handleDrop}
                    onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                    onDragLeave={() => setDragging(false)}
                >
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