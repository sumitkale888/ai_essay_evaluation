import React, { useState, useEffect } from 'react';
import { teacherService } from '../services/api';
import { useNavigate } from 'react-router-dom';

const ExistingTopics = () => {
    const [topics, setTopics] = useState([]);
    const navigate = useNavigate();

    const fetchTopics = async () => {
        const data = await teacherService.getTopicsForTeacher();
        setTopics(data);
    };

    useEffect(() => { fetchTopics(); }, []);

   const handleDelete = async (topicId) => {
    // Force convert to Number to remove any hidden strings like ":1"
    const cleanId = Number(topicId); 

    if (window.confirm("Delete this topic and all related grades?")) {
        try {
            console.log("Sending Delete Request for ID:", cleanId); 
            await teacherService.deleteTopic(cleanId);
            alert("Topic deleted successfully");
            fetchTopics(); 
        } catch (err) {
            console.error("Delete failed. Check if route exists in main.py", err);
            alert("Delete failed. Ensure backend has /delete-topic route.");
        }
    }
};

    return (
        <div className="max-w-5xl mx-auto">
            <h1 className="text-3xl font-black mb-8 text-gray-800">Your Assignments</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {topics.map(topic => (
                    <div key={topic.topic_id} className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex flex-col justify-between">
                        <div>
                            <h3 className="font-black text-xl text-gray-800 mb-2">{topic.title}</h3>
                            <p className="text-sm text-gray-500 line-clamp-2 mb-4">{topic.description}</p>
                            <div className="flex flex-wrap gap-2 mb-6">
                                {topic.keywords.split(',').map((kw, i) => (
                                    <span key={i} className="bg-blue-50 text-blue-600 px-2 py-1 rounded text-xs font-bold">#{kw.trim()}</span>
                                ))}
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <button 
                                onClick={() => navigate(`/teacher/submissions/${topic.topic_id}`)}
                                className="flex-1 bg-gray-800 text-white py-3 rounded-xl font-bold hover:bg-black transition"
                            >
                                View Submissions
                            </button>
                            <button onClick={() => handleDelete(topic.topic_id)} className="bg-red-50 text-red-500 p-3 rounded-xl hover:bg-red-100">
                                🗑️
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ExistingTopics;