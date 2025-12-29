import React, { useState, useEffect } from 'react';

const EventConfigurator = ({ eventConfig, setEventConfig, venueData, onNext, onBack }) => {
  const [riskFactors, setRiskFactors] = useState([]);

  
  const eventTypes = {
    political_rally: {
      name: 'Political Rally',
      icon: '🎤',
      description: 'High risk, VIP-dependent, unpredictable crowd',
      baseRisk: 9.2,
      characteristics: ['VIP delays common', 'Mixed age groups', 'High rush tendency']
    },
    concert: {
      name: 'Concert',
      icon: '🎵',
      description: 'Young crowd, high energy, alcohol influence',
      baseRisk: 7.3,
      characteristics: ['Fast-moving crowd', 'High density tolerance', 'Impatient']
    },
    religious_gathering: {
      name: 'Religious Gathering',
      icon: '🕉️',
      description: 'Elderly crowd, patient, high density tolerance',
      baseRisk: 2.9,
      characteristics: ['Slow movement', 'Very patient', 'High devotion']
    },
    sports_match: {
      name: 'Sports Match',
      icon: '⚽',
      description: 'Controlled environment, predictable patterns',
      baseRisk: 4.5,
      characteristics: ['Moderate speed', 'Controlled entry/exit', 'Alcohol present']
    },
    transport_hub: {
      name: 'Transport Hub',
      icon: '🚉',
      description: 'Time pressure, impatient crowd, rush tendency',
      baseRisk: 6.5,
      characteristics: ['Very impatient', 'Time-sensitive', 'High rush']
    }
  };

  // Calculate risk score based on event type + crowd size
  useEffect(() => {
    const baseRisk = eventTypes[eventConfig.eventType]?.baseRisk || 5.0;
    const crowdSize = eventConfig.crowdSize;
    
    // Size multiplier
    let sizeMultiplier = 0.5;
    if (crowdSize >= 50000) sizeMultiplier = 2.0;
    else if (crowdSize >= 20000) sizeMultiplier = 1.5;
    else if (crowdSize >= 5000) sizeMultiplier = 1.0;
    
    // Calculate final risk
    const calculatedRisk = Math.min(baseRisk * sizeMultiplier / 10, 10);
    
    setEventConfig(prev => ({
      ...prev,
      riskScore: calculatedRisk
    }));

    // Update risk factors
    const factors = [];
    if (crowdSize > 30000) factors.push('Very large crowd');
    if (calculatedRisk > 7) factors.push('High-risk event type');
    if (venueData.zones.length < 3) factors.push('Limited venue capacity');
    if (venueData.exits.length < 2) factors.push('Insufficient exits');
    setRiskFactors(factors);
  }, [eventConfig.eventType, eventConfig.crowdSize, venueData]);

  const updateEventType = (type) => {
    setEventConfig(prev => ({ ...prev, eventType: type }));
  };

  const updateCrowdSize = (size) => {
    setEventConfig(prev => ({ ...prev, crowdSize: parseInt(size) }));
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">🎪 Configure Your Event</h2>

      {/* Event Type Selection */}
      <div className="mb-8">
        <h3 className="font-semibold text-lg mb-4">Select Event Type:</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(eventTypes).map(([key, event]) => (
            <button
              key={key}
              onClick={() => updateEventType(key)}
              className={`p-6 rounded-xl border-2 transition-all text-left ${
                eventConfig.eventType === key
                  ? 'border-blue-600 bg-blue-50 shadow-lg scale-105'
                  : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
              }`}
            >
              <div className="text-4xl mb-2">{event.icon}</div>
              <h4 className="font-bold text-lg mb-1">{event.name}</h4>
              <p className="text-sm text-gray-600 mb-3">{event.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-500">Base Risk:</span>
                <span className={`text-sm font-bold ${
                  event.baseRisk > 7 ? 'text-red-600' :
                  event.baseRisk > 5 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {event.baseRisk.toFixed(1)}/10
                </span>
              </div>
            </button>
          ))}
        </div>

        {/* Event Characteristics */}
        {eventConfig.eventType && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-2">📋 Characteristics:</h4>
            <div className="flex flex-wrap gap-2">
              {eventTypes[eventConfig.eventType].characteristics.map((char, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-white rounded-full text-sm border border-gray-200"
                >
                  {char}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Crowd Size */}
      <div className="mb-8">
        <h3 className="font-semibold text-lg mb-4">Expected Crowd Size:</h3>
        
        <div className="space-y-4">
          {/* Slider */}
          <div>
            <input
              type="range"
              min="1000"
              max="50000"
              step="1000"
              value={eventConfig.crowdSize}
              onChange={(e) => updateCrowdSize(e.target.value)}
              className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1,000</span>
              <span>10,000</span>
              <span>25,000</span>
              <span>50,000</span>
            </div>
          </div>

          {/* Number Input */}
          <div className="flex items-center gap-4">
            <input
              type="number"
              min="1000"
              max="50000"
              step="1000"
              value={eventConfig.crowdSize}
              onChange={(e) => updateCrowdSize(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg text-xl font-bold text-center w-40"
            />
            <span className="text-lg text-gray-700">people</span>
          </div>

          {/* Density Calculation */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-sm text-gray-600">Total Venue Area</p>
                <p className="text-2xl font-bold text-blue-600">
                  {venueData.zones.reduce((sum, z) => sum + z.area, 0).toLocaleString()} m²
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Capacity</p>
                <p className="text-2xl font-bold text-green-600">
                  {venueData.zones.reduce((sum, z) => sum + z.capacity, 0).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Avg Expected Density</p>
                <p className={`text-2xl font-bold ${
                  (eventConfig.crowdSize / venueData.zones.reduce((sum, z) => sum + z.area, 0)) > 5
                    ? 'text-red-600'
                    : (eventConfig.crowdSize / venueData.zones.reduce((sum, z) => sum + z.area, 0)) > 3
                    ? 'text-yellow-600'
                    : 'text-green-600'
                }`}>
                  {(eventConfig.crowdSize / venueData.zones.reduce((sum, z) => sum + z.area, 0)).toFixed(1)} p/m²
                </p>
              </div>
            </div>

            {/* Capacity Warning */}
            {eventConfig.crowdSize > venueData.zones.reduce((sum, z) => sum + z.capacity, 0) && (
              <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg">
                <p className="text-red-800 font-semibold">
                  ⚠️ Warning: Crowd size exceeds total venue capacity!
                </p>
                <p className="text-red-700 text-sm mt-1">
                  Overcrowding detected. Consider reducing crowd size or expanding venue.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Risk Assessment */}
      <div className="mb-8">
        <h3 className="font-semibold text-lg mb-4">📊 Risk Assessment:</h3>
        
        <div className="p-6 bg-gradient-to-r from-green-50 via-yellow-50 to-red-50 rounded-xl border-2 border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <span className="text-2xl font-bold text-gray-700">Overall Risk Score:</span>
            <div className="flex items-center gap-3">
              <div className="text-5xl font-black" style={{
                color: eventConfig.riskScore > 7 ? '#DC2626' :
                       eventConfig.riskScore > 5 ? '#F59E0B' :
                       eventConfig.riskScore > 3 ? '#10B981' :
                       '#059669'
              }}>
                {eventConfig.riskScore.toFixed(1)}
              </div>
              <span className="text-3xl text-gray-400 font-bold">/10</span>
            </div>
          </div>

          {/* Risk Bar */}
          <div className="relative h-8 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="absolute h-full transition-all duration-500"
              style={{
                width: `${eventConfig.riskScore * 10}%`,
                background: eventConfig.riskScore > 7 
                  ? 'linear-gradient(90deg, #EF4444, #DC2626)'
                  : eventConfig.riskScore > 5
                  ? 'linear-gradient(90deg, #FBBF24, #F59E0B)'
                  : 'linear-gradient(90deg, #34D399, #10B981)'
              }}
            />
          </div>

          {/* Risk Labels */}
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>Low (0-3)</span>
            <span>Moderate (3-5)</span>
            <span>High (5-7)</span>
            <span>Critical (7-10)</span>
          </div>

          {/* Risk Factors */}
          {riskFactors.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-300">
              <p className="font-semibold text-sm mb-2">⚠️ Risk Factors:</p>
              <ul className="space-y-1">
                {riskFactors.map((factor, idx) => (
                  <li key={idx} className="text-sm text-gray-700">
                    • {factor}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={onBack}
          className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 font-medium"
        >
          ← Back
        </button>
        <button
          onClick={onNext}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold text-lg"
        >
          Next: Add Triggers →
        </button>
      </div>
    </div>
  );
};

export default EventConfigurator;
