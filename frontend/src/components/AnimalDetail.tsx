'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, Activity, Calendar, Weight, Dna, Clock, FileText, CheckCircle } from 'lucide-react';
import { api, Animal, HealthRecord, Attendance } from '@/lib/api';

interface AnimalDetailProps {
    animalId: number;
    onBack: () => void;
}

export default function AnimalDetail({ animalId, onBack }: AnimalDetailProps) {
    const [animal, setAnimal] = useState<Animal | null>(null);
    const [healthRecords, setHealthRecords] = useState<HealthRecord[]>([]);
    const [attendanceRecords, setAttendanceRecords] = useState<Attendance[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'health' | 'attendance'>('overview');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [animalData, healthData, attendanceData] = await Promise.all([
                    api.getAnimal(animalId),
                    api.getAnimalHealthHistory(animalId),
                    api.getAnimalAttendanceHistory(animalId, 30),
                ]);
                setAnimal(animalData);
                setHealthRecords(healthData.health_records);
                setAttendanceRecords(attendanceData.attendance_records);
            } catch (error) {
                console.error('Failed to fetch animal data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [animalId]);

    if (loading) {
        return (
            <div className="space-y-6">
                <div className="h-8 w-32 rounded-lg shimmer" />
                <div className="h-48 rounded-2xl shimmer" />
            </div>
        );
    }

    if (!animal) {
        return (
            <div className="text-center py-16 bg-white rounded-2xl border border-[#D8F3DC]">
                <p className="text-[#6C757D]">Animal not found</p>
                <button onClick={onBack} className="btn-secondary mt-4">Go Back</button>
            </div>
        );
    }

    const speciesEmojis: Record<string, string> = {
        cattle: '🐄', goat: '🐐', sheep: '🐑', pig: '🐷', horse: '🐴', poultry: '🐔', other: '🐾',
    };

    const statusStyles: Record<string, string> = {
        healthy: 'bg-[#D8F3DC] border-[#74C69D] text-[#1B4332]',
        needs_attention: 'bg-[#FFF3CD] border-[#FFB703] text-[#856404]',
        critical: 'bg-[#F8D7DA] border-[#F5C6CB] text-[#721C24]',
        unknown: 'bg-[#E9ECEF] border-[#CED4DA] text-[#6C757D]',
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center gap-4">
                <button onClick={onBack} className="p-2 rounded-lg bg-white border border-[#D8F3DC] hover:bg-[#D8F3DC] transition-colors">
                    <ArrowLeft className="w-5 h-5 text-[#1B4332]" />
                </button>
                <div>
                    <h1 className="text-2xl lg:text-3xl font-bold text-[#1B4332]">{animal.tag_id}</h1>
                    <p className="text-[#6C757D]">{animal.name || 'Unnamed'} • {animal.species}</p>
                </div>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                <div className="flex flex-col lg:flex-row gap-6">
                    <div className="flex-shrink-0">
                        <div className="w-32 h-32 rounded-2xl bg-[#D8F3DC] flex items-center justify-center text-6xl">
                            {speciesEmojis[animal.species] || speciesEmojis.other}
                        </div>
                    </div>

                    <div className="flex-1 grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-[#D8F3DC] rounded-xl p-4">
                            <div className="flex items-center gap-2 text-sm text-[#6C757D] mb-1">
                                <Activity className="w-4 h-4" />Health Status
                            </div>
                            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium border ${statusStyles[animal.current_health_status] || statusStyles.unknown}`}>
                                {animal.current_health_status.replace('_', ' ')}
                            </span>
                        </div>

                        <div className="bg-[#D8F3DC] rounded-xl p-4">
                            <div className="flex items-center gap-2 text-sm text-[#6C757D] mb-1">
                                <Dna className="w-4 h-4" />Breed
                            </div>
                            <p className="text-[#1B4332] font-medium">{animal.breed || 'Unknown'}</p>
                        </div>

                        <div className="bg-[#D8F3DC] rounded-xl p-4">
                            <div className="flex items-center gap-2 text-sm text-[#6C757D] mb-1">
                                <Calendar className="w-4 h-4" />Age
                            </div>
                            <p className="text-[#1B4332] font-medium">
                                {animal.age_months
                                    ? animal.age_months < 12 ? `${animal.age_months} months` : `${Math.floor(animal.age_months / 12)}y ${animal.age_months % 12}m`
                                    : 'Unknown'}
                            </p>
                        </div>

                        <div className="bg-[#D8F3DC] rounded-xl p-4">
                            <div className="flex items-center gap-2 text-sm text-[#6C757D] mb-1">
                                <Weight className="w-4 h-4" />Weight
                            </div>
                            <p className="text-[#1B4332] font-medium">{animal.weight_kg ? `${animal.weight_kg.toFixed(1)} kg` : 'Unknown'}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="flex gap-2 border-b border-[#D8F3DC] pb-2">
                {(['overview', 'health', 'attendance'] as const).map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-4 py-2 rounded-lg font-medium transition-all capitalize ${activeTab === tab ? 'bg-[#2D6A4F] text-white' : 'text-[#6C757D] hover:bg-[#D8F3DC]'
                            }`}
                    >
                        {tab}
                    </button>
                ))}
            </div>

            {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC]">
                        <h3 className="text-lg font-semibold text-[#1B4332] mb-4">Recent Health Checks</h3>
                        {healthRecords.length === 0 ? (
                            <p className="text-[#6C757D]">No health records</p>
                        ) : (
                            <div className="space-y-3">
                                {healthRecords.slice(0, 3).map((record) => (
                                    <div key={record.id} className="bg-[#D8F3DC] rounded-xl p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className={`px-2 py-1 rounded text-xs font-medium border ${statusStyles[record.status] || statusStyles.unknown}`}>
                                                {record.status}
                                            </span>
                                            <span className="text-xs text-[#6C757D]">{new Date(record.created_at).toLocaleDateString()}</span>
                                        </div>
                                        <div className="text-sm text-[#6C757D]">Confidence: {(record.confidence * 100).toFixed(1)}%</div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC]">
                        <h3 className="text-lg font-semibold text-[#1B4332] mb-4">Recent Attendance</h3>
                        {attendanceRecords.length === 0 ? (
                            <p className="text-[#6C757D]">No attendance records</p>
                        ) : (
                            <div className="space-y-3">
                                {attendanceRecords.slice(0, 5).map((record) => (
                                    <div key={record.id} className="flex items-center justify-between bg-[#D8F3DC] rounded-xl p-3">
                                        <div className="flex items-center gap-2">
                                            <CheckCircle className="w-4 h-4 text-[#2D6A4F]" />
                                            <span className="text-[#1B4332]">{record.date}</span>
                                        </div>
                                        <span className="text-xs text-[#6C757D]">{(record.detection_confidence * 100).toFixed(0)}%</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {activeTab === 'attendance' && (
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC]">
                    <h3 className="text-lg font-semibold text-[#1B4332] mb-4">Attendance History (Last 30 Days)</h3>
                    <div className="grid grid-cols-7 gap-2">
                        {Array.from({ length: 30 }, (_, i) => {
                            const date = new Date();
                            date.setDate(date.getDate() - (29 - i));
                            const dateStr = date.toISOString().split('T')[0];
                            const hasAttendance = attendanceRecords.some(r => r.date === dateStr);

                            return (
                                <div
                                    key={i}
                                    className={`aspect-square rounded-lg flex items-center justify-center text-xs font-medium ${hasAttendance ? 'bg-[#2D6A4F] text-white' : 'bg-[#E9ECEF] text-[#6C757D]'
                                        }`}
                                    title={dateStr}
                                >
                                    {date.getDate()}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
