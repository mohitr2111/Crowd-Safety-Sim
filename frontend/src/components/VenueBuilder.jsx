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

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>🏗️ Venue Builder</h2>

      {/* Template Selection */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>1. Select Template</h3>
        <div style={styles.templateGrid}>
          {Object.entries(templates).map(([key, template]) => (
            <button
              key={key}
              onClick={() => loadTemplate(key)}
              style={{
                ...styles.templateButton,
                backgroundColor: selectedTemplate === key ? '#3b82f6' : '#f3f4f6',
                color: selectedTemplate === key ? '#fff' : '#1f2937'
              }}
            >
              <div style={{ fontWeight: 'bold' }}>{template.name}</div>
              <div style={{ fontSize: '12px' }}>{template.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Canvas - Drag zones to position */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>2. Position Zones (Click and drag to move)</h3>
        <div
          style={styles.canvas}
          onMouseMove={handleZoneMouseMove}
          onMouseUp={handleZoneMouseUp}
          onMouseLeave={handleZoneMouseUp}
        >
          {/* SVG Grid - More detailed grid like the image */}
          <svg style={styles.grid}>
            {Array.from({ length: 21 }, (_, i) => i * 5).map(i => (
              <line 
                key={`v${i}`} 
                x1={`${i}%`} 
                y1="0" 
                x2={`${i}%`} 
                y2="100%" 
                stroke="#e5e7eb" 
                strokeWidth={i % 25 === 0 ? 1.5 : 0.5}
                opacity={i % 25 === 0 ? 1 : 0.5}
              />
            ))}
            {Array.from({ length: 21 }, (_, i) => i * 5).map(i => (
              <line 
                key={`h${i}`} 
                x1="0" 
                y1={`${i}%`} 
                x2="100%" 
                y2={`${i}%`} 
                stroke="#e5e7eb" 
                strokeWidth={i % 25 === 0 ? 1.5 : 0.5}
                opacity={i % 25 === 0 ? 1 : 0.5}
              />
            ))}
          </svg>

          {/* Draggable Zones - Rectangular like the image */}
          {scenario.zones.map(zone => (
            <div
              key={zone.id}
              onMouseDown={(e) => handleZoneMouseDown(zone.id, e)}
              style={{
                ...styles.zoneElement,
                left: `${zone.x}%`,
                top: `${zone.y}%`,
                backgroundColor: getZoneColor(zone.type),
                cursor: draggingZone === zone.id ? 'grabbing' : 'grab',
                transform: 'translate(-50%, -50%)',
                boxShadow: draggingZone === zone.id 
                  ? '0 4px 12px rgba(0, 0, 0, 0.3)' 
                  : '0 2px 4px rgba(0, 0, 0, 0.1)',
                zIndex: draggingZone === zone.id ? 10 : 1,
                transition: draggingZone === zone.id ? 'none' : 'box-shadow 0.2s ease'
              }}
              title={`${zone.name} - ${zone.type} (${zone.area}m²)`}
            >
              <div style={{ 
                fontSize: '11px', 
                fontWeight: 'bold', 
                color: '#fff',
                textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                textAlign: 'center',
                padding: '2px'
              }}>
                {zone.name}
              </div>
              <div style={{ 
                fontSize: '9px', 
                color: '#fff',
                textShadow: '0 1px 2px rgba(0,0,0,0.5)',
                textAlign: 'center',
                opacity: 0.9
              }}>
                {zone.area}m²
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Zone */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>3. Add Custom Zone</h3>
        <div style={styles.formGroup}>
          <input
            type="text"
            placeholder="Zone name (e.g., 'Queue Area')"
            value={newZoneName}
            onChange={(e) => setNewZoneName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addZone()}
            style={styles.input}
          />
          <select value={newZoneType} onChange={(e) => setNewZoneType(e.target.value)} style={styles.select}>
            <option value="zone">Zone (Crowd Area)</option>
            <option value="entrance">Entrance</option>
            <option value="exit">Exit</option>
            <option value="corridor">Corridor</option>
          </select>
          <button onClick={addZone} style={styles.button}>+ Add Zone</button>
        </div>
      </div>

      {/* Zone Properties */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>4. Adjust Zone Properties</h3>
        <div style={styles.zoneList}>
          {scenario.zones.map(zone => (
            <div key={zone.id} style={styles.zoneItem}>
              <div style={styles.zoneInfo}>
                <strong>{zone.name}</strong>
                <span style={styles.zoneType}>{zone.type}</span>
              </div>
              <div style={styles.zoneControls}>
                <input
                  type="number"
                  placeholder="Area m²"
                  value={zone.area}
                  onChange={(e) => updateZone(zone.id, { area: parseInt(e.target.value) })}
                  style={styles.numberInput}
                />
                <span style={styles.capacity}>Cap: {Math.round(zone.area * 0.45)}</span>
                <button
                  onClick={() => removeZone(zone.id)}
                  style={styles.deleteButton}
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Save */}
      <div style={styles.section}>
        <input
          type="text"
          placeholder="Scenario name"
          value={scenario.name}
          onChange={(e) => setScenario({ ...scenario, name: e.target.value })}
          style={styles.input}
        />
        <button
          onClick={() => {
            onSave(scenario);
            alert(`✅ Scenario "${scenario.name}" saved!`);
          }}
          style={styles.saveButton}
        >
          💾 Save Scenario
        </button>
      </div>

      {/* Preview */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>Preview (JSON)</h3>
        <pre style={styles.preview}>
          {JSON.stringify(scenario, null, 2)}
        </pre>
      </div>
    </div>
  );
};

const getZoneColor = (type) => {
  const colors = {
    entrance: '#86efac',    // Green
    zone: '#fbbf24',        // Amber
    corridor: '#93c5fd',    // Blue
    exit: '#f87171'         // Red
  };
  return colors[type] || '#d1d5db';
};

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
    fontFamily: 'system-ui, sans-serif',
    backgroundColor: '#f9fafb',
    borderRadius: '8px'
  },
  heading: {
    marginTop: 0,
    marginBottom: '20px',
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1f2937'
  },
  section: {
    marginBottom: '20px',
    padding: '16px',
    backgroundColor: '#fff',
    borderRadius: '6px',
    border: '1px solid #e5e7eb'
  },
  sectionTitle: {
    marginTop: 0,
    marginBottom: '12px',
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#374151'
  },
  templateGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '10px'
  },
  templateButton: {
    padding: '12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    cursor: 'pointer',
    textAlign: 'left',
    fontSize: '13px',
    transition: 'all 0.2s'
  },
  canvas: {
    position: 'relative',
    width: '100%',
    height: '300px',
    border: '2px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: '#fafafa',
    overflow: 'hidden'
  },
  grid: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    top: 0,
    left: 0
  },
  zoneElement: {
    position: 'absolute',
    width: '100px',
    height: '70px',
    border: '2px solid #1f2937',
    borderRadius: '6px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'grab',
    userSelect: 'none',
    color: '#fff',
    textShadow: '0 1px 2px rgba(0,0,0,0.5)',
    opacity: 0.95,
    transition: 'all 0.2s ease'
  },
  formGroup: {
    display: 'flex',
    gap: '10px'
  },
  input: {
    flex: 1,
    padding: '8px',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
    fontSize: '14px'
  },
  select: {
    padding: '8px',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
    fontSize: '14px'
  },
  button: {
    padding: '8px 12px',
    backgroundColor: '#3b82f6',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold'
  },
  zoneList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  zoneItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px',
    backgroundColor: '#f3f4f6',
    borderRadius: '4px',
    border: '1px solid #e5e7eb'
  },
  zoneInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  zoneType: {
    fontSize: '11px',
    color: '#6b7280',
    padding: '2px 6px',
    backgroundColor: '#e5e7eb',
    borderRadius: '3px'
  },
  zoneControls: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  numberInput: {
    width: '80px',
    padding: '4px',
    border: '1px solid #d1d5db',
    borderRadius: '3px',
    fontSize: '12px'
  },
  capacity: {
    fontSize: '12px',
    color: '#6b7280'
  },
  deleteButton: {
    padding: '4px 8px',
    backgroundColor: '#ef4444',
    color: '#fff',
    border: 'none',
    borderRadius: '3px',
    cursor: 'pointer',
    fontSize: '12px'
  },
  saveButton: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#059669',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
    fontSize: '14px'
  },
  preview: {
    backgroundColor: '#1f2937',
    color: '#10b981',
    padding: '12px',
    borderRadius: '4px',
    overflow: 'auto',
    fontSize: '11px',
    maxHeight: '200px'
  }
};

export default VenueBuilder;