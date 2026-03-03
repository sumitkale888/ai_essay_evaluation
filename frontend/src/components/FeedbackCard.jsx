import React from 'react';

const FeedbackCard = ({ feedback }) => {
    return (
        <div className="border-l-4 border-blue-500 bg-blue-50 p-5 rounded-r-xl shadow-sm">
            <div className="flex items-start gap-3">
                <span className="text-2xl">🤖</span>
                <div>
                    <h4 className="font-bold text-blue-900">AI Analysis</h4>
                    <p className="text-blue-800 leading-relaxed mt-1">
                        {feedback || "Evaluating your content structure..."}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default FeedbackCard;