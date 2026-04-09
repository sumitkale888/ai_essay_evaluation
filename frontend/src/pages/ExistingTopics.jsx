import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { teacherService } from '../services/api';

const ExistingTopics = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const navigate = useNavigate();

    const [classrooms, setClassrooms] = useState([]);
    const [topics, setTopics] = useState([]);

    const [subjectName, setSubjectName] = useState('');
    const [classroomName, setClassroomName] = useState('');

    const [title, setTitle] = useState('');
    const [desc, setDesc] = useState('');
    const [keywords, setKeywords] = useState('');
    const [selectedClassroomId, setSelectedClassroomId] = useState('');

    const groupedTopics = useMemo(() => {
        return topics.reduce((acc, topic) => {
            const key = topic.classroom_id || 'unassigned';
            if (!acc[key]) acc[key] = [];
            acc[key].push(topic);
            return acc;
        }, {});
    }, [topics]);

    const refreshData = async () => {
        try {
            const [classroomData, topicData] = await Promise.all([
                teacherService.getClassrooms(user.user_id),
                teacherService.getTopicsForTeacher(user.user_id),
            ]);
            setClassrooms(classroomData);
            setTopics(topicData);
            if (!selectedClassroomId && classroomData.length > 0) {
                setSelectedClassroomId(String(classroomData[0].classroom_id));
            }
        } catch (err) {
            console.error('Failed to load teacher dashboard data', err);
        }
    };

    useEffect(() => {
        let isMounted = true;

        Promise.all([
            teacherService.getClassrooms(user.user_id),
            teacherService.getTopicsForTeacher(user.user_id),
        ])
            .then(([classroomData, topicData]) => {
                if (!isMounted) return;
                setClassrooms(classroomData);
                setTopics(topicData);
                if (classroomData.length > 0) {
                    setSelectedClassroomId((prev) => prev || String(classroomData[0].classroom_id));
                }
            })
            .catch((err) => {
                console.error('Failed to load teacher dashboard data', err);
            });

        return () => {
            isMounted = false;
        };
    }, [user.user_id]);

    const handleCreateClassroom = async (e) => {
        e.preventDefault();
        try {
            await teacherService.createClassroom({
                teacher_id: user.user_id,
                subject_name: subjectName,
                classroom_name: classroomName,
            });
            setSubjectName('');
            setClassroomName('');
            await refreshData();
            alert('Classroom created! Share the code with students.');
        } catch (err) {
            alert(err.response?.data?.detail || 'Could not create classroom');
        }
    };

    const handleCreateTopic = async (e) => {
        e.preventDefault();
        if (!selectedClassroomId) {
            alert('Create a classroom first.');
            return;
        }

        try {
            await teacherService.addTopic({
                title,
                description: desc,
                keywords,
                teacher_id: user.user_id,
                classroom_id: Number(selectedClassroomId),
            });
            setTitle('');
            setDesc('');
            setKeywords('');
            await refreshData();
            alert('Assignment created for classroom.');
        } catch (err) {
            alert(err.response?.data?.detail || 'Could not add topic');
        }
    };

    const handleDelete = async (topicId) => {
        if (!window.confirm('Delete this topic and all related grades?')) return;
        try {
            await teacherService.deleteTopic(Number(topicId));
            await refreshData();
        } catch (err) {
            alert(err.response?.data?.detail || 'Delete failed');
        }
    };

    const handleDeleteClassroom = async (classroomId) => {
        if (!window.confirm('Are you sure? This will delete the classroom, all assignments, and submissions.')) return;
        try {
            await teacherService.deleteClassroom(Number(classroomId), user.user_id);
            await refreshData();
        } catch (err) {
            alert(err.response?.data?.detail || 'Could not delete classroom');
        }
    };

    const getWhatsAppLink = (room) => {
        const message = `Join my classroom "${room.classroom_name}" (${room.subject_name}). Code: ${room.join_code}`;
        return `https://wa.me/?text=${encodeURIComponent(message)}`;
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <h1 className="text-3xl font-black text-slate-800">Teacher Classroom Dashboard</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <form onSubmit={handleCreateClassroom} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
                    <h2 className="text-lg font-bold text-slate-700">Create Classroom</h2>
                    <input
                        className="w-full p-3 rounded-xl border border-slate-200"
                        placeholder="Subject (e.g. English Literature)"
                        value={subjectName}
                        onChange={(e) => setSubjectName(e.target.value)}
                        required
                    />
                    <input
                        className="w-full p-3 rounded-xl border border-slate-200"
                        placeholder="Classroom name (e.g. Grade 10 - A)"
                        value={classroomName}
                        onChange={(e) => setClassroomName(e.target.value)}
                    />
                    <button className="w-full bg-indigo-600 text-white py-3 rounded-xl font-bold hover:bg-indigo-700">
                        Create Classroom
                    </button>
                </form>

                <form onSubmit={handleCreateTopic} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
                    <h2 className="text-lg font-bold text-slate-700">Create Essay Assignment</h2>
                    <select
                        className="w-full p-3 rounded-xl border border-slate-200"
                        value={selectedClassroomId}
                        onChange={(e) => setSelectedClassroomId(e.target.value)}
                        required
                    >
                        <option value="">Select classroom</option>
                        {classrooms.map((room) => (
                            <option key={room.classroom_id} value={room.classroom_id}>
                                {room.classroom_name} - {room.subject_name}
                            </option>
                        ))}
                    </select>
                    <input
                        className="w-full p-3 rounded-xl border border-slate-200"
                        placeholder="Assignment title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                    />
                    <textarea
                        className="w-full p-3 rounded-xl border border-slate-200 h-24"
                        placeholder="Instructions"
                        value={desc}
                        onChange={(e) => setDesc(e.target.value)}
                    />
                    <input
                        className="w-full p-3 rounded-xl border border-slate-200"
                        placeholder="Keywords (comma separated)"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        required
                    />
                    <button className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700">
                        Publish Assignment
                    </button>
                </form>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                <h2 className="text-lg font-bold text-slate-700 mb-4">Your Classrooms</h2>
                {classrooms.length === 0 && <p className="text-slate-500">No classrooms yet.</p>}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {classrooms.map((room) => (
                        <div key={room.classroom_id} className="rounded-xl border border-slate-200 p-4 bg-slate-50">
                            <p className="font-bold text-slate-800">{room.classroom_name}</p>
                            <p className="text-sm text-slate-600">{room.subject_name}</p>
                            <p className="text-xs text-slate-500 mt-1">Students: {room.student_count}</p>
                            <div className="mt-3 flex items-center gap-2">
                                <span className="px-3 py-1 rounded-lg bg-indigo-100 text-indigo-700 font-black text-sm">
                                    Code: {room.join_code}
                                </span>
                                <a
                                    href={getWhatsAppLink(room)}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="px-3 py-1 rounded-lg bg-emerald-100 text-emerald-700 text-sm font-bold"
                                >
                                    Share on WhatsApp
                                </a>
                                <button
                                    onClick={() => handleDeleteClassroom(room.classroom_id)}
                                    className="px-3 py-1 rounded-lg bg-red-100 text-red-700 text-sm font-bold"
                                >
                                    Delete Classroom
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
                <h2 className="text-lg font-bold text-slate-700 mb-4">Assignments</h2>
                {topics.length === 0 && <p className="text-slate-500">No assignments published yet.</p>}
                <div className="space-y-6">
                    {Object.entries(groupedTopics).map(([classroomId, roomTopics]) => {
                        const room = classrooms.find((r) => String(r.classroom_id) === String(classroomId));
                        return (
                            <div key={classroomId} className="border border-slate-200 rounded-xl p-4">
                                <h3 className="font-bold text-slate-800 mb-3">
                                    {room ? `${room.classroom_name} (${room.subject_name})` : 'Unassigned'}
                                </h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {roomTopics.map((topic) => (
                                        <div key={topic.topic_id} className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                                            <p className="font-semibold text-slate-800">{topic.title}</p>
                                            <p className="text-xs text-slate-600 mt-1">{topic.description}</p>
                                            <div className="mt-3 flex gap-2">
                                                <button
                                                    onClick={() => navigate(`/teacher/submissions/${topic.topic_id}`)}
                                                    className="flex-1 bg-indigo-600 text-white py-2 rounded-lg text-sm font-bold"
                                                >
                                                    View Submissions
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(topic.topic_id)}
                                                    className="bg-red-50 text-red-600 px-3 rounded-lg text-sm font-bold"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default ExistingTopics;