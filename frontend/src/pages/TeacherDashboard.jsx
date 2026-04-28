import React, { useState, useEffect } from 'react';
import { teacherService } from '../services/api';

const getPlagiarismLevel = (value) => {
    const percentage = Number(value);

    if (!Number.isFinite(percentage) || percentage <= 0) return 'low';
    if (percentage < 30) return 'low';
    if (percentage <= 70) return 'medium';
    if (percentage < 90) return 'high';
    return 'critical';
};

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
    } catch {
        console.error("Failed to fetch topics");
    }
};

    useEffect(() => {
        let isMounted = true;

        const loadTopics = async () => {
            try {
                const data = await teacherService.getTopicsForTeacher();
                if (isMounted) {
                    setTopics(data);
                }
            } catch {
                console.error("Failed to fetch topics");
            }
        };

        loadTopics();
        return () => {
            isMounted = false;
        };
    }, []);

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
        } catch {
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
        } catch {
            alert("Could not fetch submissions. Check if database column exists.");
        }
    };

    return (
        <div className="max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-black text-slate-800 mb-8">Teacher <span className="text-indigo-700">Management</span> Console</h1>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                
                {/* 1. LEFT COLUMN: ADD TOPIC FORM */}
                <div className="bg-gradient-to-br from-white to-indigo-50 p-6 rounded-2xl shadow-md border border-indigo-100 h-fit">
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <span className="bg-blue-600 text-white p-1 rounded">➕</span> Create New Topic
                    </h2>
                    <form onSubmit={handleAddTopic} className="space-y-4">
                        <input 
                            type="text" placeholder="Topic Title" 
                            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-400" 
                            value={title} onChange={(e) => setTitle(e.target.value)} required
                        />
                        <textarea 
                            placeholder="Brief Description/Instructions" 
                            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl h-24 outline-none focus:ring-2 focus:ring-blue-400" 
                            value={desc} onChange={(e) => setDesc(e.target.value)}
                        />
                        <input 
                            type="text" placeholder="Keywords (comma separated)" 
                            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-400" 
                            value={keywords} onChange={(e) => setKeywords(e.target.value)} required
                        />
                        <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition shadow-lg shadow-blue-100">
                            Publish Topic
                        </button>
                    </form>
                </div>

                {/* 2. MIDDLE COLUMN: MANAGE TOPICS */}
                <div className="lg:col-span-1 space-y-4">
                    <h2 className="text-xl font-bold text-slate-700 mb-2">Existing Topics</h2>
                    <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                        {topics.map(topic => (
                            <div key={topic.topic_id} className="bg-gradient-to-br from-white to-cyan-50 p-5 rounded-xl shadow-sm border border-cyan-100 hover:border-blue-200 transition">
                                <h3 className="font-bold text-lg text-slate-800">{topic.title}</h3>
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
                <div className="bg-gradient-to-b from-white to-sky-50 p-6 rounded-2xl border border-sky-100 shadow-sm">
                    <h2 className="text-xl font-bold mb-4">Student Submissions</h2>
                    {!selectedSubmissions ? (
                        <div className="text-center py-20">
                            <p className="text-slate-400">Select "View Results" to see student grades.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {selectedSubmissions.length === 0 && <p className="text-slate-500 text-center">No one has submitted yet.</p>}
                            {selectedSubmissions.map((sub, i) => (
                                (() => {
                                    const plagiarismPercentage = Number(sub.plagiarism_percentage ?? 0);
                                    const plagiarismLevel = getPlagiarismLevel(plagiarismPercentage);

                                    return (
                                <div
                                    key={i}
                                    className={`bg-white p-4 rounded-xl shadow-sm border-l-4 ${
                                        sub.is_plagiarized ? 'border-red-500' : 'border-green-500'
                                    }`}
                                >
                                    <div className="flex justify-between items-center gap-3">
                                        <span className="font-bold text-slate-800">{sub.student_name || sub.name}</span>
                                        <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full font-black text-sm whitespace-nowrap">
                                            {sub.final_score}/10
                                        </span>
                                    </div>

                                    <div className="mt-2 flex items-center justify-between text-sm">
                                        <span className="text-slate-500">Plagiarism</span>
                                        <span
                                            className={`font-bold ${
                                                sub.is_plagiarized ? 'text-red-600' : 'text-emerald-600'
                                            }`}
                                        >
                                            {plagiarismPercentage.toFixed(2).replace(/\.00$/, '')}% ({plagiarismLevel})
                                        </span>
                                    </div>

                                    {sub.suspected_source && (
                                        <p className="text-xs text-slate-500 mt-2">
                                            Most similar to: <span className="font-semibold">{sub.suspected_source.name}</span>
                                            {' '}({sub.suspected_source.similarity_percentage}%)
                                        </p>
                                    )}

                                    <p className="text-xs text-slate-400 mt-2">
                                        {plagiarismLevel !== 'low' ? 'Flagged for plagiarism review' : 'Completed'}
                                    </p>
                                </div>
                                    );
                                })()
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default TeacherDashboard;