'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { Camera, CameraOff, Scan, RefreshCw, Download } from 'lucide-react';

interface LiveCameraProps {
    onCapture: (file: File) => void;
    isAnalyzing: boolean;
}

export default function LiveCamera({ onCapture, isAnalyzing }: LiveCameraProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const streamRef = useRef<MediaStream | null>(null);

    const [isActive, setIsActive] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment');
    const [lastCapture, setLastCapture] = useState<string | null>(null);

    // Start camera
    const startCamera = useCallback(async () => {
        try {
            setError(null);

            // Stop any existing stream
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }

            const constraints: MediaStreamConstraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            streamRef.current = stream;

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                await videoRef.current.play();
            }

            setIsActive(true);
        } catch (err: any) {
            console.error('Camera error:', err);
            if (err.name === 'NotAllowedError') {
                setError('Camera access denied. Please allow camera access in your browser settings.');
            } else if (err.name === 'NotFoundError') {
                setError('No camera found. Please connect a camera and try again.');
            } else {
                setError(`Camera error: ${err.message}`);
            }
            setIsActive(false);
        }
    }, [facingMode]);

    // Stop camera
    const stopCamera = useCallback(() => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }
        if (videoRef.current) {
            videoRef.current.srcObject = null;
        }
        setIsActive(false);
    }, []);

    // Switch between front and back camera
    const switchCamera = useCallback(() => {
        setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
    }, []);

    // Restart camera when facing mode changes
    useEffect(() => {
        if (isActive) {
            startCamera();
        }
    }, [facingMode]);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, []);

    // Capture frame
    const captureFrame = useCallback(() => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        if (!ctx) return;

        // Set canvas size to video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw video frame to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert to blob and create file
        canvas.toBlob((blob) => {
            if (blob) {
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                const file = new File([blob], `capture_${timestamp}.jpg`, { type: 'image/jpeg' });

                // Store preview
                setLastCapture(canvas.toDataURL('image/jpeg'));

                // Send to parent
                onCapture(file);
            }
        }, 'image/jpeg', 0.9);
    }, [onCapture]);

    // Download last capture
    const downloadCapture = useCallback(() => {
        if (!lastCapture) return;

        const link = document.createElement('a');
        link.download = `livestock_capture_${Date.now()}.jpg`;
        link.href = lastCapture;
        link.click();
    }, [lastCapture]);

    return (
        <div className="space-y-4">
            {/* Camera Preview */}
            <div className="relative aspect-video bg-[#1B4332] rounded-2xl overflow-hidden">
                {isActive ? (
                    <>
                        <video
                            ref={videoRef}
                            autoPlay
                            playsInline
                            muted
                            className="w-full h-full object-cover"
                        />

                        {/* Overlay controls */}
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3">
                            <button
                                onClick={switchCamera}
                                className="p-3 rounded-full bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 transition-colors"
                                title="Switch Camera"
                            >
                                <RefreshCw className="w-5 h-5" />
                            </button>

                            <button
                                onClick={captureFrame}
                                disabled={isAnalyzing}
                                className="p-4 rounded-full bg-[#FFB703] text-[#1B4332] hover:bg-[#FFA000] transition-colors disabled:opacity-50 shadow-lg"
                                title="Capture & Analyze"
                            >
                                <Scan className="w-6 h-6" />
                            </button>

                            <button
                                onClick={stopCamera}
                                className="p-3 rounded-full bg-red-500/80 backdrop-blur-sm text-white hover:bg-red-600 transition-colors"
                                title="Stop Camera"
                            >
                                <CameraOff className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Analyzing indicator */}
                        {isAnalyzing && (
                            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                                <div className="text-center text-white">
                                    <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                                    <p className="font-medium">Analyzing with AI...</p>
                                </div>
                            </div>
                        )}
                    </>
                ) : (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
                        <Camera className="w-16 h-16 mb-4 opacity-50" />
                        {error ? (
                            <div className="text-center px-4">
                                <p className="text-red-400 mb-3">{error}</p>
                                <button
                                    onClick={startCamera}
                                    className="px-4 py-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
                                >
                                    Try Again
                                </button>
                            </div>
                        ) : (
                            <>
                                <p className="text-lg font-medium mb-2">Live Camera</p>
                                <p className="text-sm opacity-70 mb-4">Point at livestock for real-time analysis</p>
                                <button
                                    onClick={startCamera}
                                    className="px-6 py-3 rounded-xl bg-[#2D6A4F] hover:bg-[#40916C] transition-colors font-medium flex items-center gap-2"
                                >
                                    <Camera className="w-5 h-5" />
                                    Start Camera
                                </button>
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Hidden canvas for capture */}
            <canvas ref={canvasRef} className="hidden" />

            {/* Last capture preview */}
            {lastCapture && (
                <div className="flex items-center gap-4 bg-[#D8F3DC] rounded-xl p-3">
                    <img
                        src={lastCapture}
                        alt="Last capture"
                        className="w-20 h-14 object-cover rounded-lg"
                    />
                    <div className="flex-1">
                        <p className="text-sm font-medium text-[#1B4332]">Last Capture</p>
                        <p className="text-xs text-[#6C757D]">Ready for analysis</p>
                    </div>
                    <button
                        onClick={downloadCapture}
                        className="p-2 rounded-lg bg-white text-[#1B4332] hover:bg-[#B7E4C7] transition-colors"
                        title="Download"
                    >
                        <Download className="w-5 h-5" />
                    </button>
                </div>
            )}

            {/* Instructions */}
            <div className="grid grid-cols-3 gap-3 text-center text-sm">
                <div className="bg-white rounded-xl p-3 border border-[#D8F3DC]">
                    <div className="w-8 h-8 rounded-lg bg-[#2D6A4F] text-white flex items-center justify-center mx-auto mb-2 text-xs font-bold">1</div>
                    <p className="text-[#6C757D]">Start Camera</p>
                </div>
                <div className="bg-white rounded-xl p-3 border border-[#D8F3DC]">
                    <div className="w-8 h-8 rounded-lg bg-[#2D6A4F] text-white flex items-center justify-center mx-auto mb-2 text-xs font-bold">2</div>
                    <p className="text-[#6C757D]">Point at Animal</p>
                </div>
                <div className="bg-white rounded-xl p-3 border border-[#D8F3DC]">
                    <div className="w-8 h-8 rounded-lg bg-[#FFB703] text-[#1B4332] flex items-center justify-center mx-auto mb-2 text-xs font-bold">3</div>
                    <p className="text-[#6C757D]">Tap to Analyze</p>
                </div>
            </div>
        </div>
    );
}
