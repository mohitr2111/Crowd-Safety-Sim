import React, { useState, useEffect } from 'react';
import { simulationApi } from '../api/simulationApi';

const AdvancedMonitoring = ({ simulationId }) => {
  const [health, setHealth] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (simulationId) {
      loadMonitoringData();
      const interval = setInterval(loadMonitoringData, 5000); // Update every 5 seconds
      return () => clearInterval(interval);
    }
  }, [simulationId]);

  const loadMonitoringData = async () => {
    if (!simulationId) return;
    setLoading(true);
    try {
      const [healthData, predictionData] = await Promise.all([
        simulationApi.getSystemHealth(simulationId).catch(() => null),
        simulationApi.getStampedePrediction(simulationId).catch(() => null)
      ]);
      if (healthData) setHealth(healthData.health);
      if (predictionData) setPrediction(predictionData.prediction);
    } catch (error) {
      console.error('Error loading monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!simulationId) return null;

  const getStatusColor = (status) => {
    switch (status) {
      case 'HEALTHY': return 'emerald';
      case 'WARNING': return 'amber';
      case 'CRITICAL': return 'red';
      default: return 'slate';
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'LOW': return 'emerald';
      case 'MEDIUM': return 'amber';
      case 'HIGH': return 'orange';
      case 'CRITICAL': return 'red';
      default: return 'slate';
    }
  };

  return (
    <div className="space-y-4">
      {/* System Health */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-slate-200">System Health</h3>
          {loading && (
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          )}
        </div>

        {health ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Overall Status</span>
              <span
                className={`px-3 py-1 rounded-lg text-sm font-bold text-${getStatusColor(health.overall_status)}-400 bg-${getStatusColor(health.overall_status)}-500/20 border border-${getStatusColor(health.overall_status)}-500/30`}
              >
                {health.overall_status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="stat-card">
                <div className="text-xs text-slate-400 mb-1">Intervention Frequency</div>
                <div className="text-xl font-bold text-slate-200">
                  {health.intervention_frequency?.toFixed(2)}/min
                </div>
              </div>

              <div className="stat-card">
                <div className="text-xs text-slate-400 mb-1">Avg Effectiveness</div>
                <div className="text-xl font-bold text-slate-200">
                  {(health.average_effectiveness * 100).toFixed(1)}%
                </div>
              </div>

              <div className="stat-card">
                <div className="text-xs text-slate-400 mb-1">Danger Zones</div>
                <div className="text-xl font-bold text-red-400">
                  {health.danger_zone_count || 0}
                </div>
              </div>

              <div className="stat-card">
                <div className="text-xs text-slate-400 mb-1">Max Density</div>
                <div className="text-xl font-bold text-slate-200">
                  {health.max_density?.toFixed(2)} p/m²
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">System Stability</span>
                <span className="text-sm font-semibold text-slate-200">
                  {(health.system_stability * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-2 transition-all rounded-full bg-gradient-to-r from-${getStatusColor(health.overall_status)}-600 to-${getStatusColor(health.overall_status)}-500`}
                  style={{ width: `${health.system_stability * 100}%` }}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            Loading health data...
          </div>
        )}
      </div>

      {/* Stampede Prediction */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-slate-200">Stampede Prediction</h3>
          {loading && (
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          )}
        </div>

        {prediction ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Risk Level</span>
              <span
                className={`px-3 py-1 rounded-lg text-sm font-bold text-${getRiskColor(prediction.risk_level)}-400 bg-${getRiskColor(prediction.risk_level)}-500/20 border border-${getRiskColor(prediction.risk_level)}-500/30`}
              >
                {prediction.risk_level}
              </span>
            </div>

            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-slate-400">Probability</span>
              <span className={`text-2xl font-bold text-${getRiskColor(prediction.risk_level)}-400`}>
                {(prediction.probability * 100).toFixed(1)}%
              </span>
            </div>

            <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden mb-4">
              <div
                className={`h-4 transition-all rounded-full bg-gradient-to-r from-${getRiskColor(prediction.risk_level)}-600 to-${getRiskColor(prediction.risk_level)}-500`}
                style={{ width: `${prediction.probability * 100}%` }}
              />
            </div>

            {prediction.contributing_factors && prediction.contributing_factors.length > 0 && (
              <div className="pt-4 border-t border-slate-700">
                <div className="text-xs text-slate-400 mb-2">Contributing Factors:</div>
                <ul className="space-y-1">
                  {prediction.contributing_factors.map((factor, index) => (
                    <li key={index} className="text-sm text-slate-300 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {prediction.predicted_time && (
              <div className="pt-4 border-t border-slate-700">
                <div className="text-xs text-slate-400 mb-1">Predicted Time</div>
                <div className="text-sm font-semibold text-slate-200">
                  {prediction.predicted_time.toFixed(1)}s
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-slate-700">
              <div className="text-xs text-slate-400 mb-1">Confidence</div>
              <div className="text-sm font-semibold text-slate-200">
                {(prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500">
            Loading prediction data...
          </div>
        )}
      </div>
    </div>
  );
};

export default AdvancedMonitoring;

