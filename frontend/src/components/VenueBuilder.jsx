import React, { useState } from 'react';

const VenueBuilder = ({ onSave }) => {
  const [scenario, setScenario] = useState({
    name: 'My Venue',
    template: 'temple',
    zones: [],
    paths: []
  });

  const [selectedTemplate, setSelectedTemplate] = useState('temple');
  const [newZoneName, setNewZoneName] = useState('');
  const [newZoneType, setNewZoneType] = useState('zone');
  const [draggingZone, setDraggingZone] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const templates = {
    temple: {
      name: 'Temple/Pilgrimage',
      description: 'Like Mahakumbh - entrances → sanctum → exits',
      defaultZones: [
        { id: 'entrance', name: 'Main Entrance', type: 'entrance', x: 50, y: 80, area: 400 },
        { id: 'sanctum', name: 'Sanctum', type: 'zone', x: 50, y: 40, area: 150 },
        { id: 'exit', name: 'Main Exit', type: 'exit', x: 50, y: 0, area: 120 }
      ]
    },
    stadium: {
      name: 'Stadium',
      description: 'Sports venue with sections and concourse',
      defaultZones: [
        { id: 'north', name: 'North Section', type: 'zone', x: 50, y: 70, area: 800 },
        { id: 'concourse', name: 'Concourse', type: 'zone', x: 50, y: 40, area: 300 },
        { id: 'exit_main', name: 'Main Exit', type: 'exit', x: 50, y: 0, area: 150 }
      ]
    },
    rally: {
      name: 'Rally Ground',
      description: 'Large outdoor event - stage area',
      defaultZones: [
        { id: 'stage', name: 'Stage Area', type: 'zone', x: 50, y: 80, area: 3000 },
        { id: 'crowd', name: 'Crowd Area', type: 'zone', x: 50, y: 50, area: 5000 },
        { id: 'exit_main', name: 'Main Exit', type: 'exit', x: 50, y: 0, area: 300 }
      ]
    }
  };

  const loadTemplate = (templateName) => {
    const template = templates[templateName];
    setScenario({
      name: template.name,
      template: templateName,
      zones: template.defaultZones,
      paths: []
    });
    setSelectedTemplate(templateName);
  };

  const addZone = () => {
    if (!newZoneName.trim()) return;

    const newZone = {
      id: `zone_${Date.now()}`,
      name: newZoneName,
      type: newZoneType,
      x: 50,
      y: 50,
      area: 500
    };

    setScenario({
      ...scenario,
      zones: [...scenario.zones, newZone]
    });

    setNewZoneName('');
  };

  const removeZone = (zoneId) => {
    setScenario({
      ...scenario,
      zones: scenario.zones.filter(z => z.id !== zoneId),
      paths: scenario.paths.filter(p => p.from !== zoneId && p.to !== zoneId)
    });
  };

  const updateZone = (zoneId, updates) => {
    setScenario({
      ...scenario,
      zones: scenario.zones.map(z =>
        z.id === zoneId ? { ...z, ...updates } : z
      )
    });
  };

  const handleZoneMouseDown = (zoneId, e) => {
    e.preventDefault();
    const zone = scenario.zones.find(z => z.id === zoneId);
    if (!zone) return;
    
    const canvas = e.currentTarget.parentElement;
    const rect = canvas.getBoundingClientRect();
    const zoneX = (zone.x / 100) * rect.width;
    const zoneY = (zone.y / 100) * rect.height;
    
    setDragOffset({
      x: e.clientX - rect.left - zoneX,
      y: e.clientY - rect.top - zoneY
    });
    setDraggingZone(zoneId);
  };

  const handleZoneMouseMove = (e) => {
    if (!draggingZone) return;
    
    const canvas = e.currentTarget;
    const rect = canvas.getBoundingClientRect();
    const x = ((e.clientX - rect.left - dragOffset.x) / rect.width) * 100;
    const y = ((e.clientY - rect.top - dragOffset.y) / rect.height) * 100;

    updateZone(draggingZone, { 
      x: Math.max(0, Math.min(100, x)), 
      y: Math.max(0, Math.min(100, y)) 
    });
  };

  const handleZoneMouseUp = () => {
    setDraggingZone(null);
    setDragOffset({ x: 0, y: 0 });
  };

  const getZoneColor = (type) => {
    const colors = {
      entrance: '#10b981',
      zone: '#f59e0b',
      corridor: '#3b82f6',
      exit: '#ef4444'
    };
    return colors[type] || '#64748b';
  };

  return (
    <div className="glass-card p-6 space-y-6">
      <h2 className="text-xl font-bold text-slate-200">Venue Builder</h2>

      <div>
        <h3 className="text-sm font-bold text-slate-400 mb-3">1. Select Template</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {Object.entries(templates).map(([key, template]) => (
            <button
              key={key}
              onClick={() => loadTemplate(key)}
              className={`p-4 rounded-xl border-2 text-left transition-all ${
                selectedTemplate === key
                  ? 'bg-blue-500/20 border-blue-500 text-blue-400'
                  : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:border-slate-500'
              }`}
            >
              <div className="font-bold">{template.name}</div>
              <div className="text-xs opacity-75">{template.description}</div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-bold text-slate-400 mb-3">2. Position Zones (Click and drag)</h3>
        <div
          className="relative w-full h-72 bg-slate-900 rounded-xl border border-slate-700 overflow-hidden"
          onMouseMove={handleZoneMouseMove}
          onMouseUp={handleZoneMouseUp}
          onMouseLeave={handleZoneMouseUp}
        >
          <svg className="absolute inset-0 w-full h-full">
            {Array.from({ length: 11 }, (_, i) => i * 10).map(i => (
              <line key={`v${i}`} x1={`${i}%`} y1="0" x2={`${i}%`} y2="100%" stroke="#334155" strokeWidth="0.5" />
            ))}
            {Array.from({ length: 11 }, (_, i) => i * 10).map(i => (
              <line key={`h${i}`} x1="0" y1={`${i}%`} x2="100%" y2={`${i}%`} stroke="#334155" strokeWidth="0.5" />
            ))}
          </svg>

          {scenario.zones.map(zone => (
            <div
              key={zone.id}
              onMouseDown={(e) => handleZoneMouseDown(zone.id, e)}
              className="absolute flex flex-col items-center justify-center rounded-lg cursor-grab active:cursor-grabbing transition-shadow"
              style={{
                left: `${zone.x}%`,
                top: `${zone.y}%`,
                transform: 'translate(-50%, -50%)',
                width: '100px',
                height: '60px',
                backgroundColor: getZoneColor(zone.type),
                boxShadow: draggingZone === zone.id ? '0 0 20px rgba(59, 130, 246, 0.5)' : 'none',
                zIndex: draggingZone === zone.id ? 10 : 1,
                opacity: 0.9
              }}
            >
              <div className="text-xs font-bold text-white text-center px-1">{zone.name}</div>
              <div className="text-[10px] text-white/80">{zone.area}m²</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-bold text-slate-400 mb-3">3. Add Custom Zone</h3>
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Zone name (e.g., 'Queue Area')"
            value={newZoneName}
            onChange={(e) => setNewZoneName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addZone()}
            className="input-modern flex-1"
          />
          <select 
            value={newZoneType} 
            onChange={(e) => setNewZoneType(e.target.value)} 
            className="input-modern w-auto"
          >
            <option value="zone">Zone (Crowd Area)</option>
            <option value="entrance">Entrance</option>
            <option value="exit">Exit</option>
            <option value="corridor">Corridor</option>
          </select>
          <button onClick={addZone} className="btn-primary">Add Zone</button>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-bold text-slate-400 mb-3">4. Adjust Zone Properties</h3>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {scenario.zones.map(zone => (
            <div key={zone.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
              <div className="flex items-center gap-3">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getZoneColor(zone.type) }}
                ></div>
                <strong className="text-slate-200">{zone.name}</strong>
                <span className="text-xs text-slate-500 px-2 py-0.5 bg-slate-700 rounded">{zone.type}</span>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  placeholder="Area m²"
                  value={zone.area}
                  onChange={(e) => updateZone(zone.id, { area: parseInt(e.target.value) })}
                  className="input-modern w-20 text-sm py-1"
                />
                <span className="text-xs text-slate-500">Cap: {Math.round(zone.area * 0.45)}</span>
                <button
                  onClick={() => removeZone(zone.id)}
                  className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-sm hover:bg-red-500/30"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Scenario name"
          value={scenario.name}
          onChange={(e) => setScenario({ ...scenario, name: e.target.value })}
          className="input-modern flex-1"
        />
        <button
          onClick={() => {
            onSave(scenario);
            alert(`Scenario "${scenario.name}" saved!`);
          }}
          className="btn-primary"
        >
          Save Scenario
        </button>
      </div>

      <div>
        <h3 className="text-sm font-bold text-slate-400 mb-3">Preview (JSON)</h3>
        <pre className="bg-slate-900 p-4 rounded-lg overflow-auto text-xs text-emerald-400 max-h-48">
          {JSON.stringify(scenario, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default VenueBuilder;
