import React from 'react';

const AIRecommendations = ({ stadiumStatus }) => {
  if (!stadiumStatus) return null;

  const hasRecommendations = stadiumStatus.recommendations && stadiumStatus.recommendations.length > 0;

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-200">AI Safety Recommendations</h3>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-slate-400">Live Monitoring</span>
        </div>
      </div>

      {hasRecommendations ? (
        <div className="space-y-3">
          {stadiumStatus.recommendations.map((rec, index) => (
            <div
              key={index}
              className={`p-4 rounded-xl border-l-4 transition-all ${
                rec.priority === 'CRITICAL'
                  ? 'bg-red-500/10 border-red-500'
                  : rec.priority === 'WARNING'
                  ? 'bg-amber-500/10 border-amber-500'
                  : 'bg-blue-500/10 border-blue-500'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-bold ${
                        rec.priority === 'CRITICAL'
                          ? 'bg-red-500 text-white'
                          : rec.priority === 'WARNING'
                          ? 'bg-amber-500 text-white'
                          : 'bg-blue-500 text-white'
                      }`}
                    >
                      {rec.priority}
                    </span>
                    <span className="font-semibold text-slate-300">{rec.location}</span>
                  </div>
                  
                  <p className="text-sm text-slate-400 mb-2">
                    <strong className="text-slate-300">Issue:</strong> {rec.reason}
                  </p>
                  
                  <p className="text-sm text-slate-500 bg-slate-800/50 p-2 rounded-lg">
                    <strong className="text-emerald-400">Recommendation:</strong> {rec.recommendation}
                  </p>
                </div>
                
                <button
                  className={`px-4 py-2 rounded-lg font-semibold text-white text-sm transition-all hover:scale-105 ${
                    rec.priority === 'CRITICAL'
                      ? 'bg-red-600 hover:bg-red-500'
                      : rec.priority === 'WARNING'
                      ? 'bg-amber-600 hover:bg-amber-500'
                      : 'bg-blue-600 hover:bg-blue-500'
                  }`}
                >
                  {rec.action.replace(/_/g, ' ')}
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-lg font-semibold text-emerald-400">All Clear!</p>
          <p className="text-sm text-slate-500">No safety issues detected</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
