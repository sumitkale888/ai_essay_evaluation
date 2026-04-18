import React from 'react';

const StudentPerformancePanel = ({ history }) => {
    const totalSubmissions = history.length;
    const avgScore = totalSubmissions
        ? history.reduce((sum, item) => sum + Number(item.final_score || 0), 0) / totalSubmissions
        : 0;
    const reviewedByTeacher = history.filter((item) => item.teacher_feedback).length;
    const aiOnly = totalSubmissions - reviewedByTeacher;

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <p className="text-xs uppercase tracking-wide text-slate-500 font-bold">Total Essays</p>
                    <p className="text-3xl font-black text-slate-800 mt-1">{totalSubmissions}</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <p className="text-xs uppercase tracking-wide text-slate-500 font-bold">Average Score</p>
                    <p className="text-3xl font-black text-emerald-700 mt-1">{avgScore.toFixed(1)}</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <p className="text-xs uppercase tracking-wide text-slate-500 font-bold">Teacher Reviewed</p>
                    <p className="text-3xl font-black text-amber-700 mt-1">{reviewedByTeacher}</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <p className="text-xs uppercase tracking-wide text-slate-500 font-bold">AI Only</p>
                    <p className="text-3xl font-black text-slate-700 mt-1">{aiOnly}</p>
                </div>
            </div>

            <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-2xl font-black text-slate-800 mb-6">Your Performance</h2>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                    {history.length === 0 && <p className="text-slate-400 py-10">No essays completed yet.</p>}
                    {history.map((item, i) => (
                        <div key={i} className="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                            <div className="flex justify-between items-start mb-2 gap-3">
                                <h4 className="font-bold text-slate-800 text-sm">{item.title}</h4>
                                <span className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded-lg text-xs font-black whitespace-nowrap">
                                    {Number(item.final_score) > 10
                                        ? `${Math.round(Number(item.final_score))}/100`
                                        : `${Number(item.final_score).toFixed(2).replace(/\.00$/, '')}/10`
                                    }
                                </span>
                            </div>

                            <div className="space-y-2 mb-2">
                                <div>
                                    <p className="text-[10px] uppercase tracking-wide text-slate-400 font-bold">AI Feedback</p>
                                    <p className="text-xs text-slate-600 italic line-clamp-4">"{item.feedback_text || 'No AI feedback available.'}"</p>
                                </div>

                                {item.teacher_feedback && (
                                    <div className="rounded-lg bg-amber-50 border border-amber-100 p-2">
                                        <div className="flex items-center justify-between gap-2 mb-1">
                                            <p className="text-[10px] uppercase tracking-wide text-amber-700 font-bold">Teacher Feedback</p>
                                            {item.teacher_score !== null && item.teacher_score !== undefined && (
                                                <span className="text-[10px] font-bold bg-amber-100 text-amber-700 px-2 py-1 rounded-full">
                                                    {Number(item.teacher_score).toFixed(1)}/100
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-xs text-slate-700">{item.teacher_feedback}</p>
                                    </div>
                                )}
                            </div>

                            <p className="text-[10px] text-slate-400 font-medium uppercase">
                                {new Date(item.submission_date).toLocaleDateString()}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default StudentPerformancePanel;
