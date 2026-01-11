<<<<<<< HEAD
import React, { useState, useEffect } from 'react';

const AIActionLogger = ({ simulationData, stampedePrediction }) => {
  const [expandedAction, setExpandedAction] = useState(null);
  const [filterLevel, setFilterLevel] = useState('all'); // all, critical, warning, info
=======
import React, { useState } from 'react';

const AIActionLogger = ({ simulationData, stampedePrediction }) => {
  const [expandedAction, setExpandedAction] = useState(null);
  const [filterLevel, setFilterLevel] = useState('all');
>>>>>>> nikhil

  if (!simulationData) return null;

  const actions = simulationData.ai_actions || [];

<<<<<<< HEAD
  // Filter actions by level
=======
>>>>>>> nikhil
  const filteredActions = actions.filter(action => {
    if (filterLevel === 'all') return true;
    return action.severity === filterLevel;
  });

<<<<<<< HEAD
  // Action severity colors
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return '#dc2626'; // Red
      case 'WARNING': return '#f59e0b'; // Orange
      case 'INFO': return '#3b82f6'; // Blue
      default: return '#6b7280';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'CRITICAL': return '🚨';
      case 'WARNING': return '⚠️';
      case 'INFO': return 'ℹ️';
      default: return '•';
=======
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL': return 'red';
      case 'WARNING': return 'amber';
      case 'INFO': return 'blue';
      default: return 'slate';
>>>>>>> nikhil
    }
  };

  return (
<<<<<<< HEAD
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h3 style={styles.title}>🤖 AI Real-Time Intervention Log</h3>
        <p style={styles.subtitle}>Shows every action taken to prevent stampede</p>
      </div>

      {/* Stampede Prediction Alert */}
      {stampedePrediction && (
        <div style={styles.predictionAlert}>
          <div style={styles.predictionContent}>
            <div style={styles.predictionMain}>
              <span style={styles.predictionPercent}>
                {stampedePrediction.stampede_probability}%
              </span>
              <span style={styles.predictionLabel}>Stampede Risk</span>
            </div>
            <div style={styles.predictionDetails}>
              <p>⏱️ <strong>{stampedePrediction.minutes_until_critical}</strong> minutes until critical</p>
              <p>🎯 Max Density: <strong>{stampedePrediction.max_density}</strong> p/m²</p>
              <p style={{ color: '#16a34a', fontWeight: 'bold' }}>
                💡 {stampedePrediction.recommendation}
              </p>
            </div>
          </div>
          <div style={{
            fontSize: '48px',
            opacity: stampedePrediction.stampede_probability > 70 ? 0.9 : 0.3,
            animation: stampedePrediction.stampede_probability > 70 ? 'pulse 1s infinite' : 'none'
          }}>
            ⚠️
=======
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
>>>>>>> nikhil
          </div>
        </div>
      )}

<<<<<<< HEAD
      {/* Filter Controls */}
      <div style={styles.filterContainer}>
=======
      <div className="flex flex-wrap gap-2">
>>>>>>> nikhil
        {['all', 'CRITICAL', 'WARNING', 'INFO'].map(level => (
          <button
            key={level}
            onClick={() => setFilterLevel(level)}
<<<<<<< HEAD
            style={{
              ...styles.filterButton,
              backgroundColor: filterLevel === level ? getSeverityColor(level) : '#e5e7eb',
              color: filterLevel === level ? '#fff' : '#374151',
              fontWeight: filterLevel === level ? 'bold' : 'normal'
            }}
=======
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filterLevel === level
                ? level === 'CRITICAL' ? 'bg-red-500 text-white' :
                  level === 'WARNING' ? 'bg-amber-500 text-white' :
                  level === 'INFO' ? 'bg-blue-500 text-white' :
                  'bg-slate-600 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
>>>>>>> nikhil
          >
            {level === 'all' ? 'All Actions' : level}
            {level !== 'all' && ` (${actions.filter(a => a.severity === level).length})`}
          </button>
        ))}
      </div>

<<<<<<< HEAD
      {/* Actions List */}
      <div style={styles.actionsList}>
        {filteredActions.length === 0 ? (
          <div style={styles.emptyState}>
            <p>✅ No {filterLevel !== 'all' ? filterLevel.toLowerCase() : ''} actions yet</p>
            <p style={{ fontSize: '12px', color: '#9ca3af' }}>AI is monitoring crowd...</p>
          </div>
        ) : (
          filteredActions.map((action, index) => (
            <ActionCard
              key={index}
              action={action}
              isExpanded={expandedAction === index}
              onToggle={() => setExpandedAction(expandedAction === index ? null : index)}
              getSeverityColor={getSeverityColor}
              getSeverityIcon={getSeverityIcon}
            />
=======
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
>>>>>>> nikhil
          ))
        )}
      </div>

<<<<<<< HEAD
      {/* Summary Statistics */}
      {actions.length > 0 && (
        <div style={styles.summary}>
          <div style={styles.summaryItem}>
            <span style={{ fontSize: '20px' }}>{actions.length}</span>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>Total Actions</span>
          </div>
          <div style={styles.summaryItem}>
            <span style={{ fontSize: '20px', color: '#dc2626' }}>
              {actions.filter(a => a.severity === 'CRITICAL').length}
            </span>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>Critical</span>
          </div>
          <div style={styles.summaryItem}>
            <span style={{ fontSize: '20px', color: '#f59e0b' }}>
              {actions.filter(a => a.severity === 'WARNING').length}
            </span>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>Warnings</span>
          </div>
          <div style={styles.summaryItem}>
            <span style={{ fontSize: '20px', color: '#059669' }}>
              {actions.filter(a => a.impact === 'prevented_stampede').length}
            </span>
            <span style={{ fontSize: '12px', color: '#6b7280' }}>Lives Saved</span>
          </div>
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.8; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};

// Individual action card
const ActionCard = ({ action, isExpanded, onToggle, getSeverityColor, getSeverityIcon }) => {
  return (
    <div
      style={{
        ...styles.actionCard,
        borderLeft: `4px solid ${getSeverityColor(action.severity)}`
      }}
      onClick={onToggle}
    >
      {/* Action Header */}
      <div style={styles.actionHeader}>
        <div style={styles.actionTitle}>
          <span style={{ fontSize: '18px', marginRight: '8px' }}>
            {getSeverityIcon(action.severity)}
          </span>
          <strong>{action.action}</strong>
          <span style={styles.timeStamp}>{action.time_seconds.toFixed(1)}s</span>
        </div>
        <span style={{ fontSize: '12px', color: '#6b7280' }}>
          {isExpanded ? '▼' : '▶'}
        </span>
      </div>

      {/* Zone and Density */}
      <div style={styles.actionDetails}>
        <span>📍 <strong>{action.zone}</strong></span>
        <span>•</span>
        <span>👥 {action.density.toFixed(2)} p/m²</span>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div style={styles.expandedContent}>
          <div style={styles.detailRow}>
            <span style={styles.label}>Action Type:</span>
            <span style={styles.value}>{action.action_type}</span>
          </div>

          <div style={styles.detailRow}>
            <span style={styles.label}>Effect:</span>
            <span style={styles.value}>{action.expected_effect}</span>
          </div>

          <div style={styles.detailRow}>
            <span style={styles.label}>Confidence:</span>
            <div style={styles.confidenceBar}>
              <div
                style={{
                  width: `${action.confidence * 100}%`,
                  height: '100%',
                  backgroundColor: '#059669',
                  borderRadius: '4px',
                  transition: 'width 0.3s ease'
                }}
              />
            </div>
            <span style={styles.value}>{(action.confidence * 100).toFixed(0)}%</span>
          </div>

          <div style={styles.detailRow}>
            <span style={styles.label}>Recommendation:</span>
            <span style={styles.recommendation}>{action.recommendation}</span>
          </div>

          {action.impact && (
            <div style={styles.detailRow}>
              <span style={styles.label}>Impact:</span>
              <span style={{
                ...styles.value,
                color: action.impact === 'prevented_stampede' ? '#059669' : '#f59e0b',
                fontWeight: 'bold'
              }}>
                {action.impact === 'prevented_stampede' ? '✅ Prevented stampede' : '⚠️ ' + action.impact}
              </span>
            </div>
          )}
=======
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
>>>>>>> nikhil
        </div>
      )}
    </div>
  );
};

