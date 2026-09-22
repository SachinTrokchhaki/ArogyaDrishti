import React, { useState, useEffect, useRef } from 'react';
import api from '../../services/api';
import './Assistant.css';

const SUGGESTED_QUESTIONS = [
    "What are my abnormal values?",
    "What should I do next?",
    "Should I be worried?",
    "What foods should I eat?",
    "Explain my results in simple terms",
];

export default function Assistant() {
    const [reports, setReports] = useState([]);
    const [selectedReportId, setSelectedReportId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [question, setQuestion] = useState('');
    const [loading, setLoading] = useState(false);
    const [reportsLoading, setReportsLoading] = useState(true);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [error, setError] = useState(null);
    const [rateLimit, setRateLimit] = useState({ used: 0, limit: 30 });

    const messagesEndRef = useRef(null);

    // Load user's reports on mount
    useEffect(() => {
        fetchReports();
    }, []);

    // When report changes, load its chat history
    useEffect(() => {
        if (selectedReportId) {
            fetchChatHistory(selectedReportId);
        } else {
            setMessages([]);
        }
    }, [selectedReportId]);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const fetchReports = async () => {
        try {
            const res = await api.get('/reports/');
            const list = res.data.reports || [];
            setReports(list);
            if (list.length > 0) {
                setSelectedReportId(list[0].id);
            }
        } catch (err) {
            console.error('Reports fetch error:', err);
            setError('Failed to load reports');
        } finally {
            setReportsLoading(false);
        }
    };

    const fetchChatHistory = async (reportId) => {
        setHistoryLoading(true);
        try {
            const res = await api.get(`/reports/${reportId}/chat/`);
            setMessages(res.data.messages || []);
        } catch (err) {
            console.error('Chat history fetch error:', err);
            setMessages([]);
        } finally {
            setHistoryLoading(false);
        }
    };

    const handleSend = async (text) => {
        const q = (text || question).trim();
        if (!q || !selectedReportId || loading) return;

        setError(null);
        setQuestion('');

        // Optimistically add user message
        const tempId = `temp-${Date.now()}`;
        setMessages(prev => [
            ...prev,
            {
                id: tempId,
                question: q,
                answer: null,
                created_at: new Date().toISOString(),
            }
        ]);
        setLoading(true);

        try {
            const res = await api.post(`/reports/${selectedReportId}/ask/`, {
                question: q,
            });

            // Replace temp message with real one
            setMessages(prev => prev.map(m =>
                m.id === tempId ? res.data : m
            ));

            setRateLimit({
                used: res.data.questions_today || 0,
                limit: res.data.daily_limit || 30,
            });
        } catch (err) {
            console.error('Ask error:', err);
            const errMsg = err.response?.data?.error || 'Failed to get answer. Please try again.';
            setError(errMsg);

            // Remove the temp user message on error
            setMessages(prev => prev.filter(m => m.id !== tempId));
        } finally {
            setLoading(false);
        }
    };

    const handleClearChat = async () => {
        if (!selectedReportId) return;
        if (!window.confirm('Clear all chat messages for this report?')) return;

        try {
            await api.delete(`/reports/${selectedReportId}/chat/clear/`);
            setMessages([]);
        } catch (err) {
            console.error('Clear chat error:', err);
            setError('Failed to clear chat');
        }
    };

    const getSelectedReportName = () => {
        const r = reports.find(r => r.id === selectedReportId);
        return r ? r.file_name : 'Select a report';
    };

    if (reportsLoading) {
        return (
            <div className="assistant-page">
                <div className="assistant-loading">Loading your reports...</div>
            </div>
        );
    }

    if (reports.length === 0) {
        return (
            <div className="assistant-page">
                <div className="assistant-empty">
                    <h2>💬 AI Assistant</h2>
                    <p>You need to upload at least one report before using the AI Assistant.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="assistant-page">
            {/* Header */}
            <div className="assistant-header">
                <div>
                    <h1>💬 AI Assistant</h1>
                    <p>Ask questions about any of your reports</p>
                </div>
                <button
                    className="btn-clear-chat"
                    onClick={handleClearChat}
                    disabled={messages.length === 0}
                >
                    🗑️ Clear Chat
                </button>
            </div>

            {/* Report selector */}
            <div className="assistant-report-selector">
                <label>Report:</label>
                <select
                    value={selectedReportId || ''}
                    onChange={(e) => setSelectedReportId(Number(e.target.value))}
                >
                    {reports.map(r => (
                        <option key={r.id} value={r.id}>
                            {r.file_name} ({new Date(r.created_at).toLocaleDateString()})
                        </option>
                    ))}
                </select>
                <span className="assistant-rate-limit">
                    {rateLimit.used}/{rateLimit.limit} today
                </span>
            </div>

            {/* Chat area */}
            <div className="assistant-chat-area">
                {historyLoading ? (
                    <div className="assistant-loading">Loading chat...</div>
                ) : messages.length === 0 ? (
                    <div className="assistant-welcome">
                        <div className="assistant-welcome-icon">🤖</div>
                        <h2>Hi! I'm your AI Assistant</h2>
                        <p>I can answer questions about <strong>{getSelectedReportName()}</strong>.</p>
                        <p className="assistant-welcome-hint">Try one of these questions to get started:</p>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div key={msg.id} className="assistant-message-group">
                            {/* User question */}
                            <div className="assistant-message assistant-message-user">
                                <div className="assistant-bubble assistant-bubble-user">
                                    {msg.question}
                                </div>
                                <div className="assistant-avatar assistant-avatar-user">👤</div>
                            </div>

                            {/* AI answer */}
                            {msg.answer ? (
                                <div className="assistant-message assistant-message-ai">
                                    <div className="assistant-avatar assistant-avatar-ai">🤖</div>
                                    <div className="assistant-bubble assistant-bubble-ai">
                                        <div
                                            dangerouslySetInnerHTML={{
                                                __html: msg.answer
                                                    .replace(/\n/g, '<br/>')
                                                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                                                    .replace(/^-\s+(.+)/gm, '<li>$1</li>')
                                                    .replace(/<li>.+<\/li>/g, (m) => `<ul>${m}</ul>`),
                                            }}
                                        />
                                        {msg.provider && (
                                            <div className="assistant-provider">
                                                via {msg.provider}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                <div className="assistant-message assistant-message-ai">
                                    <div className="assistant-avatar assistant-avatar-ai">🤖</div>
                                    <div className="assistant-bubble assistant-bubble-ai assistant-typing">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Error */}
            {error && (
                <div className="assistant-error">⚠️ {error}</div>
            )}

            {/* Suggested questions */}
            {messages.length === 0 && !historyLoading && (
                <div className="assistant-suggestions">
                    <span className="assistant-suggestions-label">Suggested:</span>
                    <div className="assistant-suggestions-chips">
                        {SUGGESTED_QUESTIONS.map((q, i) => (
                            <button
                                key={i}
                                className="assistant-chip"
                                onClick={() => handleSend(q)}
                                disabled={loading}
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input */}
            <div className="assistant-input-area">
                <input
                    type="text"
                    className="assistant-input"
                    placeholder="Type your question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSend();
                        }
                    }}
                    disabled={loading}
                    maxLength={500}
                />
                <button
                    className="assistant-send-btn"
                    onClick={() => handleSend()}
                    disabled={!question.trim() || loading}
                >
                    {loading ? '...' : 'Send →'}
                </button>
            </div>
        </div>
    );
}