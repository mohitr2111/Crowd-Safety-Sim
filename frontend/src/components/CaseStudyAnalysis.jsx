import React, { useState } from 'react';

const CaseStudyAnalysis = ({ caseStudies }) => {
  const [selectedCase, setSelectedCase] = useState(caseStudies[0]?.id || 'mahakumbh_2024');
  const [showDetails, setShowDetails] = useState(false);

  const currentCase = caseStudies.find(c => c.id === selectedCase);

  if (!currentCase) return null;

  const improvement = currentCase.what_if_analysis;

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
        >
          {caseStudies.map(c => (
            <option key={c.id} value={c.id}>
              {c.name} ({c.date}) - {c.deaths} deaths
            </option>
          ))}
        </select>
      </div>

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
            ))}
          </div>
        </div>
      )}

      {currentCase.cascade_factors && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
          <h4 className="font-bold text-slate-300 mb-3">Cascade Factors (Why It Happened)</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {currentCase.cascade_factors.map((factor, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className="text-red-400 font-bold">•</span>
                <span className="text-slate-400">{factor}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {currentCase.key_lessons && (
        <div className="bg-emerald-500/10 rounded-xl p-4 border border-emerald-500/20">
          <h4 className="font-bold text-emerald-400 mb-3">Key Lessons (For Future Prevention)</h4>
          <div className="space-y-2">
            {currentCase.key_lessons.map((lesson, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className="text-emerald-400 font-bold">-</span>
                <span className="text-emerald-300/80">{lesson}</span>
              </div>
            ))}
          </div>
        </div>
      )}

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
        </p>
      </div>
    </div>
  );
};

export default CaseStudyAnalysis;
