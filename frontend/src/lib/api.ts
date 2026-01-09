const API_BASE_URL = '';

// Types
export interface Animal {
    id: number;
    tag_id: string;
    name: string | null;
    species: string;
    breed: string | null;
    age_months: number | null;
    gender: string;
    weight_kg: number | null;
    notes: string | null;
    image_path: string | null;
    current_health_status: string;
    last_health_check: string | null;
    created_at: string;
    updated_at: string;
}

export interface HealthRecord {
    id: number;
    animal_id: number;
    status: string;
    confidence: number;
    posture_score: number | null;
    coat_condition_score: number | null;
    mobility_score: number | null;
    alertness_score: number | null;
    findings: Record<string, any> | null;
    symptoms: string | null;
    notes: string | null;
    image_path: string | null;
    created_at: string;
}

export interface Attendance {
    id: number;
    animal_id: number;
    date: string;
    detected_at: string;
    detection_confidence: number;
    identification_method: string;
}

export interface Alert {
    id: number;
    animal_id: number | null;
    alert_type: string;
    severity: string;
    title: string;
    message: string;
    resolved: boolean;
    created_at: string;
    animal?: Animal;
}

export interface DashboardStats {
    total_animals: number;
    health_distribution: {
        healthy: number;
        needs_attention: number;
        critical: number;
        unknown: number;
    };
    todays_attendance: number;
    attendance_rate: number;
    recent_alerts: Alert[];
    animals_needing_attention: Animal[];
    recent_health_checks: number;
    species_distribution: Record<string, number>;
}

export interface DetectionResult {
    image_path: string;
    detected_animals: Array<{
        bounding_box: { x1: number; y1: number; x2: number; y2: number };
        species: string;
        confidence: number;
    }>;
    total_detected: number;
    processing_time_ms: number;
}

export interface HealthAssessment {
    status: string;
    confidence: number;
    posture_score: number;
    coat_condition_score: number;
    mobility_score: number;
    alertness_score: number;
    findings: Record<string, any>;
    recommendations: string[];
}

// API functions
async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

export const api = {
    // Dashboard
    getDashboardStats: () => fetchApi<DashboardStats>('/api/dashboard/stats'),
    getQuickStats: () => fetchApi<any>('/api/dashboard/quick-stats'),
    seedDemoData: () => fetchApi<any>('/api/dashboard/seed-demo-data', { method: 'POST' }),
    getHealthTrends: (days = 7) => fetchApi<any>(`/api/dashboard/trends/health?days=${days}`),
    getAttendanceTrends: (days = 7) => fetchApi<any>(`/api/dashboard/trends/attendance?days=${days}`),

    // Animals
    getAnimals: (page = 1, perPage = 20, search = '') =>
        fetchApi<{ items: Animal[]; total: number; page: number; per_page: number }>(
            `/api/animals?page=${page}&per_page=${perPage}${search ? `&search=${search}` : ''}`
        ),
    getAnimal: (id: number) => fetchApi<Animal>(`/api/animals/${id}`),
    createAnimal: (data: Partial<Animal>) =>
        fetchApi<Animal>('/api/animals', { method: 'POST', body: JSON.stringify(data) }),
    updateAnimal: (id: number, data: Partial<Animal>) =>
        fetchApi<Animal>(`/api/animals/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    deleteAnimal: (id: number) =>
        fetchApi<void>(`/api/animals/${id}`, { method: 'DELETE' }),
    getAnimalHealthHistory: (id: number) =>
        fetchApi<{ animal: Animal; health_records: HealthRecord[] }>(`/api/animals/${id}/health-history`),
    getAnimalAttendanceHistory: (id: number, days = 30) =>
        fetchApi<{ animal: Animal; attendance_records: Attendance[] }>(
            `/api/animals/${id}/attendance-history?days=${days}`
        ),

    // Health
    assessHealth: (imagePath: string, animalId?: number) =>
        fetchApi<HealthAssessment>('/api/health/assess', {
            method: 'POST',
            body: JSON.stringify({ image_path: imagePath, animal_id: animalId }),
        }),
    getHealthRecords: (animalId: number) =>
        fetchApi<any>(`/api/health/records/${animalId}`),
    getHealthSummary: () => fetchApi<any>('/api/health/summary'),

    // Attendance
    getTodayAttendance: () => fetchApi<any>('/api/attendance/today'),
    getAttendanceStats: (days = 7) => fetchApi<any>(`/api/attendance/stats?days=${days}`),
    markAttendance: (animalId: number, confidence = 1.0) =>
        fetchApi<Attendance>('/api/attendance/mark', {
            method: 'POST',
            body: JSON.stringify({ animal_id: animalId, detection_confidence: confidence }),
        }),
    getMissingAnimals: (days = 1) => fetchApi<any>(`/api/attendance/missing?days=${days}`),

    // Alerts
    getAlerts: (resolved?: boolean, limit = 20) =>
        fetchApi<{ alerts: Alert[]; total: number }>(
            `/api/dashboard/alerts?limit=${limit}${resolved !== undefined ? `&resolved=${resolved}` : ''}`
        ),
    resolveAlert: (alertId: number, notes?: string) =>
        fetchApi<any>(`/api/dashboard/alerts/${alertId}/resolve`, {
            method: 'PUT',
            body: JSON.stringify({ resolution_notes: notes }),
        }),

    // Detection
    detectAnimals: (imagePath: string) =>
        fetchApi<DetectionResult>('/api/detect/animals', {
            method: 'POST',
            body: JSON.stringify({ image_path: imagePath }),
        }),
    identifyAnimal: (imagePath: string) =>
        fetchApi<any>('/api/detect/identify', {
            method: 'POST',
            body: JSON.stringify({ image_path: imagePath, use_ocr: true }),
        }),

    // Upload
    uploadImage: async (file: File): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/upload/image`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        return response.json();
    },

    uploadAndAnalyze: async (file: File, animalId?: number): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);
        if (animalId) {
            formData.append('animal_id', animalId.toString());
        }

        const response = await fetch(`${API_BASE_URL}/api/upload/analyze-image`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Upload and analyze failed');
        }

        return response.json();
    },
};
