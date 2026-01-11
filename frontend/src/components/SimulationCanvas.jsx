import React, { useEffect, useRef } from 'react';

const SimulationCanvas = ({ graphData, state }) => {
  const canvasRef = useRef(null);

<<<<<<< HEAD
  // Helper function to get color based on density
  const getDensityColor = (density) => {
    if (density < 2.0) {
      return '#4ade80'; // Green for safe
    } else if (density < 4.0) {
      return '#fbbf24'; // Yellow/Amber for warning
    } else {
      return '#ef4444'; // Red for danger
    }
  };

=======
>>>>>>> nikhil
  useEffect(() => {
    if (!graphData || !state) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
<<<<<<< HEAD
    // White background like the image
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw faint grey grid lines (like the image)
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 1;
    const gridSize = 20;
=======
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = 'rgba(51, 65, 85, 0.5)';
    ctx.lineWidth = 1;
    const gridSize = 30;
>>>>>>> nikhil
    for (let x = 0; x < canvas.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

<<<<<<< HEAD
    // Scale for visualization
    const scaleX = canvas.width / 100;
    const scaleY = canvas.height / 100;

    // Draw edges (pathways) in light grey
=======
    const scaleX = canvas.width / 100;
    const scaleY = canvas.height / 100;

>>>>>>> nikhil
    graphData.edges.forEach(edge => {
      const fromNode = graphData.nodes.find(n => n.id === edge.from);
      const toNode = graphData.nodes.find(n => n.id === edge.to);
      
      if (fromNode && toNode) {
<<<<<<< HEAD
        ctx.strokeStyle = '#d1d5db';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
=======
        const gradient = ctx.createLinearGradient(
          fromNode.x * scaleX, fromNode.y * scaleY,
          toNode.x * scaleX, toNode.y * scaleY
        );
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.3)');
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.setLineDash([8, 4]);
>>>>>>> nikhil
        ctx.beginPath();
        ctx.moveTo(fromNode.x * scaleX, fromNode.y * scaleY);
        ctx.lineTo(toNode.x * scaleX, toNode.y * scaleY);
        ctx.stroke();
<<<<<<< HEAD
      }
    });

    // Draw zones as rectangular areas (like floor plan)
=======
        ctx.setLineDash([]);
      }
    });

>>>>>>> nikhil
    graphData.nodes.forEach(node => {
      const nodeState = state.nodes[node.id];
      const x = node.x * scaleX;
      const y = node.y * scaleY;
      
<<<<<<< HEAD
      // Calculate density
=======
>>>>>>> nikhil
      const density = node.area_m2 > 0 
        ? nodeState.current_count / node.area_m2 
        : 0;
      
<<<<<<< HEAD
      // Zone size based on area (rectangular)
      const zoneWidth = Math.sqrt(node.area_m2) * 3;
      const zoneHeight = Math.sqrt(node.area_m2) * 2.5;
      
      // Draw zone background - light grey for pathways, pale yellow for important areas
      const isImportant = node.type === 'entrance' || node.type === 'exit' || node.id.toLowerCase().includes('sanctum') || node.id.toLowerCase().includes('hall');
      ctx.fillStyle = isImportant ? '#fef3c7' : '#f3f4f6'; // Pale yellow for important, light grey for others
      ctx.fillRect(x - zoneWidth/2, y - zoneHeight/2, zoneWidth, zoneHeight);
      
      // Draw zone border
      ctx.strokeStyle = density > 4.0 ? '#ef4444' : '#9ca3af';
      ctx.lineWidth = density > 4.0 ? 3 : 1;
      ctx.strokeRect(x - zoneWidth/2, y - zoneHeight/2, zoneWidth, zoneHeight);

      // Draw zone label (like "ENTRANCE", "INNER HALL", "SANCTUM")
      ctx.font = 'bold 12px Arial';
      ctx.fillStyle = '#1f2937';
      ctx.textAlign = 'center';
      const label = node.id.replace(/_/g, ' ').toUpperCase().substring(0, 15);
      
      // Label background for readability
      const labelWidth = ctx.measureText(label).width;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.fillRect(x - labelWidth/2 - 4, y - zoneHeight/2 - 18, labelWidth + 8, 16);
      
      // Label text
      ctx.fillStyle = '#1f2937';
      ctx.fillText(label, x, y - zoneHeight/2 - 6);
    });

    // Draw agents as rectangles (not circles) - distributed in grid within zones