<<<<<<< HEAD
const styles = {
  container: {
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    padding: '16px',
    border: '1px solid #e5e7eb'
  },
  header: {
    marginBottom: '16px',
    paddingBottom: '8px',
    borderBottom: '1px solid #e5e7eb'
  },
  title: {
    margin: '0 0 4px 0',
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#1f2937'
  },
  subtitle: {
    margin: 0,
    fontSize: '12px',
    color: '#6b7280'
  },
  predictionAlert: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fef2f2',
    border: '2px solid #fca5a5',
    borderRadius: '6px',
    padding: '12px',
    marginBottom: '12px',
    gap: '12px'
  },
  predictionContent: {
    flex: 1,
    display: 'flex',
    gap: '16px',
    alignItems: 'flex-start'
  },
  predictionMain: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '80px'
  },
  predictionPercent: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#dc2626'
  },
  predictionLabel: {
    fontSize: '11px',
    color: '#991b1b'
  },
  predictionDetails: {
    flex: 1,
    fontSize: '13px',
    color: '#374151',
    gap: '4px'
  },
  filterContainer: {
    display: 'flex',
    gap: '8px',
    marginBottom: '12px',
    flexWrap: 'wrap'
  },
  filterButton: {
    padding: '6px 12px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    transition: 'all 0.2s ease'
  },
  actionsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    maxHeight: '400px',
    overflowY: 'auto',
    marginBottom: '12px'
  },
  actionCard: {
    backgroundColor: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '4px',
    padding: '10px',
    cursor: 'pointer',
    transition: 'box-shadow 0.2s ease',
    ':hover': {
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }
  },
  actionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '6px'
  },
  actionTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '13px',
    fontWeight: 'bold',
    color: '#1f2937'
  },
  timeStamp: {
    fontSize: '11px',
    color: '#9ca3af',
    fontWeight: 'normal',
    marginLeft: '8px'
  },
  actionDetails: {
    fontSize: '11px',
    color: '#6b7280',
    display: 'flex',
    gap: '8px',
    alignItems: 'center'
  },
  expandedContent: {
    marginTop: '10px',
    paddingTop: '10px',
    borderTop: '1px solid #f3f4f6',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  detailRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px'
  },
  label: {
    fontWeight: 'bold',
    color: '#6b7280',
    minWidth: '100px'
  },
  value: {
    color: '#374151',
    flex: 1
  },
  recommendation: {
    color: '#059669',
    fontStyle: 'italic',
    flex: 1
  },
  confidenceBar: {
    flex: 1,
    height: '6px',
    backgroundColor: '#e5e7eb',
    borderRadius: '3px',
    overflow: 'hidden'
  },
  summary: {
    display: 'flex',
    gap: '16px',
    padding: '12px',
    backgroundColor: '#f3f4f6',
    borderRadius: '4px',
    justifyContent: 'space-around'
  },
  summaryItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px'
  },
  emptyState: {
    textAlign: 'center',
    padding: '20px',
    color: '#9ca3af'
  }
};

export default AIActionLogger;
=======
export default AIActionLogger;
>>>>>>> nikhil
