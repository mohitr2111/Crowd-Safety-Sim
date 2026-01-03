import React, { useState, useEffect } from 'react';
import SimulationCanvas from '../components/SimulationCanvas';
import StadiumCapacity from '../components/stadiumcapacity';
import AIRecommendations from '../components/AIRecommendation';
import CrowdSizeSelector from '../components/CrowdSizeSelector';
import AIActionLogger from '../components/AiActionLogger';
import CaseStudyAnalysis from '../components/CaseStudyAnalysis';
import VenueBuilder from '../components/VenueBuilder';

const LiveSimulation = () => {
  const [selectedScenario, setSelectedScenario] = useState('stadium_exit');
  const [simulationId, setSimulationId] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [state, setState] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [stadiumStatus, setStadiumStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('simulation');
  const [aiActions, setAiActions] = useState([]);
  const [caseStudies, setCaseStudies] = useState([]);
  const [stampedePrediction, setStampedePrediction] = useState(null);
  const [spawnConfig, setSpawnConfig] = useState([
    { start: 'zone_north', goal: 'exit_main', count: 500, type: 'normal' },
    { start: 'zone_south', goal: 'exit_main', count: 400, type: 'family' },
    { start: 'zone_east', goal: 'exit_main', count: 100, type: 'rushing' },
    { start: 'zone_west', goal: 'exit_main', count: 100, type: 'elderly' }
  ]);

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
      
      const graphResponse = await fetch(
        `http://localhost:8000/simulation/${data.simulation_id}/graph`
      );
      const graphData = await graphResponse.json();
      setGraphData(graphData);
      
      console.log('Simulation created:', data.simulation_id);
    } catch (error) {
      console.error('Error creating simulation:', error);
      alert('Failed to create simulation. Check console for details.');
    }
  };

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

  useEffect(() => {
    if (!simulationId || !isPlaying) return;
    
    const fetchStadiumStatus = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/simulation/${simulationId}/stadium-status`
        );
        const data = await response.json();
        setStadiumStatus(data);
      } catch (error) {
        console.error('Error fetching stadium status:', error);
      }
    };
    
    fetchStadiumStatus();
    const interval = setInterval(fetchStadiumStatus, 2000);
    return () => clearInterval(interval);
  }, [simulationId, isPlaying]);

  useEffect(() => {
    if (!simulationId) return;
    
    const fetchAIData = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/simulation/${simulationId}/ai-actions`
        );
        const data = await response.json();
        setAiActions(data.ai_actions || []);
        setStampedePrediction(data.stampede_prediction);
      } catch (error) {
        console.error('Error fetching AI data:', error);
      }
    };
    
    fetchAIData();
    const interval = setInterval(fetchAIData, 1000);
    return () => clearInterval(interval);
  }, [simulationId]);

  useEffect(() => {
    const fetchCaseStudies = async () => {
      try {
        const response = await fetch('http://localhost:8000/simulation/case-studies');
        const data = await response.json();
        setCaseStudies(data.case_studies || []);
      } catch (error) {
        console.error('Error fetching case studies:', error);
      }
    };
    fetchCaseStudies();
  }, []);

  useEffect(() => {
    if (!isPlaying || !simulationId) return;
    const interval = setInterval(() => {
      stepSimulation();
    }, 1000);
    return () => clearInterval(interval);
  }, [isPlaying, simulationId]);

  const resetSimulation = () => {
    setSimulationId(null);
    setState(null);
    setGraphData(null);
    setIsPlaying(false);
    setStadiumStatus(null);
  };

  const tabs = [
    { id: 'simulation', label: 'Simulation' },
    { id: 'actions', label: 'AI Actions' },
    { id: 'builder', label: 'Venue Builder' },
    { id: 'cases', label: 'Case Studies' }
  ];

  return (
    <div className="p-6 animate-fade-in">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">
            Live Crowd Safety Simulation
          </h1>
          <p className="text-slate-400">
            AI-Powered Real-Time Monitoring & Recommendations
          </p>
        </div>

        <div className="flex gap-2 mb-6 p-1 bg-slate-800/50 rounded-xl border border-slate-700/50 inline-flex">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="animate-fade-in">
          {activeTab === 'simulation' && (
            <div className="space-y-6">
              {!simulationId && (
                <div className="glass-card p-6">
                  <label className="block text-sm font-semibold mb-3 text-slate-300">
                    Select Scenario
                  </label>
                  <select
                    value={selectedScenario}
                    onChange={(e) => setSelectedScenario(e.target.value)}
                    className="input-modern"
                  >
                    <option value="stadium_exit">Stadium Exit</option>
                    <option value="railway_station">Railway Station</option>
                  </select>
                </div>
              )}

              {!simulationId && (
                <CrowdSizeSelector 
                  selectedScenario={selectedScenario}
                  onSelectPreset={(config) => setSpawnConfig(config)}
                />
              )}

              {!simulationId && (
                <button
                  onClick={createSimulation}
                  className="w-full btn-primary text-lg py-4"
                >
                  Create Simulation ({spawnConfig.reduce((sum, cfg) => sum + cfg.count, 0)} agents)
                </button>
              )}

              {simulationId && (
                <div className="glass-card p-6">
                  <div className="flex flex-col md:flex-row gap-4">
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className={`flex-1 font-bold py-3 px-6 rounded-xl transition-all ${
                        isPlaying
                          ? 'bg-orange-500 hover:bg-orange-600 text-white'
                          : 'bg-emerald-500 hover:bg-emerald-600 text-white'
                      }`}
                    >
                      {isPlaying ? 'Pause' : 'Play'}
                    </button>
                    
                    <button
                      onClick={stepSimulation}
                      disabled={isPlaying}
                      className="flex-1 btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Step Forward
                    </button>
                    
                    <button
                      onClick={resetSimulation}
                      className="flex-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 font-bold py-3 px-6 rounded-xl transition-all"
                    >
                      Reset
                    </button>
                  </div>

                  {state && (
                    <div className="mt-4 text-center">
                      <span className="text-lg font-semibold text-slate-300">
                        Time: {state.time?.toFixed(1)}s
                      </span>
                    </div>
                  )}
                </div>
              )}

              {graphData && state && (
                <div className="glass-card p-6">
                  <h3 className="text-xl font-bold mb-4 text-slate-200">
                    Real-Time Visualization
                  </h3>
                  <SimulationCanvas graphData={graphData} state={state} />
                </div>
              )}

              {simulationId && stadiumStatus && (
                <StadiumCapacity stadiumStatus={stadiumStatus} />
              )}

              {simulationId && stadiumStatus && (
                <AIRecommendations stadiumStatus={stadiumStatus} />
              )}

              {state && (
                <div className="glass-card p-6">
                  <h3 className="text-xl font-bold mb-4 text-slate-200">Statistics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="stat-card">
                      <div className="text-sm text-slate-400 mb-1">Active Agents</div>
                      <div className="text-2xl font-bold text-blue-400">
                        {state.total_agents 
                          ? (state.total_agents - (state.reached_goal || 0))
                          : Object.keys(state.agents || {}).length
                        }
                      </div>
                    </div>
                    
                    <div className="stat-card">
                      <div className="text-sm text-slate-400 mb-1">Reached Goal</div>
                      <div className="text-2xl font-bold text-emerald-400">
                        {state.reached_goal || state.stats?.agents_reached_goal || 0}
                      </div>
                    </div>
                    
                    <div className="stat-card">
                      <div className="text-sm text-slate-400 mb-1">Max Density</div>
                      <div className="text-2xl font-bold text-orange-400">
                        {state.max_density?.toFixed(2) 
                          || state.stats?.max_density_reached?.toFixed(2) 
                          || '0.00'
                        } p/m²
                      </div>
                    </div>
                    
                    <div className="stat-card">
                      <div className="text-sm text-slate-400 mb-1">Danger Zones</div>
                      <div className="text-2xl font-bold text-red-400">
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
          )}

          {activeTab === 'actions' && (
            <AIActionLogger simulationData={{ ai_actions: aiActions }} stampedePrediction={stampedePrediction} />
          )}

          {activeTab === 'builder' && (
            <VenueBuilder onSave={(scenario) => {
              console.log('Scenario saved:', scenario);
              alert(`Scenario "${scenario.name}" saved! (Check console)`);
            }} />
          )}

          {activeTab === 'cases' && (
            <CaseStudyAnalysis caseStudies={caseStudies} />
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveSimulation;
