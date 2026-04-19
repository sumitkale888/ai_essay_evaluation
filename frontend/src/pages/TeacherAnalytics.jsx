import React, { useEffect, useMemo, useState } from 'react';
import { teacherService } from '../services/api';
import TrendSparkline from '../components/TrendSparkline';
import AnalyticsHeatmap from '../components/AnalyticsHeatmap';

const TeacherAnalytics = () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadAnalytics = async () => {
            try {
                const data = await teacherService.getAnalytics(user.user_id);
                setAnalytics(data);
            } catch (err) {
                console.error('Failed to load analytics', err);
            } finally {
                setLoading(false);
            }
        };

        loadAnalytics();
    }, [user.user_id]);

    const scoreTrend = useMemo(() => {
        if (!analytics?.improvement_trends) return [];
        return analytics.improvement_trends.map((item) => ({
            label: item.month,
            value: item.average_score,
        }));
    }, [analytics]);

    const plagiarismTrend = useMemo(() => {
        if (!analytics?.plagiarism_trends) return [];
        return analytics.plagiarism_trends.map((item) => ({
            label: item.month,
            value: item.avg_similarity,
        }));
    }, [analytics]);

    if (loading) {
        return <div className="text-slate-500">Loading analytics...</div>;
    }

    if (!analytics) {
        return <div className="text-slate-500">Analytics are unavailable right now.</div>;
    }

    const summary = analytics.summary || {};

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <h1 className="text-3xl font-black text-slate-800">Analytics & Insights</h1>

            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="bg-white border border-slate-200 rounded-2xl p-4">
                    <p className="text-xs uppercase text-slate-500 font-bold">Classrooms</p>
                    <p className="text-2xl font-black text-slate-800 mt-1">{summary.classroom_count || 0}</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4">
                    <p className="text-xs uppercase text-slate-500 font-bold">Students</p>
                    <p className="text-2xl font-black text-slate-800 mt-1">{summary.student_count || 0}</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4">
                    <p className="text-xs uppercase text-slate-500 font-bold">Submissions</p>
                    <p className="text-2xl font-black text-slate-800 mt-1">{summary.submission_count || 0}</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4">
                    <p className="text-xs uppercase text-slate-500 font-bold">Average Score</p>
                    <p className="text-2xl font-black text-emerald-700 mt-1">{summary.average_class_score || 0}</p>
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-4">
                    <p className="text-xs uppercase text-slate-500 font-bold">High Plagiarism</p>
                    <p className="text-2xl font-black text-rose-700 mt-1">{summary.high_plagiarism_rate || 0}%</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-slate-200 rounded-2xl p-5">
                    <h2 className="text-lg font-bold text-slate-700 mb-3">Improvement Trend (Average Score)</h2>
                    <TrendSparkline data={scoreTrend} color="#059669" />
                </div>
                <div className="bg-white border border-slate-200 rounded-2xl p-5">
                    <h2 className="text-lg font-bold text-slate-700 mb-3">Plagiarism Trend (Avg Similarity)</h2>
                    <TrendSparkline data={plagiarismTrend} color="#e11d48" />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-slate-200 rounded-2xl p-5">
                    <h2 className="text-lg font-bold text-slate-700 mb-3">Common Mistakes</h2>
                    {(analytics.common_mistakes || []).length === 0 && (
                        <p className="text-sm text-slate-500">No common mistakes detected yet.</p>
                    )}
                    <div className="space-y-2">
                        {(analytics.common_mistakes || []).map((item) => (
                            <div key={item.category} className="flex items-center justify-between bg-slate-50 rounded-lg p-2 border border-slate-200">
                                <span className="text-sm font-semibold text-slate-700 capitalize">{item.category}</span>
                                <span className="text-sm font-black text-slate-800">{item.count}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white border border-slate-200 rounded-2xl p-5">
                    <h2 className="text-lg font-bold text-slate-700 mb-3">Classroom Analytics</h2>
                    <div className="space-y-2">
                        {(analytics.classroom_analytics || []).map((room) => (
                            <div key={room.classroom_id ?? room.classroom_name} className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                                <p className="font-bold text-slate-800">{room.classroom_name}</p>
                                <p className="text-xs text-slate-500 mt-1">
                                    Avg: {room.average_score} | Students: {room.student_count} | Submissions: {room.submission_count} | Plagiarism: {room.plagiarism_rate}%
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-5">
                <h2 className="text-lg font-bold text-slate-700 mb-3">Student Profiling (Strength/Weakness Heatmap)</h2>
                <div className="space-y-4">
                    {(analytics.student_profiles || []).map((student) => (
                        <div key={student.student_id} className="border border-slate-200 rounded-xl p-4 bg-slate-50">
                            <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                                <p className="font-bold text-slate-800">{student.student_name}</p>
                                <p className="text-xs text-slate-600">
                                    Avg Score: <span className="font-bold">{student.average_score}</span>
                                    {' '}| Trend: <span className={`font-bold ${student.trend_delta >= 0 ? 'text-emerald-700' : 'text-rose-700'}`}>{student.trend_delta >= 0 ? '+' : ''}{student.trend_delta}</span>
                                    {' '}| Avg Similarity: <span className="font-bold">{student.avg_similarity}%</span>
                                </p>
                            </div>
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-3">
                                <div>
                                    <p className="text-xs uppercase font-bold text-emerald-700">Strengths</p>
                                    <p className="text-sm text-slate-700 capitalize">{(student.strengths || []).join(', ') || '-'}</p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase font-bold text-rose-700">Weaknesses</p>
                                    <p className="text-sm text-slate-700 capitalize">{(student.weaknesses || []).join(', ') || '-'}</p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase font-bold text-slate-500">Submissions</p>
                                    <p className="text-sm text-slate-700">{student.submission_count}</p>
                                </div>
                            </div>
                            <AnalyticsHeatmap heatmap={student.heatmap} />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TeacherAnalytics;
