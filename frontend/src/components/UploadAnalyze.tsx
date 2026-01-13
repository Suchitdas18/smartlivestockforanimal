'use client';

import { useState, useCallback } from 'react';
import {
    Upload,
    Camera,
    FileImage,
    CheckCircle,
    AlertTriangle,
    XCircle,
    Loader,
    Eye,
    Scan,
    Activity,
    Video
} from 'lucide-react';
import { api } from '@/lib/api';
import LiveCamera from './LiveCamera';

export default function UploadAnalyze() {
    const [activeTab, setActiveTab] = useState<'upload' | 'camera'>('upload');
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [results, setResults] = useState<any>(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleFile = (file: File) => {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }

        setFile(file);
        setResults(null);

        const reader = new FileReader();
        reader.onload = (e) => {
            setPreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);
    };

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleAnalyze = async () => {
        if (!file) return;

        setUploading(true);
        setAnalyzing(true);

        try {
            const result = await api.uploadAndAnalyze(file);
            setResults(result);
        } catch (error) {
            console.error('Analysis failed:', error);
            alert('Analysis failed. Please try again.');
        } finally {
            setUploading(false);
            setAnalyzing(false);
        }
    };

    // Handle camera capture
    const handleCameraCapture = async (capturedFile: File) => {
        setFile(capturedFile);
        setAnalyzing(true);

        // Create preview
        const reader = new FileReader();
        reader.onload = (e) => {
            setPreview(e.target?.result as string);
        };
        reader.readAsDataURL(capturedFile);

        try {
            const result = await api.uploadAndAnalyze(capturedFile);
            setResults(result);
        } catch (error) {
            console.error('Analysis failed:', error);
            alert('Analysis failed. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setPreview(null);
        setResults(null);
    };

    const getHealthStatusIcon = (status: string) => {
        switch (status) {
            case 'healthy':
                return <CheckCircle className="w-6 h-6 text-[#2D6A4F]" />;
            case 'needs_attention':
                return <AlertTriangle className="w-6 h-6 text-[#FFB703]" />;
            case 'critical':
                return <XCircle className="w-6 h-6 text-[#DC3545]" />;
            default:
                return <Activity className="w-6 h-6 text-[#6C757D]" />;
        }
    };

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl lg:text-3xl font-bold text-[#1B4332]">Upload & Analyze</h1>
                <p className="text-[#6C757D] mt-1">Upload images or use live camera for AI-powered health assessment</p>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 bg-white rounded-xl p-1.5 border border-[#D8F3DC] w-fit">
                <button
                    onClick={() => setActiveTab('upload')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'upload'
                            ? 'bg-[#2D6A4F] text-white'
                            : 'text-[#6C757D] hover:bg-[#D8F3DC]'
                        }`}
                >
                    <Upload className="w-4 h-4" />
                    Upload Image
                </button>
                <button
                    onClick={() => setActiveTab('camera')}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === 'camera'
                            ? 'bg-[#2D6A4F] text-white'
                            : 'text-[#6C757D] hover:bg-[#D8F3DC]'
                        }`}
                >
                    <Video className="w-4 h-4" />
                    Live Camera
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Area (Upload or Camera) */}
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                    {activeTab === 'upload' ? (
                        <>
                            <h3 className="text-lg font-semibold text-[#1B4332] mb-4 flex items-center gap-2">
                                <Camera className="w-5 h-5 text-[#2D6A4F]" />
                                Upload Image
                            </h3>

                            {!preview ? (
                                <div
                                    className={`
                                        relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300
                                        ${dragActive ? 'border-[#2D6A4F] bg-[#D8F3DC]' : 'border-[#B7E4C7] hover:border-[#2D6A4F]'}
                                    `}
                                    onDragEnter={handleDrag}
                                    onDragLeave={handleDrag}
                                    onDragOver={handleDrag}
                                    onDrop={handleDrop}
                                    onClick={() => document.getElementById('file-input')?.click()}
                                >
                                    <input
                                        id="file-input"
                                        type="file"
                                        accept="image/*"
                                        onChange={handleFileInput}
                                        className="hidden"
                                    />

                                    <div className="w-16 h-16 rounded-2xl bg-[#D8F3DC] flex items-center justify-center mx-auto mb-4">
                                        <Upload className="w-8 h-8 text-[#2D6A4F]" />
                                    </div>

                                    <h4 className="text-lg font-medium text-[#1B4332] mb-2">
                                        Drop your image here
                                    </h4>
                                    <p className="text-[#6C757D] text-sm mb-4">
                                        or click to browse files
                                    </p>
                                    <p className="text-xs text-[#ADB5BD]">
                                        Supports: JPG, PNG, WebP (Max 50MB)
                                    </p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="relative aspect-video rounded-xl overflow-hidden bg-[#D8F3DC]">
                                        <img src={preview} alt="Preview" className="w-full h-full object-contain" />
                                        {analyzing && (
                                            <div className="absolute inset-0 bg-white/80 flex items-center justify-center">
                                                <div className="text-center">
                                                    <Loader className="w-10 h-10 text-[#2D6A4F] animate-spin mx-auto mb-2" />
                                                    <p className="text-[#1B4332] font-medium">Analyzing...</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    <div className="flex items-center gap-3 bg-[#D8F3DC] rounded-xl p-3">
                                        <FileImage className="w-8 h-8 text-[#2D6A4F]" />
                                        <div className="flex-1 min-w-0">
                                            <p className="text-[#1B4332] font-medium truncate">{file?.name}</p>
                                            <p className="text-xs text-[#6C757D]">
                                                {file && (file.size / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex gap-3">
                                        <button onClick={handleReset} className="flex-1 btn-secondary">Clear</button>
                                        <button
                                            onClick={handleAnalyze}
                                            disabled={analyzing}
                                            className="flex-1 btn-primary flex items-center justify-center gap-2"
                                        >
                                            {analyzing ? (
                                                <><Loader className="w-4 h-4 animate-spin" />Analyzing...</>
                                            ) : (
                                                <><Scan className="w-4 h-4" />Analyze</>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            )}
                        </>
                    ) : (
                        <>
                            <h3 className="text-lg font-semibold text-[#1B4332] mb-4 flex items-center gap-2">
                                <Video className="w-5 h-5 text-[#2D6A4F]" />
                                Live Camera
                            </h3>
                            <LiveCamera
                                onCapture={handleCameraCapture}
                                isAnalyzing={analyzing}
                            />
                        </>
                    )}
                </div>

                {/* Results */}
                <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                    <h3 className="text-lg font-semibold text-[#1B4332] mb-4 flex items-center gap-2">
                        <Eye className="w-5 h-5 text-[#2D6A4F]" />
                        Analysis Results
                    </h3>

                    {!results ? (
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <div className="w-16 h-16 rounded-2xl bg-[#D8F3DC] flex items-center justify-center mb-4">
                                <Activity className="w-8 h-8 text-[#6C757D]" />
                            </div>
                            <p className="text-[#6C757D]">
                                {activeTab === 'upload'
                                    ? 'Upload an image to see AI analysis results'
                                    : 'Start camera and capture to see AI analysis results'}
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* AI Status Badge */}
                            {results.detection?.using_real_ai !== undefined && (
                                <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${results.detection.using_real_ai
                                        ? 'bg-[#D8F3DC] text-[#1B4332]'
                                        : 'bg-[#E9ECEF] text-[#6C757D]'
                                    }`}>
                                    <span className={`w-2 h-2 rounded-full ${results.detection.using_real_ai ? 'bg-[#2D6A4F]' : 'bg-[#ADB5BD]'
                                        }`} />
                                    {results.detection.using_real_ai ? 'Real YOLOv8 AI' : 'Mock Detection'}
                                </div>
                            )}

                            {results.detection && (
                                <div>
                                    <h4 className="text-sm font-medium text-[#6C757D] mb-3">Animal Detection</h4>
                                    <div className="bg-[#D8F3DC] rounded-xl p-4">
                                        <p className="text-[#1B4332] font-medium">
                                            {results.detection.total_detected} animal(s) detected
                                        </p>
                                        {results.detection.processing_time_ms && (
                                            <p className="text-xs text-[#6C757D] mt-1">
                                                Processed in {results.detection.processing_time_ms}ms
                                            </p>
                                        )}
                                        {results.detection.detected_animals?.length > 0 && (
                                            <div className="mt-3 space-y-2">
                                                {results.detection.detected_animals.slice(0, 3).map((animal: any, i: number) => (
                                                    <div key={i} className="flex items-center justify-between text-sm bg-white/50 rounded-lg px-3 py-2">
                                                        <span className="capitalize text-[#1B4332]">{animal.species}</span>
                                                        <span className="text-[#6C757D]">{(animal.confidence * 100).toFixed(1)}%</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {results.health && (
                                <div>
                                    <h4 className="text-sm font-medium text-[#6C757D] mb-3">Health Assessment</h4>
                                    <div className={`rounded-xl p-4 ${results.health.status === 'healthy' ? 'bg-[#D8F3DC]' :
                                        results.health.status === 'critical' ? 'bg-[#F8D7DA]' : 'bg-[#FFF3CD]'
                                        }`}>
                                        <div className="flex items-center gap-3 mb-4">
                                            {getHealthStatusIcon(results.health.status)}
                                            <div>
                                                <p className="text-[#1B4332] font-semibold capitalize">
                                                    {results.health.status?.replace('_', ' ')}
                                                </p>
                                                <p className="text-sm text-[#6C757D]">
                                                    {(results.health.confidence * 100).toFixed(1)}% confidence
                                                </p>
                                            </div>
                                        </div>

                                        {/* Health Scores */}
                                        {results.health.posture_score && (
                                            <div className="grid grid-cols-2 gap-2 mt-3">
                                                <div className="bg-white/50 rounded-lg px-3 py-2">
                                                    <p className="text-xs text-[#6C757D]">Posture</p>
                                                    <p className="text-sm font-medium text-[#1B4332]">{(results.health.posture_score * 100).toFixed(0)}%</p>
                                                </div>
                                                <div className="bg-white/50 rounded-lg px-3 py-2">
                                                    <p className="text-xs text-[#6C757D]">Coat</p>
                                                    <p className="text-sm font-medium text-[#1B4332]">{(results.health.coat_condition_score * 100).toFixed(0)}%</p>
                                                </div>
                                                <div className="bg-white/50 rounded-lg px-3 py-2">
                                                    <p className="text-xs text-[#6C757D]">Mobility</p>
                                                    <p className="text-sm font-medium text-[#1B4332]">{(results.health.mobility_score * 100).toFixed(0)}%</p>
                                                </div>
                                                <div className="bg-white/50 rounded-lg px-3 py-2">
                                                    <p className="text-xs text-[#6C757D]">Alertness</p>
                                                    <p className="text-sm font-medium text-[#1B4332]">{(results.health.alertness_score * 100).toFixed(0)}%</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {results.attendance_marked && (
                                <div className="flex items-center gap-2 p-3 rounded-xl bg-[#D8F3DC] border border-[#74C69D]">
                                    <CheckCircle className="w-5 h-5 text-[#2D6A4F]" />
                                    <span className="text-[#1B4332] text-sm">Attendance marked for today</span>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Instructions */}
            <div className="bg-white rounded-2xl p-6 border border-[#D8F3DC] shadow-card">
                <h3 className="text-lg font-semibold text-[#1B4332] mb-4">How It Works</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                        <div className="w-12 h-12 rounded-xl bg-[#2D6A4F] flex items-center justify-center mx-auto mb-3">
                            <span className="text-xl font-bold text-white">1</span>
                        </div>
                        <h4 className="font-medium text-[#1B4332] mb-1">
                            {activeTab === 'upload' ? 'Upload Image' : 'Start Camera'}
                        </h4>
                        <p className="text-sm text-[#6C757D]">
                            {activeTab === 'upload'
                                ? 'Drop or select a livestock image'
                                : 'Allow camera access to begin'}
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="w-12 h-12 rounded-xl bg-[#2D6A4F] flex items-center justify-center mx-auto mb-3">
                            <span className="text-xl font-bold text-white">2</span>
                        </div>
                        <h4 className="font-medium text-[#1B4332] mb-1">AI Analysis</h4>
                        <p className="text-sm text-[#6C757D]">YOLOv8 detects animals & assesses health</p>
                    </div>
                    <div className="text-center">
                        <div className="w-12 h-12 rounded-xl bg-[#FFB703] flex items-center justify-center mx-auto mb-3">
                            <span className="text-xl font-bold text-[#1B4332]">3</span>
                        </div>
                        <h4 className="font-medium text-[#1B4332] mb-1">Get Results</h4>
                        <p className="text-sm text-[#6C757D]">View health status, scores & recommendations</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
