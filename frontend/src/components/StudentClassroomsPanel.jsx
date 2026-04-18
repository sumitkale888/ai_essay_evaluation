import React from 'react';
import { Link } from 'react-router-dom';

const StudentClassroomsPanel = ({ classrooms, topics, joinCode, setJoinCode, handleJoinClassroom }) => {
    return (
        <div className="space-y-6">
            <form onSubmit={handleJoinClassroom} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
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

            <h2 className="text-xl font-bold text-emerald-700 uppercase tracking-wider">My Classrooms</h2>
            {classrooms.length === 0 && (
                <div className="rounded-2xl border border-slate-200 bg-white p-6 text-slate-500">
                    No classroom joined yet. Ask teacher for the classroom code.
                </div>
            )}

            <div className="space-y-5">
                {classrooms.map((room) => {
                    const roomTopics = topics.filter((topic) => topic.classroom_id === room.classroom_id);
                    return (
                        <div key={room.classroom_id} className="bg-gradient-to-br from-white to-emerald-50 p-5 rounded-2xl shadow-sm border border-emerald-100">
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
                                            className="block text-center bg-emerald-600 text-white py-2 rounded-lg text-sm font-bold hover:bg-emerald-700"
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
    );
};

export default StudentClassroomsPanel;
