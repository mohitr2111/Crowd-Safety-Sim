import React from 'react';

const AIRecommendations = ({ stadiumStatus }) => {
  if (!stadiumStatus) return null;

  const hasRecommendations = stadiumStatus.recommendations && stadiumStatus.recommendations.length > 0;

  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg shadow-lg p-6 border-2 border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-purple-900 flex items-center gap-2">
          <span>🤖</span>
          <span>AI Safety Recommendations</span>
        </h3>
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Live Monitoring</span>
        </div>
      </div>

      {hasRecommendations ? (
        <div className="space-y-3">
          {stadiumStatus.recommendations.map((rec, index) => (
            <div
              key={index}
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
                          : 'bg-blue-500 text-white'
                      }`}
                    >
                      {rec.priority}
                    </span>
                    <span className="font-semibold text-gray-700">{rec.location}</span>
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-2">
                    <strong>Issue:</strong> {rec.reason}
                  </p>
                  
                  <p className="text-sm text-gray-800 bg-white/60 p-2 rounded">
                    <strong>💡 Recommendation:</strong> {rec.recommendation}
                  </p>
                </div>
                
                <button
                  className={`ml-4 px-4 py-2 rounded-lg font-semibold text-white transition-all hover:scale-105 ${
                    rec.priority === 'CRITICAL'
                      ? 'bg-red-600 hover:bg-red-700'
                      : rec.priority === 'WARNING'
                      ? 'bg-orange-600 hover:bg-orange-700'
                      : 'bg-blue-600 hover:bg-blue-700'
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
          <div className="text-6xl mb-3">✅</div>
          <p className="text-lg font-semibold text-green-700">All Clear!</p>
          <p className="text-sm text-gray-600">No safety issues detected</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
