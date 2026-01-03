import React, { useState } from 'react';

const AIActionLogger = ({ simulationData, stampedePrediction }) => {
  const [expandedAction, setExpandedAction] = useState(null);
  const [filterLevel, setFilterLevel] = useState('all');

  if (!simulationData) return null;

  const actions = simulationData.ai_actions || [];

  const filteredActions = actions.filter(action => {
    if (filterLevel === 'all') return true;
    return action.severity === filterLevel;
  });

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'red';
      case 'WARNING': return 'amber';
      case 'INFO': return 'blue';
      default: return 'slate';
    }
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div>
        <h3 className="text-lg font-bold text-slate-200">AI Real-Time Intervention Log</h3>
        <p className="text-sm text-slate-500">Shows every action taken to prevent stampede</p>
      </div>

      {stampedePrediction && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-center">
                <span className="text-3xl font-bold text-red-400">
                  {stampedePrediction.stampede_probability}%
                </span>
                <div className="text-xs text-red-400">Stampede Risk</div>
              </div>
              <div className="text-sm text-slate-400 space-y-1">
                <p><span className="text-slate-300 font-medium">{stampedePrediction.minutes_until_critical}</span> minutes until critical</p>
                <p>Max Density: <span className="text-slate-300 font-medium">{stampedePrediction.max_density}</span> p/m²</p>
                <p className="text-emerald-400 font-medium">{stampedePrediction.recommendation}</p>
              </div>
            </div>
            <div className={`w-8 h-8 rounded-full ${stampedePrediction.stampede_probability > 70 ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`}></div>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {['all', 'CRITICAL', 'WARNING', 'INFO'].map(level => (
          <button
            key={level}
            onClick={() => setFilterLevel(level)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filterLevel === level
                ? level === 'CRITICAL' ? 'bg-red-500 text-white' :
                  level === 'WARNING' ? 'bg-amber-500 text-white' :
                  level === 'INFO' ? 'bg-blue-500 text-white' :
                  'bg-slate-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {level === 'all' ? 'All Actions' : level}
            {level !== 'all' && ` (${actions.filter(a => a.severity === level).length})`}
          </button>
        ))}
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredActions.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
              <p>No {filterLevel !== 'all' ? filterLevel.toLowerCase() : ''} actions yet</p>
              <p className="text-xs">AI is monitoring crowd...</p>
            </div>
        ) : (
          filteredActions.map((action, index) => (
            <div
              key={index}
              onClick={() => setExpandedAction(expandedAction === index ? null : index)}
              className={`bg-slate-800/50 border-l-4 p-4 rounded-lg cursor-pointer transition-all hover:bg-slate-800 ${
                action.severity === 'CRITICAL' ? 'border-red-500' :
                action.severity === 'WARNING' ? 'border-amber-500' : 'border-blue-500'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${
                      action.severity === 'CRITICAL' ? 'bg-red-400' :
                      action.severity === 'WARNING' ? 'bg-amber-400' : 'bg-blue-400'
                    }`}></span>
                    <strong className="text-slate-200">{action.action}</strong>
                    <span className="text-xs text-slate-500">{action.time_seconds.toFixed(1)}s</span>
                  </div>
                <span className="text-slate-500 text-sm">{expandedAction === index ? '-' : '+'}</span>
              </div>

              <div className="text-xs text-slate-500 flex gap-3">
                <span>Zone: {action.zone}</span>
                <span>Density: {action.density.toFixed(2)} p/m²</span>
              </div>

              {expandedAction === index && (
                <div className="mt-4 pt-4 border-t border-slate-700 space-y-3 text-sm">
                  <div className="flex gap-2">
                    <span className="text-slate-500 w-24">Action Type:</span>
                    <span className="text-slate-300">{action.action_type}</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-slate-500 w-24">Effect:</span>
                    <span className="text-slate-300">{action.expected_effect}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500 w-24">Confidence:</span>
                    <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-emerald-500 rounded-full transition-all"
                        style={{ width: `${action.confidence * 100}%` }}
                      />
                    </div>
                    <span className="text-slate-300">{(action.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="text-slate-500 w-24">Advice:</span>
                    <span className="text-emerald-400 italic">{action.recommendation}</span>
                  </div>
                  {action.impact && (
                    <div className="flex gap-2">
                      <span className="text-slate-500 w-24">Impact:</span>
                      <span className={action.impact === 'prevented_stampede' ? 'text-emerald-400 font-medium' : 'text-amber-400'}>
                          {action.impact === 'prevented_stampede' ? 'Prevented stampede' : action.impact}
                        </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {actions.length > 0 && (
        <div className="grid grid-cols-4 gap-4 pt-4 border-t border-slate-700">
          <div className="text-center">
            <div className="text-xl font-bold text-slate-200">{actions.length}</div>
            <div className="text-xs text-slate-500">Total Actions</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-red-400">
              {actions.filter(a => a.severity === 'CRITICAL').length}
            </div>
            <div className="text-xs text-slate-500">Critical</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-amber-400">
              {actions.filter(a => a.severity === 'WARNING').length}
            </div>
            <div className="text-xs text-slate-500">Warnings</div>
          </div>
          <div className="text-center">
            <div className="text-xl font-bold text-emerald-400">
              {actions.filter(a => a.impact === 'prevented_stampede').length}
            </div>
            <div className="text-xs text-slate-500">Lives Saved</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIActionLogger;
