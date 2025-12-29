import React from 'react';

const CrowdSizeSelector = ({ selectedScenario, onSelectPreset }) => {
  if (selectedScenario !== 'stadium_exit' && selectedScenario !== 'stadium_exit_enhanced') {
    return null;
  }

  const presets = [
    {
      id: 'light',
      emoji: '🟢',
      label: 'Light',
      count: '800 people',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 200, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 200, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 200, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 200, type: 'elderly' }
      ]
    },
    {
      id: 'moderate',
      emoji: '🟡',
      label: 'Moderate',
      count: '2,000 people',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 500, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 500, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 500, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 500, type: 'elderly' }
      ]
    },
    {
      id: 'heavy',
      emoji: '🟠',
      label: 'Heavy',
      count: '5,000 people',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 1250, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 1250, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 1250, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 1250, type: 'elderly' }
      ]
    },
    {
      id: 'peak',
      emoji: '🔴',
      label: 'Peak',
      count: '10,000 people',
      config: [
        { start: 'zone_north', goal: 'exit_main', count: 2500, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 2500, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 2500, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 2500, type: 'elderly' }
      ]
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span>🏟️</span>
        <span>Stadium Crowd Configuration</span>
      </h3>
      
      <div className="mb-4">
        <label className="block text-sm font-semibold mb-3 text-gray-700">
          Select Crowd Size:
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {presets.map((preset) => (
            <button
              key={preset.id}
              onClick={() => onSelectPreset(preset.config)}
              className="p-4 rounded-lg border-2 transition-all transform hover:scale-105 bg-white border-gray-300 hover:border-blue-400 hover:shadow-lg"
            >
              <div className="text-3xl mb-1">{preset.emoji}</div>
              <div className="font-bold text-lg">{preset.label}</div>
              <div className="text-sm text-gray-600">{preset.count}</div>
            </button>
          ))}
        </div>
      </div>
      
      <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800">
          💡 <strong>Stadium Capacity:</strong> 10,000 people | 
          Click a preset to configure crowd size before creating simulation
        </p>
      </div>
    </div>
  );
};

export default CrowdSizeSelector;
