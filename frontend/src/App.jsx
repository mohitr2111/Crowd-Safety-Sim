import React, { useState } from 'react';
import ComparisonDashboard from './components/CompariosonDashboard';
import LiveSimulation from './Pages/AiSimulation';
<<<<<<< HEAD
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
=======
import Background3D from './components/Background3D';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('live');

  return (
    <div className="min-h-screen relative">
      <Background3D />
      
      <div className="relative" style={{ zIndex: 1 }}>
        <header className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-slate-700/50">
          <div className="max-w-7xl mx-auto px-6 py-5">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold gradient-text">
                  Crowd Safety Simulation Platform
                </h1>
                <p className="text-slate-400 text-sm mt-1">
                  AI-Driven Infrastructure Simulation for Disaster Prevention
                </p>
              </div>

              <nav className="flex gap-2 p-1 bg-slate-800/50 rounded-xl border border-slate-700/50">
                <button
                  onClick={() => setActiveTab('live')}
                  className={`tab-button ${activeTab === 'live' ? 'active' : ''}`}
                >
                  Live AI Simulation
                </button>
                <button
                  onClick={() => setActiveTab('comparison')}
                  className={`tab-button ${activeTab === 'comparison' ? 'active' : ''}`}
                >
                  AI vs Baseline
                </button>
              </nav>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto animate-fade-in">
          {activeTab === 'live' ? (
            <LiveSimulation />
          ) : (
            <div className="p-6">
              <ComparisonDashboard />
            </div>
          )}
        </main>
>>>>>>> nikhil
      </div>
    </div>
  );
}

export default App;
