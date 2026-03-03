import React from 'react';

const TopicSelector = ({ topic }) => {
    if (!topic) return null;

    return (
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-6 rounded-2xl text-white mb-8 shadow-lg">
            <p className="text-blue-200 text-sm font-bold uppercase tracking-widest mb-1">Selected Topic</p>
            <h1 className="text-3xl font-black mb-2">{topic.title}</h1>
            <p className="text-blue-100 opacity-90">{topic.description}</p>
        </div>
    );
};

export default TopicSelector;