=======
      const zoneWidth = Math.sqrt(node.area_m2) * 3.5;
      const zoneHeight = Math.sqrt(node.area_m2) * 2.8;
      
      let bgColor, borderColor, glowColor;
      if (density > 4.0) {
        bgColor = 'rgba(239, 68, 68, 0.15)';
        borderColor = '#ef4444';
        glowColor = 'rgba(239, 68, 68, 0.4)';
      } else if (density > 2.0) {
        bgColor = 'rgba(251, 191, 36, 0.1)';
        borderColor = '#fbbf24';
        glowColor = 'rgba(251, 191, 36, 0.3)';
      } else {
        bgColor = 'rgba(30, 41, 59, 0.8)';
        borderColor = '#334155';
        glowColor = 'transparent';
      }
      
      if (density > 2.0) {
        ctx.shadowColor = glowColor;
        ctx.shadowBlur = 20;
      }
      
      ctx.fillStyle = bgColor;
      ctx.beginPath();
      ctx.roundRect(x - zoneWidth/2, y - zoneHeight/2, zoneWidth, zoneHeight, 8);
      ctx.fill();
      
      ctx.shadowBlur = 0;
      
      ctx.strokeStyle = borderColor;
      ctx.lineWidth = density > 4.0 ? 3 : 2;
      ctx.beginPath();
      ctx.roundRect(x - zoneWidth/2, y - zoneHeight/2, zoneWidth, zoneHeight, 8);
      ctx.stroke();

      ctx.font = 'bold 11px Inter, system-ui, sans-serif';
      ctx.fillStyle = '#94a3b8';
      ctx.textAlign = 'center';
      const label = node.id.replace(/_/g, ' ').toUpperCase().substring(0, 15);
      ctx.fillText(label, x, y - zoneHeight/2 - 8);
    });

>>>>>>> nikhil
    const agentsByNode = {};
    Object.entries(state.agents).forEach(([agentId, agent]) => {
      if (!agentsByNode[agent.current_node]) {
        agentsByNode[agent.current_node] = [];
      }
      agentsByNode[agent.current_node].push(agent);
    });

    Object.entries(agentsByNode).forEach(([nodeId, agents]) => {
      const node = graphData.nodes.find(n => n.id === nodeId);
      if (!node) return;

<<<<<<< HEAD
      const nodeState = state.nodes[nodeId];
      const density = node.area_m2 > 0 
        ? nodeState.current_count / node.area_m2 
        : 0;

      const nodeX = node.x * scaleX;
      const nodeY = node.y * scaleY;
      const zoneWidth = Math.sqrt(node.area_m2) * 3;
      const zoneHeight = Math.sqrt(node.area_m2) * 2.5;
      
      // Calculate grid layout for agents
=======
      const nodeX = node.x * scaleX;
      const nodeY = node.y * scaleY;
      const zoneWidth = Math.sqrt(node.area_m2) * 3.5;
      const zoneHeight = Math.sqrt(node.area_m2) * 2.8;
      
>>>>>>> nikhil
      const agentsInNode = agents.length;
      const gridCols = Math.ceil(Math.sqrt(agentsInNode));
      const gridRows = Math.ceil(agentsInNode / gridCols);
      
      const spacingX = zoneWidth / (gridCols + 1);
      const spacingY = zoneHeight / (gridRows + 1);
      
      agents.forEach((agent, index) => {
        const col = index % gridCols;
        const row = Math.floor(index / gridCols);
        
        const offsetX = (col + 1) * spacingX - zoneWidth/2;
        const offsetY = (row + 1) * spacingY - zoneHeight/2;
        
        const agentX = nodeX + offsetX;
        const agentY = nodeY + offsetY;

<<<<<<< HEAD
        // Agent color - green rectangles like in the image
        const agentColor = '#22c55e'; // Green like the image

        // Draw rectangular agent (not circle)
        const rectSize = 5;
        ctx.fillStyle = agentColor;
        ctx.fillRect(agentX - rectSize/2, agentY - rectSize/2, rectSize, rectSize);
        
        // Draw border
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.strokeRect(agentX - rectSize/2, agentY - rectSize/2, rectSize, rectSize);
      });
    });

    // Draw green rectangles with numbers (like in the image) for each zone
