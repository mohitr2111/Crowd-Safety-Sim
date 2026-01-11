import React, { useState } from 'react';
import ComparisonDashboard from './components/CompariosonDashboard';
import LiveSimulation from './Pages/AiSimulation';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('live'); // Only 2 tabs now

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🚨 Crowd Safety Simulation Platform
          </h1>
          <p className="text-gray-600">
            AI-Driven Infrastructure Simulation for Disaster Prevention
          </p>

          {/* Tabs - Only 2 now */}
          <div className="mt-4 flex gap-2">
            <button
              onClick={() => setActiveTab('live')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                activeTab === 'live'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              🚀 Live AI Simulation
            </button>
            <button
              onClick={() => setActiveTab('comparison')}
              className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                activeTab === 'comparison'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              📊 AI vs Baseline Comparison
            </button>
          </div>
        </div>
      </div>

      {/* Content - Only 2 options */}
      <div className="max-w-7xl mx-auto">
        {activeTab === 'live' ? (
          <LiveSimulation />
        ) : (
          <div className="p-8">
            <ComparisonDashboard />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
