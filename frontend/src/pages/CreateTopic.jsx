import React, { useState } from 'react';
import { teacherService } from '../services/api';
import { useNavigate } from 'react-router-dom';

const CreateTopic = () => {
    const [title, setTitle] = useState('');
    const [desc, setDesc] = useState('');
    const [keywords, setKeywords] = useState('');
    const user = JSON.parse(localStorage.getItem('user'));
    const navigate = useNavigate();

    const handleAddTopic = async (e) => {
        e.preventDefault();
        try {
            await teacherService.addTopic({
                title,
                description: desc,
                keywords,
                teacher_id: user.user_id
            });
            alert("Topic Published!");
            navigate('/teacher/topics'); 
        } catch {
            alert("Error adding topic.");
        }
    };

    return (
        <div className="max-w-2xl mx-auto mt-10">
            <div className="bg-gradient-to-br from-white to-indigo-50 p-8 rounded-3xl shadow-xl border border-indigo-100">
                <h2 className="text-2xl font-black mb-6 flex items-center gap-2 text-slate-800">
                    <span className="bg-blue-600 text-white p-2 rounded-lg text-lg">➕</span> 
                    Create New Assignment
                </h2>
                <form onSubmit={handleAddTopic} className="space-y-5">
                    <div>
                        <label className="block text-sm font-bold text-slate-600 mb-2">Essay Title</label>
                        <input 
                            type="text" placeholder="e.g. The Future of AI" 
                            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-400" 
                            value={title} onChange={(e) => setTitle(e.target.value)} required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-slate-600 mb-2">Instructions</label>
                        <textarea 
                            placeholder="Describe what students should write about..." 
                            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl h-32 outline-none focus:ring-2 focus:ring-blue-400" 
                            value={desc} onChange={(e) => setDesc(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-bold text-slate-600 mb-2">AI Keywords (Comma Separated)</label>
                        <input 
                            type="text" placeholder="technology, ethics, robotics" 
                            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl outline-none focus:ring-2 focus:ring-blue-400" 
                            value={keywords} onChange={(e) => setKeywords(e.target.value)} required
                        />
                    </div>
                    <button type="submit" className="w-full bg-blue-600 text-white py-4 rounded-2xl font-black hover:bg-blue-700 transition shadow-lg shadow-blue-200">
                        Publish Assignment
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CreateTopic;