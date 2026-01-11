import React from 'react';

const StadiumCapacity = ({ stadiumStatus }) => {
  if (!stadiumStatus) return null;

<<<<<<< HEAD
  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">🏟️ Stadium Capacity</h3>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {stadiumStatus.stadium_status.occupancy_percent?.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">
            {stadiumStatus.stadium_status.current_occupancy} / {stadiumStatus.stadium_status.capacity} people
=======
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
>>>>>>> nikhil
          </div>
        </div>
      </div>

<<<<<<< HEAD
      {/* Progress Bar */}
      <div className="relative w-full bg-gray-200 rounded-full h-6 overflow-hidden mb-3">
        <div
          className={`h-6 transition-all duration-500 flex items-center justify-end pr-2 ${
            stadiumStatus.stadium_status.occupancy_percent > 90
              ? 'bg-gradient-to-r from-red-500 to-red-600'
              : stadiumStatus.stadium_status.occupancy_percent > 70
              ? 'bg-gradient-to-r from-orange-400 to-orange-500'
              : 'bg-gradient-to-r from-green-400 to-green-500'
          }`}
          style={{ width: `${Math.min(100, stadiumStatus.stadium_status.occupancy_percent || 0)}%` }}
        >
          <span className="text-xs font-bold text-white drop-shadow">
            {stadiumStatus.stadium_status.occupancy_percent > 10 && 
              `${stadiumStatus.stadium_status.current_occupancy} people`
            }
          </span>
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center justify-between">
        <span
          className={`px-4 py-2 rounded-full text-sm font-bold ${
            stadiumStatus.stadium_status.status === 'FULL'
              ? 'bg-red-100 text-red-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {stadiumStatus.stadium_status.status === 'FULL' ? '🔴 AT CAPACITY' : '🟢 AVAILABLE'}
        </span>
        
        <div className="text-xs text-gray-500">
=======
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
>>>>>>> nikhil
          Updated: {new Date(stadiumStatus.timestamp * 1000).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

export default StadiumCapacity;
