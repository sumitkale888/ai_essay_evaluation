import React from 'react';

const PerformanceChart = ({ score }) => {
    const percentage = (score / 10) * 100;
    const strokeDasharray = 251.2; // 2 * PI * r
    const strokeDashoffset = strokeDasharray - (strokeDasharray * percentage) / 100;

    return (
        <div className="flex flex-col items-center justify-center p-6 bg-white rounded-2xl shadow-inner border border-gray-100">
            <div className="relative inline-flex items-center justify-center">
                <svg className="w-32 h-32 transform -rotate-90">
                    <circle
                        className="text-gray-200"
                        strokeWidth="10"
                        stroke="currentColor"
                        fill="transparent"
                        r="40"
                        cx="64"
                        cy="64"
                    />
                    <circle
                        className="text-blue-600 transition-all duration-1000 ease-out"
                        strokeWidth="10"
                        strokeDasharray={strokeDasharray}
                        strokeDashoffset={strokeDashoffset}
                        strokeLinecap="round"
                        stroke="currentColor"
                        fill="transparent"
                        r="40"
                        cx="64"
                        cy="64"
                    />
                </svg>
                <span className="absolute text-2xl font-black text-gray-800">{score}/10</span>
            </div>
            <p className="mt-4 font-bold text-gray-400 text-sm uppercase tracking-tighter">AI Confidence Score</p>
        </div>
    );
};

export default PerformanceChart;