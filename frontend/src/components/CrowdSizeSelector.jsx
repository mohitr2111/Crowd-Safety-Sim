<<<<<<< HEAD
import React from 'react';

const CrowdSizeSelector = ({ selectedScenario, onSelectPreset }) => {
=======
import React, { useState } from 'react';

const CrowdSizeSelector = ({ selectedScenario, onSelectPreset }) => {
  const [activePreset, setActivePreset] = useState('moderate');
  
>>>>>>> nikhil
  if (selectedScenario !== 'stadium_exit' && selectedScenario !== 'stadium_exit_enhanced') {
    return null;
  }

  const presets = [
    {
      id: 'light',
<<<<<<< HEAD
      emoji: '🟢',
      label: 'Light',
      count: '800 people',
=======
      label: 'Light',
      count: '800',
      color: 'emerald',
>>>>>>> nikhil
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 200, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 200, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 200, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 200, type: 'elderly' }
      ]
    },
    {
      id: 'moderate',
<<<<<<< HEAD
      emoji: '🟡',
      label: 'Moderate',
      count: '2,000 people',
=======
      label: 'Moderate',
      count: '2,000',
      color: 'amber',
>>>>>>> nikhil
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 500, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 500, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 500, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 500, type: 'elderly' }
      ]
    },
    {
      id: 'heavy',
<<<<<<< HEAD
      emoji: '🟠',
      label: 'Heavy',
      count: '5,000 people',
=======
      label: 'Heavy',
      count: '5,000',
      color: 'orange',
>>>>>>> nikhil
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 1250, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 1250, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 1250, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 1250, type: 'elderly' }
      ]
    },
    {
      id: 'peak',
<<<<<<< HEAD
      emoji: '🔴',
      label: 'Peak',
      count: '10,000 people',
=======
      label: 'Peak',
      count: '10,000',
      color: 'red',
>>>>>>> nikhil
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 2500, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 2500, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 2500, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 2500, type: 'elderly' }
      ]
    }
  ];

<<<<<<< HEAD
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span>🏟️</span>
        <span>Stadium Crowd Configuration</span>
      </h3>
      
      <div className="mb-4">
        <label className="block text-sm font-semibold mb-3 text-gray-700">
          Select Crowd Size:
=======
  const handleSelect = (preset) => {
    setActivePreset(preset.id);
    onSelectPreset(preset.config);
  };

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-bold text-slate-200 mb-4">
        Stadium Crowd Configuration
      </h3>
      
      <div className="mb-4">
        <label className="block text-sm font-semibold mb-3 text-slate-400">
          Select Crowd Size
>>>>>>> nikhil
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {presets.map((preset) => (
            <button
              key={preset.id}
<<<<<<< HEAD
              onClick={() => onSelectPreset(preset.config)}
              className="p-4 rounded-lg border-2 transition-all transform hover:scale-105 bg-white border-gray-300 hover:border-blue-400 hover:shadow-lg"
            >
              <div className="text-3xl mb-1">{preset.emoji}</div>
              <div className="font-bold text-lg">{preset.label}</div>
              <div className="text-sm text-gray-600">{preset.count}</div>
=======
              onClick={() => handleSelect(preset)}
              className={`p-4 rounded-xl border-2 transition-all ${
                activePreset === preset.id
                  ? `bg-${preset.color}-500/20 border-${preset.color}-500 text-${preset.color}-400`
                  : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-500'
              }`}
            >
              <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${
                preset.id === 'light' ? 'bg-emerald-500' :
                preset.id === 'moderate' ? 'bg-amber-500' :
                preset.id === 'heavy' ? 'bg-orange-500' : 'bg-red-500'
              }`}></div>
              <div className="font-bold text-lg">{preset.label}</div>
              <div className="text-sm opacity-75">{preset.count} people</div>
>>>>>>> nikhil
            </button>
          ))}
        </div>
      </div>
      
<<<<<<< HEAD
      <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800">
          💡 <strong>Stadium Capacity:</strong> 10,000 people | 
=======
      <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
        <p className="text-sm text-slate-400">
          <span className="text-blue-400 font-semibold">Stadium Capacity:</span> 10,000 people | 
>>>>>>> nikhil
          Click a preset to configure crowd size before creating simulation
        </p>
      </div>
    </div>
  );
};

export default CrowdSizeSelector;
