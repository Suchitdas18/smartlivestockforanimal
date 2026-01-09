'use client';

import { useState, useEffect } from 'react';
import {
    Activity,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Users,
    Calendar,
    TrendingUp,
    Eye,
    RefreshCw
} from 'lucide-react';
import { api, DashboardStats } from '@/lib/api';
import StatsCard from './StatsCard';
import HealthChart from './HealthChart';

interface DashboardProps {
    onViewAnimal: (id: number) => void;
}

export default function Dashboard({ onViewAnimal }: DashboardProps) {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const fetchStats = async () => {
        try {
            const data = await api.getDashboardStats();
            setStats(data);
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const handleRefresh = () => {
        setRefreshing(true);
        fetchStats();
    };

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 w-48 rounded-lg shimmer" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="h-32 rounded-2xl shimmer" />
                    ))}
                </div>
            </div>
        );
    }

    if (!stats) {
        return (
            <div className="flex items-center justify-center h-64">
                <p className="text-[#6C757D]">Failed to load dashboard data</p>
            </div>
        );
    }

    const healthTotal = stats.health_distribution.healthy +
        stats.health_distribution.needs_attention +
        stats.health_distribution.critical +
        stats.health_distribution.unknown;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl lg:text-3xl font-bold text-[#1B4332]">Dashboard</h1>
                    <p className="text-[#6C757D] mt-1">Real-time livestock health monitoring</p>
                </div>
                <button
                    onClick={handleRefresh}
                    disabled={refreshing}
                    className="btn-secondary flex items-center gap-2 self-start"
                >
                    <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                    Refresh
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                    title="Total Animals"
                    value={stats.total_animals}
                    icon={Users}
                    color="blue"
                    subtitle="Registered in system"
                />
                <StatsCard
                    title="Healthy"
                    value={stats.health_distribution.healthy}
                    icon={CheckCircle}
                    color="green"
                    subtitle={`${healthTotal > 0 ? Math.round(stats.health_distribution.healthy / healthTotal * 100) : 0}% of herd`}
                />
                <StatsCard
                    title="Needs Attention"
                    value={stats.health_distribution.needs_attention}
                    icon={AlertTriangle}
                    color="orange"
                    subtitle="Require checkup"
                />
                <StatsCard
                    title="Critical"
                    value={stats.health_distribution.critical}
                    icon={XCircle}
                    color="red"
                    subtitle="Immediate care needed"
                />
            </div>

            {/* Attendance & Health Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Attendance Card */}
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card card-hover">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-[#2D6A4F] flex items-center justify-center">
                                <Calendar className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-[#1B4332]">Today's Attendance</h3>
                                <p className="text-sm text-[#6C757D]">Daily presence tracking</p>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-end gap-4 mb-4">
                        <div className="text-5xl font-bold text-[#2D6A4F]">{stats.todays_attendance}</div>
                        <div className="text-[#6C757D] mb-2">/ {stats.total_animals} animals</div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                            <span className="text-[#6C757D]">Attendance Rate</span>
                            <span className="text-[#1B4332] font-semibold">{stats.attendance_rate}%</span>
                        </div>
                        <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${stats.attendance_rate}%` }} />
                        </div>
                    </div>
                </div>

                {/* Health Distribution Chart */}
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card card-hover">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-xl bg-[#1B4332] flex items-center justify-center">
                            <Activity className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-[#1B4332]">Health Distribution</h3>
                            <p className="text-sm text-[#6C757D]">{stats.recent_health_checks} checks in 24h</p>
                        </div>
                    </div>

                    <HealthChart distribution={stats.health_distribution} />
                </div>
            </div>

            {/* Recent Alerts & Animals Needing Attention */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Recent Alerts */}
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-[#DC3545] flex items-center justify-center">
                                <AlertTriangle className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-[#1B4332]">Recent Alerts</h3>
                                <p className="text-sm text-[#6C757D]">Unresolved notifications</p>
                            </div>
                        </div>
                        <span className="px-3 py-1 rounded-full bg-[#F8D7DA] text-[#721C24] text-sm font-medium">
                            {stats.recent_alerts.length}
                        </span>
                    </div>

                    <div className="space-y-3 max-h-64 overflow-y-auto">
                        {stats.recent_alerts.length === 0 ? (
                            <div className="text-center py-8 text-[#6C757D]">
                                <CheckCircle className="w-12 h-12 mx-auto mb-2 text-[#2D6A4F]" />
                                <p>No active alerts</p>
                            </div>
                        ) : (
                            stats.recent_alerts.slice(0, 5).map((alert) => (
                                <div
                                    key={alert.id}
                                    className={`p-4 rounded-xl border ${alert.severity === 'critical' ? 'bg-[#F8D7DA] border-[#F5C6CB]' : 'bg-[#FFF3CD] border-[#FFE082]'
                                        }`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <h4 className="font-medium text-[#1B4332]">{alert.title}</h4>
                                            <p className="text-sm text-[#6C757D] mt-1 line-clamp-2">{alert.message}</p>
                                        </div>
                                        <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${alert.severity === 'critical' ? 'bg-[#DC3545] text-white' : 'bg-[#FFB703] text-[#1B4332]'
                                            }`}>
                                            {alert.severity}
                                        </span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Animals Needing Attention */}
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-[#FFB703] flex items-center justify-center">
                                <Eye className="w-5 h-5 text-[#1B4332]" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-[#1B4332]">Needs Attention</h3>
                                <p className="text-sm text-[#6C757D]">Animals requiring care</p>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-3 max-h-64 overflow-y-auto">
                        {stats.animals_needing_attention.length === 0 ? (
                            <div className="text-center py-8 text-[#6C757D]">
                                <CheckCircle className="w-12 h-12 mx-auto mb-2 text-[#2D6A4F]" />
                                <p>All animals are healthy</p>
                            </div>
                        ) : (
                            stats.animals_needing_attention.map((animal) => (
                                <button
                                    key={animal.id}
                                    onClick={() => onViewAnimal(animal.id)}
                                    className="w-full p-4 rounded-xl bg-[#D8F3DC] border border-[#B7E4C7] flex items-center gap-4 hover:bg-[#B7E4C7] transition-colors"
                                >
                                    <div className="w-12 h-12 rounded-xl bg-white flex items-center justify-center">
                                        <span className="text-lg font-bold text-[#1B4332]">
                                            {animal.tag_id.substring(0, 2)}
                                        </span>
                                    </div>
                                    <div className="flex-1 text-left">
                                        <h4 className="font-medium text-[#1B4332]">{animal.tag_id}</h4>
                                        <p className="text-sm text-[#6C757D]">{animal.species} • {animal.breed || 'Unknown breed'}</p>
                                    </div>
                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${animal.current_health_status === 'critical' ? 'bg-[#F8D7DA] text-[#721C24]' : 'bg-[#FFF3CD] text-[#856404]'
                                        }`}>
                                        {animal.current_health_status.replace('_', ' ')}
                                    </span>
                                </button>
                            ))
                        )}
                    </div>
                </div>
            </div>

            {/* Species Distribution */}
            <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-[#2D6A4F] flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-[#1B4332]">Herd Composition</h3>
                        <p className="text-sm text-[#6C757D]">Distribution by species</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                    {Object.entries(stats.species_distribution).map(([species, count]) => (
                        <div key={species} className="text-center p-4 rounded-xl bg-[#D8F3DC] border border-[#B7E4C7]">
                            <div className="text-2xl font-bold text-[#1B4332] mb-1">{count}</div>
                            <div className="text-sm text-[#6C757D] capitalize">{species}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
