'use client';

import { useState, useEffect } from 'react';
import { Search, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import { api, Animal } from '@/lib/api';
import AnimalCard from './AnimalCard';
import AddAnimalModal from './AddAnimalModal';

interface AnimalsListProps {
    onViewAnimal: (id: number) => void;
}

export default function AnimalsList({ onViewAnimal }: AnimalsListProps) {
    const [animals, setAnimals] = useState<Animal[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const [showAddModal, setShowAddModal] = useState(false);
    const [filter, setFilter] = useState<string>('');

    const perPage = 12;

    const fetchAnimals = async () => {
        setLoading(true);
        try {
            const data = await api.getAnimals(page, perPage, search);
            setAnimals(data.items);
            setTotal(data.total);
            setTotalPages(Math.ceil(data.total / perPage));
        } catch (error) {
            console.error('Failed to fetch animals:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnimals();
    }, [page, search]);

    const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(e.target.value);
        setPage(1);
    };

    const handleAddAnimal = async (animalData: Partial<Animal>) => {
        try {
            await api.createAnimal(animalData);
            setShowAddModal(false);
            fetchAnimals();
        } catch (error) {
            console.error('Failed to create animal:', error);
        }
    };

    const filteredAnimals = filter
        ? animals.filter(a => a.current_health_status === filter)
        : animals;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl lg:text-3xl font-bold text-[#1B4332]">Animals</h1>
                    <p className="text-[#6C757D] mt-1">{total} animals registered</p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="btn-primary flex items-center gap-2 self-start"
                >
                    <Plus className="w-5 h-5" />
                    Add Animal
                </button>
            </div>

            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#ADB5BD]" />
                    <input
                        type="text"
                        placeholder="Search by tag ID or name..."
                        value={search}
                        onChange={handleSearch}
                        className="input-field pl-12"
                    />
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setFilter('')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all border ${filter === ''
                                ? 'bg-[#1B4332] text-white border-[#1B4332]'
                                : 'bg-white text-[#6C757D] border-[#D8F3DC] hover:border-[#2D6A4F]'
                            }`}
                    >
                        All
                    </button>
                    <button
                        onClick={() => setFilter('healthy')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all border ${filter === 'healthy'
                                ? 'bg-[#2D6A4F] text-white border-[#2D6A4F]'
                                : 'bg-white text-[#6C757D] border-[#D8F3DC] hover:border-[#2D6A4F]'
                            }`}
                    >
                        Healthy
                    </button>
                    <button
                        onClick={() => setFilter('needs_attention')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all border ${filter === 'needs_attention'
                                ? 'bg-[#FFB703] text-[#1B4332] border-[#FFB703]'
                                : 'bg-white text-[#6C757D] border-[#D8F3DC] hover:border-[#FFB703]'
                            }`}
                    >
                        Attention
                    </button>
                    <button
                        onClick={() => setFilter('critical')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all border ${filter === 'critical'
                                ? 'bg-[#DC3545] text-white border-[#DC3545]'
                                : 'bg-white text-[#6C757D] border-[#D8F3DC] hover:border-[#DC3545]'
                            }`}
                    >
                        Critical
                    </button>
                </div>
            </div>

            {/* Animals Grid */}
            {loading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                        <div key={i} className="h-48 rounded-2xl shimmer" />
                    ))}
                </div>
            ) : filteredAnimals.length === 0 ? (
                <div className="text-center py-16 bg-white rounded-2xl border border-[#D8F3DC]">
                    <div className="w-20 h-20 rounded-full bg-[#D8F3DC] flex items-center justify-center mx-auto mb-4">
                        <Search className="w-8 h-8 text-[#6C757D]" />
                    </div>
                    <h3 className="text-lg font-medium text-[#1B4332] mb-2">No animals found</h3>
                    <p className="text-[#6C757D]">Try adjusting your search or filters</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {filteredAnimals.map((animal) => (
                        <AnimalCard
                            key={animal.id}
                            animal={animal}
                            onClick={() => onViewAnimal(animal.id)}
                        />
                    ))}
                </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2">
                    <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="p-2 rounded-lg bg-white border border-[#D8F3DC] disabled:opacity-50 text-[#1B4332]"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>

                    <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                            let pageNum;
                            if (totalPages <= 5) {
                                pageNum = i + 1;
                            } else if (page <= 3) {
                                pageNum = i + 1;
                            } else if (page >= totalPages - 2) {
                                pageNum = totalPages - 4 + i;
                            } else {
                                pageNum = page - 2 + i;
                            }

                            return (
                                <button
                                    key={pageNum}
                                    onClick={() => setPage(pageNum)}
                                    className={`w-10 h-10 rounded-lg font-medium transition-all ${page === pageNum
                                            ? 'bg-[#2D6A4F] text-white'
                                            : 'bg-white text-[#6C757D] border border-[#D8F3DC] hover:border-[#2D6A4F]'
                                        }`}
                                >
                                    {pageNum}
                                </button>
                            );
                        })}
                    </div>

                    <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="p-2 rounded-lg bg-white border border-[#D8F3DC] disabled:opacity-50 text-[#1B4332]"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            )}

            {/* Add Animal Modal */}
            {showAddModal && (
                <AddAnimalModal
                    onClose={() => setShowAddModal(false)}
                    onSubmit={handleAddAnimal}
                />
            )}
        </div>
    );
}
