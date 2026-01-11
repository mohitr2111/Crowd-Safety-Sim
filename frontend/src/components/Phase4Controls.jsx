import React, { useState, useEffect } from 'react';
import { simulationApi } from '../api/simulationApi';

const Phase4Controls = ({ simulationId, nodes }) => {
  const [selectedNode, setSelectedNode] = useState('');
  const [spawnRateMultiplier, setSpawnRateMultiplier] = useState(1.0);
  const [capacityExpansion, setCapacityExpansion] = useState(1.0);
  const [spawnControlState, setSpawnControlState] = useState(null);
  const [capacityState, setCapacityState] = useState(null);
  const [loading, setLoading] = useState({});
  const [duration, setDuration] = useState(60); // seconds

  const nodeList = nodes ? Object.keys(nodes) : [];

  useEffect(() => {
    if (selectedNode && simulationId) {
      loadStates();
    }
  }, [selectedNode, simulationId]);

  const loadStates = async () => {
    if (!selectedNode) return;
    try {
      const [spawnState, capState] = await Promise.all([
        simulationApi.getSpawnControlState(simulationId, selectedNode).catch(() => null),
        simulationApi.getCapacityState(simulationId, selectedNode).catch(() => null)
      ]);
      if (spawnState) setSpawnControlState(spawnState.state);
      if (capState) setCapacityState(capState.state);
    } catch (error) {
      console.error('Error loading states:', error);
    }
  };

  const handleSpawnRateControl = async () => {
    if (!selectedNode || !simulationId) return;
    setLoading({ ...loading, spawn: true });
    try {
      await simulationApi.controlSpawnRate(
        simulationId,
        selectedNode,
        spawnRateMultiplier,
        duration
      );
      await loadStates();
      alert(`Spawn rate control applied: ${(spawnRateMultiplier * 100).toFixed(0)}%`);
    } catch (error) {
      console.error('Error controlling spawn rate:', error);
      alert(`Failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, spawn: false });
    }
  };

  const handleExpandCapacity = async () => {
    if (!selectedNode || !simulationId) return;
    setLoading({ ...loading, expand: true });
    try {
      await simulationApi.adjustCapacity(
        simulationId,
        selectedNode,
        'expand_area',
        capacityExpansion,
        duration
      );
      await loadStates();
      alert(`Capacity expanded: ${((capacityExpansion - 1) * 100).toFixed(0)}%`);
    } catch (error) {
      console.error('Error expanding capacity:', error);
      alert(`Failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, expand: false });
    }
  };

  const handleBlockZone = async () => {
    if (!selectedNode || !simulationId) return;
    if (!confirm(`Block zone ${selectedNode}?`)) return;
    setLoading({ ...loading, block: true });
    try {
      await simulationApi.adjustCapacity(
        simulationId,
        selectedNode,
        'block_zone',
        null,
        duration
      );
      await loadStates();
      alert(`Zone ${selectedNode} blocked`);
    } catch (error) {
      console.error('Error blocking zone:', error);
      alert(`Failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, block: false });
    }
  };

  const handleRestoreCapacity = async () => {
    if (!selectedNode || !simulationId) return;
    setLoading({ ...loading, restore: true });
    try {
      await simulationApi.adjustCapacity(simulationId, selectedNode, 'restore');
      await loadStates();
      alert(`Capacity restored for ${selectedNode}`);
    } catch (error) {
      console.error('Error restoring capacity:', error);
      alert(`Failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading({ ...loading, restore: false });
    }
  };

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-slate-200 mb-4">Phase 4: Advanced Controls</h3>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Select Node
        </label>
        <select
          value={selectedNode}
          onChange={(e) => setSelectedNode(e.target.value)}
          className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Select a node...</option>
          {nodeList.map((node) => (
            <option key={node} value={node}>
              {node.replace(/_/g, ' ').toUpperCase()}
            </option>
          ))}
        </select>
      </div>

      {selectedNode && (
        <>
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Duration (seconds)
            </label>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(parseFloat(e.target.value) || 60)}
              min="1"
              className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Spawn Rate Control */}
          <div className="mb-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Spawn Rate Control</h4>
            {spawnControlState && (
              <div className="mb-3 text-xs text-slate-400">
                Current rate: {spawnControlState.current_rate?.toFixed(1)} agents/s
                (multiplier: {(spawnControlState.rate_multiplier * 100).toFixed(0)}%)
              </div>
            )}
            <div className="mb-3">
              <label className="block text-xs text-slate-400 mb-2">
                Rate Multiplier: {(spawnRateMultiplier * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={spawnRateMultiplier}
                onChange={(e) => setSpawnRateMultiplier(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
            <button
              onClick={handleSpawnRateControl}
              disabled={loading.spawn}
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold text-sm transition-all disabled:opacity-50"
            >
              {loading.spawn ? 'Applying...' : 'Apply Spawn Rate Control'}
            </button>
          </div>

          {/* Capacity Adjustments */}
          <div className="mb-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Capacity Adjustments</h4>
            {capacityState && (
              <div className="mb-3 text-xs text-slate-400">
                Current area: {capacityState.current_area_m2?.toFixed(1)} m²
                {capacityState.original_area_m2 && (
                  <> (original: {capacityState.original_area_m2.toFixed(1)} m²)</>
                )}
              </div>
            )}
            <div className="mb-3">
              <label className="block text-xs text-slate-400 mb-2">
                Expansion Factor: {((capacityExpansion - 1) * 100).toFixed(0)}% increase
              </label>
              <input
                type="range"
                min="1"
                max="1.5"
                step="0.05"
                value={capacityExpansion}
                onChange={(e) => setCapacityExpansion(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={handleExpandCapacity}
                disabled={loading.expand}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold text-sm transition-all disabled:opacity-50"
              >
                {loading.expand ? 'Expanding...' : 'Expand'}
              </button>
              <button
                onClick={handleBlockZone}
                disabled={loading.block}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg font-semibold text-sm transition-all disabled:opacity-50"
              >
                {loading.block ? 'Blocking...' : 'Block Zone'}
              </button>
            </div>
            <button
              onClick={handleRestoreCapacity}
              disabled={loading.restore}
              className="w-full mt-2 px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-semibold text-sm transition-all disabled:opacity-50"
            >
              {loading.restore ? 'Restoring...' : 'Restore Capacity'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Phase4Controls;

