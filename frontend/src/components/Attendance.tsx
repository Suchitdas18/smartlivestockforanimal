'use client';

import { useState, useEffect } from 'react';
import { Calendar, CheckCircle, XCircle, TrendingUp, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';

export default function Attendance() {
    const [todayData, setTodayData] = useState<any>(null);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const [today, statsData] = await Promise.all([
                api.getTodayAttendance(),
                api.getAttendanceStats(7),
            ]);
            setTodayData(today);
            setStats(statsData);
        } catch (error) {
            console.error('Failed to fetch attendance:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 w-48 rounded-lg shimmer" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-32 rounded-2xl shimmer" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl lg:text-3xl font-bold text-[#1B4332]">Attendance</h1>
                    <p className="text-[#6C757D] mt-1">Daily livestock presence tracking</p>
                </div>
                <button onClick={fetchData} className="btn-secondary flex items-center gap-2 self-start">
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card card-hover">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[#2D6A4F] flex items-center justify-center">
                            <CheckCircle className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <p className="text-sm text-[#6C757D]">Present Today</p>
                            <p className="text-2xl font-bold text-[#1B4332]">{todayData?.detected_count || 0}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card card-hover">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[#DC3545] flex items-center justify-center">
                            <XCircle className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <p className="text-sm text-[#6C757D]">Missing Today</p>
                            <p className="text-2xl font-bold text-[#1B4332]">{todayData?.missing_count || 0}</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card card-hover">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[#FFB703] flex items-center justify-center">
                            <TrendingUp className="w-6 h-6 text-[#1B4332]" />
                        </div>
                        <div>
                            <p className="text-sm text-[#6C757D]">Attendance Rate</p>
                            <p className="text-2xl font-bold text-[#1B4332]">{todayData?.attendance_rate || 0}%</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-[#2D6A4F] flex items-center justify-center">
                        <Calendar className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-[#1B4332]">Last 7 Days</h3>
                </div>
                {stats?.daily_stats && (
                    <div className="space-y-3">
                        {stats.daily_stats.map((day: any, i: number) => (
                            <div key={day.date} className="flex items-center gap-4">
                                <div className="w-20 text-sm text-[#6C757D]">{i === 0 ? 'Today' : new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}</div>
                                <div className="flex-1 h-6 bg-[#D8F3DC] rounded-lg overflow-hidden">
                                    <div className="h-full bg-gradient-to-r from-[#2D6A4F] to-[#40916C]" style={{ width: `${day.rate}%` }} />
                                </div>
                                <div className="w-16 text-right text-sm text-[#1B4332] font-medium">{day.rate}%</div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
