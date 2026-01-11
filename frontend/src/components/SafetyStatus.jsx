import React, { useState, useEffect } from 'react';
import { simulationApi } from '../api/simulationApi';

const SafetyStatus = ({ simulationId }) => {
  const [safetyStatus, setSafetyStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (simulationId) {
      loadSafetyStatus();
      const interval = setInterval(loadSafetyStatus, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [simulationId]);

  const loadSafetyStatus = async () => {
    if (!simulationId) return;
    setLoading(true);
    try {
      const data = await simulationApi.getSafetyStatus(simulationId);
      setSafetyStatus(data.safety_status);
    } catch (error) {
      console.error('Error loading safety status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateConstraints = async (updates) => {
    if (!simulationId) return;
    setUpdating(true);
    try {
      await simulationApi.updateSafetyConstraints(simulationId, updates);
      await loadSafetyStatus();
      alert('Safety constraints updated successfully');
    } catch (error) {
      console.error('Error updating constraints:', error);
      alert(`Failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  if (!simulationId) return null;

  const constraints = safetyStatus?.constraints || {};
  const currentStatus = safetyStatus?.current_status || {};

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-200">Safety Status</h3>
        {loading && (
          <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        )}
      </div>

      {safetyStatus ? (
        <div className="space-y-4">
          {/* Current Status */}
          <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Current Status</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-slate-400 mb-1">Current Frequency</div>
                <div className="text-lg font-bold text-slate-200">
                  {currentStatus.current_frequency?.toFixed(1)}/min
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-400 mb-1">Active Interventions</div>
                <div className="text-lg font-bold text-slate-200">
                  {currentStatus.active_interventions || 0}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-400 mb-1">Time Since Last</div>
                <div className="text-lg font-bold text-slate-200">
                  {currentStatus.time_since_last ? `${currentStatus.time_since_last.toFixed(1)}s` : 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-400 mb-1">Can Intervene</div>
                <div className={`text-lg font-bold ${safetyStatus.can_intervene ? 'text-emerald-400' : 'text-red-400'}`}>
                  {safetyStatus.can_intervene ? 'Yes' : 'No'}
                </div>
              </div>
            </div>
          </div>

          {/* Constraints */}
          <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Safety Constraints</h4>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Max Interventions/min</span>
                <span className="text-sm font-semibold text-slate-200">
                  {constraints.max_interventions_per_minute || 'N/A'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Min Interval (s)</span>
                <span className="text-sm font-semibold text-slate-200">
                  {constraints.min_interval_seconds || 'N/A'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Max Active</span>
                <span className="text-sm font-semibold text-slate-200">
                  {constraints.max_active_interventions || 'N/A'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Rollback Enabled</span>
                <span className={`text-sm font-semibold ${constraints.enable_rollback ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {constraints.enable_rollback ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Manual Override</span>
                <span className={`text-sm font-semibold ${constraints.enable_manual_override ? 'text-emerald-400' : 'text-slate-500'}`}>
                  {constraints.enable_manual_override ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="pt-4 border-t border-slate-700">
            <button
              onClick={() => handleUpdateConstraints({
                max_interventions_per_minute: 15.0,
                min_interval_seconds: 3.0,
                max_active_interventions: 10
              })}
              disabled={updating}
              className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold text-sm transition-all disabled:opacity-50"
            >
              {updating ? 'Updating...' : 'Update Constraints (Preset)'}
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-slate-500">
          Loading safety status...
        </div>
      )}
    </div>
  );
};

export default SafetyStatus;

