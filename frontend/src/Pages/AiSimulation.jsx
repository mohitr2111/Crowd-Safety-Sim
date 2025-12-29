import React, { useState, useEffect } from 'react';
import SimulationCanvas from '../components/SimulationCanvas';
import AIRecommendations from '../components/AIRecommendation';
import DynamicCrowdSelector from '../components/DynaminCrowdSelector';
import VenueCapacity from '../components/stadiumcapacity';

const LiveSimulation = () => {
  // State management
  const [selectedScenario, setSelectedScenario] = useState('stadium_exit');
  const [simulationId, setSimulationId] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [state, setState] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [stadiumStatus, setStadiumStatus] = useState(null);

  // NEW: AI Intervention tracking
  const [interventionCount, setInterventionCount] = useState(0);
  const [lastAction, setLastAction] = useState(null);
  const [recentActions, setRecentActions] = useState([]);


  // Default spawn configuration
  const [spawnConfig, setSpawnConfig] = useState([
    { start: 'zone_north', goal: 'exit_main', count: 500, type: 'normal' },
    { start: 'zone_south', goal: 'exit_main', count: 400, type: 'family' },
    { start: 'zone_east', goal: 'exit_main', count: 100, type: 'rushing' },
    { start: 'zone_west', goal: 'exit_main', count: 100, type: 'elderly' }
  ]);


  // Fetch available scenarios on mount
  const [scenarios, setScenarios] = useState([]);

  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const response = await fetch('http://localhost:8000/scenarios');
        const data = await response.json();
        setScenarios(data.scenarios || []);
      } catch (error) {
        console.error('Error fetching scenarios:', error);
      }
    };

    fetchScenarios();
  }, []);


  // Create simulation
  const createSimulation = async () => {
    try {
      const response = await fetch('http://localhost:8000/simulation/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario: selectedScenario,
          spawn_config: spawnConfig,
          time_step: 1.0
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create simulation');
      }

      const data = await response.json();
      setSimulationId(data.simulation_id);
      setState(data.initial_state);

      // Fetch graph structure
      const graphResponse = await fetch(
        `http://localhost:8000/simulation/${data.simulation_id}/graph`
      );
      const graphData = await graphResponse.json();
      setGraphData(graphData);

      // Reset intervention tracking
      setInterventionCount(0);
      setLastAction(null);
      setRecentActions([]);

      console.log('✅ Simulation created:', data.simulation_id);
    } catch (error) {
      console.error('❌ Error creating simulation:', error);
      alert('Failed to create simulation. Check console for details.');
    }
  };


  // NEW: Check for AI interventions in state
  useEffect(() => {
    if (!state || !state.nodes) return;

    // Detect high-density nodes that would trigger AI action
    Object.entries(state.nodes).forEach(([nodeId, nodeData]) => {
      if (nodeData.density > 3.5) {
        const timestamp = state.time || Date.now();

        // Check if this is a new intervention (not already in recent actions)
        const isNewIntervention = !recentActions.some(
          action => action.node === nodeId && Math.abs(action.time - timestamp) < 2
        );

        if (isNewIntervention) {
          const action = {
            node: nodeId,
            density: nodeData.density,
            time: timestamp,
            action: nodeData.density > 4.5 ? 'reduce_inflow_25' : 'reroute_to_alt_exit'
          };

          setInterventionCount(prev => prev + 1);
          setLastAction(action);
          setRecentActions(prev => [action, ...prev].slice(0, 5)); // Keep last 5 actions
        }
      }
    });
  }, [state]);


  // Step simulation forward
  const stepSimulation = async () => {
    if (!simulationId) return;

    try {
      const response = await fetch('http://localhost:8000/simulation/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulation_id: simulationId,
          steps: 1
        })
      });

      const data = await response.json();
      setState(data.current_state);
    } catch (error) {
      console.error('Error stepping simulation:', error);
    }
  };


  // Fetch stadium status periodically
  useEffect(() => {
    if (!simulationId || !isPlaying) return;

    const fetchStadiumStatus = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/simulation/${simulationId}/venue-status`
        );
        const data = await response.json();
        
        if (data.venue_status) {
          setStadiumStatus(data.venue_status);
        } else {
          console.error('No venue_status in response:', data);
        }
      } catch (error) {
        console.error('Error fetching stadium status:', error);
      }
    };

    // Initial fetch
    fetchStadiumStatus();

    // Poll every 2 seconds
    const interval = setInterval(fetchStadiumStatus, 2000);

    return () => clearInterval(interval);
  }, [simulationId, isPlaying]);


  // Auto-play functionality
  useEffect(() => {
    if (!isPlaying || !simulationId) return;

    const interval = setInterval(() => {
      stepSimulation();
    }, 1000); // Step every 1 second

    return () => clearInterval(interval);
  }, [isPlaying, simulationId]);


  // Reset simulation
  const resetSimulation = () => {
    setSimulationId(null);
    setState(null);
    setGraphData(null);
    setIsPlaying(false);
    setStadiumStatus(null);
    setInterventionCount(0);
    setLastAction(null);
    setRecentActions([]);
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            🚦 Live Crowd Safety Simulation
          </h1>
          <p className="text-gray-600 text-lg">
            AI-Powered Real-Time Monitoring & Recommendations
          </p>
        </div>

        {/* NEW: AI Intervention Counter - Fixed Position */}
        {simulationId && (
          <div className="fixed top-6 right-6 z-50">
            <div className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-4 rounded-xl shadow-2xl border-2 border-purple-300">
              <div className="flex items-center gap-3 mb-2">
                <span className="text-3xl">🤖</span>
                <div>
                  <div className="text-sm font-medium opacity-90">AI Interventions</div>
                  <div className="text-3xl font-bold">{interventionCount}</div>
                </div>
              </div>

              {lastAction && (
                <div className="mt-3 pt-3 border-t border-purple-300/30">
                  <div className="text-xs font-semibold opacity-75 mb-1">Last Action:</div>
                  <div className="text-sm bg-white/20 rounded-lg px-3 py-2">
                    <div className="font-bold">{lastAction.action.replace(/_/g, ' ').toUpperCase()}</div>
                    <div className="text-xs opacity-90">
                      @ {lastAction.node} ({lastAction.density.toFixed(1)} p/m²)
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Recent Actions List */}
            {recentActions.length > 0 && (
              <div className="mt-3 bg-white rounded-lg shadow-lg p-4 max-w-xs">
                <div className="text-xs font-bold text-gray-600 mb-2">📋 Recent Actions</div>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {recentActions.map((action, idx) => (
                    <div 
                      key={idx}
                      className="text-xs bg-gray-50 rounded px-3 py-2 border-l-2 border-purple-400"
                    >
                      <div className="font-semibold text-gray-700">
                        {action.action.replace(/_/g, ' ')}
                      </div>
                      <div className="text-gray-500">
                        {action.node} • {action.density.toFixed(1)} p/m² • t={action.time.toFixed(0)}s
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Scenario Selector */}
        {!simulationId && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <label className="block text-sm font-semibold mb-2 text-gray-700">
              📍 Select Scenario:
            </label>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="w-full p-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition-all"
            >
              <option value="stadium_exit">🏟️ Stadium Exit</option>
              <option value="railway_station">🚉 Railway Station</option>
            </select>
          </div>
        )}


        {/* Crowd Size Selector */}
        {!simulationId && (
          <DynamicCrowdSelector 
            selectedScenario={selectedScenario}
            onCrowdChange={(config) => setSpawnConfig(config)}
          />
        )}



        {/* Create Simulation Button */}
        {!simulationId && (
          <button
            onClick={createSimulation}
            className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-4 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all mb-6 text-lg shadow-lg transform hover:scale-105"
          >
            🚀 Create Simulation ({spawnConfig.reduce((sum, cfg) => sum + cfg.count, 0)} agents)
          </button>
        )}


        {/* Control Panel */}
        {simulationId && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className={`flex-1 font-bold py-3 px-6 rounded-lg transition-all transform hover:scale-105 ${
                  isPlaying
                    ? 'bg-orange-500 hover:bg-orange-600 text-white shadow-lg'
                    : 'bg-green-500 hover:bg-green-600 text-white shadow-lg'
                }`}
              >
                {isPlaying ? '⏸️ Pause' : '▶️ Play'}
              </button>

              <button
                onClick={stepSimulation}
                disabled={isPlaying}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 px-6 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105"
              >
                ⏭️ Step Forward
              </button>

              <button
                onClick={resetSimulation}
                className="flex-1 bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg transition-all transform hover:scale-105"
              >
                🔄 Reset
              </button>
            </div>


            {/* Time Display */}
            {state && (
              <div className="mt-4 text-center">
                <span className="text-lg font-semibold text-gray-700">
                  ⏱️ Time: {state.time?.toFixed(1)}s
                </span>
              </div>
            )}
          </div>
        )}


        {/* Canvas Visualization */}
        {graphData && state && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-xl font-bold mb-4 text-gray-800">
              📊 Real-Time Visualization
            </h3>
            <SimulationCanvas graphData={graphData} state={state} />
          </div>
        )}


        {/* Stadium Capacity Indicator */}
        {simulationId && stadiumStatus && (
          <div className="mb-6">
            <VenueCapacity stadiumStatus={stadiumStatus} />
          </div>
        )}


        {/* AI Recommendations Panel */}
        {simulationId && stadiumStatus && (
          <div className="mb-6">
            <AIRecommendations stadiumStatus={stadiumStatus} simulationId={simulationId} />
          </div>
        )}


        {/* Stats Panel */}
        {state && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4 text-gray-800">📈 Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Active Agents</div>
                <div className="text-2xl font-bold text-blue-600">
                  {state.total_agents 
                    ? (state.total_agents - (state.reached_goal || 0))
                    : Object.keys(state.agents || {}).length
                  }
                </div>
              </div>

              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Reached Goal</div>
                <div className="text-2xl font-bold text-green-600">
                  {state.reached_goal || state.stats?.agents_reached_goal || 0}
                </div>
              </div>

              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Max Density</div>
                <div className="text-2xl font-bold text-orange-600">
                  {state.max_density?.toFixed(2) 
                    || state.stats?.max_density_reached?.toFixed(2) 
                    || '0.00'
                  } p/m²
                </div>
              </div>

              <div className="bg-red-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Danger Zones</div>
                <div className="text-2xl font-bold text-red-600">
                  {state.danger_zones?.length 
                    || state.stats?.danger_violations 
                    || 0
                  }
                </div>
              </div>
            </div>
          </div>
        )}


      </div>
    </div>
  );
};


export default LiveSimulation;