import React from 'react';

const DIMENSION_LABELS = {
    argument: 'Argument',
    coherence: 'Coherence',
    vocabulary: 'Vocabulary',
    sentence: 'Sentence',
    introduction: 'Introduction',
    conclusion: 'Conclusion',
    logic: 'Logic',
    facts: 'Facts',
    relevance: 'Relevance',
};

const scoreClass = (score) => {
    if (score >= 8) return 'bg-emerald-500';
    if (score >= 6) return 'bg-lime-500';
    if (score >= 4) return 'bg-amber-500';
    return 'bg-rose-500';
};

const AnalyticsHeatmap = ({ heatmap }) => {
    const entries = Object.entries(heatmap || {});

    if (entries.length === 0) {
        return <p className="text-xs text-slate-400">No heatmap data</p>;
    }

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {entries.map(([key, value]) => {
                const score = Number(value) || 0;
                return (
                    <div key={key} className="border border-slate-200 rounded-lg p-2 bg-white">
                        <p className="text-[11px] font-semibold text-slate-600">{DIMENSION_LABELS[key] || key}</p>
                        <div className="mt-1 h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                            <div
                                className={`h-full ${scoreClass(score)}`}
                                style={{ width: `${Math.max(0, Math.min(100, score * 10))}%` }}
                            />
                        </div>
                        <p className="text-[10px] text-slate-500 mt-1">{score.toFixed(1)}/10</p>
                    </div>
                );
            })}
        </div>
    );
};

export default AnalyticsHeatmap;
