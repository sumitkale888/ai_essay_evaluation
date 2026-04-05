import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { essayService } from '../services/api';

const SubmitEssay = () => {
    const { topicId } = useParams();
    const navigate = useNavigate();
    const [essay, setEssay] = useState('');
    const [loading, setLoading] = useState(false);
    
    const user = JSON.parse(localStorage.getItem('user'));
    const wordCount = essay.trim() ? essay.trim().split(/\s+/).length : 0;

    const handleSubmit = async () => {
        if (wordCount < 10) {
            alert("Essay is too short for AI evaluation!");
            return;
        }

        setLoading(true);
        try {
            const payload = {
                student_id: user.user_id,
                topic_id: parseInt(topicId),
                essay_text: essay
            };
            const result = await essayService.submitEssay(payload);
            // Navigate to result page with the AI data
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
            <textarea
                className="w-full h-80 p-4 border-2 border-blue-100 bg-white rounded-xl focus:border-blue-400 outline-none resize-none text-lg"
                placeholder="Start typing your essay here..."
                value={essay}
                onChange={(e) => setEssay(e.target.value)}
                disabled={loading}
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