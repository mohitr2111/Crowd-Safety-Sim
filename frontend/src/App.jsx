import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Header from './Pages/Header';
import ComparisonDashboard from './components/CompariosonDashboard';
import LiveSimulation from './Pages/AiSimulation';
import ScenarioBuilder from './Pages/ScenarioBuilder';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Header with Navigation */}
        <Header />
        
        {/* Main Content */}
        <main className="max-w-7xl mx-auto">
          <Routes>
            {/* Route 1: Live Simulation (Home) */}
            <Route path="/" element={<LiveSimulation />} />
            
            {/* Route 2: Scenario Builder */}
            <Route 
              path="/scenario-builder" 
              element={
                <div className="p-8">
                  <ScenarioBuilder />
                </div>
              } 
            />
            
            {/* Route 3: Comparison Dashboard */}
            <Route 
              path="/comparison" 
              element={
                <div className="p-8">
                  <ComparisonDashboard />
                </div>
              } 
            />

            {/* 404 Page */}
            <Route 
              path="*" 
              element={
                <div className="p-8 text-center">
                  <div className="max-w-md mx-auto">
                    <h2 className="text-6xl mb-4">🤔</h2>
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">
                      404 - Page Not Found
                    </h2>
                    <p className="text-gray-600 mb-6">
                      The page you're looking for doesn't exist.
                    </p>
                    <Link 
                      to="/" 
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold inline-block"
                    >
                      ← Go Back Home
                    </Link>
                  </div>
                </div>
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
