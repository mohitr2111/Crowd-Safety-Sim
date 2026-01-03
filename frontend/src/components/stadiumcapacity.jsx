import React from 'react';

const StadiumCapacity = ({ stadiumStatus }) => {
  if (!stadiumStatus) return null;

  const { occupancy_percent, current_occupancy, capacity, status } = stadiumStatus.stadium_status;
  
  let statusColor = 'emerald';
  if (occupancy_percent > 90) statusColor = 'red';
  else if (occupancy_percent > 70) statusColor = 'amber';

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-200">Stadium Capacity</h3>
        <div className="text-right">
          <div className={`text-2xl font-bold text-${statusColor}-400`}>
            {occupancy_percent?.toFixed(1)}%
          </div>
          <div className="text-xs text-slate-500">
            {current_occupancy} / {capacity} people
          </div>
        </div>
      </div>

      <div className="relative w-full bg-slate-800 rounded-full h-4 overflow-hidden mb-4">
        <div
          className={`h-4 transition-all duration-500 rounded-full ${
            occupancy_percent > 90
              ? 'bg-gradient-to-r from-red-600 to-red-500'
              : occupancy_percent > 70
              ? 'bg-gradient-to-r from-amber-600 to-amber-500'
              : 'bg-gradient-to-r from-emerald-600 to-emerald-500'
          }`}
          style={{ width: `${Math.min(100, occupancy_percent || 0)}%` }}
        />
      </div>

      <div className="flex items-center justify-between">
        <span
          className={`px-3 py-1.5 rounded-lg text-sm font-bold ${
            status === 'FULL'
              ? 'bg-red-500/20 text-red-400 border border-red-500/30'
              : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
          }`}
        >
          {status === 'FULL' ? 'AT CAPACITY' : 'AVAILABLE'}
        </span>
        
        <div className="text-xs text-slate-500">
          Updated: {new Date(stadiumStatus.timestamp * 1000).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default StadiumCapacity;
