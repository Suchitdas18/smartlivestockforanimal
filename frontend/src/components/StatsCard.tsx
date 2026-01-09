'use client';

import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
    title: string;
    value: number | string;
    icon: LucideIcon;
    color: 'green' | 'blue' | 'orange' | 'red' | 'purple';
    subtitle?: string;
}

const colorStyles = {
    green: {
        bg: 'bg-[#D8F3DC]',
        icon: 'bg-[#2D6A4F] text-white',
        border: 'border-[#B7E4C7]',
    },
    blue: {
        bg: 'bg-[#D8F3DC]',
        icon: 'bg-[#1B4332] text-white',
        border: 'border-[#B7E4C7]',
    },
    orange: {
        bg: 'bg-[#FFF3CD]',
        icon: 'bg-[#FFB703] text-[#1B4332]',
        border: 'border-[#FFE082]',
    },
    red: {
        bg: 'bg-[#F8D7DA]',
        icon: 'bg-[#DC3545] text-white',
        border: 'border-[#F5C6CB]',
    },
    purple: {
        bg: 'bg-[#E8D4F8]',
        icon: 'bg-[#6F42C1] text-white',
        border: 'border-[#D4B8E8]',
    },
};

export default function StatsCard({
    title,
    value,
    icon: Icon,
    color,
    subtitle,
}: StatsCardProps) {
    const styles = colorStyles[color];

    return (
        <div className={`
      bg-white rounded-2xl p-6 border ${styles.border}
      shadow-card card-hover
    `}>
            <div className="flex items-start justify-between mb-4">
                <div className={`
          w-12 h-12 rounded-xl ${styles.icon}
          flex items-center justify-center shadow-md
        `}>
                    <Icon className="w-6 h-6" />
                </div>
            </div>

            <div className="space-y-1">
                <h3 className="text-sm font-medium text-[#6C757D]">{title}</h3>
                <p className="text-3xl font-bold text-[#1B4332]">{value}</p>
                {subtitle && (
                    <p className="text-xs text-[#ADB5BD]">{subtitle}</p>
                )}
            </div>
        </div>
    );
}
