import React, { useState } from 'react';

const TriggerTimeline = ({ triggers, setTriggers, eventConfig, onStart, onBack }) => {
  const [selectedTrigger, setSelectedTrigger] = useState('');
  const [triggerStep, setTriggerStep] = useState(100);
  const [triggerParams, setTriggerParams] = useState({});

  // Available trigger types (from backend event_triggers.py)
  const triggerTypes = {
    vip_delayed: {
      name: 'VIP Delay',
      icon: '⏰',
      description: 'Political leader or VIP arrives late',
      severity: 'moderate',
      params: [
        { key: 'delay_hours', label: 'Delay Duration (hours)', type: 'number', default: 2, min: 0.5, max: 5, step: 0.5 }
      ]
    },
    fire_outbreak: {
      name: 'Fire Outbreak',
      icon: '🔥',
      description: 'Fire starts at specific location',
      severity: 'critical',
      params: [
        { key: 'location', label: 'Fire Location', type: 'text', default: 'stage' },
        { key: 'severity', label: 'Fire Severity (0-1)', type: 'number', default: 0.9, min: 0.1, max: 1.0, step: 0.1 }
      ]
    },
    explosion: {
      name: 'Explosion',
      icon: '💥',
      description: 'Sudden explosion or blast',
      severity: 'critical',
      params: [
        { key: 'location', label: 'Explosion Location', type: 'text', default: 'entrance' },
        { key: 'casualties', label: 'Immediate Casualties', type: 'number', default: 0, min: 0, max: 100, step: 1 }
      ]
    },
    gate_malfunction: {
      name: 'Gate Malfunction',
      icon: '🚪',
      description: 'Entry or exit gate stops working',
      severity: 'moderate',
      params: [
        { key: 'gate_id', label: 'Gate ID', type: 'text', default: 'gate_a' },
        { key: 'duration_minutes', label: 'Duration (minutes)', type: 'number', default: 20, min: 5, max: 60, step: 5 }
      ]
    },
    weather_change: {
      name: 'Weather Change',
      icon: '🌧️',
      description: 'Sudden rain, storm, or extreme weather',
      severity: 'moderate',
      params: [
        { key: 'weather_type', label: 'Weather Type', type: 'select', default: 'rain', options: ['rain', 'storm', 'heat_wave'] },
        { key: 'duration_minutes', label: 'Duration (minutes)', type: 'number', default: 30, min: 10, max: 120, step: 10 }
      ]
    },
    structural_collapse: {
      name: 'Structural Collapse',
      icon: '🏗️',
      description: 'Stage, barrier, or ceiling collapses',
      severity: 'critical',
      params: [
        { key: 'location', label: 'Collapse Location', type: 'text', default: 'stage' }
      ]
    },
    medical_emergency: {
      name: 'Medical Emergency',
      icon: '🚑',
      description: 'Someone collapses, crowd panics',
      severity: 'low',
      params: [
        { key: 'location', label: 'Location', type: 'text', default: 'main_area' }
      ]
    },
    bomb_threat: {
      name: 'Bomb Threat',
      icon: '💣',
      description: 'Bomb threat received, evacuation needed',
      severity: 'critical',
      params: [
        { key: 'credibility', label: 'Threat Credibility (0-1)', type: 'number', default: 0.7, min: 0.1, max: 1.0, step: 0.1 }
      ]
    },
    rumor_spread: {
      name: 'Rumor/False Alarm',
      icon: '📢',
      description: 'False rumor spreads causing panic',
      severity: 'moderate',
      params: [
        { key: 'rumor', label: 'Rumor Content', type: 'text', default: 'Security threat reported' },
        { key: 'spread_rate', label: 'Spread Rate (0-1)', type: 'number', default: 0.7, min: 0.1, max: 1.0, step: 0.1 }
      ]
    }
  };

  // Add trigger
  const addTrigger = () => {
    if (!selectedTrigger) {
      alert('Please select a trigger type');
      return;
    }

    const newTrigger = {
      id: `trigger_${Date.now()}`,
      type: selectedTrigger,
      step: triggerStep,
      params: { ...triggerParams },
      name: triggerTypes[selectedTrigger].name
    };

    setTriggers(prev => [...prev, newTrigger].sort((a, b) => a.step - b.step));
    
    // Reset form
    setSelectedTrigger('');
    setTriggerStep(100);
    setTriggerParams({});
  };

  // Delete trigger
  const deleteTrigger = (triggerId) => {
    setTriggers(prev => prev.filter(t => t.id !== triggerId));
  };

  // Update params when trigger type changes
  const handleTriggerTypeChange = (type) => {
    setSelectedTrigger(type);
    
    // Set default params
    const defaults = {};
    triggerTypes[type].params.forEach(param => {
      defaults[param.key] = param.default;
    });
    setTriggerParams(defaults);
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">⚡ Add Event Triggers</h2>

      <div className="grid grid-cols-2 gap-6">
        {/* Left: Add Trigger */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
          <h3 className="font-semibold text-lg mb-4">➕ Add New Trigger</h3>

          {/* Trigger Type Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trigger Type
            </label>
            <select
              value={selectedTrigger}
              onChange={(e) => handleTriggerTypeChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select trigger type...</option>
              {Object.entries(triggerTypes).map(([key, trigger]) => (
                <option key={key} value={key}>
                  {trigger.icon} {trigger.name}
                </option>
              ))}
            </select>
          </div>

          {/* Trigger Description */}
          {selectedTrigger && (
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700">
                {triggerTypes[selectedTrigger].description}
              </p>
              <span className={`inline-block mt-2 px-2 py-1 text-xs rounded ${
                triggerTypes[selectedTrigger].severity === 'critical' ? 'bg-red-100 text-red-700' :
                triggerTypes[selectedTrigger].severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                'bg-green-100 text-green-700'
              }`}>
                {triggerTypes[selectedTrigger].severity.toUpperCase()} SEVERITY
              </span>
            </div>
          )}

          {/* Trigger Timing */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trigger at Step (30s per step)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="number"
                value={triggerStep}
                onChange={(e) => setTriggerStep(parseInt(e.target.value))}
                min="0"
                max="500"
                step="10"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
              />
              <span className="text-sm text-gray-600">
                (~{(triggerStep * 0.5).toFixed(0)} min)
              </span>
            </div>
          </div>

          {/* Dynamic Parameters */}
          {selectedTrigger && triggerTypes[selectedTrigger].params.map(param => (
            <div key={param.key} className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {param.label}
              </label>
              
              {param.type === 'select' ? (
                <select
                  value={triggerParams[param.key] || param.default}
                  onChange={(e) => setTriggerParams(prev => ({
                    ...prev,
                    [param.key]: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {param.options.map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : param.type === 'number' ? (
                <input
                  type="number"
                  value={triggerParams[param.key] ?? param.default}
                  onChange={(e) => setTriggerParams(prev => ({
                    ...prev,
                    [param.key]: parseFloat(e.target.value)
                  }))}
                  min={param.min}
                  max={param.max}
                  step={param.step}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              ) : (
                <input
                  type="text"
                  value={triggerParams[param.key] || param.default}
                  onChange={(e) => setTriggerParams(prev => ({
                    ...prev,
                    [param.key]: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              )}
            </div>
          ))}

          {/* Add Button */}
          <button
            onClick={addTrigger}
            disabled={!selectedTrigger}
            className={`w-full px-4 py-2 rounded-lg font-medium ${
              selectedTrigger
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            ➕ Add Trigger
          </button>
        </div>

        {/* Right: Timeline */}
        <div>
          <h3 className="font-semibold text-lg mb-4">
            📅 Event Timeline ({triggers.length} triggers)
          </h3>

          {triggers.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <p className="text-6xl mb-4">⏰</p>
              <p>No triggers yet.</p>
              <p className="text-sm">Add triggers to simulate realistic events.</p>
            </div>
          ) : (
            <div className="relative">
              {/* Timeline Line */}
              <div className="absolute left-6 top-0 bottom-0 w-1 bg-gray-200" />

              {/* Triggers */}
              <div className="space-y-4">
                {triggers.map((trigger, idx) => {
                  const triggerInfo = triggerTypes[trigger.type];
                  return (
                    <div key={trigger.id} className="relative pl-14">
                      {/* Timeline Dot */}
                      <div className={`absolute left-3 top-3 w-6 h-6 rounded-full border-4 border-white shadow-lg ${
                        triggerInfo.severity === 'critical' ? 'bg-red-500' :
                        triggerInfo.severity === 'moderate' ? 'bg-yellow-500' :
                        'bg-green-500'
                      }`} />

                      {/* Trigger Card */}
                      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-2xl">{triggerInfo.icon}</span>
                              <h4 className="font-semibold">{trigger.name}</h4>
                            </div>
                            <p className="text-sm text-gray-600 mb-2">
                              Step {trigger.step} (~{(trigger.step * 0.5).toFixed(0)} min)
                            </p>
                            
                            {/* Parameters */}
                            {Object.entries(trigger.params).length > 0 && (
                              <div className="text-xs text-gray-500 space-y-1">
                                {Object.entries(trigger.params).map(([key, value]) => (
                                  <p key={key}>
                                    <span className="font-medium">{key}:</span> {value}
                                  </p>
                                ))}
                              </div>
                            )}
                          </div>

                          <button
                            onClick={() => deleteTrigger(trigger.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Warning if no triggers */}
      {triggers.length === 0 && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800">
            💡 <strong>Tip:</strong> Add at least one trigger to make the simulation more realistic.
            Real events often have unexpected factors!
          </p>
        </div>
      )}

      {/* Navigation */}
      <div className="mt-8 flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 font-medium"
        >
          ← Back
        </button>
        <button
          onClick={onStart}
          className="px-8 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 font-semibold text-lg shadow-lg"
        >
          🚀 Start Simulation
        </button>
      </div>
    </div>
  );
};

export default TriggerTimeline;
