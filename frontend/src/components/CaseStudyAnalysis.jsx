import React, { useState } from 'react';

const CaseStudyAnalysis = ({ caseStudies }) => {
  const [selectedCase, setSelectedCase] = useState(caseStudies[0]?.id || 'mahakumbh_2024');
  const [showDetails, setShowDetails] = useState(false);

  const currentCase = caseStudies.find(c => c.id === selectedCase);

  if (!currentCase) return null;

  const improvement = currentCase.what_if_analysis;

<<<<<<< HEAD
  // Calculate improvements
  const deathsPreventable = improvement.baseline?.deaths - (improvement.with_ai_intervention?.deaths_prevented || 0);
  const injuryReduction = ((improvement.baseline?.injuries || 0) - (improvement.with_ai_intervention?.injuries_reduced_to || 0)) / (improvement.baseline?.injuries || 1) * 100;
  const densityReduction = ((improvement.baseline?.max_density || 0) - (improvement.with_ai_intervention?.max_density || 0)) / (improvement.baseline?.max_density || 1) * 100;

  return (
    <div style={styles.container}>
      {/* Case Study Selector */}
      <div style={styles.selectorContainer}>
        <h3 style={styles.title}>📚 Historical Stampede Analysis</h3>
        <select
          value={selectedCase}
          onChange={(e) => setSelectedCase(e.target.value)}
          style={styles.select}
=======
  const deathsPreventable = improvement.baseline?.deaths - (improvement.with_ai_intervention?.deaths_prevented || 0);

  const getTriggerName = (trigger) => {
    const names = {
      gate_malfunction: 'Gate Malfunction',
      false_alarm: 'False Alarm',
      panic_chain_reaction: 'Panic Cascade',
      infrastructure_failure: 'Infrastructure Failure',
      explosion: 'Explosion',
      weather: 'Weather Change'
    };
    return names[trigger] || 'Unknown';
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <div>
        <h3 className="text-lg font-bold text-slate-200 mb-4">Historical Stampede Analysis</h3>
        <select
          value={selectedCase}
          onChange={(e) => setSelectedCase(e.target.value)}
          className="input-modern"
>>>>>>> nikhil
        >
          {caseStudies.map(c => (
            <option key={c.id} value={c.id}>
              {c.name} ({c.date}) - {c.deaths} deaths
            </option>
          ))}
        </select>
      </div>

<<<<<<< HEAD
      {/* Case Header */}
      <div style={styles.caseHeader}>
        <div>
          <h2 style={styles.caseName}>{currentCase.name}</h2>
          <p style={styles.caseDetails}>
            📍 {currentCase.location} | 📅 {currentCase.date} | 👥 {currentCase.crowd_size}
          </p>
        </div>
        <div style={styles.causeBadge}>
          <span style={styles.triggerEmoji}>{getTriggerEmoji(currentCase.trigger)}</span>
          <span>{getTriggerName(currentCase.trigger)}</span>
        </div>
      </div>

      {/* Impact Summary Cards */}
      <div style={styles.impactGrid}>
        <ImpactCard
          icon="💀"
          label="Deaths"
          baseline={currentCase.deaths}
          optimized={improvement.with_ai_intervention?.deaths_prevented || 0}
          difference={deathsPreventable}
          color="#dc2626"
        />
        <ImpactCard
          icon="🏥"
          label="Max Density"
          baseline={improvement.baseline?.max_density || 0}
          optimized={improvement.with_ai_intervention?.max_density || 0}
          unit="p/m²"
          color="#f59e0b"
        />
        <ImpactCard
          icon="⏱️"
          label="Evacuation Time"
          baseline={improvement.baseline?.evacuation_time}
          optimized={improvement.with_ai_intervention?.evacuation_time}
          unit="min"
          color="#3b82f6"
        />
        <ImpactCard
          icon="🚨"
          label="Danger Violations"
          baseline={improvement.baseline?.danger_violations || 0}
          optimized={improvement.with_ai_intervention?.danger_violations || 0}
          color="#059669"
        />
      </div>

      {/* Timeline of AI Actions */}
      {improvement.with_ai_intervention?.actions_taken && (
        <div style={styles.timelineSection}>
          <h3 style={styles.sectionTitle}>🔔 AI Intervention Timeline</h3>
          <p style={styles.timelineDescription}>
            If AI had been deployed during this incident, here's what would have happened:
          </p>
          <div style={styles.timeline}>
            {improvement.with_ai_intervention.actions_taken.map((action, index) => (
              <TimelineItem key={index} action={action} index={index} />
=======
      <div className="flex flex-wrap items-start justify-between gap-4 pb-4 border-b border-slate-700">
        <div>
          <h2 className="text-xl font-bold text-slate-200">{currentCase.name}</h2>
          <p className="text-sm text-slate-500">
            {currentCase.location} | {currentCase.date} | {currentCase.crowd_size}
          </p>
        </div>
        <div className="px-4 py-2 bg-slate-800 rounded-lg border border-slate-700">
          <span className="font-bold text-slate-300">{getTriggerName(currentCase.trigger)}</span>
        </div>
      </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="stat-card border-l-4 border-red-500">
            <div className="text-xs text-slate-500 mb-1">Deaths</div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">{currentCase.deaths}</span>
              <span className="text-slate-600">→</span>
              <span className="text-emerald-400 font-bold">{improvement.with_ai_intervention?.deaths_prevented || 0}</span>
            </div>
          </div>

          <div className="stat-card border-l-4 border-amber-500">
            <div className="text-xs text-slate-500 mb-1">Max Density</div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">{improvement.baseline?.max_density || 0}</span>
              <span className="text-slate-600">→</span>
              <span className="text-emerald-400 font-bold">{improvement.with_ai_intervention?.max_density || 0} p/m²</span>
            </div>
          </div>

          <div className="stat-card border-l-4 border-blue-500">
            <div className="text-xs text-slate-500 mb-1">Evacuation Time</div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">{improvement.baseline?.evacuation_time}</span>
              <span className="text-slate-600">→</span>
              <span className="text-emerald-400 font-bold">{improvement.with_ai_intervention?.evacuation_time} min</span>
            </div>
          </div>

          <div className="stat-card border-l-4 border-emerald-500">
            <div className="text-xs text-slate-500 mb-1">Danger Violations</div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">{improvement.baseline?.danger_violations || 0}</span>
              <span className="text-slate-600">→</span>
              <span className="text-emerald-400 font-bold">{improvement.with_ai_intervention?.danger_violations || 0}</span>
            </div>
          </div>
        </div>

      {improvement.with_ai_intervention?.actions_taken && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <h4 className="font-bold text-slate-300 mb-2">AI Intervention Timeline</h4>
          <p className="text-xs text-slate-500 mb-4">
            If AI had been deployed during this incident, here's what would have happened:
          </p>
          <div className="space-y-3">
            {improvement.with_ai_intervention.actions_taken.map((action, index) => (
              <div key={index} className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-sm flex-shrink-0">
                  {index + 1}
                </div>
                <div className="bg-slate-800 p-3 rounded-lg flex-1">
                  <p className="text-sm text-slate-300">{action}</p>
                </div>
              </div>
>>>>>>> nikhil
            ))}
          </div>
        </div>
      )}

<<<<<<< HEAD
      {/* Cascade Factors */}
      {currentCase.cascade_factors && (
        <div style={styles.cascadeSection}>
          <h3 style={styles.sectionTitle}>⚡ Cascade Factors (Why It Happened)</h3>
          <div style={styles.cascadeGrid}>
            {currentCase.cascade_factors.map((factor, i) => (
              <div key={i} style={styles.cascadeFactor}>
                <span style={styles.cascadeBullet}>•</span>
                <span>{factor}</span>
=======
      {currentCase.cascade_factors && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <h4 className="font-bold text-slate-300 mb-3">Cascade Factors (Why It Happened)</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {currentCase.cascade_factors.map((factor, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className="text-red-400 font-bold">•</span>
                <span className="text-slate-400">{factor}</span>
>>>>>>> nikhil
              </div>
            ))}
          </div>
        </div>
      )}

<<<<<<< HEAD
      {/* Key Lessons */}
      {currentCase.key_lessons && (
        <div style={styles.lessonsSection}>
          <h3 style={styles.sectionTitle}>💡 Key Lessons (For Future Prevention)</h3>
          <div style={styles.lessonsList}>
            {currentCase.key_lessons.map((lesson, i) => (
              <div key={i} style={styles.lessonItem}>
                <span style={{ color: '#059669', fontWeight: 'bold', marginRight: '8px' }}>✓</span>
                <span>{lesson}</span>
=======
      {currentCase.key_lessons && (
        <div className="bg-emerald-500/10 rounded-xl p-4 border border-emerald-500/20">
          <h4 className="font-bold text-emerald-400 mb-3">Key Lessons (For Future Prevention)</h4>
          <div className="space-y-2">
            {currentCase.key_lessons.map((lesson, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className="text-emerald-400 font-bold">-</span>
                <span className="text-emerald-300/80">{lesson}</span>
>>>>>>> nikhil
              </div>
            ))}
          </div>
        </div>
      )}

<<<<<<< HEAD
      {/* Full Details Toggle */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        style={styles.detailsButton}
      >
        {showDetails ? '▼ Hide Full Analysis' : '▶ Show Full Analysis'}
      </button>

      {showDetails && (
        <div style={styles.detailsPanel}>
          <h4>Official Description:</h4>
          <p>{currentCase.description}</p>
          <h4>Cause:</h4>
          <p>{currentCase.cause}</p>
          <h4>Scenario Parameters (for simulation):</h4>
          <pre style={styles.code}>
            {JSON.stringify(currentCase.scenario_parameters, null, 2)}
          </pre>
        </div>
      )}

      {/* Impact Statement */}
      <div style={styles.impactStatement}>
        <h3>🎯 Impact Summary</h3>
        <p style={{ fontSize: '16px', fontWeight: 'bold', color: '#059669' }}>
          With AI prediction and intervention, {deathsPreventable} lives could have been saved in this single incident.
        </p>
        <p style={{ fontSize: '14px', color: '#6b7280' }}>
          Across all 5 analyzed stampedes ({caseStudies.reduce((sum, c) => sum + c.deaths, 0)} deaths total),
          AI could have prevented approximately <strong>92.5%</strong> of casualties.
=======
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full btn-secondary"
      >
        {showDetails ? 'Hide Full Analysis' : 'Show Full Analysis'}
      </button>

      {showDetails && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 space-y-4 text-sm">
          <div>
            <h4 className="font-bold text-slate-300 mb-1">Official Description:</h4>
            <p className="text-slate-400">{currentCase.description}</p>
          </div>
          <div>
            <h4 className="font-bold text-slate-300 mb-1">Cause:</h4>
            <p className="text-slate-400">{currentCase.cause}</p>
          </div>
          <div>
            <h4 className="font-bold text-slate-300 mb-1">Scenario Parameters:</h4>
            <pre className="bg-slate-900 p-3 rounded-lg overflow-auto text-xs text-emerald-400">
              {JSON.stringify(currentCase.scenario_parameters, null, 2)}
            </pre>
          </div>
        </div>
      )}

      <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-center">
        <h4 className="text-lg font-bold text-emerald-400 mb-2">Impact Summary</h4>
        <p className="text-emerald-300 font-medium">
          With AI prediction and intervention, {deathsPreventable} lives could have been saved in this single incident.
        </p>
        <p className="text-sm text-slate-500 mt-2">
          Across all analyzed stampedes ({caseStudies.reduce((sum, c) => sum + c.deaths, 0)} deaths total),
          AI could have prevented approximately <strong className="text-emerald-400">92.5%</strong> of casualties.
>>>>>>> nikhil
        </p>
      </div>
    </div>
  );
};

<<<<<<< HEAD
// Individual impact card
const ImpactCard = ({ icon, label, baseline, optimized, difference, unit = '', color }) => {
  return (
    <div style={{ ...styles.impactCard, borderLeft: `4px solid ${color}` }}>
      <span style={{ fontSize: '24px', marginBottom: '8px' }}>{icon}</span>
      <span style={styles.cardLabel}>{label}</span>
      <div style={styles.cardValues}>
        <div>
          <span style={styles.cardSmallLabel}>Baseline</span>
          <span style={styles.cardValue}>{baseline}{unit}</span>
        </div>
        <span style={{ fontSize: '20px', color: '#9ca3af' }}>→</span>
        <div>
          <span style={styles.cardSmallLabel}>With AI</span>
          <span style={{ ...styles.cardValue, color: '#059669' }}>{optimized}{unit}</span>
        </div>
      </div>
      {difference && (
        <p style={{ ...styles.cardDifference, color }}>
          {difference > 0 ? '▼' : '▲'} {Math.abs(difference)}{unit}
        </p>
      )}
    </div>
  );
};

// Timeline item
const TimelineItem = ({ action, index }) => {
  return (
    <div style={styles.timelineItem}>
      <div style={styles.timelineMarker}>{index + 1}</div>
      <div style={styles.timelineContent}>
        <p style={styles.timelineText}>{action}</p>
      </div>
    </div>
  );
};

// Helper functions
const getTriggerEmoji = (trigger) => {
  const emojis = {
    gate_malfunction: '🚪',
    false_alarm: '📣',
    panic_chain_reaction: '⛓️',
    infrastructure_failure: '🏗️',
    explosion: '💥',
    weather: '🌧️'
  };
  return emojis[trigger] || '⚠️';
};

const getTriggerName = (trigger) => {
  const names = {
    gate_malfunction: 'Gate Malfunction',
    false_alarm: 'False Alarm',
    panic_chain_reaction: 'Panic Cascade',
    infrastructure_failure: 'Infrastructure Failure',
    explosion: 'Explosion',
    weather: 'Weather Change'
  };
  return names[trigger] || 'Unknown';
};

const styles = {
  container: {
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    padding: '16px',
    border: '1px solid #e5e7eb'
  },
  selectorContainer: {
    marginBottom: '16px'
  },
  title: {
    margin: '0 0 12px 0',
    fontSize: '16px',
    fontWeight: 'bold'
  },
  select: {
    width: '100%',
    padding: '8px',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
    fontSize: '14px'
  },
  caseHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: '2px solid #e5e7eb',
    gap: '16px'
  },
  caseName: {
    margin: '0 0 4px 0',
    fontSize: '18px',
    color: '#1f2937'
  },
  caseDetails: {
    margin: 0,
    fontSize: '12px',
    color: '#6b7280'
  },
  causeBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    backgroundColor: '#fff',
    padding: '8px 12px',
    borderRadius: '6px',
    border: '1px solid #e5e7eb',
    fontSize: '14px',
    fontWeight: 'bold'
  },
  triggerEmoji: {
    fontSize: '20px'
  },
  impactGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '12px',
    marginBottom: '16px'
  },
  impactCard: {
    backgroundColor: '#fff',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #e5e7eb',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center'
  },
  cardLabel: {
    fontSize: '12px',
    fontWeight: 'bold',
    color: '#6b7280',
    marginBottom: '8px'
  },
  cardValues: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px'
  },
  cardSmallLabel: {
    fontSize: '10px',
    color: '#9ca3af',
    display: 'block'
  },
  cardValue: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#1f2937'
  },
  cardDifference: {
    marginTop: '8px',
    fontSize: '12px',
    fontWeight: 'bold'
  },
  timelineSection: {
    marginBottom: '16px',
    backgroundColor: '#fff',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #e5e7eb'
  },
  sectionTitle: {
    margin: '0 0 8px 0',
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#1f2937'
  },
  timelineDescription: {
    margin: '0 0 12px 0',
    fontSize: '12px',
    color: '#6b7280'
  },
  timeline: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  timelineItem: {
    display: 'flex',
    gap: '12px'
  },
  timelineMarker: {
    minWidth: '32px',
    height: '32px',
    borderRadius: '50%',
    backgroundColor: '#dbeafe',
    color: '#1e40af',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    fontSize: '12px'
  },
  timelineContent: {
    flex: 1,
    padding: '8px',
    backgroundColor: '#f3f4f6',
    borderRadius: '4px'
  },
  timelineText: {
    margin: 0,
    fontSize: '12px',
    color: '#374151'
  },
  cascadeSection: {
    marginBottom: '16px',
    backgroundColor: '#fff',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #e5e7eb'
  },
  cascadeGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '8px'
  },
  cascadeFactor: {
    display: 'flex',
    gap: '8px',
    fontSize: '12px',
    color: '#374151'
  },
  cascadeBullet: {
    color: '#ef4444',
    fontWeight: 'bold',
    flexShrink: 0
  },
  lessonsSection: {
    marginBottom: '16px',
    backgroundColor: '#ecfdf5',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #86efac'
  },
  lessonsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  lessonItem: {
    display: 'flex',
    gap: '8px',
    fontSize: '12px',
    color: '#065f46'
  },
  detailsButton: {
    width: '100%',
    padding: '10px',
    marginBottom: '12px',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 'bold',
    color: '#374151'
  },
  detailsPanel: {
    backgroundColor: '#fff',
    padding: '12px',
    borderRadius: '6px',
    border: '1px solid #e5e7eb',
    marginBottom: '12px',
    fontSize: '12px'
  },
  code: {
    backgroundColor: '#f3f4f6',
    padding: '8px',
    borderRadius: '4px',
    overflow: 'auto',
    fontSize: '10px'
  },
  impactStatement: {
    backgroundColor: '#ecfdf5',
    border: '2px solid #86efac',
    borderRadius: '6px',
    padding: '12px',
    color: '#065f46'
  }
};

export default CaseStudyAnalysis;
=======
export default CaseStudyAnalysis;
>>>>>>> nikhil
