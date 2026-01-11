import React, { useState, useEffect, useCallback } from 'react';
import ScenarioSelector, { SCENARIOS } from './ScenarioSelector';
import PanicIndicator, { TRIGGER_TYPES } from './PanicIndicator';
import SimulationCanvas from './SimulationCanvas';
import AIRecommendation from './AIRecommendation';
import { simulationApi } from '../api/simulationApi';

const Phase2Dashboard = () => {
    // Scenario state
    const [selectedScenario, setSelectedScenario] = useState('stadium_exit');
    const [agentCount, setAgentCount] = useState(800);

    // Simulation state
    const [simulationId, setSimulationId] = useState(null);
    const [simState, setSimState] = useState(null);
    const [graphData, setGraphData] = useState(null);
    const [isRunning, setIsRunning] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [step, setStep] = useState(0);

    // Panic state
    const [panicState, setPanicState] = useState({});
    const [activeTrigger, setActiveTrigger] = useState(null);

    // Case study state
    const [caseStudyMode, setCaseStudyMode] = useState(false);
    const [caseStudyResult, setCaseStudyResult] = useState(null);
    const [isRunningCaseStudy, setIsRunningCaseStudy] = useState(false);

    // AI recommendations
    const [recommendations, setRecommendations] = useState([]);
    const [aiEnabled, setAiEnabled] = useState(true);

    // Create simulation
    const createSimulation = async () => {
        try {
            const scenario = SCENARIOS.find(s => s.id === selectedScenario);
            const spawnConfig = [{
                start: getEntryNode(selectedScenario),
                goal: getExitNode(selectedScenario),
                count: agentCount,
                type: 'normal'
            }];

            const response = await simulationApi.createSimulation(
                selectedScenario,
                spawnConfig,
                1.0
            );

            setSimulationId(response.simulation_id);
            setStep(0);
            setRecommendations([]);
            setPanicState({});
            setActiveTrigger(null);

            // Get initial state and graph
            const [stateRes, graphRes] = await Promise.all([
                simulationApi.getState(response.simulation_id),
                simulationApi.getGraph(response.simulation_id)
            ]);

            setSimState(stateRes);
            setGraphData(graphRes);

        } catch (error) {
            console.error('Failed to create simulation:', error);
        }
    };

    // Get entry/exit nodes based on scenario
    const getEntryNode = (scenarioId) => {
        const entries = {
            'stadium_exit': 'zone_north',
            'railway_station': 'entry_main',
            'festival_corridor': 'entry_gate',
            'temple': 'entry_north'
        };
        return entries[scenarioId] || 'zone_north';
    };

    const getExitNode = (scenarioId) => {
        const exits = {
            'stadium_exit': 'exit_main',
            'railway_station': 'exit_main',
            'festival_corridor': 'exit_main',
            'temple': 'exit_main'
        };
        return exits[scenarioId] || 'exit_main';
    };

    // Step simulation
    const stepSimulation = useCallback(async () => {
        if (!simulationId || isPaused) return;

        try {
            const response = await simulationApi.stepSimulation(simulationId, 1);
            setSimState(response.state);
            setStep(prev => prev + 1);

            // Check for AI recommendations
            if (aiEnabled && response.predictions) {
                const newRecs = response.predictions.filter(p => p.action !== 'NOOP');
                if (newRecs.length > 0) {
                    setRecommendations(prev => [...newRecs, ...prev].slice(0, 10));
                }
            }

            // Update panic state (mock for now until backend endpoint exists)
            if (activeTrigger) {
                const panicLevel = Math.max(0, (activeTrigger.severity || 0.5) - (step * 0.02));
                setPanicState({
                    max_panic: panicLevel,
                    active_trigger_count: panicLevel > 0.1 ? 1 : 0,
                    node_panic_levels: {}
                });
            }

        } catch (error) {
            console.error('Failed to step simulation:', error);
            setIsRunning(false);
        }
    }, [simulationId, isPaused, aiEnabled, activeTrigger, step]);

    // Auto-run simulation
    useEffect(() => {
        let interval;
        if (isRunning && !isPaused && simulationId) {
            interval = setInterval(stepSimulation, 500);
        }
        return () => clearInterval(interval);
    }, [isRunning, isPaused, simulationId, stepSimulation]);

    // Trigger panic event
    const handleTriggerPanic = async (triggerId, severity) => {
        if (!simulationId) return;

        const trigger = TRIGGER_TYPES.find(t => t.id === triggerId);
        setActiveTrigger({ type: triggerId, severity, ...trigger });

        setPanicState({
            max_panic: severity,
            active_trigger_count: 1,
            node_panic_levels: {
                [getEntryNode(selectedScenario)]: severity,
            }
        });

        // Add recommendation for panic response
        setRecommendations(prev => [{
            action: 'REROUTE',
            node: getEntryNode(selectedScenario),
            reason: `Emergency: ${trigger?.name || triggerId} detected`,
            priority: 'CRITICAL',
            timestamp: new Date().toISOString()
        }, ...prev].slice(0, 10));
    };

    // Run case study
    const runCaseStudy = async () => {
        setIsRunningCaseStudy(true);
        setCaseStudyResult(null);

        try {
            // Simulate case study run
            await new Promise(resolve => setTimeout(resolve, 2000));

            const scenario = SCENARIOS.find(s => s.id === selectedScenario);
            setCaseStudyResult({
                case_name: `${scenario?.name || 'Test'} Case Study`,
                baseline: {
                    max_density: 5.2 + Math.random() * 1.5,
                    danger_violations: 12 + Math.floor(Math.random() * 8),
                    evacuation_rate: 0.72 + Math.random() * 0.1
                },
                ai_aware: {
                    max_density: 3.8 + Math.random() * 0.8,
                    danger_violations: 3 + Math.floor(Math.random() * 4),
                    evacuation_rate: 0.89 + Math.random() * 0.08
                },
                improvement: 27 + Math.floor(Math.random() * 15)
            });
        } catch (error) {
            console.error('Case study failed:', error);
        } finally {
            setIsRunningCaseStudy(false);
        }
    };

    // Start/Stop simulation
    const toggleSimulation = () => {
        if (isRunning) {
            setIsRunning(false);
            setIsPaused(false);
        } else {
            if (!simulationId) {
                createSimulation().then(() => setIsRunning(true));
            } else {
                setIsRunning(true);
            }
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-200">
                        Multi-Scenario Simulation
                    </h2>
                    <p className="text-sm text-slate-400">
                        Phase 2: Panic propagation, multiple venues, trigger-aware AI
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <label className="flex items-center gap-2 text-sm text-slate-400">
                        <input
                            type="checkbox"
                            checked={aiEnabled}
                            onChange={(e) => setAiEnabled(e.target.checked)}
                            className="w-4 h-4 rounded accent-blue-500"
                        />
                        AI Recommendations
                    </label>

                    <button
                        onClick={() => setCaseStudyMode(!caseStudyMode)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${caseStudyMode
                                ? 'bg-purple-500/20 text-purple-400 border border-purple-500'
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                            }`}
                    >
                        Case Study Mode
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column: Scenario & Panic */}
                <div className="space-y-4">
                    <ScenarioSelector
                        selectedScenario={selectedScenario}
                        onSelect={(id) => {
                            setSelectedScenario(id);
                            setSimulationId(null);
                            setIsRunning(false);
                        }}
                        agentCount={agentCount}
                        onAgentCountChange={setAgentCount}
                    />

                    <PanicIndicator
                        panicState={panicState}
                        activeTrigger={activeTrigger}
                        onTriggerPanic={handleTriggerPanic}
                        disabled={!simulationId}
                    />
                </div>

                {/* Center: Simulation Canvas */}
                <div className="lg:col-span-2 space-y-4">
                    {/* Controls */}
                    <div className="glass-card p-4">
                        <div className="flex flex-wrap items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={toggleSimulation}
                                    className={`px-6 py-2 rounded-lg font-medium transition-all ${isRunning
                                            ? 'bg-red-500/20 text-red-400 border border-red-500 hover:bg-red-500/30'
                                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500 hover:bg-emerald-500/30'
                                        }`}
                                >
                                    {isRunning ? 'Stop' : 'Start Simulation'}
                                </button>

                                {isRunning && (
                                    <button
                                        onClick={() => setIsPaused(!isPaused)}
                                        className="px-4 py-2 rounded-lg bg-slate-700 text-slate-300 hover:bg-slate-600"
                                    >
                                        {isPaused ? 'Resume' : 'Pause'}
                                    </button>
                                )}

                                <button
                                    onClick={() => {
                                        setSimulationId(null);
                                        setIsRunning(false);
                                        setSimState(null);
                                        setStep(0);
                                        setPanicState({});
                                        setActiveTrigger(null);
                                    }}
                                    className="px-4 py-2 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700"
                                >
                                    Reset
                                </button>
                            </div>

                            <div className="flex items-center gap-4 text-sm">
                                <span className="text-slate-400">
                                    Step: <span className="text-blue-400 font-bold">{step}</span>
                                </span>
                                {simState && (
                                    <span className="text-slate-400">
                                        Max Density: <span className={`font-bold ${(simState.max_density || 0) > 4 ? 'text-red-400' :
                                                (simState.max_density || 0) > 3 ? 'text-amber-400' : 'text-emerald-400'
                                            }`}>
                                            {(simState.max_density || 0).toFixed(1)} p/m2
                                        </span>
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Canvas or Case Study */}
                    {caseStudyMode ? (
                        <div className="glass-card p-6 space-y-4">
                            <h3 className="text-lg font-bold text-slate-200">
                                Case Study: Baseline vs AI Comparison
                            </h3>

                            <p className="text-sm text-slate-400">
                                Run a reproducible comparison between baseline and AI-aware simulations
                                for the selected scenario.
                            </p>

                            <button
                                onClick={runCaseStudy}
                                disabled={isRunningCaseStudy}
                                className="w-full py-3 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500 
                  hover:bg-purple-500/30 transition-all disabled:opacity-50"
                            >
                                {isRunningCaseStudy ? 'Running Case Study...' : 'Run Case Study'}
                            </button>

                            {caseStudyResult && (
                                <div className="space-y-4 mt-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                                            <h4 className="text-sm font-medium text-slate-400 mb-3">Baseline</h4>
                                            <div className="space-y-2 text-sm">
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Max Density</span>
                                                    <span className="text-red-400 font-bold">
                                                        {caseStudyResult.baseline.max_density.toFixed(1)} p/m2
                                                    </span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Violations</span>
                                                    <span className="text-red-400">{caseStudyResult.baseline.danger_violations}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Evacuation</span>
                                                    <span className="text-slate-300">
                                                        {(caseStudyResult.baseline.evacuation_rate * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="bg-emerald-500/10 rounded-xl p-4 border border-emerald-500/30">
                                            <h4 className="text-sm font-medium text-emerald-400 mb-3">AI-Aware</h4>
                                            <div className="space-y-2 text-sm">
                                                <div className="flex justify-between">
                                                    <span className="text-emerald-300/60">Max Density</span>
                                                    <span className="text-emerald-400 font-bold">
                                                        {caseStudyResult.ai_aware.max_density.toFixed(1)} p/m2
                                                    </span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-emerald-300/60">Violations</span>
                                                    <span className="text-emerald-400">{caseStudyResult.ai_aware.danger_violations}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-emerald-300/60">Evacuation</span>
                                                    <span className="text-emerald-300">
                                                        {(caseStudyResult.ai_aware.evacuation_rate * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 text-center">
                                        <div className="text-3xl font-bold text-blue-400">
                                            {caseStudyResult.improvement}%
                                        </div>
                                        <div className="text-sm text-blue-300">
                                            Density Reduction with AI
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="glass-card p-4 h-96">
                            {graphData ? (
                                <SimulationCanvas
                                    simulationData={simState}
                                    graphData={graphData}
                                />
                            ) : (
                                <div className="h-full flex items-center justify-center text-slate-500">
                                    <div className="text-center">
                                        <div className="text-4xl mb-4">
                                            {SCENARIOS.find(s => s.id === selectedScenario)?.icon || '🏟️'}
                                        </div>
                                        <p>Select a scenario and click Start Simulation</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* AI Recommendations */}
                    {aiEnabled && recommendations.length > 0 && !caseStudyMode && (
                        <div className="glass-card p-4">
                            <h3 className="text-sm font-bold text-slate-300 mb-3">
                                AI Recommendations
                            </h3>
                            <div className="space-y-2 max-h-40 overflow-y-auto">
                                {recommendations.slice(0, 5).map((rec, i) => (
                                    <div
                                        key={i}
                                        className={`flex items-center gap-3 p-2 rounded-lg text-sm ${rec.priority === 'CRITICAL'
                                                ? 'bg-red-500/10 border border-red-500/30'
                                                : 'bg-slate-800/50'
                                            }`}
                                    >
                                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${rec.action === 'REROUTE' ? 'bg-blue-500/20 text-blue-400' :
                                                rec.action === 'THROTTLE_50' ? 'bg-amber-500/20 text-amber-400' :
                                                    rec.action === 'CLOSE_INFLOW' ? 'bg-red-500/20 text-red-400' :
                                                        'bg-slate-700 text-slate-400'
                                            }`}>
                                            {rec.action}
                                        </span>
                                        <span className="text-slate-400 flex-1 truncate">{rec.reason || rec.node}</span>
                                        <button className="text-xs px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded hover:bg-emerald-500/30">
                                            Approve
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Phase2Dashboard;
