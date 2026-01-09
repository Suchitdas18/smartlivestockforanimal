'use client';

import { useState, useEffect } from 'react';
import { Bell, CheckCircle, AlertTriangle, XCircle, RefreshCw, Clock } from 'lucide-react';
import { api, Alert } from '@/lib/api';

export default function Alerts() {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<'all' | 'unresolved' | 'resolved'>('unresolved');

    const fetchAlerts = async () => {
        setLoading(true);
        try {
            const resolved = filter === 'all' ? undefined : filter === 'resolved';
            const data = await api.getAlerts(resolved, 50);
            setAlerts(data.alerts);
        } catch (error) {
            console.error('Failed to fetch alerts:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAlerts();
    }, [filter]);

    const handleResolve = async (alertId: number) => {
        try {
            await api.resolveAlert(alertId, 'Resolved via dashboard');
            fetchAlerts();
        } catch (error) {
            console.error('Failed to resolve alert:', error);
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'critical': return <XCircle className="w-5 h-5 text-[#DC3545]" />;
            case 'high': return <AlertTriangle className="w-5 h-5 text-[#FFB703]" />;
            case 'medium': return <AlertTriangle className="w-5 h-5 text-[#FFC107]" />;
            default: return <Bell className="w-5 h-5 text-[#2D6A4F]" />;
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl lg:text-3xl font-bold text-[#1B4332]">Alerts</h1>
                    <p className="text-[#6C757D] mt-1">Health notifications and warnings</p>
                </div>
                <button onClick={fetchAlerts} className="btn-secondary flex items-center gap-2 self-start">
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                </button>
            </div>

            <div className="flex gap-2">
                {(['unresolved', 'resolved', 'all'] as const).map((f) => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all border capitalize ${filter === f
                                ? 'bg-[#2D6A4F] text-white border-[#2D6A4F]'
                                : 'bg-white text-[#6C757D] border-[#D8F3DC] hover:border-[#2D6A4F]'
                            }`}
                    >
                        {f}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => <div key={i} className="h-24 rounded-2xl shimmer" />)}
                </div>
            ) : alerts.length === 0 ? (
                <div className="text-center py-16 bg-white rounded-2xl border border-[#D8F3DC]">
                    <CheckCircle className="w-16 h-16 mx-auto mb-4 text-[#2D6A4F]" />
                    <h3 className="text-lg font-medium text-[#1B4332] mb-2">No alerts</h3>
                    <p className="text-[#6C757D]">All clear! No {filter} alerts found.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {alerts.map((alert) => (
                        <div key={alert.id} className={`bg-white rounded-2xl p-5 border shadow-card ${alert.severity === 'critical' ? 'border-[#DC3545]' :
                                alert.severity === 'high' ? 'border-[#FFB703]' : 'border-[#D8F3DC]'
                            }`}>
                            <div className="flex items-start gap-4">
                                <div className={`p-2 rounded-xl ${alert.severity === 'critical' ? 'bg-[#F8D7DA]' :
                                        alert.severity === 'high' ? 'bg-[#FFF3CD]' : 'bg-[#D8F3DC]'
                                    }`}>
                                    {getSeverityIcon(alert.severity)}
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <h4 className="font-semibold text-[#1B4332]">{alert.title}</h4>
                                            <p className="text-sm text-[#6C757D] mt-1">{alert.message}</p>
                                        </div>
                                        <span className={`px-2 py-1 rounded text-xs font-medium uppercase ${alert.severity === 'critical' ? 'bg-[#DC3545] text-white' :
                                                alert.severity === 'high' ? 'bg-[#FFB703] text-[#1B4332]' : 'bg-[#D8F3DC] text-[#1B4332]'
                                            }`}>
                                            {alert.severity}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-4 mt-3">
                                        <span className="text-xs text-[#ADB5BD] flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {new Date(alert.created_at).toLocaleString()}
                                        </span>
                                        {!alert.resolved && (
                                            <button
                                                onClick={() => handleResolve(alert.id)}
                                                className="text-xs text-[#2D6A4F] font-medium hover:underline"
                                            >
                                                Mark Resolved
                                            </button>
                                        )}
                                        {alert.resolved && (
                                            <span className="text-xs text-[#2D6A4F] font-medium">✓ Resolved</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
