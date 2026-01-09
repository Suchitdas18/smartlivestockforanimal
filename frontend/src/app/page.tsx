'use client';

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import Dashboard from '@/components/Dashboard';
import AnimalsList from '@/components/AnimalsList';
import AnimalDetail from '@/components/AnimalDetail';
import UploadAnalyze from '@/components/UploadAnalyze';
import Attendance from '@/components/Attendance';
import Alerts from '@/components/Alerts';
import { api } from '@/lib/api';

export type View = 'dashboard' | 'animals' | 'animal-detail' | 'upload' | 'attendance' | 'alerts';

export default function Home() {
    const [currentView, setCurrentView] = useState<View>('dashboard');
    const [selectedAnimalId, setSelectedAnimalId] = useState<number | null>(null);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Initialize data
        const init = async () => {
            try {
                // Check if we need to seed demo data
                const stats = await api.getDashboardStats();
                if (stats.total_animals === 0) {
                    await api.seedDemoData();
                }
            } catch (error) {
                console.error('Initialization error:', error);
            } finally {
                setIsLoading(false);
            }
        };
        init();
    }, []);

    const handleViewAnimal = (id: number) => {
        setSelectedAnimalId(id);
        setCurrentView('animal-detail');
    };

    const handleBackToList = () => {
        setSelectedAnimalId(null);
        setCurrentView('animals');
    };

    const renderContent = () => {
        switch (currentView) {
            case 'dashboard':
                return <Dashboard onViewAnimal={handleViewAnimal} />;
            case 'animals':
                return <AnimalsList onViewAnimal={handleViewAnimal} />;
            case 'animal-detail':
                return selectedAnimalId ? (
                    <AnimalDetail animalId={selectedAnimalId} onBack={handleBackToList} />
                ) : (
                    <AnimalsList onViewAnimal={handleViewAnimal} />
                );
            case 'upload':
                return <UploadAnalyze />;
            case 'attendance':
                return <Attendance />;
            case 'alerts':
                return <Alerts />;
            default:
                return <Dashboard onViewAnimal={handleViewAnimal} />;
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#F8F9FA]">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-[#2D6A4F] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <h2 className="text-xl font-semibold text-[#1B4332]">Loading Smart Livestock AI...</h2>
                    <p className="text-[#6C757D] mt-2">Initializing system</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex">
            {/* Mobile menu button */}
            <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-white shadow-md border border-[#D8F3DC]"
            >
                <svg className="w-6 h-6 text-[#1B4332]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {isMobileMenuOpen ? (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    )}
                </svg>
            </button>

            {/* Sidebar */}
            <Sidebar
                currentView={currentView}
                onViewChange={(view) => {
                    setCurrentView(view);
                    setIsMobileMenuOpen(false);
                }}
                isOpen={isMobileMenuOpen}
                onClose={() => setIsMobileMenuOpen(false)}
            />

            {/* Main content */}
            <main className="flex-1 lg:ml-64 min-h-screen">
                <div className="p-4 lg:p-8">
                    {renderContent()}
                </div>
            </main>

            {/* Mobile menu overlay */}
            {isMobileMenuOpen && (
                <div
                    className="lg:hidden fixed inset-0 bg-black/50 z-30"
                    onClick={() => setIsMobileMenuOpen(false)}
                />
            )}
        </div>
    );
}
