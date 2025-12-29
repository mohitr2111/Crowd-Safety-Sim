import React from 'react';

const VenueCapacity = ({ stadiumStatus }) => {
  // Handle loading state
  if (!stadiumStatus) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold mb-4 text-gray-800">
          🏟️ Venue Capacity
        </h3>
        <div className="text-gray-500">Loading venue status...</div>
      </div>
    );
  }

  // ✅ Safe destructuring with defaults
  const {
    name = "Venue",
    capacity = 0,
    current_occupancy = 0,
    occupancy_percent = 0,
    status = "AVAILABLE"
  } = stadiumStatus || {};

  // Determine status color
  const getStatusColor = () => {
    if (occupancy_percent >= 90) return 'bg-red-500';
    if (occupancy_percent >= 70) return 'bg-orange-500';
    if (occupancy_percent >= 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusText = () => {
    if (occupancy_percent >= 90) return 'CRITICAL';
    if (occupancy_percent >= 70) return 'HIGH';
    if (occupancy_percent >= 50) return 'MODERATE';
    return 'SAFE';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-bold mb-4 text-gray-800 flex items-center gap-2">
        <span className="text-2xl">🏟️</span>
        {name || 'Venue'} Capacity
      </h3>

      {/* Capacity Bar */}
      <div className="mb-4">
        <div className="flex justify-between mb-2">
          <span className="text-sm text-gray-600">Current Occupancy</span>
          <span className="text-sm font-bold text-gray-800">
            {current_occupancy?.toLocaleString() || 0} / {capacity?.toLocaleString() || 0} people
          </span>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
          <div
            className={`h-6 transition-all duration-500 flex items-center justify-center text-white text-xs font-bold ${getStatusColor()}`}
            style={{ width: `${Math.min(occupancy_percent || 0, 100)}%` }}
          >
            {occupancy_percent?.toFixed(1) || 0}%
          </div>
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
          <span className="text-sm font-semibold text-gray-700">
            Status: {getStatusText()}
          </span>
        </div>

        {status === 'FULL' && (
          <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs font-bold">
            ⚠️ AT CAPACITY
          </span>
        )}
        {status === 'AVAILABLE' && occupancy_percent < 50 && (
          <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold">
            ✅ AVAILABLE
          </span>
        )}
      </div>

      {/* Capacity Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-gray-500">Total Capacity</div>
            <div className="text-lg font-bold text-gray-800">
              {capacity?.toLocaleString() || 0}
            </div>
          </div>
          <div>
            <div className="text-gray-500">Remaining</div>
            <div className="text-lg font-bold text-blue-600">
              {((capacity || 0) - (current_occupancy || 0)).toLocaleString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VenueCapacity;
