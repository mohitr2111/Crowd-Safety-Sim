import React, { useState } from 'react';

const CrowdSizeSelector = ({ selectedScenario, onSelectPreset }) => {
  const [activePreset, setActivePreset] = useState('moderate');
  
  if (selectedScenario !== 'stadium_exit' && selectedScenario !== 'stadium_exit_enhanced') {
    return null;
  }

  const presets = [
    {
      id: 'light',
      label: 'Light',
      count: '800',
      color: 'emerald',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 200, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 200, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 200, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 200, type: 'elderly' }
      ]
    },
    {
      id: 'moderate',
      label: 'Moderate',
      count: '2,000',
      color: 'amber',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 500, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 500, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 500, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 500, type: 'elderly' }
      ]
    },
    {
      id: 'heavy',
      label: 'Heavy',
      count: '5,000',
      color: 'orange',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 1250, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 1250, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 1250, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 1250, type: 'elderly' }
      ]
    },
    {
      id: 'peak',
      label: 'Peak',
      count: '10,000',
      color: 'red',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 2500, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 2500, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 2500, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 2500, type: 'elderly' }
      ]
    }
  ];

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
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {presets.map((preset) => (
            <button
              key={preset.id}
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
            </button>
          ))}
        </div>
      </div>
      
      <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
        <p className="text-sm text-slate-400">
          <span className="text-blue-400 font-semibold">Stadium Capacity:</span> 10,000 people | 
          Click a preset to configure crowd size before creating simulation
        </p>
      </div>
    </div>
  );
};

export default CrowdSizeSelector;
