import React, { useState } from 'react';

const SCENARIOS = [
    {
        id: 'stadium_exit',
        name: 'Stadium Exit',
        description: 'Stadium evacuation after event',
        agentRange: [600, 1200],
        bottlenecks: ['Concourse', 'Main Exit'],
        icon: '🏟️',
        dangerThreshold: 4.0
    },
    {
        id: 'railway_station',
        name: 'Railway Platform',
        description: 'Station during peak hours',
        agentRange: [300, 600],
        bottlenecks: ['Foot-over-bridge', 'Platform 2'],
        icon: '🚂',
        dangerThreshold: 3.5
    },
    {
        id: 'festival_corridor',
        name: 'Festival Corridor',
        description: 'Festival with linear stages',
        agentRange: [400, 800],
        bottlenecks: ['Stage corridors'],
        icon: '🎪',
        dangerThreshold: 4.0
    },
    {
        id: 'temple',
        name: 'Temple / Pilgrimage',
        description: 'Religious venue with sanctum',
        agentRange: [200, 500],
        bottlenecks: ['Sanctum queue', 'Inner corridor'],
        icon: '🛕',
        dangerThreshold: 3.0
    }
];

const ScenarioSelector = ({ selectedScenario, onSelect, agentCount, onAgentCountChange }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const currentScenario = SCENARIOS.find(s => s.id === selectedScenario) || SCENARIOS[0];

    return (
        <div className="glass-card p-4 space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-slate-200">Venue Scenario</h3>
                <span className="text-xs px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-full">
                    Phase 2
                </span>
            </div>

            {/* Scenario Cards Grid */}
            <div className="grid grid-cols-2 gap-3">
                {SCENARIOS.map(scenario => (
                    <button
                        key={scenario.id}
                        onClick={() => onSelect(scenario.id)}
                        className={`p-3 rounded-xl border transition-all text-left ${selectedScenario === scenario.id
                                ? 'bg-blue-500/20 border-blue-500 shadow-lg shadow-blue-500/20'
                                : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
                            }`}
                    >
                        <div className="flex items-start gap-2">
                            <span className="text-2xl">{scenario.icon}</span>
                            <div className="flex-1 min-w-0">
                                <div className="font-semibold text-slate-200 text-sm truncate">
                                    {scenario.name}
                                </div>
                                <div className="text-xs text-slate-500 truncate">
                                    {scenario.description}
                                </div>
                            </div>
                        </div>
                        {selectedScenario === scenario.id && (
                            <div className="mt-2 flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                <span className="text-xs text-emerald-400">Selected</span>
                            </div>
                        )}
                    </button>
                ))}
            </div>

            {/* Selected Scenario Details */}
            <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700">
                <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium text-slate-300">
                        {currentScenario.icon} {currentScenario.name}
                    </span>
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="text-xs text-blue-400 hover:text-blue-300"
                    >
                        {isExpanded ? 'Less' : 'More'}
                    </button>
                </div>

                {isExpanded && (
                    <div className="space-y-2 mb-3 text-xs">
                        <div className="flex justify-between text-slate-400">
                            <span>Agent Range:</span>
                            <span className="text-slate-300">
                                {currentScenario.agentRange[0]} - {currentScenario.agentRange[1]}
                            </span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                            <span>Danger Threshold:</span>
                            <span className="text-amber-400">
                                {currentScenario.dangerThreshold} p/m2
                            </span>
                        </div>
                        <div className="text-slate-400">
                            <span>Bottlenecks: </span>
                            <span className="text-red-400">
                                {currentScenario.bottlenecks.join(', ')}
                            </span>
                        </div>
                    </div>
                )}

                {/* Agent Count Slider */}
                <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Crowd Size</span>
                        <span className="text-blue-400 font-bold">{agentCount} agents</span>
                    </div>
                    <input
                        type="range"
                        min={currentScenario.agentRange[0]}
                        max={currentScenario.agentRange[1]}
                        value={Math.min(Math.max(agentCount, currentScenario.agentRange[0]), currentScenario.agentRange[1])}
                        onChange={(e) => onAgentCountChange(parseInt(e.target.value))}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    />
                    <div className="flex justify-between text-xs text-slate-500">
                        <span>{currentScenario.agentRange[0]}</span>
                        <span>{currentScenario.agentRange[1]}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ScenarioSelector;
export { SCENARIOS };
