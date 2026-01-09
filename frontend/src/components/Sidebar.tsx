'use client';

import { View } from '@/app/page';
import {
    LayoutDashboard,
    PawPrint,
    Upload,
    Calendar,
    Bell,
    Activity,
    Beef
} from 'lucide-react';

interface SidebarProps {
    currentView: View;
    onViewChange: (view: View) => void;
    isOpen: boolean;
    onClose: () => void;
}

const menuItems = [
    { id: 'dashboard' as View, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'animals' as View, label: 'Animals', icon: PawPrint },
    { id: 'upload' as View, label: 'Upload & Analyze', icon: Upload },
    { id: 'attendance' as View, label: 'Attendance', icon: Calendar },
    { id: 'alerts' as View, label: 'Alerts', icon: Bell },
];

export default function Sidebar({ currentView, onViewChange, isOpen, onClose }: SidebarProps) {
    return (
        <aside
            className={`
        fixed top-0 left-0 h-full w-64 bg-[#1B4332] z-40
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 shadow-xl
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}
        >
            <div className="flex flex-col h-full">
                {/* Logo */}
                <div className="p-6 border-b border-[#2D6A4F]">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-[#2D6A4F] flex items-center justify-center shadow-lg">
                            <Beef className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-white">Smart Livestock</h1>
                            <p className="text-xs text-[#95D5B2]">AI Health Monitor</p>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-2">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = currentView === item.id ||
                            (currentView === 'animal-detail' && item.id === 'animals');

                        return (
                            <button
                                key={item.id}
                                onClick={() => onViewChange(item.id)}
                                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-xl
                  transition-all duration-300 group
                  ${isActive
                                        ? 'bg-[#2D6A4F] text-white shadow-md'
                                        : 'text-[#95D5B2] hover:text-white hover:bg-[#2D6A4F]/50'
                                    }
                `}
                            >
                                <Icon className={`w-5 h-5 ${isActive ? 'text-[#FFB703]' : 'group-hover:text-[#FFB703]'}`} />
                                <span className="font-medium">{item.label}</span>
                                {isActive && (
                                    <div className="ml-auto w-2 h-2 rounded-full bg-[#FFB703]" />
                                )}
                            </button>
                        );
                    })}
                </nav>

                {/* System Status */}
                <div className="p-4 border-t border-[#2D6A4F]">
                    <div className="bg-[#2D6A4F] rounded-xl p-4">
                        <div className="flex items-center gap-2 mb-3">
                            <Activity className="w-4 h-4 text-[#FFB703]" />
                            <span className="text-sm font-medium text-white">System Status</span>
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs">
                                <span className="text-[#95D5B2]">AI Engine</span>
                                <span className="text-[#74C69D] flex items-center gap-1">
                                    <span className="w-2 h-2 rounded-full bg-[#74C69D] animate-pulse" />
                                    Online
                                </span>
                            </div>
                            <div className="flex items-center justify-between text-xs">
                                <span className="text-[#95D5B2]">Database</span>
                                <span className="text-[#74C69D] flex items-center gap-1">
                                    <span className="w-2 h-2 rounded-full bg-[#74C69D] animate-pulse" />
                                    Connected
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-[#2D6A4F]">
                    <div className="flex items-center gap-2 text-[#95D5B2] text-sm">
                        <span>v1.0.0</span>
                        <span>•</span>
                        <span>Hackathon Ready</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}
