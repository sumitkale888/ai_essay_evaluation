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
        <div className="max-w-5xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-black text-slate-800">Student Results</h1>
                <Link to="/teacher/topics" className="text-blue-600 font-bold hover:underline">← Back to Topics</Link>
            </div>
            
            <div className="bg-white/95 rounded-3xl shadow-xl overflow-hidden border border-blue-100">
                <table className="w-full text-left">
                    <thead className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
                        <tr>
                            <th className="p-5 font-bold text-slate-600">Student Name</th>
                            <th className="p-5 font-bold text-slate-600">Grade</th>
                            <th className="p-5 font-bold text-slate-600">Plagiarism</th>
                            <th className="p-5 font-bold text-slate-600">Possible Source</th>
                            <th className="p-5 font-bold text-slate-600">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {submissions.length === 0 && (
                            <tr><td colSpan="5" className="p-10 text-center text-slate-400">No submissions found for this topic.</td></tr>
                        )}
                        {submissions.map((sub, i) => (
                            <tr key={i} className="border-b last:border-0 hover:bg-blue-50/30 transition">
                                <td className="p-5 font-bold text-slate-800">{sub.student_name || sub.name}</td>
                                <td className="p-5">
                                    <span className="bg-green-100 text-green-700 px-4 py-1 rounded-full font-black">
                                        {Number(sub.final_score) > 10
                                            ? `${Math.round(Number(sub.final_score))}/100`
                                            : `${Number(sub.final_score).toFixed(2).replace(/\.00$/, '')}/10`
                                        }
                                    </span>
                                </td>
                                <td className="p-5">
                                    <span
                                        className={`px-3 py-1 rounded-full text-sm font-bold ${
                                            sub.is_plagiarized
                                                ? 'bg-red-100 text-red-700'
                                                : 'bg-emerald-100 text-emerald-700'
                                        }`}
                                    >
                                        {sub.plagiarism_percentage ?? 0}% ({sub.plagiarism_level || 'low'})
                                    </span>
                                </td>
                                <td className="p-5 text-sm text-slate-700">
                                    {sub.suspected_source
                                        ? `${sub.suspected_source.name} (${sub.suspected_source.similarity_percentage}%)`
                                        : 'N/A'}
                                </td>
                                <td className="p-5">
                                    <span
                                        className={`text-sm font-medium italic ${
                                            sub.is_plagiarized ? 'text-red-600' : 'text-slate-500'
                                        }`}
                                    >
                                        {sub.is_plagiarized ? 'Needs review' : 'Evaluated by AI'}
                                    </span>
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