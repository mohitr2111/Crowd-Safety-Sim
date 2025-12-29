// frontend/src/components/LiveMonitor.jsx

import React, { useState, useEffect, useRef } from 'react';
import SimulationCanvas from './SimulationCanvas';

const LiveMonitor = ({ simulationId, venueData, eventConfig, triggers, onReset }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [zoneData, setZoneData] = useState({});
  const [predictions, setPredictions] = useState([]);
  const [cascades, setCascades] = useState([]);
  const [interventions, setInterventions] = useState([]);
  const [activeTriggers, setActiveTriggers] = useState([]);
  const [appliedInterventions, setAppliedInterventions] = useState([]);
  const [aiActions, setAiActions] = useState([]); // ✅ AI action log
  const [recentActions, setRecentActions] = useState([]); // ✅ Recent actions
  const [stats, setStats] = useState({
    activeAgents: 0,
    reachedGoal: 0,
    maxDensity: 0,
    stampedes: 0
  });

  const intervalRef = useRef(null);

  // Fetch simulation data
  const fetchSimulationData = async () => {
    try {
      // Step simulation
      const stepResponse = await fetch(`http://localhost:8000/simulation/${simulationId}/step-custom`, {
        method: 'POST'
      });
      const stepData = await stepResponse.json();

      // Get predictions
      const predResponse = await fetch(`http://localhost:8000/simulation/${simulationId}/predictions`);
      const predData = await predResponse.json();

      // Get cascades
      const cascadeResponse = await fetch(`http://localhost:8000/simulation/${simulationId}/cascades`);
      const cascadeData = await cascadeResponse.json();

      // Get interventions
      const intResponse = await fetch(`http://localhost:8000/simulation/${simulationId}/interventions`);
      const intData = await intResponse.json();

      // Get applied interventions
      const appliedResponse = await fetch(`http://localhost:8000/simulation/${simulationId}/applied-interventions`);
      const appliedData = await appliedResponse.json();

      // ✅ Get AI actions log
      const actionsResponse = await fetch(`http://localhost:8000/simulation/${simulationId}/ai-actions`);
      const actionsData = await actionsResponse.json();

      // Update state
      setCurrentStep(stepData.current_step);
      setZoneData(stepData.zone_data || {});
      setPredictions(predData.predictions || []);
      setCascades(cascadeData.cascades || []);
      setInterventions(intData.interventions || []);
      setAppliedInterventions(appliedData.interventions || []);
      setAiActions(actionsData.actions || []); // ✅ Set AI actions

      // ✅ Update recent actions (last 5)
      if (stepData.ai_actions_taken && stepData.ai_actions_taken.length > 0) {
        setRecentActions(prev => [...stepData.ai_actions_taken, ...prev].slice(0, 5));
      }

      setStats({
        activeAgents: stepData.active_agents || 0,
        reachedGoal: stepData.reached_goal || 0,
        maxDensity: stepData.max_density || 0,
        stampedes: stepData.stampedes || 0
      });

      // Check active triggers
      const active = triggers.filter(t => 
        t.step <= stepData.current_step && 
        t.step + 100 > stepData.current_step
      );
      setActiveTriggers(active);

    } catch (error) {
      console.error('Failed to fetch simulation data:', error);
    }
  };

  // Auto-play simulation
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        fetchSimulationData();
      }, 1000); // Update every second
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, simulationId]);

  // Initial fetch
  useEffect(() => {
    if (simulationId) {
      fetchSimulationData();
    }
  }, [simulationId]);

  // Apply intervention
  const applyIntervention = async (interventionId) => {
    try {
      await fetch(`http://localhost:8000/simulation/${simulationId}/intervention`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intervention_id: interventionId })
      });
      
      alert('✅ Intervention applied successfully!');
      fetchSimulationData();
    } catch (error) {
      console.error('Failed to apply intervention:', error);
      alert('❌ Failed to apply intervention');
    }
  };

  // Format data for SimulationCanvas
  const getGraphData = () => {
    const nodes = venueData.zones.map(zone => {
      const zoneInfo = zoneData[zone.id] || {};
      return {
        id: zone.id,
        name: zone.name,
        label: zone.name,
        capacity: zone.capacity,
        area: zone.area,
        area_m2: zone.area,
        agent_count: zoneInfo.agent_count || 0,
        density: zoneInfo.density || 0,
        type: venueData.entries.includes(zone.id) ? 'entry' :
              venueData.exits.includes(zone.id) ? 'exit' : 'zone'
      };
    });

    const edges = venueData.connections.map(conn => ({
      from: conn.from,
      to: conn.to,
      source: conn.from,
      target: conn.to
    }));

    return { nodes, edges };
  };

  // Format state for SimulationCanvas
  const getSimulationState = () => {
    return {
      agents: [],
      reached_goal: stats.reachedGoal,
      nodes: Object.fromEntries(
        venueData.zones.map(zone => {
          const zoneInfo = zoneData[zone.id] || {};
          return [
            zone.id,
            {
              current_count: zoneInfo.agent_count || 0,
              density: zoneInfo.density || 0
            }
          ];
        })
      )
    };
  };

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">📊 Live Simulation Monitor</h2>
          <p className="text-gray-600">
            Step {currentStep} (~{(currentStep * 0.5).toFixed(1)} minutes elapsed)
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`px-6 py-2 rounded-lg font-semibold ${
              isPlaying 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isPlaying ? '⏸️ Pause' : '▶️ Play'}
          </button>
          
          <button
            onClick={fetchSimulationData}
            disabled={isPlaying}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            ⏭️ Step
          </button>

          <button
            onClick={onReset}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
          <p className="text-sm text-gray-600">Active Agents</p>
          <p className="text-3xl font-bold text-blue-600">{stats.activeAgents}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
          <p className="text-sm text-gray-600">Reached Goal</p>
          <p className="text-3xl font-bold text-green-600">{stats.reachedGoal}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
          <p className="text-sm text-gray-600">Max Density</p>
          <p className={`text-3xl font-bold ${
            stats.maxDensity > 7 ? 'text-red-600' :
            stats.maxDensity > 5 ? 'text-orange-600' :
            'text-green-600'
          }`}>
            {stats.maxDensity.toFixed(1)} p/m²
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
          <p className="text-sm text-gray-600">Stampedes</p>
          <p className="text-3xl font-bold text-red-600">{stats.stampedes}</p>
        </div>
        {/* ✅ NEW: AI Actions Card */}
        <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
          <p className="text-sm text-gray-600">AI Actions</p>
          <p className="text-3xl font-bold text-purple-600">{aiActions.length}</p>
        </div>
      </div>

      {/* ✅ Real-Time AI Actions Banner */}
      {recentActions.length > 0 && (
        <div className="mb-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-lg flex items-center gap-2">
              🤖 AI Taking Actions
            </h3>
            <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-bold">
              {aiActions.length} actions total
            </span>
          </div>
          
          <div className="space-y-2">
            {recentActions.map((action, idx) => (
              <div 
                key={idx} 
                className="bg-white/10 backdrop-blur-sm p-3 rounded-lg animate-pulse"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        action.severity === 'CRITICAL' ? 'bg-red-500' :
                        action.severity === 'HIGH' ? 'bg-orange-500' :
                        'bg-yellow-500'
                      }`}>
                        {action.severity}
                      </span>
                      <span className="font-semibold">{action.zone}</span>
                    </div>
                    <p className="text-sm">{action.action}: {action.reason}</p>
                  </div>
                  <span className="text-xs opacity-75">
                    Step {action.step}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Digital Twin Visualization */}
      <div className="mb-6 bg-white rounded-lg shadow p-6">
        <h3 className="font-bold text-lg mb-4">🗺️ Digital Twin & Heatmap</h3>
        <SimulationCanvas
          graphData={getGraphData()}
          state={getSimulationState()}
          width={800}
          height={500}
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left Column: Zones & Predictions */}
        <div className="space-y-6">
          {/* Zone Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-lg mb-4">🏛️ Zone Status</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {venueData.zones.map(zone => {
                const data = zoneData[zone.id] || {};
                const density = data.density || 0;
                
                return (
                  <div key={zone.id} className="p-3 border rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold">{zone.name}</span>
                      <span className={`px-2 py-1 rounded text-sm font-bold ${
                        density > 7 ? 'bg-red-100 text-red-700' :
                        density > 5 ? 'bg-orange-100 text-orange-700' :
                        density > 3 ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {density.toFixed(1)} p/m²
                      </span>
                    </div>
                    
                    {/* Density Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          density > 7 ? 'bg-red-600' :
                          density > 5 ? 'bg-orange-600' :
                          density > 3 ? 'bg-yellow-600' :
                          'bg-green-600'
                        }`}
                        style={{ width: `${Math.min((density / 10) * 100, 100)}%` }}
                      />
                    </div>

                    <div className="flex justify-between text-xs text-gray-600 mt-1">
                      <span>{data.agent_count || 0} people</span>
                      <span>Speed: {(data.speed || 0).toFixed(1)} m/s</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Stampede Predictions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-lg mb-4">🔮 AI Predictions</h3>
            
            {predictions.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-4xl mb-2">✅</p>
                <p>All zones safe</p>
              </div>
            ) : (
              <div className="space-y-3">
                {predictions.map((pred, idx) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg border-2 ${
                      pred.risk_level === 'imminent' || pred.risk_level === 'critical'
                        ? 'bg-red-50 border-red-300'
                        : pred.risk_level === 'high'
                        ? 'bg-orange-50 border-orange-300'
                        : 'bg-yellow-50 border-yellow-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-semibold">{pred.zone_id}</span>
                      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                        pred.risk_level === 'imminent' ? 'bg-red-600 text-white' :
                        pred.risk_level === 'critical' ? 'bg-red-500 text-white' :
                        pred.risk_level === 'high' ? 'bg-orange-500 text-white' :
                        'bg-yellow-500 text-white'
                      }`}>
                        {pred.risk_level}
                      </span>
                    </div>
                    
                    <p className="text-sm font-semibold mb-1">
                      {(pred.probability * 100).toFixed(0)}% stampede risk
                    </p>
                    
                    {pred.time_to_stampede && pred.time_to_stampede > 0 && (
                      <p className="text-sm text-red-700 font-bold">
                        ⏰ Stampede in {pred.time_to_stampede} steps (~{(pred.time_to_stampede * 0.5).toFixed(0)} min)
                      </p>
                    )}
                    
                    <p className="text-xs text-gray-600 mt-2">
                      Current: {pred.current_density.toFixed(1)} p/m² → 
                      Peak: {pred.predicted_peak_density.toFixed(1)} p/m²
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Interventions & AI Actions */}
        <div className="space-y-6">
          {/* ✅ AI Actions Log (TOP PRIORITY) */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-lg mb-4">
              🤖 AI Actions Log ({aiActions.length})
            </h3>
            
            {aiActions.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-4">
                No AI actions taken yet
              </p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {aiActions.slice().reverse().map((action, idx) => (
                  <div 
                    key={idx} 
                    className={`p-3 rounded-lg border-2 ${
                      action.severity === 'CRITICAL' 
                        ? 'bg-red-50 border-red-300' :
                      action.severity === 'HIGH' 
                        ? 'bg-orange-50 border-orange-300' :
                        'bg-yellow-50 border-yellow-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            action.severity === 'CRITICAL' ? 'bg-red-600 text-white' :
                            action.severity === 'HIGH' ? 'bg-orange-600 text-white' :
                            'bg-yellow-600 text-white'
                          }`}>
                            {action.action}
                          </span>
                        </div>
                        <p className="font-semibold text-sm">{action.zone}</p>
                        <p className="text-xs text-gray-600 mt-1">{action.reason}</p>
                      </div>
                      <span className="text-xs text-gray-500">
                        Step {action.step}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI Recommendations (Manual) */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="font-bold text-lg mb-4">💡 Manual Interventions</h3>
            
            {interventions.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-4xl mb-2">😌</p>
                <p>No manual interventions needed</p>
              </div>
            ) : (
              <div className="space-y-4">
                {interventions.map((intervention, idx) => (
                  <div
                    key={idx}
                    className="p-4 bg-blue-50 border-2 border-blue-300 rounded-lg"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            intervention.urgency === 'immediate' ? 'bg-red-600 text-white' :
                            intervention.urgency === 'critical' ? 'bg-orange-600 text-white' :
                            intervention.urgency === 'high' ? 'bg-yellow-600 text-white' :
                            'bg-blue-600 text-white'
                          }`}>
                            {intervention.urgency.toUpperCase()}
                          </span>
                        </div>
                        
                        <p className="font-semibold text-sm mb-2">
                          {intervention.action_description}
                        </p>
                        
                        <div className="text-xs text-gray-700 space-y-1">
                          <p>💚 Expected lives saved: <strong>{intervention.expected_lives_saved}</strong></p>
                          <p>📊 Success rate: <strong>{(intervention.success_probability * 100).toFixed(0)}%</strong></p>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => applyIntervention(intervention.intervention_id)}
                      className="w-full mt-3 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold text-sm"
                    >
                      ✅ Apply Manually
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Triggers */}
          {activeTriggers.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-bold text-lg mb-4">⚡ Active Triggers</h3>
              <div className="space-y-2">
                {activeTriggers.map(trigger => (
                  <div
                    key={trigger.id}
                    className="p-3 bg-orange-50 border border-orange-200 rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-sm">{trigger.name}</p>
                        <p className="text-xs text-gray-600">
                          Started at step {trigger.step}
                        </p>
                      </div>
                      <span className="text-orange-600 text-2xl">⚡</span>
                    </div>
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

export default LiveMonitor;
