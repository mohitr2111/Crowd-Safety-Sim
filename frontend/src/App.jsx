import React, { useState } from 'react';
import ComparisonDashboard from './components/CompariosonDashboard';
import LiveSimulation from './Pages/AiSimulation';
import Background3D from './components/Background3D';
import PhotoToLayout from './components/PhotoToLayout';
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
                  Live Simulation
                </button>
                <button
                  onClick={() => setActiveTab('photo')}
                  className={`tab-button ${activeTab === 'photo' ? 'active' : ''}`}
                >
                  <span className="hidden sm:inline">Photo to Layout</span>
                  <span className="sm:hidden">Layout</span>
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
          {activeTab === 'live' && <LiveSimulation />}
          {activeTab === 'photo' && (
            <div className="p-6">
              <PhotoToLayout />
            </div>
          )}
          {activeTab === 'comparison' && (
            <div className="p-6">
              <ComparisonDashboard />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;

