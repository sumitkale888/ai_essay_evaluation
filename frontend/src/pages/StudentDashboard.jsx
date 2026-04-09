import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { essayService } from '../services/api';

const StudentDashboard = () => {
    const [classrooms, setClassrooms] = useState([]);
    const [topics, setTopics] = useState([]);
    const [history, setHistory] = useState([]);
    const [joinCode, setJoinCode] = useState('');
    const user = JSON.parse(localStorage.getItem('user'));

    useEffect(() => {
        const fetchData = async () => {
            try {
                const cleanId = parseInt(user.user_id, 10);
                const [joinedClassrooms, availableTopics, studentHistory] = await Promise.all([
                    essayService.getStudentClassrooms(cleanId),
                    essayService.getTopicsForStudent(cleanId),
                    essayService.getStudentHistory(cleanId),
                ]);

                setClassrooms(joinedClassrooms);
                setTopics(availableTopics);
                setHistory(studentHistory);
            } catch (err) {
                console.error('Error fetching dashboard data:', err);
            }
        };

        fetchData();
    }, [user.user_id]);

    const handleJoinClassroom = async (e) => {
        e.preventDefault();
        try {
            await essayService.joinClassroom({
                student_id: user.user_id,
                join_code: joinCode,
            });
            const cleanId = parseInt(user.user_id, 10);
            const [joinedClassrooms, availableTopics] = await Promise.all([
                essayService.getStudentClassrooms(cleanId),
                essayService.getTopicsForStudent(cleanId),
            ]);
            setClassrooms(joinedClassrooms);
            setTopics(availableTopics);
            setJoinCode('');
            alert('Joined classroom successfully');
        } catch (err) {
            alert(err.response?.data?.detail || 'Could not join classroom');
        }
    };

    return (
        <div className="max-w-7xl mx-auto p-6">
            <h1 className="text-3xl font-black mb-8 text-slate-800">
                Welcome, <span className="text-blue-700">{user?.name}</span> 👋
            </h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
                {/* LEFT: Available Topics */}
                <div className="lg:col-span-2">
                    <form onSubmit={handleJoinClassroom} className="bg-white border border-slate-200 rounded-2xl p-5 mb-6 shadow-sm">
                        <h2 className="text-lg font-bold text-slate-700 mb-3">Join Classroom with Code</h2>
                        <div className="flex flex-col sm:flex-row gap-3">
                            <input
                                value={joinCode}
                                onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                                className="flex-1 p-3 rounded-xl border border-slate-200"
                                placeholder="Enter classroom code"
                                required
                            />
                            <button className="bg-emerald-600 text-white px-5 py-3 rounded-xl font-bold hover:bg-emerald-700">
                                Join
                            </button>
                        </div>
                    </form>

                    <h2 className="text-xl font-bold mb-4 text-blue-700 uppercase tracking-wider">My Classrooms</h2>
                    {classrooms.length === 0 && (
                        <div className="rounded-2xl border border-slate-200 bg-white p-6 text-slate-500">
                            No classroom joined yet. Ask teacher for the classroom code.
                        </div>
                    )}
                    <div className="space-y-5">
                        {classrooms.map((room) => {
                            const roomTopics = topics.filter((topic) => topic.classroom_id === room.classroom_id);
                            return (
                                <div key={room.classroom_id} className="bg-gradient-to-br from-white to-blue-50 p-5 rounded-2xl shadow-sm border border-blue-100">
                                    <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                                        <div>
                                            <h3 className="text-lg font-bold text-slate-800">{room.classroom_name}</h3>
                                            <p className="text-sm text-slate-600">{room.subject_name} · Teacher: {room.teacher_name || 'N/A'}</p>
                                        </div>
                                        <span className="bg-slate-100 text-slate-700 px-3 py-1 rounded-lg text-xs font-bold">
                                            Code: {room.join_code}
                                        </span>
                                    </div>

                                    {roomTopics.length === 0 && <p className="text-sm text-slate-500">No essay assignments yet.</p>}
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {roomTopics.map((topic) => (
                                            <div key={topic.topic_id} className="bg-white p-4 rounded-xl border border-slate-200">
                                                <h4 className="font-bold text-slate-800 mb-1">{topic.title}</h4>
                                                <p className="text-xs text-slate-500 mb-3 line-clamp-2">{topic.description}</p>
                                                <Link
                                                    to={`/submit/${topic.topic_id}`}
                                                    className="block text-center bg-blue-600 text-white py-2 rounded-lg text-sm font-bold hover:bg-blue-700"
                                                >
                                                    Write Essay
                                                </Link>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* RIGHT: Performance History */}
                <div className="bg-gradient-to-b from-white to-cyan-50/70 p-6 rounded-3xl border border-cyan-100 shadow-sm">
                    <h2 className="text-xl font-bold mb-6 text-slate-700">Your Performance</h2>
                    <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
                        {history.length === 0 && <p className="text-slate-400 text-center py-10">No essays completed yet.</p>}
                        {history.map((item, i) => (
                            <div key={i} className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 border-l-4 border-l-blue-500">
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold text-slate-800 text-sm w-3/4">{item.title}</h4>
                                    <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-lg text-xs font-black">
                                        {Number(item.final_score) > 10
                                            ? `${Math.round(Number(item.final_score))}/100`
                                            : `${Number(item.final_score).toFixed(2).replace(/\.00$/, '')}/10`
                                        }
                                    </span>
                                </div>
                                <p className="text-xs text-slate-500 italic line-clamp-2 mb-2">"{item.feedback_text}"</p>
                                <p className="text-[10px] text-slate-400 font-medium uppercase">
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