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
        } catch (err) {
            alert("Evaluation failed. Check backend connection.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-6 bg-white rounded-2xl shadow-sm">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Write Your Essay</h2>
            <textarea
                className="w-full h-80 p-4 border-2 border-gray-100 rounded-xl focus:border-blue-400 outline-none resize-none text-lg"
                placeholder="Start typing your essay here..."
                value={essay}
                onChange={(e) => setEssay(e.target.value)}
                disabled={loading}
            ></textarea>
            
            <div className="flex justify-between items-center mt-4">
                <span className="text-gray-500 font-medium">Word Count: {wordCount}</span>
                <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className={`px-8 py-3 rounded-lg font-bold text-white transition ${
                        loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                >
                    {loading ? 'AI is Evaluating...' : 'Submit for AI Grading'}
                </button>
            </div>
        </div>
    );
};

export default SubmitEssay;