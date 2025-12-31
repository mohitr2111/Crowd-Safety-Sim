import React, { useState, useEffect } from 'react';

const AIActionLogger = ({ simulationData, stampedePrediction }) => {
  const [expandedAction, setExpandedAction] = useState(null);
  const [filterLevel, setFilterLevel] = useState('all'); // all, critical, warning, info

  if (!simulationData) return null;

  const actions = simulationData.ai_actions || [];

  // Filter actions by level
  const filteredActions = actions.filter(action => {
    if (filterLevel === 'all') return true;
    return action.severity === filterLevel;
  });

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
    }
  };

  return (
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
          </div>
        </div>
      )}

      {/* Filter Controls */}
      <div style={styles.filterContainer}>
        {['all', 'CRITICAL', 'WARNING', 'INFO'].map(level => (
          <button
            key={level}
            onClick={() => setFilterLevel(level)}
            style={{
              ...styles.filterButton,
              backgroundColor: filterLevel === level ? getSeverityColor(level) : '#e5e7eb',
              color: filterLevel === level ? '#fff' : '#374151',
              fontWeight: filterLevel === level ? 'bold' : 'normal'
            }}
          >
            {level === 'all' ? 'All Actions' : level}
            {level !== 'all' && ` (${actions.filter(a => a.severity === level).length})`}
          </button>
        ))}
      </div>

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
          ))
        )}
      </div>

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
        </div>
      )}
    </div>
  );
};

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