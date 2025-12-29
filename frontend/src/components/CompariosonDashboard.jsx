import React, { useState } from 'react';
import { simulationApi } from '../api/simulationApi';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const ComparisonDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [selectedScenario, setSelectedScenario] = useState('stadium_exit');
  const [viewMode, setViewMode] = useState('both'); // 'baseline', 'optimized', or 'both'

  const runComparison = async () => {
    setLoading(true);
    try {
      const spawnConfig = [
        { start: 'zone_north', goal: 'exit_main', count: 500, type: 'normal' },
        { start: 'zone_south', goal: 'exit_main', count: 400, type: 'family' },
        { start: 'zone_east', goal: 'exit_main', count: 100, type: 'rushing' },
        { start: 'zone_west', goal: 'exit_main', count: 100, type: 'elderly' }
      ];

      const response = await simulationApi.compareSimulations(
        selectedScenario,
        spawnConfig,
        1.0
      );

      setComparisonData(response);
    } catch (error) {
      console.error('Comparison failed:', error);
      alert('Comparison failed. Make sure backend is running and model is trained!');
    } finally {
      setLoading(false);
    }
  };

  const getBarChartData = () => {
    if (!comparisonData) return null;

    const densityImprovement = comparisonData.improvements.density_reduction_percent;
    const violationsImprovement = 
      ((comparisonData.baseline.danger_violations - comparisonData.optimized.danger_violations) / 
       Math.max(comparisonData.baseline.danger_violations, 1)) * 100;
    const timeImprovement = 
      ((comparisonData.baseline.evacuation_time - comparisonData.optimized.evacuation_time) / 
       comparisonData.baseline.evacuation_time) * 100;

    return {
      labels: ['Density Reduction', 'Violations Reduced', 'Time Saved'],
      datasets: [
        {
          label: 'AI Improvement (%)',
          data: [
            densityImprovement,
            violationsImprovement,
            timeImprovement
          ],
          backgroundColor: [
            densityImprovement > 0 ? 'rgba(34, 197, 94, 0.7)' : 'rgba(239, 68, 68, 0.7)',
            violationsImprovement > 0 ? 'rgba(34, 197, 94, 0.7)' : 'rgba(239, 68, 68, 0.7)',
            timeImprovement > 0 ? 'rgba(34, 197, 94, 0.7)' : 'rgba(239, 68, 68, 0.7)',
          ],
          borderColor: [
            densityImprovement > 0 ? 'rgba(34, 197, 94, 1)' : 'rgba(239, 68, 68, 1)',
            violationsImprovement > 0 ? 'rgba(34, 197, 94, 1)' : 'rgba(239, 68, 68, 1)',
            timeImprovement > 0 ? 'rgba(34, 197, 94, 1)' : 'rgba(239, 68, 68, 1)',
          ],
          borderWidth: 2,
        },
      ],
    };
  };

  const getDensityTimelineData = () => {
    if (!comparisonData) return null;

    const baselineHistory = comparisonData.baseline_history || [];
    const optimizedHistory = comparisonData.optimized_history || [];

    const datasets = [];

    if (viewMode === 'baseline' || viewMode === 'both') {
      datasets.push({
        label: 'Mode A: Baseline (No RL Policy)',
        data: baselineHistory.map(h => h.max_density),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.3,
        borderWidth: 3,
        pointRadius: 2,
      });
    }

    if (viewMode === 'optimized' || viewMode === 'both') {
      datasets.push({
        label: 'Mode B: RL-Optimized (Policy Control Active)',
        data: optimizedHistory.map(h => h.max_density),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.3,
        borderWidth: 3,
        pointRadius: 2,
      });
    }

    datasets.push({
      label: 'Danger Threshold (4.0 p/m²)',
      data: baselineHistory.map(() => 4.0),
      borderColor: 'rgb(255, 165, 0)',
      borderDash: [5, 5],
      borderWidth: 2,
      pointRadius: 0,
      fill: false,
    });

    return {
      labels: baselineHistory.map(h => `${h.time}s`),
      datasets: datasets,
    };
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function(context) {
            return context.parsed.y.toFixed(1) + '% improvement';
          }
        }
      }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Improvement (%)',
          font: { size: 14, weight: 'bold' }
        },
        ticks: {
          callback: function(value) { return value + '%'; }
        }
      },
    },
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: { size: 12, weight: 'bold' },
          padding: 15,
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' p/m²';
          }
        }
      }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Maximum Density (people/m²)',
          font: { size: 14, weight: 'bold' }
        },
        beginAtZero: true,
        max: 6,
      },
      x: {
        title: {
          display: true,
          text: 'Simulation Time',
          font: { size: 14, weight: 'bold' }
        }
      }
    },
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🤖 AI vs Baseline Comparison
          </h1>
          <p className="text-gray-600">
            Quantitative proof that RL optimization prevents crowd disasters
          </p>
        </div>

        {/* 🎯 ADDITION 1: Explanation Card */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg shadow-lg p-6 mb-6">
          <h3 className="text-lg font-bold text-blue-900 mb-3">📋 Comparison Modes Explained</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg p-4 border-2 border-red-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🚫</span>
                <span className="font-bold text-red-700 text-lg">Mode A: Baseline</span>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">
                Traditional crowd simulation with <strong>zero AI interventions</strong>. 
                Agents move freely without any optimization or control measures.
              </p>
              <div className="mt-2 text-xs text-gray-500 italic">
                → This represents current crowd management practices
              </div>
            </div>

            <div className="bg-white rounded-lg p-4 border-2 border-green-200">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🤖</span>
                <span className="font-bold text-green-700 text-lg">Mode B: RL-Optimized</span>
              </div>
              <p className="text-sm text-gray-700 leading-relaxed">
                <strong>RL policy actively controls crowd flow</strong> in real-time. 
                AI agent makes intelligent decisions to prevent dangerous congestion.
              </p>
              <div className="mt-2 text-xs text-gray-500 italic">
                → Our trained Q-learning policy preventing stampede risks
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="p-2 border border-gray-300 rounded-lg"
              disabled={loading}
            >
              <option value="stadium_exit">Stadium Exit</option>
            </select>

            <button
              onClick={runComparison}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-semibold"
            >
              {loading ? '⏳ Running...' : '▶ Run Comparison'}
            </button>

            {/* 🎯 ADDITION 2: Interactive Toggle */}
            {comparisonData && (
              <div className="ml-auto flex items-center gap-3 bg-gray-50 p-2 rounded-lg border-2">
                <span className="text-sm font-semibold">Chart View:</span>
                <button
                  onClick={() => setViewMode('baseline')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    viewMode === 'baseline' ? 'bg-red-500 text-white shadow-md' : 'bg-white text-gray-700'
                  }`}
                >
                  🚫 Baseline Only
                </button>
                <button
                  onClick={() => setViewMode('optimized')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    viewMode === 'optimized' ? 'bg-green-500 text-white shadow-md' : 'bg-white text-gray-700'
                  }`}
                >
                  🤖 RL Only
                </button>
                <button
                  onClick={() => setViewMode('both')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    viewMode === 'both' ? 'bg-blue-500 text-white shadow-md' : 'bg-white text-gray-700'
                  }`}
                >
                  📊 Both
                </button>
              </div>
            )}
          </div>
        </div>

        {comparisonData && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">Density Reduction</h3>
                <p className="text-4xl font-bold">
                  {comparisonData.improvements.density_reduction_percent.toFixed(1)}%
                </p>
                <p className="text-sm mt-2">
                  {comparisonData.baseline.max_density.toFixed(2)} → {comparisonData.optimized.max_density.toFixed(2)} p/m²
                </p>
              </div>

              <div className={`rounded-lg shadow-lg p-6 text-white ${
                comparisonData.improvements.danger_violations_prevented >= 0
                  ? 'bg-gradient-to-br from-blue-500 to-blue-600'
                  : 'bg-gradient-to-br from-yellow-500 to-yellow-600'
              }`}>
                <h3 className="text-lg font-semibold mb-2">Violations Prevented</h3>
                <p className="text-4xl font-bold">
                  {Math.abs(comparisonData.improvements.danger_violations_prevented)}
                </p>
                <p className="text-sm mt-2">
                  {comparisonData.baseline.danger_violations} → {comparisonData.optimized.danger_violations}
                </p>
              </div>

              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-2">AI Interventions</h3>
                <p className="text-4xl font-bold">{comparisonData.sample_actions.length}+</p>
                <p className="text-sm mt-2">Real-time actions</p>
              </div>
            </div>

            {/* 🎯 ADDITION 3: Enhanced Time Chart */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-bold mb-4">
                📈 Maximum Density Over Time {viewMode !== 'both' && `(${viewMode === 'baseline' ? 'Baseline' : 'RL-Optimized'} Only)`}
              </h2>
              <div className="h-96">
                <Line data={getDensityTimelineData()} options={lineChartOptions} />
              </div>
              <div className="mt-4 text-sm bg-gray-50 p-4 rounded-lg">
                <p className="font-semibold mb-2">💡 Key Insights:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li><strong className="text-red-600">Red line:</strong> Dangerous spikes without AI</li>
                  <li><strong className="text-green-600">Green line:</strong> AI keeps density safe</li>
                  <li><strong className="text-orange-500">Orange dashed:</strong> 4.0 p/m² danger threshold</li>
                </ul>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-bold mb-4">📊 AI Impact (%)</h2>
              <div className="h-80">
                <Bar data={getBarChartData()} options={barChartOptions} />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-bold mb-4">🎯 AI Decisions</h2>
              <div className="space-y-3">
                {comparisonData.sample_actions.map((action, idx) => (
                  <div key={idx} className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded-lg">
                    <p className="font-semibold">⏱️ t={action.time.toFixed(0)}s: {action.action.toUpperCase().replace(/_/g, ' ')}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      📍 {action.node} | 👥 {action.density.toFixed(2)} p/m²
                    </p>
                    <p className="text-sm italic mt-2 bg-white p-2 rounded">💡 {action.explanation}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 text-center">
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(comparisonData, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = 'comparison_report.json';
                  link.click();
                }}
                className="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 font-semibold"
              >
                📥 Download Report
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ComparisonDashboard;
