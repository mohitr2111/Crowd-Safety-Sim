import React, { useState, useRef } from 'react';
import { simulationApi } from '../api/simulationApi';

const PhotoToLayout = () => {
    const [uploadedImage, setUploadedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [detectionResult, setDetectionResult] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [venueType, setVenueType] = useState('stadium');
    const [venueName, setVenueName] = useState('');
    const [validationResult, setValidationResult] = useState(null);
    const [step, setStep] = useState(1); // 1: Upload, 2: Review, 3: Correct, 4: Finalize

    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setUploadedImage(file);
            const reader = new FileReader();
            reader.onload = (e) => setImagePreview(e.target.result);
            reader.readAsDataURL(file);
            setDetectionResult(null);
            setValidationResult(null);
            setStep(1);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            setUploadedImage(file);
            const reader = new FileReader();
            reader.onload = (e) => setImagePreview(e.target.result);
            reader.readAsDataURL(file);
        }
    };

    const processBlueprint = async () => {
        if (!uploadedImage) return;

        setIsProcessing(true);
        try {
            // Simulate API call with mock response
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Mock detection result
            const mockResult = {
                detection_id: `det_${Date.now()}`,
                elements: [
                    { element_id: 'zone_1', element_type: 'zone', label: 'Main Hall', capacity: 500 },
                    { element_id: 'zone_2', element_type: 'zone', label: 'North Wing', capacity: 300 },
                    { element_id: 'zone_3', element_type: 'zone', label: 'South Wing', capacity: 300 },
                    { element_id: 'entry_1', element_type: 'entry', label: 'Main Entry', capacity: 50 },
                    { element_id: 'entry_2', element_type: 'entry', label: 'Side Entry', capacity: 30 },
                    { element_id: 'exit_1', element_type: 'exit', label: 'Main Exit', capacity: 100 },
                    { element_id: 'exit_2', element_type: 'exit', label: 'Emergency Exit', capacity: 80 },
                    { element_id: 'corridor_1', element_type: 'corridor', label: 'Main Corridor', capacity: 200 },
                ],
                connections: [
                    { from_id: 'entry_1', to_id: 'zone_1' },
                    { from_id: 'entry_2', to_id: 'zone_2' },
                    { from_id: 'zone_1', to_id: 'corridor_1' },
                    { from_id: 'zone_2', to_id: 'corridor_1' },
                    { from_id: 'zone_3', to_id: 'corridor_1' },
                    { from_id: 'corridor_1', to_id: 'exit_1' },
                    { from_id: 'corridor_1', to_id: 'exit_2' },
                ],
                confidence: 0.85,
                requires_review: true
            };

            setDetectionResult(mockResult);
            setStep(2);
        } catch (error) {
            console.error('Processing failed:', error);
            alert('Failed to process blueprint');
        } finally {
            setIsProcessing(false);
        }
    };

    const validateGraph = async () => {
        if (!detectionResult) return;

        // Mock validation
        const mockValidation = {
            is_valid: true,
            errors: [],
            warnings: [
                'Exit capacity may be insufficient for estimated crowd size',
                'Consider adding emergency exits to South Wing'
            ],
            stats: {
                total_zones: 3,
                total_entries: 2,
                total_exits: 2,
                total_capacity: 1560
            }
        };

        setValidationResult(mockValidation);
        setStep(3);
    };

    const finalizeLayout = async () => {
        if (!venueName.trim()) {
            alert('Please enter a venue name');
            return;
        }

        setIsProcessing(true);
        try {
            await new Promise(resolve => setTimeout(resolve, 1500));
            setStep(4);
            alert(`Venue "${venueName}" created successfully! You can now use it in simulations.`);
        } catch (error) {
            console.error('Finalization failed:', error);
        } finally {
            setIsProcessing(false);
        }
    };

    const getElementIcon = (type) => {
        const icons = {
            zone: '🏛️',
            entry: '🚪',
            exit: '🚶',
            corridor: '🛤️',
            stage: '🎭',
            stairs: '🔺'
        };
        return icons[type] || '📍';
    };

    const getElementColor = (type) => {
        const colors = {
            zone: 'bg-blue-500/20 border-blue-500 text-blue-400',
            entry: 'bg-emerald-500/20 border-emerald-500 text-emerald-400',
            exit: 'bg-red-500/20 border-red-500 text-red-400',
            corridor: 'bg-amber-500/20 border-amber-500 text-amber-400'
        };
        return colors[type] || 'bg-slate-700 border-slate-600 text-slate-400';
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="text-center">
                <h1 className="text-3xl font-bold gradient-text mb-2">
                    Photo to Layout
                </h1>
                <p className="text-slate-400">
                    Upload a venue blueprint or floor plan to automatically generate a simulation layout
                </p>
            </div>

            {/* Progress Steps */}
            <div className="flex justify-center gap-2">
                {[1, 2, 3, 4].map((s) => (
                    <div key={s} className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= s
                                ? 'bg-blue-500 text-white'
                                : 'bg-slate-700 text-slate-400'
                            }`}>
                            {s}
                        </div>
                        {s < 4 && (
                            <div className={`w-12 h-1 ${step > s ? 'bg-blue-500' : 'bg-slate-700'}`} />
                        )}
                    </div>
                ))}
            </div>
            <div className="flex justify-center gap-8 text-xs text-slate-500">
                <span>Upload</span>
                <span>Review</span>
                <span>Correct</span>
                <span>Finalize</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left: Upload/Preview */}
                <div className="glass-card p-6 space-y-4">
                    <h3 className="text-lg font-bold text-slate-200">Blueprint Image</h3>

                    {!imagePreview ? (
                        <div
                            onDrop={handleDrop}
                            onDragOver={(e) => e.preventDefault()}
                            onClick={() => fileInputRef.current?.click()}
                            className="border-2 border-dashed border-slate-600 rounded-xl p-12 text-center cursor-pointer hover:border-blue-500 transition-all"
                        >
                            <div className="text-5xl mb-4">📐</div>
                            <p className="text-slate-400 mb-2">
                                Drop your blueprint image here
                            </p>
                            <p className="text-sm text-slate-500">
                                or click to browse
                            </p>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileSelect}
                                className="hidden"
                            />
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div className="relative rounded-xl overflow-hidden">
                                <img
                                    src={imagePreview}
                                    alt="Blueprint"
                                    className="w-full object-contain max-h-80"
                                />
                                {detectionResult && (
                                    <div className="absolute inset-0 bg-black/20">
                                        {/* Overlay for detected elements would go here */}
                                    </div>
                                )}
                            </div>

                            <div className="flex gap-2">
                                <select
                                    value={venueType}
                                    onChange={(e) => setVenueType(e.target.value)}
                                    className="input-modern flex-1"
                                >
                                    <option value="stadium">Stadium</option>
                                    <option value="mall">Shopping Mall</option>
                                    <option value="temple">Temple/Religious</option>
                                    <option value="station">Railway Station</option>
                                    <option value="arena">Concert Arena</option>
                                    <option value="festival">Festival Grounds</option>
                                </select>

                                <button
                                    onClick={() => {
                                        setImagePreview(null);
                                        setUploadedImage(null);
                                        setDetectionResult(null);
                                        setValidationResult(null);
                                        setStep(1);
                                    }}
                                    className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600"
                                >
                                    Clear
                                </button>
                            </div>

                            {step === 1 && (
                                <button
                                    onClick={processBlueprint}
                                    disabled={isProcessing}
                                    className="w-full btn-primary py-3 disabled:opacity-50"
                                >
                                    {isProcessing ? 'Processing...' : 'Analyze Blueprint'}
                                </button>
                            )}
                        </div>
                    )}
                </div>

                {/* Right: Detection Results */}
                <div className="glass-card p-6 space-y-4">
                    <h3 className="text-lg font-bold text-slate-200">Detected Elements</h3>

                    {!detectionResult ? (
                        <div className="h-64 flex items-center justify-center text-slate-500">
                            <div className="text-center">
                                <div className="text-4xl mb-2">🔍</div>
                                <p>Upload and analyze a blueprint to see detected elements</p>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {/* Confidence */}
                            <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                                <span className="text-slate-400">Detection Confidence</span>
                                <span className={`font-bold ${detectionResult.confidence > 0.8 ? 'text-emerald-400' :
                                        detectionResult.confidence > 0.6 ? 'text-amber-400' : 'text-red-400'
                                    }`}>
                                    {(detectionResult.confidence * 100).toFixed(0)}%
                                </span>
                            </div>

                            {/* Elements List */}
                            <div className="max-h-48 overflow-y-auto space-y-2">
                                {detectionResult.elements.map((el) => (
                                    <div
                                        key={el.element_id}
                                        className={`flex items-center justify-between p-2 rounded-lg border ${getElementColor(el.element_type)}`}
                                    >
                                        <div className="flex items-center gap-2">
                                            <span>{getElementIcon(el.element_type)}</span>
                                            <span className="font-medium">{el.label}</span>
                                        </div>
                                        <span className="text-xs opacity-70">
                                            Cap: {el.capacity}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {/* Connections */}
                            <div className="p-3 bg-slate-800/50 rounded-lg">
                                <div className="text-sm text-slate-400 mb-2">
                                    Connections: {detectionResult.connections.length}
                                </div>
                                <div className="text-xs text-slate-500">
                                    Graph structure detected between zones
                                </div>
                            </div>

                            {step === 2 && (
                                <button
                                    onClick={validateGraph}
                                    className="w-full btn-primary py-3"
                                >
                                    Validate Layout
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Validation & Finalization */}
            {validationResult && (
                <div className="glass-card p-6 space-y-4">
                    <h3 className="text-lg font-bold text-slate-200">Validation Results</h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="stat-card">
                            <div className="text-xs text-slate-500">Zones</div>
                            <div className="text-xl font-bold text-blue-400">{validationResult.stats.total_zones}</div>
                        </div>
                        <div className="stat-card">
                            <div className="text-xs text-slate-500">Entries</div>
                            <div className="text-xl font-bold text-emerald-400">{validationResult.stats.total_entries}</div>
                        </div>
                        <div className="stat-card">
                            <div className="text-xs text-slate-500">Exits</div>
                            <div className="text-xl font-bold text-red-400">{validationResult.stats.total_exits}</div>
                        </div>
                        <div className="stat-card">
                            <div className="text-xs text-slate-500">Total Capacity</div>
                            <div className="text-xl font-bold text-amber-400">{validationResult.stats.total_capacity}</div>
                        </div>
                    </div>

                    {validationResult.warnings.length > 0 && (
                        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
                            <h4 className="font-medium text-amber-400 mb-2">Warnings</h4>
                            <ul className="text-sm text-amber-300/80 space-y-1">
                                {validationResult.warnings.map((w, i) => (
                                    <li key={i}>• {w}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {validationResult.is_valid && (
                        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4">
                            <h4 className="font-medium text-emerald-400 mb-3">Ready to Finalize</h4>
                            <div className="flex gap-3">
                                <input
                                    type="text"
                                    value={venueName}
                                    onChange={(e) => setVenueName(e.target.value)}
                                    placeholder="Enter venue name..."
                                    className="input-modern flex-1"
                                />
                                <button
                                    onClick={finalizeLayout}
                                    disabled={isProcessing || !venueName.trim()}
                                    className="px-6 py-2 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-600 disabled:opacity-50"
                                >
                                    {isProcessing ? 'Creating...' : 'Create Venue'}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Success State */}
            {step === 4 && (
                <div className="glass-card p-8 text-center">
                    <div className="text-6xl mb-4">🎉</div>
                    <h3 className="text-2xl font-bold text-emerald-400 mb-2">
                        Venue Created Successfully!
                    </h3>
                    <p className="text-slate-400 mb-6">
                        "{venueName}" is now available in your simulation scenarios.
                    </p>
                    <button
                        onClick={() => {
                            setStep(1);
                            setImagePreview(null);
                            setUploadedImage(null);
                            setDetectionResult(null);
                            setValidationResult(null);
                            setVenueName('');
                        }}
                        className="btn-primary px-8 py-3"
                    >
                        Create Another Venue
                    </button>
                </div>
            )}

            {/* Help Text */}
            <div className="text-center text-sm text-slate-500">
                <p>
                    Supported formats: PNG, JPG, PDF • Maximum file size: 10MB
                </p>
                <p className="mt-1">
                    For best results, use high-resolution floor plans with clear zone boundaries
                </p>
            </div>
        </div>
    );
};

export default PhotoToLayout;
