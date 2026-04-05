import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const ResultView = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { result } = location.state || {};
    console.log("Evaluation Result Object:", result);

    const maxScore = 10;
    const rawScore = Number(result?.score ?? 0);
    const safeScore = Number.isFinite(rawScore) ? Math.min(Math.max(rawScore, 0), maxScore) : 0;
    const progress = safeScore / maxScore;
    const radius = 62;
    const strokeWidth = 10;
    const circleSize = 150;
    const circumference = 2 * Math.PI * radius;
    const dashOffset = circumference * (1 - progress);
    const displayScore = Number.isFinite(rawScore)
        ? rawScore.toFixed(2).replace(/\.00$/, '')
        : '0';

    if (!result) return <p className="text-center mt-10">No result found.</p>;

    return (
        <div className="max-w-4xl mx-auto mt-10 p-8 bg-gradient-to-b from-white to-blue-50/60 rounded-3xl shadow-xl border border-blue-100">
            <h2 className="text-3xl font-extrabold text-center text-slate-900 mb-8">AI Evaluation Result</h2>
            
            <div className="flex flex-col items-center mb-10">
                <div className="relative flex items-center justify-center w-[150px] h-[150px]">
                    <svg
                        className="w-[150px] h-[150px] -rotate-90"
                        viewBox={`0 0 ${circleSize} ${circleSize}`}
                        aria-label="Final score indicator"
                    >
                        <circle
                            className="text-blue-100"
                            strokeWidth={strokeWidth}
                            stroke="currentColor"
                            fill="transparent"
                            r={radius}
                            cx={circleSize / 2}
                            cy={circleSize / 2}
                        />
                        <circle
                            className="text-blue-600"
                            strokeWidth={strokeWidth}
                            strokeDasharray={circumference}
                            strokeDashoffset={dashOffset}
                            strokeLinecap="round"
                            stroke="currentColor"
                            fill="transparent"
                            r={radius}
                            cx={circleSize / 2}
                            cy={circleSize / 2}
                            style={{ transition: 'stroke-dashoffset 500ms ease' }}
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center leading-none">
                        <span className="text-5xl font-black text-blue-700 tracking-tight">{displayScore}</span>
                        <span className="mt-1 text-sm font-bold text-blue-500">/10</span>
                    </div>
                </div>
                <p className="mt-4 text-slate-500 font-semibold uppercase tracking-widest">Final Grade</p>
                            {result.base_score && result.base_score !== result.score && (
                                <p className="mt-2 text-sm text-orange-600">
                                    Base Score: {result.base_score}/10 (Plagiarism penalty applied)
                                </p>
                            )}
            </div>

            <div className="space-y-6">
                <div className="bg-blue-50/80 p-6 rounded-2xl border border-blue-200">
                    <h3 className="text-blue-800 font-bold mb-2 flex items-center">
                        <span className="mr-2">📝</span> Content Evaluation
                    </h3>
                    <p className="text-blue-900 leading-relaxed italic">"{result.feedback}"</p>
                                <div className={`p-6 rounded-2xl border-2 ${result.plagiarism_level === 'low' ? 'bg-green-50 border-green-200' : result.plagiarism_level === 'medium' ? 'bg-yellow-50 border-yellow-200' : result.plagiarism_level === 'high' ? 'bg-orange-50 border-orange-200' : 'bg-red-50 border-red-200'}`}>
                                    <h3 className={`${result.plagiarism_level === 'low' ? 'text-green-800' : result.plagiarism_level === 'medium' ? 'text-yellow-800' : result.plagiarism_level === 'high' ? 'text-orange-800' : 'text-red-800'} font-bold mb-3 flex items-center`}>
                                        <span className="mr-2">🔍</span> Plagiarism Detection
                                        <span className="ml-2">{result.is_plagiarized ? '⚠️' : '✓'}</span>
                                    </h3>
                                    <div className="space-y-2">
                                        <div className="flex justify-between items-center">
                                            <span className={result.plagiarism_level === 'low' ? 'text-green-800' : result.plagiarism_level === 'medium' ? 'text-yellow-800' : result.plagiarism_level === 'high' ? 'text-orange-800' : 'text-red-800'}>
                                                Similarity Score:
                                            </span>
                                            <span className={`text-2xl font-bold ${result.plagiarism_level === 'low' ? 'text-green-800' : result.plagiarism_level === 'medium' ? 'text-yellow-800' : result.plagiarism_level === 'high' ? 'text-orange-800' : 'text-red-800'}`}>
                                                {result.plagiarism}%
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className={result.plagiarism_level === 'low' ? 'text-green-800' : result.plagiarism_level === 'medium' ? 'text-yellow-800' : result.plagiarism_level === 'high' ? 'text-orange-800' : 'text-red-800'}>
                                                Level:
                                            </span>
                                            <span className={`px-3 py-1 rounded-full font-semibold capitalize ${result.plagiarism_level === 'low' ? 'bg-green-50' : result.plagiarism_level === 'medium' ? 'bg-yellow-50' : result.plagiarism_level === 'high' ? 'bg-orange-50' : 'bg-red-50'} ${result.plagiarism_level === 'low' ? 'text-green-800' : result.plagiarism_level === 'medium' ? 'text-yellow-800' : result.plagiarism_level === 'high' ? 'text-orange-800' : 'text-red-800'}`}>
                                                {result.plagiarism_level}
                                            </span>
                                        </div>
                                        <p className={`text-sm ${result.plagiarism_level === 'low' ? 'text-green-800' : result.plagiarism_level === 'medium' ? 'text-yellow-800' : result.plagiarism_level === 'high' ? 'text-orange-800' : 'text-red-800'} mt-3 italic`}>
                                            {result.plagiarism_feedback}
                                        </p>
                                        {result.comparison_count > 0 && (
                                            <p className={`text-xs ${result.plagiarism_level === 'low' ? 'text-green-800' : result.plagiarism_level === 'medium' ? 'text-yellow-800' : result.plagiarism_level === 'high' ? 'text-orange-800' : 'text-red-800'} mt-2`}>
                                                Compared against {result.comparison_count} previous submission(s) for this assignment.
                                            </p>
                                        )}
                                    </div>
                                </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-center">
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                        <p className="text-xs text-slate-400 uppercase font-bold">Word Count</p>
                        <p className="text-xl font-bold text-slate-700">{result.word_count}</p>
                    </div>
                    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                        <p className="text-xs text-slate-400 uppercase font-bold">Status</p>
                        <p className="text-xl font-bold text-green-600">Evaluated</p>
                                        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                                            <p className="text-xs text-slate-400 uppercase font-bold">Originality</p>
                                            <p className={`text-xl font-bold ${result.plagiarism < 20 ? 'text-green-600' : 'text-orange-600'}`}>
                                                {Math.round(100 - result.plagiarism)}%
                                            </p>
                                        </div>

                                    {result.is_plagiarized && (
                                        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                                            <p className="text-red-800 font-semibold flex items-center">
                                                <span className="mr-2">⚠️</span>
                                                High Plagiarism Detected
                                            </p>
                                            <p className="text-red-700 text-sm mt-2">
                                                This essay shows significant similarity to previous submissions. Please review and ensure originality.
                                            </p>
                                        </div>
                                    )}
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