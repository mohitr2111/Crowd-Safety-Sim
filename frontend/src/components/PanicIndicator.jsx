import React from 'react';

const TRIGGER_TYPES = [
    { id: 'explosion', name: 'Explosion', icon: '💥', color: 'red', severity: 0.9 },
    { id: 'gate_malfunction', name: 'Gate Malfunction', icon: '🚧', color: 'amber', severity: 0.7 },
    { id: 'false_alarm', name: 'False Alarm', icon: '📢', color: 'yellow', severity: 0.6 },
    { id: 'weather', name: 'Weather Change', icon: '🌧️', color: 'blue', severity: 0.4 },
    { id: 'infra_failure', name: 'Infrastructure', icon: '🏗️', color: 'orange', severity: 0.85 },
    { id: 'panic_cascade', name: 'Panic Cascade', icon: '😱', color: 'purple', severity: 0.65 }
];

const PanicIndicator = ({
    panicState = {},
    activeTrigger = null,
    onTriggerPanic,
    zones = [],
    disabled = false
}) => {
    const maxPanic = panicState.max_panic || 0;
    const nodePanicLevels = panicState.node_panic_levels || {};
    const activeTriggerCount = panicState.active_trigger_count || 0;

    const getPanicColor = (level) => {
        if (level > 0.7) return 'bg-red-500';
        if (level > 0.4) return 'bg-amber-500';
        if (level > 0.2) return 'bg-yellow-500';
        return 'bg-emerald-500';
    };

    const getPanicLabel = (level) => {
        if (level > 0.7) return 'CRITICAL';
        if (level > 0.4) return 'HIGH';
        if (level > 0.2) return 'MODERATE';
        return 'CALM';
    };

    return (
        <div className="glass-card p-4 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-slate-200">Panic State</h3>
                <span className="text-xs px-2 py-1 bg-purple-500/20 text-purple-400 rounded-full">
                    Phase 2.2
                </span>
            </div>

            {/* Overall Panic Level */}
            <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700">
                <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-slate-400">Overall Panic Level</span>
                    <span className={`text-sm font-bold ${maxPanic > 0.7 ? 'text-red-400' :
                            maxPanic > 0.4 ? 'text-amber-400' :
                                maxPanic > 0.2 ? 'text-yellow-400' : 'text-emerald-400'
                        }`}>
                        {getPanicLabel(maxPanic)}
                    </span>
                </div>

                <div className="relative h-3 bg-slate-700 rounded-full overflow-hidden">
                    <div
                        className={`absolute left-0 top-0 h-full transition-all duration-500 ${getPanicColor(maxPanic)}`}
                        style={{ width: `${maxPanic * 100}%` }}
                    />
                </div>

                <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>Calm</span>
                    <span>{(maxPanic * 100).toFixed(0)}%</span>
                    <span>Critical</span>
                </div>
            </div>

            {/* Active Triggers */}
            {activeTriggerCount > 0 && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3">
                    <div className="flex items-center gap-2 text-red-400">
                        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                        <span className="text-sm font-medium">
                            {activeTriggerCount} Active Trigger{activeTriggerCount > 1 ? 's' : ''}
                        </span>
                    </div>
                    {activeTrigger && (
                        <div className="mt-2 text-xs text-red-300">
                            Type: {activeTrigger.type} | Severity: {(activeTrigger.severity * 100).toFixed(0)}%
                        </div>
                    )}
                </div>
            )}

            {/* Panic by Zone */}
            {Object.keys(nodePanicLevels).length > 0 && (
                <div className="space-y-2">
                    <h4 className="text-sm font-medium text-slate-300">Panic by Zone</h4>
                    <div className="max-h-32 overflow-y-auto space-y-1">
                        {Object.entries(nodePanicLevels)
                            .sort((a, b) => b[1] - a[1])
                            .slice(0, 5)
                            .map(([nodeId, level]) => (
                                <div key={nodeId} className="flex items-center gap-2 text-xs">
                                    <div className={`w-2 h-2 rounded-full ${getPanicColor(level)}`}></div>
                                    <span className="text-slate-400 truncate flex-1">{nodeId}</span>
                                    <span className="text-slate-300">{(level * 100).toFixed(0)}%</span>
                                </div>
                            ))}
                    </div>
                </div>
            )}

            {/* Trigger Buttons */}
            <div className="space-y-2">
                <h4 className="text-sm font-medium text-slate-300">Simulate Emergency</h4>
                <div className="grid grid-cols-3 gap-2">
                    {TRIGGER_TYPES.map(trigger => (
                        <button
                            key={trigger.id}
                            onClick={() => onTriggerPanic && onTriggerPanic(trigger.id, trigger.severity)}
                            disabled={disabled}
                            className={`p-2 rounded-lg border transition-all text-center ${disabled
                                    ? 'bg-slate-800/30 border-slate-800 opacity-50 cursor-not-allowed'
                                    : 'bg-slate-800/50 border-slate-700 hover:border-slate-600 hover:bg-slate-700/50'
                                }`}
                            title={trigger.name}
                        >
                            <div className="text-lg">{trigger.icon}</div>
                            <div className="text-xs text-slate-400 truncate">{trigger.name.split(' ')[0]}</div>
                        </button>
                    ))}
                </div>
                <p className="text-xs text-slate-500 text-center">
                    Click to trigger emergency event
                </p>
            </div>
        </div>
    );
};

export default PanicIndicator;
export { TRIGGER_TYPES };
