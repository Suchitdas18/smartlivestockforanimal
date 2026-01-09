'use client';

interface HealthDistribution {
    healthy: number;
    needs_attention: number;
    critical: number;
    unknown: number;
}

interface HealthChartProps {
    distribution: HealthDistribution;
}

export default function HealthChart({ distribution }: HealthChartProps) {
    const total = distribution.healthy + distribution.needs_attention + distribution.critical + distribution.unknown;

    if (total === 0) {
        return (
            <div className="flex items-center justify-center h-40 text-[#6C757D]">
                No data available
            </div>
        );
    }

    const segments = [
        { key: 'healthy', label: 'Healthy', value: distribution.healthy, color: '#2D6A4F' },
        { key: 'needs_attention', label: 'Needs Attention', value: distribution.needs_attention, color: '#FFB703' },
        { key: 'critical', label: 'Critical', value: distribution.critical, color: '#DC3545' },
        { key: 'unknown', label: 'Unknown', value: distribution.unknown, color: '#ADB5BD' },
    ].filter(s => s.value > 0);

    let cumulativePercent = 0;
    const paths = segments.map(segment => {
        const percent = segment.value / total;
        const startAngle = cumulativePercent * 360;
        const endAngle = (cumulativePercent + percent) * 360;
        cumulativePercent += percent;

        const startX = 50 + 40 * Math.cos((startAngle - 90) * Math.PI / 180);
        const startY = 50 + 40 * Math.sin((startAngle - 90) * Math.PI / 180);
        const endX = 50 + 40 * Math.cos((endAngle - 90) * Math.PI / 180);
        const endY = 50 + 40 * Math.sin((endAngle - 90) * Math.PI / 180);
        const largeArcFlag = percent > 0.5 ? 1 : 0;

        const pathD = percent === 1
            ? `M 50 10 A 40 40 0 1 1 49.99 10 Z`
            : `M 50 50 L ${startX} ${startY} A 40 40 0 ${largeArcFlag} 1 ${endX} ${endY} Z`;

        return { ...segment, percent, path: pathD };
    });

    return (
        <div className="flex items-center gap-6">
            {/* Donut Chart */}
            <div className="relative w-32 h-32 flex-shrink-0">
                <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
                    {paths.map((segment) => (
                        <path
                            key={segment.key}
                            d={segment.path}
                            fill={segment.color}
                            className="transition-all duration-500"
                        />
                    ))}
                    <circle cx="50" cy="50" r="25" fill="#F8F9FA" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold text-[#1B4332]">{total}</span>
                    <span className="text-xs text-[#6C757D]">Total</span>
                </div>
            </div>

            {/* Legend */}
            <div className="flex-1 space-y-2">
                {segments.map(segment => (
                    <div key={segment.key} className="flex items-center gap-3">
                        <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: segment.color }}
                        />
                        <span className="text-sm text-[#6C757D] flex-1">{segment.label}</span>
                        <span className="text-sm font-semibold text-[#1B4332]">{segment.value}</span>
                        <span className="text-xs text-[#ADB5BD] w-12 text-right">
                            {Math.round(segment.percent * 100)}%
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
