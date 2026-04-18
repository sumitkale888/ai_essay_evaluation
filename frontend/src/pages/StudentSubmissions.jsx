import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { teacherService } from '../services/api';

const StudentSubmissions = () => {
    const { topicId } = useParams();
    const [submissions, setSubmissions] = useState([]);
    const [expandedEssayId, setExpandedEssayId] = useState(null);
    const [reviewDrafts, setReviewDrafts] = useState({});

    const user = JSON.parse(localStorage.getItem('user'));

    const loadSubmissions = useCallback(async () => {
        const data = await teacherService.getSubmissions(topicId);
        setSubmissions(data);
    }, [topicId]);

    useEffect(() => {
        const fetchSubmissions = async () => {
            await loadSubmissions();
        };
        fetchSubmissions();
    }, [loadSubmissions]);

    const getDraft = (sub) => {
        const existing = reviewDrafts[sub.essay_id];
        if (existing) return existing;
        return {
            teacher_score: sub.teacher_score ?? '',
            teacher_feedback: sub.teacher_feedback ?? '',
        };
    };

    const setDraftValue = (essayId, key, value) => {
        setReviewDrafts((prev) => ({
            ...prev,
            [essayId]: {
                ...(prev[essayId] || {}),
                [key]: value,
            },
        }));
    };

    const handleSaveReview = async (sub) => {
        const draft = getDraft(sub);
        try {
            await teacherService.saveSubmissionReview({
                essay_id: sub.essay_id,
                teacher_id: user.user_id,
                teacher_score: draft.teacher_score === '' ? null : Number(draft.teacher_score),
                teacher_feedback: draft.teacher_feedback,
            });
            alert('Teacher review saved');
            await loadSubmissions();
        } catch (err) {
            alert(err.response?.data?.detail || 'Could not save teacher review');
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-black text-slate-800">Student Results</h1>
                <Link to="/teacher/topics" className="text-emerald-600 font-bold hover:underline">← Back to Topics</Link>
            </div>
            
            <div className="bg-white/95 rounded-3xl shadow-xl overflow-hidden border border-emerald-100">
                <table className="w-full text-left">
                    <thead className="bg-gradient-to-r from-emerald-50 to-amber-50 border-b border-emerald-100">
                        <tr>
                            <th className="p-5 font-bold text-slate-600">Student Name</th>
                            <th className="p-5 font-bold text-slate-600">AI Grade</th>
                            <th className="p-5 font-bold text-slate-600">Teacher Grade</th>
                            <th className="p-5 font-bold text-slate-600">Plagiarism</th>
                            <th className="p-5 font-bold text-slate-600">Review</th>
                            <th className="p-5 font-bold text-slate-600">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {submissions.length === 0 && (
                            <tr><td colSpan="6" className="p-10 text-center text-slate-400">No submissions found for this topic.</td></tr>
                        )}
                        {submissions.map((sub, i) => {
                            const draft = getDraft(sub);
                            const isExpanded = expandedEssayId === sub.essay_id;

                            return (
                                <React.Fragment key={sub.essay_id || i}>
                                    <tr className="border-b last:border-0 hover:bg-emerald-50/30 transition align-top">
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
                                            {sub.teacher_score !== null && sub.teacher_score !== undefined ? (
                                                <span className="bg-amber-100 text-amber-700 px-4 py-1 rounded-full font-black">
                                                    {Number(sub.teacher_score).toFixed(1)}/100
                                                </span>
                                            ) : (
                                                <span className="text-xs text-slate-500">Not graded yet</span>
                                            )}
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
                                            <button
                                                type="button"
                                                onClick={() => setExpandedEssayId(isExpanded ? null : sub.essay_id)}
                                                className="px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 font-semibold"
                                            >
                                                {isExpanded ? 'Hide Essay' : 'View Essay & Review'}
                                            </button>
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

                                    {isExpanded && (
                                        <tr className="bg-slate-50 border-b">
                                            <td colSpan="6" className="p-5 space-y-4">
                                                <div className="rounded-xl border border-slate-200 bg-white p-4">
                                                    <p className="text-xs uppercase font-bold text-slate-500 mb-2">Essay Text</p>
                                                    <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{sub.essay_text || 'Essay text not found.'}</p>
                                                </div>

                                                <div className="rounded-xl border border-slate-200 bg-white p-4">
                                                    <p className="text-xs uppercase font-bold text-slate-500 mb-2">AI Feedback</p>
                                                    <p className="text-sm text-slate-700 whitespace-pre-wrap">{sub.ai_feedback || 'No AI feedback available.'}</p>
                                                    <p className="text-xs text-slate-500 mt-2">
                                                        {sub.suspected_source
                                                            ? `Most similar to: ${sub.suspected_source.name} (${sub.suspected_source.similarity_percentage}%)`
                                                            : 'No strong similarity source identified.'}
                                                    </p>
                                                </div>

                                                <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 space-y-3">
                                                    <p className="text-xs uppercase font-bold text-amber-700">Teacher Review</p>
                                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-start">
                                                        <div>
                                                            <label className="text-xs text-slate-600 font-semibold">Teacher Score (0-100)</label>
                                                            <input
                                                                type="number"
                                                                min="0"
                                                                max="100"
                                                                step="0.1"
                                                                value={draft.teacher_score}
                                                                onChange={(e) => setDraftValue(sub.essay_id, 'teacher_score', e.target.value)}
                                                                className="mt-1 w-full p-2 rounded-lg border border-slate-300"
                                                                placeholder="e.g. 88.5"
                                                            />
                                                        </div>

                                                        <div className="md:col-span-2">
                                                            <label className="text-xs text-slate-600 font-semibold">Teacher Feedback</label>
                                                            <textarea
                                                                value={draft.teacher_feedback}
                                                                onChange={(e) => setDraftValue(sub.essay_id, 'teacher_feedback', e.target.value)}
                                                                className="mt-1 w-full p-2 rounded-lg border border-slate-300 min-h-[92px]"
                                                                placeholder="Add manual feedback for the student"
                                                            />
                                                        </div>
                                                    </div>

                                                    <div className="flex items-center justify-between gap-2">
                                                        <p className="text-xs text-slate-500">
                                                            {sub.teacher_reviewed_at
                                                                ? `Last reviewed on ${new Date(sub.teacher_reviewed_at).toLocaleString()}${sub.teacher_name ? ` by ${sub.teacher_name}` : ''}`
                                                                : 'Not reviewed yet'}
                                                        </p>
                                                        <button
                                                            type="button"
                                                            onClick={() => handleSaveReview(sub)}
                                                            className="px-4 py-2 rounded-lg bg-amber-600 text-white font-bold hover:bg-amber-700"
                                                        >
                                                            Save Teacher Review
                                                        </button>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StudentSubmissions;