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
  const [viewMode, setViewMode] = useState('both');

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
          data: [densityImprovement, violationsImprovement, timeImprovement],
          backgroundColor: [
            densityImprovement > 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)',
            violationsImprovement > 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)',
            timeImprovement > 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)',
          ],
          borderColor: [
            densityImprovement > 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)',
            violationsImprovement > 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)',
            timeImprovement > 0 ? 'rgba(16, 185, 129, 1)' : 'rgba(239, 68, 68, 1)',
          ],
          borderWidth: 2,
          borderRadius: 8,
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
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 0,
        fill: true,
      });
    }

    if (viewMode === 'optimized' || viewMode === 'both') {
      datasets.push({
        label: 'Mode B: RL-Optimized (Policy Control Active)',
        data: optimizedHistory.map(h => h.max_density),
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 0,
        fill: true,
      });
    }

    datasets.push({
      label: 'Danger Threshold (4.0 p/m²)',
      data: baselineHistory.map(() => 4.0),
      borderColor: 'rgb(251, 191, 36)',
      borderDash: [8, 4],
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
        backgroundColor: '#1e293b',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            return context.parsed.y.toFixed(1) + '% improvement';
          }
        }
      }
    },
    scales: {
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#94a3b8', callback: (value) => value + '%' },
        title: { display: true, text: 'Improvement (%)', color: '#94a3b8', font: { size: 12 } }
      },
      x: {
        grid: { display: false },
        ticks: { color: '#94a3b8' }
      }
    },
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        position: 'top',
        labels: { color: '#94a3b8', font: { size: 11 }, padding: 20, usePointStyle: true }
      },
      tooltip: {
        backgroundColor: '#1e293b',
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        borderColor: '#334155',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' p/m²';
          }
        }
      }
    },
    scales: {
      y: {
        grid: { color: 'rgba(148, 163, 184, 0.1)' },
        ticks: { color: '#94a3b8' },
        title: { display: true, text: 'Maximum Density (p/m²)', color: '#94a3b8', font: { size: 12 } },
        beginAtZero: true,
        max: 6,
      },
      x: {
        grid: { color: 'rgba(148, 163, 184, 0.05)' },
        ticks: { color: '#94a3b8' },
        title: { display: true, text: 'Simulation Time', color: '#94a3b8', font: { size: 12 } }
      }
    },
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="glass-card p-6">
        <h1 className="text-2xl font-bold gradient-text mb-2">
          AI vs Baseline Comparison
        </h1>
        <p className="text-slate-400">
          Quantitative proof that RL optimization prevents crowd disasters
        </p>
      </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="glass-card p-5 border-l-4 border-red-500">
            <div className="flex items-center gap-3 mb-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              <span className="font-bold text-red-400">Mode A: Baseline</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              Traditional crowd simulation with <span className="text-slate-300 font-medium">zero AI interventions</span>. 
              Agents move freely without any optimization.
            </p>
          </div>

          <div className="glass-card p-5 border-l-4 border-emerald-500">
            <div className="flex items-center gap-3 mb-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
              <span className="font-bold text-emerald-400">Mode B: RL-Optimized</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              <span className="text-slate-300 font-medium">RL policy actively controls</span> crowd flow in real-time 
              to prevent dangerous congestion.
            </p>
          </div>
        </div>

      <div className="glass-card p-6">
        <div className="flex flex-wrap gap-4 items-center">
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="input-modern w-auto"
            disabled={loading}
          >
            <option value="stadium_exit">Stadium Exit</option>
          </select>

          <button
            onClick={runComparison}
            disabled={loading}
            className="btn-primary disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Comparison'}
          </button>

          {comparisonData && (
            <div className="ml-auto flex items-center gap-2 p-1 bg-slate-800/50 rounded-lg border border-slate-700/50">
              {['baseline', 'optimized', 'both'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                    viewMode === mode 
                      ? mode === 'baseline' ? 'bg-red-500 text-white' 
                        : mode === 'optimized' ? 'bg-emerald-500 text-white'
                        : 'bg-blue-500 text-white'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {mode === 'baseline' ? 'Baseline' : mode === 'optimized' ? 'RL Only' : 'Both'}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {comparisonData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-card p-6 border-t-4 border-emerald-500">
              <h3 className="text-sm text-slate-400 mb-1">Density Reduction</h3>
              <p className="text-3xl font-bold text-emerald-400">
                {comparisonData.improvements.density_reduction_percent.toFixed(1)}%
              </p>
              <p className="text-xs text-slate-500 mt-2">
                {comparisonData.baseline.max_density.toFixed(2)} → {comparisonData.optimized.max_density.toFixed(2)} p/m²
              </p>
            </div>

            <div className="glass-card p-6 border-t-4 border-blue-500">
              <h3 className="text-sm text-slate-400 mb-1">Violations Prevented</h3>
              <p className="text-3xl font-bold text-blue-400">
                {Math.abs(comparisonData.improvements.danger_violations_prevented)}
              </p>
              <p className="text-xs text-slate-500 mt-2">
                {comparisonData.baseline.danger_violations} → {comparisonData.optimized.danger_violations}
              </p>
            </div>

            <div className="glass-card p-6 border-t-4 border-purple-500">
              <h3 className="text-sm text-slate-400 mb-1">AI Interventions</h3>
              <p className="text-3xl font-bold text-purple-400">{comparisonData.sample_actions.length}+</p>
              <p className="text-xs text-slate-500 mt-2">Real-time actions</p>
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4">
              Maximum Density Over Time
            </h2>
            <div className="h-80">
              <Line data={getDensityTimelineData()} options={lineChartOptions} />
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4">AI Impact (%)</h2>
            <div className="h-64">
              <Bar data={getBarChartData()} options={barChartOptions} />
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4">AI Decisions</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {comparisonData.sample_actions.map((action, idx) => (
                <div key={idx} className="bg-slate-800/50 border-l-4 border-blue-500 p-4 rounded-lg">
                  <p className="font-semibold text-slate-200">
                    t={action.time.toFixed(0)}s: {action.action.toUpperCase().replace(/_/g, ' ')}
                  </p>
                  <p className="text-sm text-slate-400 mt-1">
                    {action.node} | {action.density.toFixed(2)} p/m²
                  </p>
                  <p className="text-sm text-slate-500 italic mt-2">{action.explanation}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6 text-center">
            <button
              onClick={() => {
                const blob = new Blob([JSON.stringify(comparisonData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'comparison_report.json';
                link.click();
              }}
              className="btn-primary"
            >
              Download Report
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ComparisonDashboard;
