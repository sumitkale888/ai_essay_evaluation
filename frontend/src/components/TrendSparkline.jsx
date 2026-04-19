import React from 'react';

const TrendSparkline = ({ data, color = '#059669' }) => {
    const width = 220;
    const height = 70;
    const padding = 8;

    if (!data || data.length === 0) {
        return <div className="text-xs text-slate-400">No trend data yet.</div>;
    }

    const values = data.map((item) => Number(item.value) || 0);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);
    const range = maxValue - minValue || 1;

    const points = values.map((value, index) => {
        const x = padding + (index * (width - 2 * padding)) / Math.max(values.length - 1, 1);
        const y = height - padding - ((value - minValue) / range) * (height - 2 * padding);
        return `${x},${y}`;
    });

    const singlePoint = values.length === 1;
    const firstX = padding;
    const firstY = height - padding - ((values[0] - minValue) / range) * (height - 2 * padding);

    return (
        <div className="space-y-1">
            <svg width={width} height={height} className="block">
                {singlePoint ? (
                    <>
                        <circle cx={firstX} cy={firstY} r="4" fill={color} />
                        <text x={firstX + 8} y={Math.max(12, firstY - 6)} fontSize="11" fill="#475569">
                            {values[0].toFixed(2)}
                        </text>
                    </>
                ) : (
                    <polyline
                        fill="none"
                        stroke={color}
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        points={points.join(' ')}
                    />
                )}
            </svg>
            <div className="flex gap-2 overflow-x-auto text-[10px] text-slate-500 uppercase tracking-wide">
                {data.map((item) => (
                    <span key={item.label} className="whitespace-nowrap">{item.label}</span>
                ))}
            </div>
        </div>
    );
};

export default TrendSparkline;
