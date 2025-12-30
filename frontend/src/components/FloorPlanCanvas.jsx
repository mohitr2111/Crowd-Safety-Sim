// frontend/src/components/FloorPlanCanvas.jsx

import React, { useEffect, useRef, useState } from 'react';

const FloorPlanCanvas = ({ graphData, state, width = 800 }) => {
  const canvasRef = useRef(null);
  const [canvasHeight, setCanvasHeight] = useState(650);

  // ✅ AUTO-DETECT zone type from node ID or metadata
  const detectZoneType = (node) => {
    const id = node.id.toLowerCase();
    const name = (node.name || '').toLowerCase();
    
    if (node.type === 'entry' || id.includes('entrance') || id.includes('entry') || name.includes('entrance')) {
      return 'entry';
    }
    if (node.type === 'exit' || id.includes('exit') || name.includes('exit')) {
      return 'exit';
    }
    if (id.includes('corridor') || name.includes('corridor') || id.includes('passage')) {
      return 'corridor';
    }
    if (id.includes('hall') || name.includes('hall') || id.includes('inner')) {
      return 'hall';
    }
    if (id.includes('sanctum') || name.includes('sanctum') || id.includes('shrine')) {
      return 'sanctum';
    }
    if (id.includes('gathering') || name.includes('gathering') || id.includes('concourse')) {
      return 'general';
    }
    if (id.includes('zone') || id.includes('stand')) {
      return 'seating';
    }
    
    return 'general';
  };

  // ✅ Get visual style based on zone type
  const getZoneStyle = (zoneType) => {
    const styles = {
      entry: {
        baseColor: '#f5f5dc',
        borderColor: '#3b82f6',
        borderWidth: 4,
        label: true,
        icon: '🚪'
      },
      exit: {
        baseColor: '#90ee90',
        borderColor: '#16a34a',
        borderWidth: 4,
        label: true,
        icon: '🚶'
      },
      corridor: {
        baseColor: '#d3d3d3',
        borderColor: '#6b7280',
        borderWidth: 2,
        label: false,
        icon: null
      },
      hall: {
        baseColor: '#fff8dc',
        borderColor: '#6366f1',
        borderWidth: 3,
        label: true,
        icon: '🏛️'
      },
      sanctum: {
        baseColor: '#fffacd',
        borderColor: '#f59e0b',
        borderWidth: 3,
        label: true,
        icon: '🕉️'
      },
      general: {
        baseColor: '#f0f0f0',
        borderColor: '#9ca3af',
        borderWidth: 2,
        label: true,
        icon: '📦'
      },
      seating: {
        baseColor: '#e6f2ff',
        borderColor: '#2563eb',
        borderWidth: 3,
        label: true,
        icon: '💺'
      }
    };
    
    return styles[zoneType] || styles.general;
  };

  // ✅ SMART LAYOUT with dynamic height calculation
  const generateSmartLayout = (graphData, canvasWidth) => {
    if (!graphData || !graphData.nodes) return { rooms: [], capacityPoints: [], maxHeight: 650 };

    const nodes = graphData.nodes;
    const edges = graphData.edges || [];

    // Build adjacency list
    const adjacency = {};
    nodes.forEach(node => {
      adjacency[node.id] = [];
    });
    edges.forEach(edge => {
      const from = edge.from || edge.source;
      const to = edge.to || edge.target;
      if (adjacency[from]) adjacency[from].push(to);
      if (adjacency[to]) adjacency[to].push(from);
    });

    const padding = 80;
    const zoneWidth = 140;
    const zoneHeight = 90;
    const verticalGap = 50;
    const horizontalGap = 30;

    const positions = {};

    // Find entry nodes (start points)
    const entryNodes = nodes.filter(n => detectZoneType(n) === 'entry');

    // Use hierarchical layout with BFS
    const layers = [];
    const visited = new Set();
    
    if (entryNodes.length > 0) {
      layers.push(entryNodes.map(n => n.id));
      entryNodes.forEach(n => visited.add(n.id));
    } else {
      layers.push([nodes[0].id]);
      visited.add(nodes[0].id);
    }

    // BFS to create layers
    let currentLayer = 0;
    while (visited.size < nodes.length && currentLayer < 20) {
      const nextLayer = new Set();
      layers[currentLayer].forEach(nodeId => {
        (adjacency[nodeId] || []).forEach(neighbor => {
          if (!visited.has(neighbor)) {
            nextLayer.add(neighbor);
            visited.add(neighbor);
          }
        });
      });
      if (nextLayer.size > 0) {
        layers.push(Array.from(nextLayer));
        currentLayer++;
      } else {
        break;
      }
    }

    // Add unvisited nodes to last layer
    const unvisited = nodes.filter(n => !visited.has(n.id));
    if (unvisited.length > 0) {
      layers.push(unvisited.map(n => n.id));
    }

    const rooms = [];
    const capacityPoints = [];
    let maxHeight = 0;

    // Calculate positions from layers
    layers.forEach((layer, layerIndex) => {
      const layerY = padding + layerIndex * (zoneHeight + verticalGap);
      
      // Calculate layer width to center zones
      const maxLayerWidth = canvasWidth - 2 * padding;
      const totalZoneWidth = layer.length * zoneWidth + (layer.length - 1) * horizontalGap;
      const startX = padding + Math.max(0, (maxLayerWidth - totalZoneWidth) / 2);

      layer.forEach((nodeId, idx) => {
        const node = nodes.find(n => n.id === nodeId);
        if (!node) return;

        const zoneType = detectZoneType(node);
        const style = getZoneStyle(zoneType);
        
        const x = startX + idx * (zoneWidth + horizontalGap);
        const y = layerY;

        // Adjust size based on zone type
        let w = zoneWidth;
        let h = zoneHeight;
        
        if (zoneType === 'corridor') {
          w = 100;
          h = 60;
        } else if (zoneType === 'hall' || zoneType === 'sanctum') {
          w = 160;
          h = 110;
        }

        positions[nodeId] = { x, y, width: w, height: h };
        
        // Track max height
        maxHeight = Math.max(maxHeight, y + h);

        rooms.push({
          id: nodeId,
          label: style.label ? (node.name || node.id).replace(/_/g, ' ').toUpperCase() : '',
          x,
          y,
          width: w,
          height: h,
          color: style.baseColor,
          borderColor: style.borderColor,
          borderWidth: style.borderWidth,
          type: zoneType,
          icon: style.icon
        });

        const capacity = node.capacity || 100;
        capacityPoints.push({
          id: nodeId,
          x: x + w / 2,
          y: y + h / 2,
          label: capacity.toString()
        });
      });
    });

    // Add bottom padding
    maxHeight += padding;

    return { rooms, capacityPoints, positions, maxHeight };
  };

  // ✅ Get density color
  const getDensityColor = (density, baseColor) => {
    if (density > 5.0) return 'rgba(239, 68, 68, 0.5)';
    if (density > 3.0) return 'rgba(251, 191, 36, 0.4)';
    if (density > 1.5) return 'rgba(251, 191, 36, 0.2)';
    return baseColor;
  };

  // ✅ Get node data
  const getNodeData = (roomId) => {
    if (state?.nodes && state.nodes[roomId]) {
      return state.nodes[roomId];
    }
    if (graphData?.nodes) {
      const node = graphData.nodes.find(n => n.id === roomId);
      if (node) {
        return {
          current_count: node.agent_count || 0,
          density: node.density || 0
        };
      }
    }
    return { current_count: 0, density: 0 };
  };

  useEffect(() => {
    if (!canvasRef.current || !graphData) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Generate layout with calculated height
    const layout = generateSmartLayout(graphData, width);
    
    // ✅ Set dynamic canvas height
    const calculatedHeight = Math.max(layout.maxHeight, 400);
    setCanvasHeight(calculatedHeight);
    
    canvas.width = width;
    canvas.height = calculatedHeight;

    // Clear with grid background
    ctx.fillStyle = '#fafafa';
    ctx.fillRect(0, 0, width, calculatedHeight);

    // Draw grid
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 0.5;
    const gridSize = 20;
    for (let x = 0; x <= width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, calculatedHeight);
      ctx.stroke();
    }
    for (let y = 0; y <= calculatedHeight; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw connections
    if (graphData.edges && layout.positions) {
      ctx.strokeStyle = '#9ca3af';
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.setLineDash([5, 5]);

      graphData.edges.forEach(edge => {
        const fromId = edge.from || edge.source;
        const toId = edge.to || edge.target;
        const fromPos = layout.positions[fromId];
        const toPos = layout.positions[toId];

        if (fromPos && toPos) {
          ctx.beginPath();
          ctx.moveTo(fromPos.x + fromPos.width / 2, fromPos.y + fromPos.height / 2);
          ctx.lineTo(toPos.x + toPos.width / 2, toPos.y + toPos.height / 2);
          ctx.stroke();
        }
      });

      ctx.setLineDash([]);
    }

    // Draw rooms
    layout.rooms.forEach(room => {
      const nodeData = getNodeData(room.id);
      const density = nodeData.density || 0;
      const agentCount = nodeData.current_count || 0;

      const fillColor = getDensityColor(density, room.color);
      ctx.fillStyle = fillColor;
      ctx.fillRect(room.x, room.y, room.width, room.height);

      ctx.strokeStyle = room.borderColor;
      ctx.lineWidth = room.borderWidth;
      ctx.strokeRect(room.x, room.y, room.width, room.height);

      if (room.type !== 'corridor') {
        ctx.strokeStyle = '#9ca3af';
        ctx.lineWidth = 1;
        ctx.strokeRect(room.x + 2, room.y + 2, room.width - 4, room.height - 4);
      }

      if (room.icon) {
        ctx.font = 'bold 18px Arial';
        ctx.fillText(room.icon, room.x + 10, room.y + 25);
      }

      if (room.label) {
        ctx.font = 'bold 11px Arial';
        ctx.fillStyle = '#1f2937';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const words = room.label.split(' ');
        if (words.length > 2 && room.width < 140) {
          ctx.fillText(words.slice(0, 2).join(' '), room.x + room.width / 2, room.y + room.height / 2 - 12);
          ctx.fillText(words.slice(2).join(' '), room.x + room.width / 2, room.y + room.height / 2 + 2);
        } else {
          ctx.fillText(room.label, room.x + room.width / 2, room.y + room.height / 2 - 8);
        }
      }

      if (density > 0) {
        ctx.font = '9px Arial';
        ctx.fillStyle = density > 5.0 ? '#dc2626' : density > 3.0 ? '#f59e0b' : '#6b7280';
        ctx.fillText(
          `${density.toFixed(1)} p/m²`,
          room.x + room.width / 2,
          room.y + room.height / 2 + (room.label ? 12 : 5)
        );
      }

      if (agentCount > 0) {
        const badgeX = room.x + room.width - 18;
        const badgeY = room.y + 15;
        
        ctx.fillStyle = 'rgba(59, 130, 246, 0.9)';
        ctx.beginPath();
        ctx.arc(badgeX, badgeY, 11, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        ctx.font = 'bold 9px Arial';
        ctx.fillStyle = '#fff';
        ctx.textAlign = 'center';
        ctx.fillText(agentCount.toString(), badgeX, badgeY + 3);
      }

      if (density > 5.0) {
        ctx.font = 'bold 20px Arial';
        ctx.fillText('⚠️', room.x + room.width - 35, room.y + room.height - 12);
      }
    });

    // Draw capacity circles
    layout.capacityPoints.forEach(point => {
      const nodeData = getNodeData(point.id);
      const density = nodeData.density || 0;

      const radius = 20;
      let circleColor = '#4ade80';
      if (density > 5.0) circleColor = '#ef4444';
      else if (density > 3.0) circleColor = '#fbbf24';

      if (density > 5.0) {
        ctx.shadowBlur = 12;
        ctx.shadowColor = 'rgba(239, 68, 68, 0.6)';
      }

      ctx.fillStyle = circleColor;
      ctx.globalAlpha = 0.9;
      ctx.beginPath();
      ctx.arc(point.x, point.y, radius, 0, 2 * Math.PI);
      ctx.fill();
      ctx.globalAlpha = 1.0;
      ctx.shadowBlur = 0;

      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      ctx.font = 'bold 12px Arial';
      ctx.fillStyle = '#fff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(point.label, point.x, point.y);
    });

    // Draw legend
    const legendX = width - 150;
    const legendY = 15;

    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 2;
    ctx.fillRect(legendX, legendY, 135, 90);
    ctx.strokeRect(legendX, legendY, 135, 90);

    ctx.font = 'bold 11px Arial';
    ctx.fillStyle = '#1f2937';
    ctx.textAlign = 'left';
    ctx.fillText('Density Levels', legendX + 8, legendY + 18);

    const legendItems = [
      { label: '< 1.5 Safe', color: '#4ade80' },
      { label: '1.5-3 Caution', color: '#fbbf24' },
      { label: '> 5.0 Danger', color: '#ef4444' }
    ];

    legendItems.forEach((item, i) => {
      const itemY = legendY + 35 + i * 20;
      ctx.fillStyle = item.color;
      ctx.fillRect(legendX + 8, itemY, 11, 11);
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 1;
      ctx.strokeRect(legendX + 8, itemY, 11, 11);
      ctx.font = '9px Arial';
      ctx.fillStyle = '#374151';
      ctx.fillText(item.label, legendX + 24, itemY + 8);
    });

  }, [graphData, state, width]);

  return (
    <div className="relative border border-gray-300 rounded-lg overflow-hidden shadow-lg bg-white">
      <canvas 
        ref={canvasRef} 
        style={{ width: '100%', height: 'auto', display: 'block' }}
      />
    </div>
  );
};

export default FloorPlanCanvas;
