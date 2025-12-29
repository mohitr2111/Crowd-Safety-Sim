import React, { useState, useEffect } from 'react';

const DynamicCrowdSelector = ({ selectedScenario, onCrowdChange }) => {
  const [crowdSize, setCrowdSize] = useState(5000);

  // Scenario-specific configurations
  const scenarioConfigs = {
    stadium_exit: {
      min: 1000,
      max: 50000,
      default: 10000,
      step: 1000,
      distribution: {
        zone_north: 0.40,
        zone_south: 0.30,
        zone_east: 0.20,
        zone_west: 0.10
      },
      goals: {
        zone_north: 'exit_main',
        zone_south: 'exit_main',
        zone_east: 'exit_side_1',
        zone_west: 'exit_side_2'
      },
      types: {
        zone_north: 'normal',
        zone_south: 'family',
        zone_east: 'rushing',
        zone_west: 'elderly'
      }
    },
    railway_station: {
      min: 500,
      max: 5000,
      default: 1500,
      step: 100,
      distribution: {
        platform_1: 0.60,
        platform_2: 0.40
      },
      goals: {
        platform_1: 'exit_east',
        platform_2: 'exit_west'
      },
      types: {
        platform_1: 'normal',
        platform_2: 'rushing'
      }
    }
  };

  const config = scenarioConfigs[selectedScenario] || scenarioConfigs.stadium_exit;

  // Initialize with default on mount
  useEffect(() => {
    setCrowdSize(config.default);
    generateAndSendConfig(config.default);
  }, [selectedScenario]);

  const generateSpawnConfig = (totalSize) => {
    const spawnConfig = [];
    
    Object.keys(config.distribution).forEach(startNode => {
      const count = Math.floor(totalSize * config.distribution[startNode]);
      spawnConfig.push({
        start: startNode,
        goal: config.goals[startNode],
        count: count,
        type: config.types[startNode]
      });
    });
    
    return spawnConfig;
  };

  const generateAndSendConfig = (size) => {
    const spawnConfig = generateSpawnConfig(size);
    onCrowdChange(spawnConfig);
  };

  const handleSliderChange = (e) => {
    const size = parseInt(e.target.value);
    setCrowdSize(size);
    generateAndSendConfig(size);
  };

  const handlePresetClick = (factor) => {
    const presetSize = Math.floor(config.min + (config.max - config.min) * factor);
    setCrowdSize(presetSize);
    generateAndSendConfig(presetSize);
  };

  const currentConfig = generateSpawnConfig(crowdSize);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
        <span className="text-2xl">👥</span>
        Dynamic Crowd Size Configuration
      </h3>
      
      {/* Main Size Display */}
      <div className="mb-6 text-center">
        <div className="text-4xl font-bold text-blue-600 mb-1">
          {crowdSize.toLocaleString()}
        </div>
        <div className="text-sm text-gray-500">Total Agents</div>
      </div>

      {/* Slider */}
      <div className="mb-6">
        <input
          type="range"
          min={config.min}
          max={config.max}
          step={config.step}
          value={crowdSize}
          onChange={handleSliderChange}
          className="w-full h-3 bg-gradient-to-r from-green-200 via-yellow-200 to-red-200 rounded-lg 
                     appearance-none cursor-pointer"
        />
        
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span className="font-semibold">{config.min.toLocaleString()}</span>
          <span className="text-gray-400">Capacity Range</span>
          <span className="font-semibold">{config.max.toLocaleString()}</span>
        </div>
      </div>

      {/* Quick Preset Buttons */}
      <div className="grid grid-cols-4 gap-3 mb-6">
        {[
          { label: 'Low', factor: 0.25, color: 'bg-green-50 hover:bg-green-100 text-green-700' },
          { label: 'Medium', factor: 0.5, color: 'bg-yellow-50 hover:bg-yellow-100 text-yellow-700' },
          { label: 'High', factor: 0.75, color: 'bg-orange-50 hover:bg-orange-100 text-orange-700' },
          { label: 'Max', factor: 1.0, color: 'bg-red-50 hover:bg-red-100 text-red-700' }
        ].map(({ label, factor, color }) => {
          const presetSize = Math.floor(config.min + (config.max - config.min) * factor);
          return (
            <button
              key={label}
              onClick={() => handlePresetClick(factor)}
              className={`${color} px-4 py-3 rounded-lg font-semibold transition-all transform hover:scale-105 shadow-sm`}
            >
              <div className="text-xs opacity-75">{label}</div>
              <div className="text-sm">{presetSize.toLocaleString()}</div>
            </button>
          );
        })}
      </div>

      {/* Distribution Preview */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-blue-700 font-semibold text-sm">📊 Agent Distribution</span>
        </div>
        
        <div className="space-y-2">
          {currentConfig.map((cfg, idx) => {
            const percentage = ((cfg.count / crowdSize) * 100).toFixed(0);
            return (
              <div key={idx} className="flex items-center gap-3 text-sm">
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="font-medium text-gray-700">
                      {cfg.start.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-blue-600 font-bold">
                      {cfg.count.toLocaleString()} ({percentage}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-400 to-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
                <div className="text-xs text-gray-500">
                  → {cfg.goal}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Capacity Warning */}
      {crowdSize > config.max * 0.8 && (
        <div className="mt-4 bg-orange-50 border border-orange-200 rounded-lg p-3 flex items-start gap-2">
          <span className="text-orange-500 text-lg">⚠️</span>
          <div className="text-sm text-orange-800">
            <strong>High Capacity Warning:</strong> Simulation may run slower with {crowdSize.toLocaleString()} agents. 
            Consider reducing crowd size for real-time performance.
          </div>
        </div>
      )}
    </div>
  );
};

export default DynamicCrowdSelector;
