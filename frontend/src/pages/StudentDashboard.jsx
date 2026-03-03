import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { essayService } from '../services/api';

const StudentDashboard = () => {
    const [topics, setTopics] = useState([]);
    const [history, setHistory] = useState([]);
    const user = JSON.parse(localStorage.getItem('user'));

    useEffect(() => {
        const fetchData = async () => {
            try {
                const availableTopics = await essayService.getTopicsForStudent();
                const studentHistory = await essayService.getStudentHistory(user.user_id);
                setTopics(availableTopics);
                setHistory(studentHistory);
            } catch (err) {
                console.error("Error fetching dashboard data");
            }
        };
        fetchData();
    }, [user.user_id]);

    return (
        <div className="max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-black mb-8 text-gray-800">Welcome, {user?.name} 👋</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                {/* LEFT: Available Topics */}
                <div className="lg:col-span-2">
                    <h2 className="text-xl font-bold mb-6 text-blue-600 uppercase tracking-wider">Available Essay Topics</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {topics.map((topic) => (
                            <div key={topic.topic_id} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-between">
                                <div>
                                    <h3 className="text-xl font-bold text-gray-800 mb-2">{topic.title}</h3>
                                    <p className="text-gray-500 text-sm mb-6 line-clamp-3">{topic.description}</p>
                                </div>
                                <Link 
                                    to={`/submit/${topic.topic_id}`}
                                    className="w-full text-center bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition"
                                >
                                    Write Essay
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>

                {/* RIGHT: Performance History */}
                <div className="bg-gray-50 p-6 rounded-3xl border border-gray-200">
                    <h2 className="text-xl font-bold mb-6 text-gray-700">Your Performance</h2>
                    <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
                        {history.length === 0 && <p className="text-gray-400 text-center py-10">No essays completed yet.</p>}
                        {history.map((item, i) => (
                            <div key={i} className="bg-white p-4 rounded-2xl shadow-sm border-l-4 border-blue-500">
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold text-gray-800 text-sm w-3/4">{item.title}</h4>
                                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-lg text-xs font-black">
                                        {item.final_score}/10
                                    </span>
                                </div>
                                <p className="text-xs text-gray-500 italic line-clamp-2 mb-2">"{item.feedback_text}"</p>
                                <p className="text-[10px] text-gray-400 font-medium uppercase">
                                    {new Date(item.submission_date).toLocaleDateString()}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;