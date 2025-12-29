// frontend/src/components/SimulationCanvas.jsx

import React, { useEffect, useRef, useState } from 'react'; // ✅ ADD useState

const SimulationCanvas = ({ graphData, state, width = 800, height = 600 }) => {
  const canvasRef = useRef(null);
  const [simulation, setSimulation] = useState(null);

  // Helper function to get gradient color based on density
  const getDensityColor = (density, maxDensity = 6.0) => {
    const normalized = Math.min(density / maxDensity, 1);
    
    if (density < 2.0) {
      // SAFE - Green gradient
      return `rgba(74, 200, 80, 0.9)`;
    } else if (density < 4.0) {
      // WARNING - Yellow to Orange gradient
      const t = (density - 2.0) / 2.0;
      const r = Math.floor(251 + (239 - 251) * t);
      const g = Math.floor(191 - (68 - 191) * t);
      const b = 36;
      return `rgba(${r}, ${g}, ${b}, 0.9)`;
    } else {
      // DANGER - Red gradient
      const intensity = Math.min((density - 4.0) / 2.0, 1);
      const r = 239;
      const g = Math.floor(68 * (1 - intensity * 0.5));
      const b = Math.floor(68 * (1 - intensity * 0.5));
      return `rgba(${r}, ${g}, ${b}, 0.9)`;
    }
  };

  // Helper function to get node radius based on capacity
  const getNodeRadius = (nodeType, capacity) => {
    if (nodeType === 'zone') return 40;
    if (nodeType === 'exit') return 25;
    return 30;
  };

  // Helper function to draw legend
  const drawLegend = (ctx, canvasWidth, canvasHeight) => {
    const legendX = canvasWidth - 150;
    const legendY = 20;
    const boxSize = 20;
    const padding = 10;

    // Legend background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 2;
    ctx.fillRect(legendX - padding, legendY - padding, 140, 140);
    ctx.strokeRect(legendX - padding, legendY - padding, 140, 140);

    // Title
    ctx.font = 'bold 12px Arial';
    ctx.fillStyle = '#1f2937';
    ctx.textAlign = 'left';
    ctx.fillText('Density Levels', legendX, legendY + 10);

    // Legend items
    const items = [
      { label: '< 2.0 p/m² (Safe)', color: getDensityColor(1.0) },
      { label: '2-4 p/m² (Warning)', color: getDensityColor(3.0) },
      { label: '> 4.0 p/m² (Danger)', color: getDensityColor(5.0) }
    ];

    items.forEach((item, index) => {
      const y = legendY + 30 + index * 30;
      
      // Color box
      ctx.fillStyle = item.color;
      ctx.fillRect(legendX, y, boxSize, boxSize);
      ctx.strokeStyle = '#374151';
      ctx.lineWidth = 1;
      ctx.strokeRect(legendX, y, boxSize, boxSize);
      
      // Label
      ctx.font = '11px Arial';
      ctx.fillStyle = '#374151';
      ctx.fillText(item.label, legendX + boxSize + 8, y + 15);
    });
  };

  useEffect(() => {
    if (!graphData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = width;
    canvas.height = height;
    
    // Clear canvas with light background
    ctx.fillStyle = '#f9fafb';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // ✅ UPDATED: Layout nodes in a circle pattern if no x,y coordinates
    const nodes = graphData.nodes.map((node, idx) => {
      if (node.x && node.y) {
        return node; // Use existing coordinates
      }
      
      // Auto-layout in circle
      const angle = (idx / graphData.nodes.length) * 2 * Math.PI;
      const radius = Math.min(width, height) * 0.3;
      return {
        ...node,
        x: width / 2 + Math.cos(angle) * radius,
        y: height / 2 + Math.sin(angle) * radius
      };
    });

    // Draw edges (paths)
    graphData.edges.forEach(edge => {
      const fromNode = nodes.find(n => n.id === edge.from || n.id === edge.source);
      const toNode = nodes.find(n => n.id === edge.to || n.id === edge.target);
      
      if (fromNode && toNode) {
        ctx.strokeStyle = '#d1d5db';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(fromNode.x, fromNode.y);
        ctx.lineTo(toNode.x, toNode.y);
        ctx.stroke();
      }
    });

    // Draw nodes with gradient heatmap
    nodes.forEach(node => {
      const x = node.x;
      const y = node.y;
      const radius = getNodeRadius(node.type, node.capacity);

      // ✅ UPDATED: Support both state formats
      let agentCount = 0;
      let density = 0;

      if (state && state.nodes) {
        // Format 1: state.nodes[node.id]
        const nodeState = state.nodes[node.id];
        agentCount = nodeState?.current_count || 0;
        density = node.area_m2 > 0 ? agentCount / node.area_m2 : 0;
      } else if (node.agent_count !== undefined) {
        // Format 2: node.agent_count and node.density
        agentCount = node.agent_count || 0;
        density = node.density || 0;
      }
      
      // Get gradient color based on density
      const fillColor = getDensityColor(density);

      // Draw outer glow for danger zones
      if (density > 4.0) {
        ctx.shadowBlur = 20;
        ctx.shadowColor = 'rgba(239, 68, 68, 0.6)';
      } else {
        ctx.shadowBlur = 0;
      }

      // Draw node circle with gradient
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      const fillColorSolid = fillColor.replace('0.9', '1.0');
      const fillColorTrans = fillColor.replace('0.9', '0.5');

      gradient.addColorStop(0, fillColorSolid);
      gradient.addColorStop(1, fillColorTrans);

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();

      // Reset shadow
      ctx.shadowBlur = 0;

      // Draw border based on node type
      if (node.type === 'exit') {
        ctx.strokeStyle = '#16a34a';
        ctx.lineWidth = 3;
      } else if (node.type === 'entry') {
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;
      } else if (node.type === 'zone') {
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;
      } else {
        ctx.strokeStyle = '#374151';
        ctx.lineWidth = 2;
      }
      ctx.stroke();

      // Draw node label with background
      ctx.font = 'bold 11px Arial';
      ctx.textAlign = 'center';
      const label = (node.label || node.name || node.id).replace(/_/g, ' ').substring(0, 10);
      const labelWidth = ctx.measureText(label).width;
      
      // Label background
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.fillRect(x - labelWidth/2 - 4, y - radius - 20, labelWidth + 8, 16);
      
      // Label text
      ctx.fillStyle = '#1f2937';
      ctx.fillText(label, x, y - radius - 8);

      // Draw occupancy count with background
      ctx.font = 'bold 14px Arial';
      const countText = agentCount.toString();
      
      // Count background circle
      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
      ctx.beginPath();
      ctx.arc(x, y, 12, 0, 2 * Math.PI);
      ctx.fill();
      
      // Count text
      ctx.fillStyle = density > 4.0 ? '#dc2626' : '#1f2937';
      ctx.fillText(countText, x, y + 5);

      // Draw density indicator below node
      ctx.font = '9px Arial';
      ctx.fillStyle = '#6b7280';
      ctx.fillText(`${density.toFixed(1)} p/m²`, x, y + radius + 15);

      // Draw danger icon for high density
      if (density > 4.0) {
        ctx.font = 'bold 20px Arial';
        ctx.fillText('⚠️', x + radius - 10, y - radius + 10);
      }
    });

    // ✅ UPDATED: Draw agents (support both formats)
    const agents = state?.agents || {};
    const agentEntries = Array.isArray(agents) 
      ? agents.map((a, i) => [i, a]) 
      : Object.entries(agents);

    agentEntries.forEach(([agentId, agent]) => {
      const nodeId = agent.current_node || agent.position;
      const node = nodes.find(n => n.id === nodeId);
      if (!node) return;

      // Random offset for visual variety
      const offsetX = (Math.random() - 0.5) * 20;
      const offsetY = (Math.random() - 0.5) * 20;
      const x = node.x + offsetX;
      const y = node.y + offsetY;

      // Agent color by type
      const agentColors = {
        normal: '#3b82f6',
        family: '#8b5cf6',
        elderly: '#f59e0b',
        rushing: '#ef4444'
      };

      const color = agentColors[agent.type] || '#3b82f6';

      // Draw agent with shadow
      ctx.shadowBlur = 3;
      ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();

      // Draw white outline
      ctx.shadowBlur = 0;
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Draw legend
    drawLegend(ctx, canvas.width, canvas.height);

  }, [graphData, state, width, height]);

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        className="border-2 border-gray-300 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 shadow-lg"
      />
      
      {/* Overlay stats */}
      <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm p-3 rounded-lg shadow-lg border-2 border-gray-200">
        <div className="text-xs font-semibold text-gray-700 mb-1">Live Statistics</div>
        <div className="text-sm">
          <span className="font-bold text-blue-600">
            {state?.agents ? (Array.isArray(state.agents) ? state.agents.length : Object.keys(state.agents).length) : 0}
          </span>
          <span className="text-gray-600"> active agents</span>
        </div>
        <div className="text-sm">
          <span className="font-bold text-green-600">{state?.reached_goal || 0}</span>
          <span className="text-gray-600"> reached goal</span>
        </div>
      </div>
    </div>
  );
};

export default SimulationCanvas;