=======
        ctx.shadowColor = 'rgba(59, 130, 246, 0.6)';
        ctx.shadowBlur = 4;
        ctx.fillStyle = '#3b82f6';
        ctx.beginPath();
        ctx.arc(agentX, agentY, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      });
    });

>>>>>>> nikhil
    graphData.nodes.forEach(node => {
      const nodeState = state.nodes[node.id];
      const x = node.x * scaleX;
      const y = node.y * scaleY;
<<<<<<< HEAD
      const zoneWidth = Math.sqrt(node.area_m2) * 3;
      const zoneHeight = Math.sqrt(node.area_m2) * 2.5;
      
      // Position count indicator (green rectangle with number)
      const countX = x + zoneWidth/2 - 30;
      const countY = y - zoneHeight/2 + 10;
      
      // Draw green rectangle background
      ctx.fillStyle = '#22c55e';
      ctx.fillRect(countX, countY, 40, 25);
      
      // Draw border
      ctx.strokeStyle = '#16a34a';
      ctx.lineWidth = 2;
      ctx.strokeRect(countX, countY, 40, 25);
      
      // Draw count number in white
      ctx.font = 'bold 14px Arial';
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.fillText(nodeState.current_count.toString(), countX + 20, countY + 18);
=======
      const zoneWidth = Math.sqrt(node.area_m2) * 3.5;
      const zoneHeight = Math.sqrt(node.area_m2) * 2.8;
      
      const density = node.area_m2 > 0 
        ? nodeState.current_count / node.area_m2 
        : 0;
      
      const badgeX = x + zoneWidth/2 - 25;
      const badgeY = y - zoneHeight/2 + 8;
      
      let badgeColor = '#10b981';
      if (density > 4.0) badgeColor = '#ef4444';
      else if (density > 2.0) badgeColor = '#fbbf24';
      
      ctx.fillStyle = badgeColor;
      ctx.beginPath();
      ctx.roundRect(badgeX, badgeY, 35, 22, 6);
      ctx.fill();
      
      ctx.font = 'bold 12px Inter, system-ui, sans-serif';
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.fillText(nodeState.current_count.toString(), badgeX + 17.5, badgeY + 15);
>>>>>>> nikhil
    });

  }, [graphData, state]);

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
<<<<<<< HEAD
        style={{
          border: '2px solid #e5e7eb',
          borderRadius: '8px',
          backgroundColor: '#ffffff',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}
      />
      
      {/* Overlay stats */}
      {state && (
        <div style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          padding: '12px',
          borderRadius: '8px',
          border: '1px solid #e5e7eb',
          color: '#1f2937',
          fontSize: '12px',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Live Statistics</div>
          <div>
            <span style={{ fontWeight: 'bold', color: '#3b82f6' }}>
              {Object.keys(state?.agents || {}).length}
            </span>
            <span style={{ color: '#6b7280' }}> active agents</span>
          </div>
          <div>
            <span style={{ fontWeight: 'bold', color: '#22c55e' }}>
              {state?.reached_goal || 0}
            </span>
            <span style={{ color: '#6b7280' }}> reached goal</span>
          </div>
        </div>
      )}
=======
        className="w-full h-auto rounded-xl border border-slate-700"
        style={{ maxWidth: '100%' }}
      />
      
      {state && (
        <div className="absolute top-4 left-4 glass-card p-3 text-xs">
          <div className="font-bold text-slate-300 mb-2">Live Statistics</div>
          <div className="space-y-1">
            <div>
              <span className="font-bold text-blue-400">
                {Object.keys(state?.agents || {}).length}
              </span>
              <span className="text-slate-500 ml-1">active agents</span>
            </div>
            <div>
              <span className="font-bold text-emerald-400">
                {state?.reached_goal || 0}
              </span>
              <span className="text-slate-500 ml-1">reached goal</span>
            </div>
          </div>
        </div>
      )}
      
      <div className="absolute bottom-4 right-4 glass-card p-3 text-xs">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            <span className="text-slate-400">Safe</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-amber-500"></div>
            <span className="text-slate-400">Warning</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-red-500"></div>
            <span className="text-slate-400">Danger</span>
          </div>
        </div>
      </div>
>>>>>>> nikhil
    </div>
  );
};

export default SimulationCanvas;
