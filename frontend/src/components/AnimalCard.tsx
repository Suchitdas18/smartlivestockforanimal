'use client';

import { Animal } from '@/lib/api';

interface AnimalCardProps {
    animal: Animal;
    onClick: () => void;
}

const statusConfig: Record<string, { bg: string; border: string; text: string; label: string }> = {
    healthy: {
        bg: 'bg-[#D8F3DC]',
        border: 'border-[#74C69D]',
        text: 'text-[#1B4332]',
        label: 'Healthy'
    },
    needs_attention: {
        bg: 'bg-[#FFF3CD]',
        border: 'border-[#FFB703]',
        text: 'text-[#856404]',
        label: 'Attention'
    },
    critical: {
        bg: 'bg-[#F8D7DA]',
        border: 'border-[#F5C6CB]',
        text: 'text-[#721C24]',
        label: 'Critical'
    },
    unknown: {
        bg: 'bg-[#E9ECEF]',
        border: 'border-[#CED4DA]',
        text: 'text-[#6C757D]',
        label: 'Unknown'
    },
};

const speciesEmojis: Record<string, string> = {
    cattle: '🐄',
    goat: '🐐',
    sheep: '🐑',
    pig: '🐷',
    horse: '🐴',
    poultry: '🐔',
    other: '🐾',
};

function formatAge(months: number | null): string {
    if (!months) return '—';
    if (months < 12) return `${months}mo`;
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    return remainingMonths > 0 ? `${years}y ${remainingMonths}mo` : `${years}y`;
}

function formatWeight(weight: number | null): string {
    if (!weight) return '—';
    return `${weight.toFixed(1)} kg`;
}

export default function AnimalCard({ animal, onClick }: AnimalCardProps) {
    const status = statusConfig[animal.current_health_status] || statusConfig.unknown;
    const emoji = speciesEmojis[animal.species] || speciesEmojis.other;

    return (
        <button
            onClick={onClick}
            className="w-full bg-white border border-[#D8F3DC] rounded-2xl p-4 text-left hover:border-[#2D6A4F] hover:shadow-medium transition-all duration-200 group"
        >
            {/* Header */}
            <div className="flex items-start gap-3 mb-4">
                {/* Emoji Avatar */}
                <div className="w-11 h-11 rounded-xl bg-[#D8F3DC] flex items-center justify-center text-xl flex-shrink-0 group-hover:scale-105 transition-transform">
                    {emoji}
                </div>

                {/* Tag & Name */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        <h3 className="font-bold text-[#1B4332] text-base truncate">{animal.tag_id}</h3>
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-semibold ${status.bg} ${status.border} ${status.text} border`}>
                            {status.label}
                        </span>
                    </div>
                    <p className="text-xs text-[#6C757D] mt-0.5 capitalize">{animal.name || animal.species}</p>
                </div>
            </div>

            {/* Info Grid */}
            <div className="grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
                <div>
                    <span className="text-[#ADB5BD] text-xs">Breed</span>
                    <p className="text-[#1B4332] truncate">{animal.breed || '—'}</p>
                </div>
                <div>
                    <span className="text-[#ADB5BD] text-xs">Age</span>
                    <p className="text-[#1B4332]">{formatAge(animal.age_months)}</p>
                </div>
                <div>
                    <span className="text-[#ADB5BD] text-xs">Weight</span>
                    <p className="text-[#1B4332]">{formatWeight(animal.weight_kg)}</p>
                </div>
                <div>
                    <span className="text-[#ADB5BD] text-xs">Gender</span>
                    <p className="text-[#1B4332] capitalize">{animal.gender}</p>
                </div>
            </div>
        </button>
    );
}
