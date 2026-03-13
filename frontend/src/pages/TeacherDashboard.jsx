import React, { useState, useEffect } from 'react';
import { teacherService, essayService } from '../services/api';

const TeacherDashboard = () => {
    
    const [topics, setTopics] = useState([]);
    const [selectedSubmissions, setSelectedSubmissions] = useState(null);
    
    const [title, setTitle] = useState('');
    const [desc, setDesc] = useState('');
    const [keywords, setKeywords] = useState('');
    
    const user = JSON.parse(localStorage.getItem('user'));

 const refreshTopics = async () => {
    try {
      
        const data = await teacherService.getTopicsForTeacher(); 
        setTopics(data);
    } catch (err) {
        console.error("Failed to fetch topics");
    }
};

    useEffect(() => { refreshTopics(); }, []);

    const handleAddTopic = async (e) => {
        e.preventDefault();
        try {
            await teacherService.addTopic({
                title,
                description: desc,
                keywords,
                teacher_id: user.user_id
            });
            alert("Topic Added Successfully!");
            setTitle(''); setDesc(''); setKeywords('');
            refreshTopics(); 
        } catch (err) {
            alert("Error adding topic.");
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm("Delete this topic and all related grades?")) {
            await teacherService.deleteTopic(id);
            refreshTopics();
        }
    };

    const viewSubmissions = async (id) => {
        try {
            const data = await teacherService.getSubmissions(id);
            setSelectedSubmissions(data);
        } catch (err) {
            alert("Could not fetch submissions. Check if database column exists.");
        }
    };

    return (
        <div className="max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-black text-gray-800 mb-8">Teacher Management Console</h1>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                
                {/* 1. LEFT COLUMN: ADD TOPIC FORM */}
                <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100 h-fit">
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <span className="bg-blue-600 text-white p-1 rounded">➕</span> Create New Topic
                    </h2>
                    <form onSubmit={handleAddTopic} className="space-y-4">
                        <input 
                            type="text" placeholder="Topic Title" 
                            className="w-full p-3 bg-gray-50 border rounded-xl outline-none focus:ring-2 focus:ring-blue-400" 
                            value={title} onChange={(e) => setTitle(e.target.value)} required
                        />
                        <textarea 
                            placeholder="Brief Description/Instructions" 
                            className="w-full p-3 bg-gray-50 border rounded-xl h-24 outline-none focus:ring-2 focus:ring-blue-400" 
                            value={desc} onChange={(e) => setDesc(e.target.value)}
                        />
                        <input 
                            type="text" placeholder="Keywords (comma separated)" 
                            className="w-full p-3 bg-gray-50 border rounded-xl outline-none focus:ring-2 focus:ring-blue-400" 
                            value={keywords} onChange={(e) => setKeywords(e.target.value)} required
                        />
                        <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition shadow-lg shadow-blue-100">
                            Publish Topic
                        </button>
                    </form>
                </div>

                {/* 2. MIDDLE COLUMN: MANAGE TOPICS */}
                <div className="lg:col-span-1 space-y-4">
                    <h2 className="text-xl font-bold text-gray-700 mb-2">Existing Topics</h2>
                    <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                        {topics.map(topic => (
                            <div key={topic.topic_id} className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:border-blue-200 transition">
                                <h3 className="font-bold text-lg text-gray-800">{topic.title}</h3>
                                <p className="text-xs text-blue-500 font-mono mb-3">{topic.keywords}</p>
                                <div className="flex gap-2">
                                    <button onClick={() => viewSubmissions(topic.topic_id)} className="flex-1 bg-blue-50 text-blue-600 py-2 rounded-lg text-sm font-bold hover:bg-blue-100">
                                        View Results
                                    </button>
                                    <button onClick={() => handleDelete(topic.topic_id)} className="bg-red-50 text-red-500 p-2 rounded-lg hover:bg-red-100">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* 3. RIGHT COLUMN: SUBMISSION DETAILS */}
                <div className="bg-gray-50 p-6 rounded-2xl border-2 border-dashed border-gray-200">
                    <h2 className="text-xl font-bold mb-4">Student Submissions</h2>
                    {!selectedSubmissions ? (
                        <div className="text-center py-20">
                            <p className="text-gray-400">Select "View Results" to see student grades.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {selectedSubmissions.length === 0 && <p className="text-gray-500 text-center">No one has submitted yet.</p>}
                            {selectedSubmissions.map((sub, i) => (
                                <div key={i} className="bg-white p-4 rounded-xl shadow-sm border-l-4 border-green-500">
                                    <div className="flex justify-between items-center">
                                        <span className="font-bold text-gray-800">{sub.name}</span>
                                        <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full font-black text-sm">
                                            {sub.final_score}/10
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-400 mt-2">Completed</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default TeacherDashboard;