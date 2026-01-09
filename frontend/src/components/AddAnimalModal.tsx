'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { Animal } from '@/lib/api';

interface AddAnimalModalProps {
    onClose: () => void;
    onSubmit: (data: Partial<Animal>) => void;
}

export default function AddAnimalModal({ onClose, onSubmit }: AddAnimalModalProps) {
    const [formData, setFormData] = useState({
        tag_id: '',
        name: '',
        species: 'cattle',
        breed: '',
        age_months: '',
        gender: 'unknown',
        weight_kg: '',
        notes: '',
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await onSubmit({
                tag_id: formData.tag_id,
                name: formData.name || null,
                species: formData.species as any,
                breed: formData.breed || null,
                age_months: formData.age_months ? parseInt(formData.age_months) : null,
                gender: formData.gender as any,
                weight_kg: formData.weight_kg ? parseFloat(formData.weight_kg) : null,
                notes: formData.notes || null,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value,
        }));
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/40" onClick={onClose} />

            <div className="relative w-full max-w-lg bg-white rounded-2xl p-6 shadow-xl animate-slide-up border border-[#D8F3DC]">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-[#1B4332]">Add New Animal</h2>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg bg-[#D8F3DC] hover:bg-[#B7E4C7] transition-colors"
                    >
                        <X className="w-5 h-5 text-[#1B4332]" />
                    </button>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="col-span-2 sm:col-span-1">
                            <label className="block text-sm font-medium text-[#6C757D] mb-2">
                                Tag ID *
                            </label>
                            <input
                                type="text"
                                name="tag_id"
                                value={formData.tag_id}
                                onChange={handleChange}
                                required
                                placeholder="e.g., CAT-001"
                                className="input-field"
                            />
                        </div>

                        <div className="col-span-2 sm:col-span-1">
                            <label className="block text-sm font-medium text-[#6C757D] mb-2">
                                Name
                            </label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Optional name"
                                className="input-field"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-[#6C757D] mb-2">
                                Species *
                            </label>
                            <select
                                name="species"
                                value={formData.species}
                                onChange={handleChange}
                                className="input-field"
                            >
                                <option value="cattle">Cattle</option>
                                <option value="goat">Goat</option>
                                <option value="sheep">Sheep</option>
                                <option value="pig">Pig</option>
                                <option value="horse">Horse</option>
                                <option value="poultry">Poultry</option>
                                <option value="other">Other</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-[#6C757D] mb-2">
                                Breed
                            </label>
                            <input
                                type="text"
                                name="breed"
                                value={formData.breed}
                                onChange={handleChange}
                                placeholder="e.g., Holstein"
                                className="input-field"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-[#6C757D] mb-2">
                                Age (months)
                            </label>
                            <input
                                type="number"
                                name="age_months"
                                value={formData.age_months}
                                onChange={handleChange}
                                min="0"
                                placeholder="0"
                                className="input-field"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-[#6C757D] mb-2">
                                Gender
                            </label>
                            <select
                                name="gender"
                                value={formData.gender}
                                onChange={handleChange}
                                className="input-field"
                            >
                                <option value="unknown">Unknown</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-[#6C757D] mb-2">
                                Weight (kg)
                            </label>
                            <input
                                type="number"
                                name="weight_kg"
                                value={formData.weight_kg}
                                onChange={handleChange}
                                min="0"
                                step="0.1"
                                placeholder="0"
                                className="input-field"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-[#6C757D] mb-2">
                            Notes
                        </label>
                        <textarea
                            name="notes"
                            value={formData.notes}
                            onChange={handleChange}
                            rows={3}
                            placeholder="Additional notes..."
                            className="input-field resize-none"
                        />
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 btn-secondary"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading || !formData.tag_id}
                            className="flex-1 btn-primary disabled:opacity-50"
                        >
                            {loading ? 'Adding...' : 'Add Animal'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
