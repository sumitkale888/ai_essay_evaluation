import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { essayService } from '../services/api';
import StudentClassroomsPanel from '../components/StudentClassroomsPanel';
import StudentPerformancePanel from '../components/StudentPerformancePanel';

const StudentDashboard = () => {
    const [classrooms, setClassrooms] = useState([]);
    const [topics, setTopics] = useState([]);
    const [history, setHistory] = useState([]);
    const [joinCode, setJoinCode] = useState('');
    const [searchParams] = useSearchParams();
    const user = JSON.parse(localStorage.getItem('user'));
    const activeView = searchParams.get('tab') === 'performance' ? 'performance' : 'classrooms';

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
                Welcome, <span className="text-emerald-700">{user?.name}</span> 👋
            </h1>

            {activeView === 'classrooms' ? (
                <StudentClassroomsPanel
                    classrooms={classrooms}
                    topics={topics}
                    joinCode={joinCode}
                    setJoinCode={setJoinCode}
                    handleJoinClassroom={handleJoinClassroom}
                />
            ) : (
                <StudentPerformancePanel history={history} />
            )}
        </div>
    );
};

export default StudentDashboard;