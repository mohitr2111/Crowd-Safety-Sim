import React, { useState } from 'react';

const VenueDesigner = ({ venueData, setVenueData, onNext }) => {
  const [zoneName, setZoneName] = useState('');
  const [zoneCapacity, setZoneCapacity] = useState(1000);
  const [zoneArea, setZoneArea] = useState(500);
  const [selectedZone, setSelectedZone] = useState(null);
  const [connectionTarget, setConnectionTarget] = useState('');

  // Add new zone
  const addZone = () => {
    if (!zoneName) {
      alert('Please enter zone name');
      return;
    }

    const newZone = {
      id: `zone_${Date.now()}`,
      name: zoneName,
      capacity: zoneCapacity,
      area: zoneArea,
      type: 'regular'
    };

    setVenueData(prev => ({
      ...prev,
      zones: [...prev.zones, newZone]
    }));

    // Reset form
    setZoneName('');
    setZoneCapacity(1000);
    setZoneArea(500);
  };

  // Mark as entry/exit
  const markAsEntry = (zoneId) => {
    setVenueData(prev => ({
      ...prev,
      entries: [...prev.entries, zoneId]
    }));
  };

  const markAsExit = (zoneId) => {
    setVenueData(prev => ({
      ...prev,
      exits: [...prev.exits, zoneId]
    }));
  };

  // Add connection
  const addConnection = () => {
    if (!selectedZone || !connectionTarget) {
      alert('Select both zones to connect');
      return;
    }

    setVenueData(prev => ({
      ...prev,
      connections: [...prev.connections, {
        from: selectedZone,
        to: connectionTarget
      }]
    }));

    setConnectionTarget('');
  };

  // Delete zone
  const deleteZone = (zoneId) => {
    setVenueData(prev => ({
      zones: prev.zones.filter(z => z.id !== zoneId),
      connections: prev.connections.filter(c => c.from !== zoneId && c.to !== zoneId),
      entries: prev.entries.filter(e => e !== zoneId),
      exits: prev.exits.filter(e => e !== zoneId)
    }));
  };

  // Templates
  const loadTemplate = (templateName) => {
    const templates = {
      stadium: {
        zones: [
          { id: 'entry_gate', name: 'Entry Gate', capacity: 2000, area: 400, type: 'entry' },
          { id: 'corridor_main', name: 'Main Corridor', capacity: 3000, area: 600, type: 'corridor' },
          { id: 'zone_north', name: 'North Stands', capacity: 10000, area: 2000, type: 'seating' },
          { id: 'zone_south', name: 'South Stands', capacity: 10000, area: 2000, type: 'seating' },
          { id: 'exit_a', name: 'Exit A', capacity: 2000, area: 400, type: 'exit' },
          { id: 'exit_b', name: 'Exit B', capacity: 2000, area: 400, type: 'exit' }
        ],
        connections: [
          { from: 'entry_gate', to: 'corridor_main' },
          { from: 'corridor_main', to: 'zone_north' },
          { from: 'corridor_main', to: 'zone_south' },
          { from: 'zone_north', to: 'exit_a' },
          { from: 'zone_south', to: 'exit_b' }
        ],
        entries: ['entry_gate'],
        exits: ['exit_a', 'exit_b']
      },
      concert_hall: {
        zones: [
          { id: 'entrance', name: 'Entrance', capacity: 1500, area: 300, type: 'entry' },
          { id: 'lobby', name: 'Lobby', capacity: 2000, area: 500, type: 'regular' },
          { id: 'main_hall', name: 'Main Hall', capacity: 8000, area: 1600, type: 'venue' },
          { id: 'emergency_exit', name: 'Emergency Exit', capacity: 1000, area: 200, type: 'exit' }
        ],
        connections: [
          { from: 'entrance', to: 'lobby' },
          { from: 'lobby', to: 'main_hall' },
          { from: 'main_hall', to: 'emergency_exit' }
        ],
        entries: ['entrance'],
        exits: ['emergency_exit']
      }
    };

    if (templates[templateName]) {
      setVenueData(templates[templateName]);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">🏛️ Design Your Venue</h2>

      {/* Templates */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold mb-3">📋 Quick Start Templates:</h3>
        <div className="flex gap-3">
          <button
            onClick={() => loadTemplate('stadium')}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            🏟️ Stadium
          </button>
          <button
            onClick={() => loadTemplate('concert_hall')}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            🎵 Concert Hall
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Left: Add Zone Form */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
          <h3 className="font-semibold text-lg mb-4">➕ Add New Zone</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Zone Name
              </label>
              <input
                type="text"
                value={zoneName}
                onChange={(e) => setZoneName(e.target.value)}
                placeholder="e.g., Main Hall"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Capacity (people)
              </label>
              <input
                type="number"
                value={zoneCapacity}
                onChange={(e) => setZoneCapacity(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Area (m²)
              </label>
              <input
                type="number"
                value={zoneArea}
                onChange={(e) => setZoneArea(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Max density: {(zoneCapacity / zoneArea).toFixed(1)} p/m²
              </p>
            </div>

            <button
              onClick={addZone}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
            >
              ➕ Add Zone
            </button>
          </div>

          {/* Connections */}
          {venueData.zones.length >= 2 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="font-semibold text-lg mb-4">🔗 Connect Zones</h3>
              
              <div className="space-y-3">
                <select
                  value={selectedZone || ''}
                  onChange={(e) => setSelectedZone(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Select Zone 1</option>
                  {venueData.zones.map(zone => (
                    <option key={zone.id} value={zone.id}>{zone.name}</option>
                  ))}
                </select>

                <select
                  value={connectionTarget}
                  onChange={(e) => setConnectionTarget(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="">Select Zone 2</option>
                  {venueData.zones.filter(z => z.id !== selectedZone).map(zone => (
                    <option key={zone.id} value={zone.id}>{zone.name}</option>
                  ))}
                </select>

                <button
                  onClick={addConnection}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  🔗 Connect
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right: Zone List */}
        <div>
          <h3 className="font-semibold text-lg mb-4">📍 Zones ({venueData.zones.length})</h3>
          
          {venueData.zones.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <p className="text-6xl mb-4">🏗️</p>
              <p>No zones yet. Add your first zone!</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {venueData.zones.map(zone => (
                <div
                  key={zone.id}
                  className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="font-semibold text-lg">{zone.name}</h4>
                      <p className="text-sm text-gray-600">
                        {zone.capacity.toLocaleString()} people • {zone.area} m²
                      </p>
                    </div>
                    <button
                      onClick={() => deleteZone(zone.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      🗑️
                    </button>
                  </div>

                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => markAsEntry(zone.id)}
                      disabled={venueData.entries.includes(zone.id)}
                      className={`px-3 py-1 text-sm rounded ${
                        venueData.entries.includes(zone.id)
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 hover:bg-green-50'
                      }`}
                    >
                      {venueData.entries.includes(zone.id) ? '✓ Entry' : 'Mark Entry'}
                    </button>
                    <button
                      onClick={() => markAsExit(zone.id)}
                      disabled={venueData.exits.includes(zone.id)}
                      className={`px-3 py-1 text-sm rounded ${
                        venueData.exits.includes(zone.id)
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 hover:bg-blue-50'
                      }`}
                    >
                      {venueData.exits.includes(zone.id) ? '✓ Exit' : 'Mark Exit'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Connections Display */}
          {venueData.connections.length > 0 && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold mb-2">🔗 Connections:</h4>
              <div className="text-sm space-y-1">
                {venueData.connections.map((conn, idx) => {
                  const fromZone = venueData.zones.find(z => z.id === conn.from);
                  const toZone = venueData.zones.find(z => z.id === conn.to);
                  return (
                    <p key={idx} className="text-gray-700">
                      {fromZone?.name} ↔ {toZone?.name}
                    </p>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Next Button */}
      <div className="mt-8 flex justify-end">
        <button
          onClick={onNext}
          disabled={venueData.zones.length < 2}
          className={`px-8 py-3 rounded-lg font-semibold text-lg ${
            venueData.zones.length < 2
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          Next: Configure Event →
        </button>
      </div>
    </div>
  );
};

export default VenueDesigner;
