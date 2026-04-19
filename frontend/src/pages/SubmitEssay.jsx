import React, { useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { essayService } from '../services/api';

const SubmitEssay = () => {
    const { topicId } = useParams();
    const navigate = useNavigate();
    const [essay, setEssay] = useState('');
    const [fileName, setFileName] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const fileInputRef = useRef(null);
    
    const user = JSON.parse(localStorage.getItem('user'));
    const hasTypedEssay = essay.trim().length > 0;
    const hasSelectedFile = Boolean(selectedFile);
    const wordCount = essay.trim() ? essay.trim().split(/\s+/).length : 0;

    const handleFileUpload = async (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        if (hasTypedEssay) {
            alert('Clear the typed essay first before uploading a file.');
            event.target.value = '';
            return;
        }

        const allowedTypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
        ];

        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|doc)$/i)) {
            alert('Upload a PDF, DOCX, or DOC file.');
            event.target.value = '';
            return;
        }

        setSelectedFile(file);
        setFileName(file.name);
        setEssay('');
    };

    const handleSubmit = async () => {
        if (!selectedFile && wordCount < 10) {
            alert("Essay is too short for AI evaluation!");
            return;
        }

        setLoading(true);
        try {
            if (selectedFile) {
                const result = await essayService.submitFile(user.user_id, parseInt(topicId), selectedFile);
                navigate('/result', { state: { result } });
                return;
            }

            const payload = {
                student_id: user.user_id,
                topic_id: parseInt(topicId),
                essay_text: essay
            };
            const result = await essayService.submitEssay(payload);
            navigate('/result', { state: { result } });
        } catch {
            alert("Evaluation failed. Check backend connection.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6 bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-lg border border-blue-100">
            <h2 className="text-2xl font-bold text-slate-800 mb-2">Write Your Essay</h2>
            <p className="text-sm text-slate-500 mb-4">Share your response clearly and keep it original.</p>
            <div className="mb-4 rounded-xl border border-dashed border-blue-200 bg-blue-50/60 p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <p className="text-sm font-semibold text-slate-700">Upload a file instead</p>
                        <p className="text-xs text-slate-500">Upload PDF, DOCX, or DOC and submit directly. If you start typing, file upload is locked until you clear the text.</p>
                        {fileName && <p className="mt-1 text-xs font-medium text-emerald-700">Loaded: {fileName}</p>}
                    </div>
                    <div className="flex gap-2">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".pdf,.doc,.docx"
                            onChange={handleFileUpload}
                            className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:text-white file:font-semibold hover:file:bg-blue-700"
                            disabled={loading || hasTypedEssay}
                        />
                    </div>
                </div>
                {selectedFile && <p className="mt-3 text-xs text-blue-600 font-medium">This file will be uploaded directly when you click submit.</p>}
                {hasTypedEssay && !hasSelectedFile && (
                    <p className="mt-3 text-xs text-amber-700 font-medium">Typing mode is active. Clear the text to upload a file instead.</p>
                )}
                {(selectedFile || essay) && (
                    <button
                        type="button"
                        onClick={() => {
                            setEssay('');
                            setFileName('');
                            setSelectedFile(null);
                            if (fileInputRef.current) fileInputRef.current.value = '';
                        }}
                        className="mt-3 text-xs font-semibold text-slate-500 hover:text-slate-700"
                    >
                        Clear file / text
                    </button>
                )}
            </div>
            <textarea
                className="w-full h-80 p-4 border-2 border-blue-100 bg-white rounded-xl focus:border-blue-400 outline-none resize-none text-lg"
                placeholder="Start typing your essay here..."
                value={essay}
                onChange={(e) => setEssay(e.target.value)}
                disabled={loading || hasSelectedFile}
            ></textarea>
            
            <div className="flex justify-between items-center mt-4">
                <span className="text-slate-500 font-medium">Word Count: {wordCount}</span>
                <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className={`px-8 py-3 rounded-lg font-bold text-white transition ${
                        loading ? 'bg-slate-400' : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-sm'
                    }`}
                >
                    {loading ? 'AI is Evaluating...' : 'Submit for AI Grading'}
                </button>
            </div>
        </div>
    );
};

export default SubmitEssay;