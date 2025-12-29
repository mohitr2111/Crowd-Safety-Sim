// frontend/src/pages/ScenarioBuilder.jsx

import React, { useState } from 'react';
import VenueDesigner from '../components/VenueDesigner';
import EventConfigurator from '../components/EventConfigurator';
import TriggerTimeline from '../components/TriggerTimeline';
import LiveMonitor from '../components/LiveMonitor';

const ScenarioBuilder = () => {
  // State management
  const [currentStep, setCurrentStep] = useState(1); // Wizard steps: 1-4
  const [venueData, setVenueData] = useState({
    zones: [],
    connections: [],
    entries: [],
    exits: []
  });
  const [eventConfig, setEventConfig] = useState({
    eventType: 'political_rally',
    crowdSize: 30000,
    riskScore: 0
  });
  const [triggers, setTriggers] = useState([]);
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [simulationId, setSimulationId] = useState(null);

  // Navigation
  const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 4));
  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));

  // Start simulation
  const startSimulation = async () => {
    try {
      const response = await fetch('http://localhost:8000/simulation/create-custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          venue: venueData,
          event: eventConfig,
          triggers: triggers,
          num_agents: eventConfig.crowdSize
        })
      });

      const data = await response.json();
      setSimulationId(data.simulation_id);
      setSimulationRunning(true);
      setCurrentStep(4); // Move to monitoring
    } catch (error) {
      console.error('Failed to start simulation:', error);
      alert('Error starting simulation. Check backend connection.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          🎯 AI Scenario Builder
        </h1>
        <p className="text-gray-600">
          Create custom event scenarios and test AI interventions
        </p>
      </div>

      {/* Progress Steps */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          {[
            { num: 1, title: 'Design Venue', icon: '🏛️' },
            { num: 2, title: 'Configure Event', icon: '🎪' },
            { num: 3, title: 'Add Triggers', icon: '⚡' },
            { num: 4, title: 'Monitor & Test', icon: '📊' }
          ].map((step, idx) => (
            <div key={step.num} className="flex items-center flex-1">
              {/* Step Circle */}
              <div className="flex flex-col items-center">
                <div
                  className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold transition-all ${
                    currentStep >= step.num
                      ? 'bg-blue-600 text-white shadow-lg scale-110'
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {currentStep > step.num ? '✓' : step.icon}
                </div>
                <p className={`mt-2 text-sm font-medium ${
                  currentStep >= step.num ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {step.title}
                </p>
              </div>

              {/* Connector Line */}
              {idx < 3 && (
                <div className={`flex-1 h-1 mx-4 transition-all ${
                  currentStep > step.num ? 'bg-blue-600' : 'bg-gray-300'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Step 1: Venue Designer */}
          {currentStep === 1 && (
            <VenueDesigner
              venueData={venueData}
              setVenueData={setVenueData}
              onNext={nextStep}
            />
          )}

          {/* Step 2: Event Configurator */}
          {currentStep === 2 && (
            <EventConfigurator
              eventConfig={eventConfig}
              setEventConfig={setEventConfig}
              venueData={venueData}
              onNext={nextStep}
              onBack={prevStep}
            />
          )}

          {/* Step 3: Trigger Timeline */}
          {currentStep === 3 && (
            <TriggerTimeline
              triggers={triggers}
              setTriggers={setTriggers}
              eventConfig={eventConfig}
              onStart={startSimulation}
              onBack={prevStep}
            />
          )}

          {/* Step 4: Live Monitor */}
          {currentStep === 4 && simulationRunning && (
            <LiveMonitor
              simulationId={simulationId}
              venueData={venueData}
              eventConfig={eventConfig}
              triggers={triggers}
              onReset={() => {
                setSimulationRunning(false);
                setCurrentStep(1);
              }}
            />
          )}
        </div>
      </div>

      {/* Quick Stats Footer */}
      <div className="max-w-7xl mx-auto mt-8 grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-gray-500 text-sm">Zones</p>
          <p className="text-2xl font-bold text-blue-600">{venueData.zones.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-gray-500 text-sm">Crowd Size</p>
          <p className="text-2xl font-bold text-green-600">
            {eventConfig.crowdSize.toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-gray-500 text-sm">Triggers</p>
          <p className="text-2xl font-bold text-orange-600">{triggers.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <p className="text-gray-500 text-sm">Risk Score</p>
          <p className={`text-2xl font-bold ${
            eventConfig.riskScore > 7 ? 'text-red-600' :
            eventConfig.riskScore > 5 ? 'text-yellow-600' :
            'text-green-600'
          }`}>
            {eventConfig.riskScore.toFixed(1)}/10
          </p>
        </div>
      </div>
    </div>
  );
};

export default ScenarioBuilder;
