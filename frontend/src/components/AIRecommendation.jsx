import React from 'react';

const AIRecommendations = ({ stadiumStatus }) => {
  if (!stadiumStatus) return null;

  const hasRecommendations = stadiumStatus.recommendations && stadiumStatus.recommendations.length > 0;

  return (
<<<<<<< HEAD
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg shadow-lg p-6 border-2 border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-purple-900 flex items-center gap-2">
          <span>🤖</span>
          <span>AI Safety Recommendations</span>
        </h3>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Live Monitoring</span>
=======
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-200">AI Safety Recommendations</h3>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-slate-400">Live Monitoring</span>
>>>>>>> nikhil
        </div>
      </div>

      {hasRecommendations ? (
        <div className="space-y-3">
          {stadiumStatus.recommendations.map((rec, index) => (
            <div
              key={index}
<<<<<<< HEAD
              className={`p-4 rounded-lg border-l-4 ${
                rec.priority === 'CRITICAL'
                  ? 'bg-red-50 border-red-500'
                  : rec.priority === 'WARNING'
                  ? 'bg-orange-50 border-orange-500'
                  : 'bg-blue-50 border-blue-500'
              } transition-all hover:shadow-md`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">
                      {rec.priority === 'CRITICAL' ? '🚨' : rec.priority === 'WARNING' ? '⚠️' : 'ℹ️'}
                    </span>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold ${
                        rec.priority === 'CRITICAL'
                          ? 'bg-red-500 text-white'
                          : rec.priority === 'WARNING'
                          ? 'bg-orange-500 text-white'
=======
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
>>>>>>> nikhil
                          : 'bg-blue-500 text-white'
                      }`}
                    >
                      {rec.priority}
                    </span>
<<<<<<< HEAD
                    <span className="font-semibold text-gray-700">{rec.location}</span>
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-2">
                    <strong>Issue:</strong> {rec.reason}
                  </p>
                  
                  <p className="text-sm text-gray-800 bg-white/60 p-2 rounded">
                    <strong>💡 Recommendation:</strong> {rec.recommendation}
=======
                    <span className="font-semibold text-slate-300">{rec.location}</span>
                  </div>
                  
                  <p className="text-sm text-slate-400 mb-2">
                    <strong className="text-slate-300">Issue:</strong> {rec.reason}
                  </p>
                  
                  <p className="text-sm text-slate-500 bg-slate-800/50 p-2 rounded-lg">
                    <strong className="text-emerald-400">Recommendation:</strong> {rec.recommendation}
>>>>>>> nikhil
                  </p>
                </div>
                
                <button
<<<<<<< HEAD
                  className={`ml-4 px-4 py-2 rounded-lg font-semibold text-white transition-all hover:scale-105 ${
                    rec.priority === 'CRITICAL'
                      ? 'bg-red-600 hover:bg-red-700'
                      : rec.priority === 'WARNING'
                      ? 'bg-orange-600 hover:bg-orange-700'
                      : 'bg-blue-600 hover:bg-blue-700'
=======
                  className={`px-4 py-2 rounded-lg font-semibold text-white text-sm transition-all hover:scale-105 ${
                    rec.priority === 'CRITICAL'
                      ? 'bg-red-600 hover:bg-red-500'
                      : rec.priority === 'WARNING'
                      ? 'bg-amber-600 hover:bg-amber-500'
                      : 'bg-blue-600 hover:bg-blue-500'
>>>>>>> nikhil
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
<<<<<<< HEAD
          <div className="text-6xl mb-3">✅</div>
          <p className="text-lg font-semibold text-green-700">All Clear!</p>
          <p className="text-sm text-gray-600">No safety issues detected</p>
=======
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-lg font-semibold text-emerald-400">All Clear!</p>
          <p className="text-sm text-slate-500">No safety issues detected</p>
>>>>>>> nikhil
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
