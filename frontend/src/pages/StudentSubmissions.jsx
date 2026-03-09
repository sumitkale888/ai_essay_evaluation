import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { teacherService } from '../services/api';

const StudentSubmissions = () => {
    const { topicId } = useParams();
    const [submissions, setSubmissions] = useState([]);

    useEffect(() => {
        const fetchSubmissions = async () => {
            const data = await teacherService.getSubmissions(topicId);
            setSubmissions(data);
        };
        fetchSubmissions();
    }, [topicId]);

    return (
        <div className="max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-black text-gray-800">Student Results</h1>
                <Link to="/teacher/topics" className="text-blue-600 font-bold hover:underline">← Back to Topics</Link>
            </div>
            
            <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b">
                        <tr>
                            <th className="p-5 font-bold text-gray-600">Student Name</th>
                            <th className="p-5 font-bold text-gray-600">Grade</th>
                            <th className="p-5 font-bold text-gray-600">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {submissions.length === 0 && (
                            <tr><td colSpan="3" className="p-10 text-center text-gray-400">No submissions found for this topic.</td></tr>
                        )}
                        {submissions.map((sub, i) => (
                            <tr key={i} className="border-b last:border-0 hover:bg-blue-50/30 transition">
                                <td className="p-5 font-bold text-gray-800">{sub.name}</td>
                                <td className="p-5">
                                    <span className="bg-green-100 text-green-700 px-4 py-1 rounded-full font-black">
                                        {sub.final_score}/10
                                    </span>
                                </td>
                                <td className="p-5">
                                    <span className="text-sm text-gray-400 font-medium italic">Evaluated by AI</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StudentSubmissions;