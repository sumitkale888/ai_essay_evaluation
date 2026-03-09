import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const ResultView = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { result } = location.state || {};
    console.log("Evaluation Result Object:", result);

    if (!result) return <p className="text-center mt-10">No result found.</p>;

    return (
        <div className="max-w-2xl mx-auto mt-10 p-8 bg-white rounded-3xl shadow-xl border border-gray-50">
            <h2 className="text-3xl font-extrabold text-center text-gray-900 mb-8">AI Evaluation Result</h2>
            
            <div className="flex flex-col items-center mb-10">
                <div className="relative flex items-center justify-center">
                    <svg className="w-32 h-32">
                        <circle className="text-gray-200" strokeWidth="8" stroke="currentColor" fill="transparent" r="58" cx="64" cy="64"/>
                        <circle className="text-blue-600" strokeWidth="8" strokeDasharray={364} strokeDashoffset={364 - (364 * result.score) / 10} strokeLinecap="round" stroke="currentColor" fill="transparent" r="58" cx="64" cy="64"/>
                    </svg>
                    <span className="absolute text-4xl font-black text-blue-700">{result.score}/10</span>
                </div>
                <p className="mt-4 text-gray-500 font-semibold uppercase tracking-widest">Final Grade</p>
            </div>

            <div className="space-y-6">
                <div className="bg-blue-50 p-6 rounded-2xl">
                    <h3 className="text-blue-800 font-bold mb-2 flex items-center">
                        <span className="mr-2">📝</span> AI Feedback
                    </h3>
                    <p className="text-blue-900 leading-relaxed italic">"{result.feedback}"</p>
                </div>

                <div className="grid grid-cols-2 gap-4 text-center">
                    <div className="p-4 bg-gray-50 rounded-xl">
                        <p className="text-xs text-gray-400 uppercase font-bold">Word Count</p>
                        <p className="text-xl font-bold text-gray-700">{result.word_count}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-xl">
                        <p className="text-xs text-gray-400 uppercase font-bold">Status</p>
                        <p className="text-xl font-bold text-green-600">Evaluated</p>
                    </div>
                </div>
            </div>

            <button 
                onClick={() => navigate('/student-dashboard')}
                className="w-full mt-10 bg-gray-900 text-white py-4 rounded-2xl font-bold hover:bg-black transition"
            >
                Back to Dashboard
            </button>
        </div>
    );
};

export default ResultView;