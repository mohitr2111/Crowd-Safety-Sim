import React, { useState } from 'react';

const AIRecommendations = ({ stadiumStatus, simulationId }) => {
  const [executingActions, setExecutingActions] = useState({});
  const [executedActions, setExecutedActions] = useState({});

  if (!stadiumStatus) return null;

  const hasRecommendations = stadiumStatus.recommendations && 
                              stadiumStatus.recommendations.length > 0;

  const handleExecuteAction = async (rec, index) => {
    if (!simulationId) return;
    
    // Mark as executing
    setExecutingActions(prev => ({ ...prev, [index]: true }));

    try {
      // Map recommendation action to API action type
      const actionMap = {
        'CLOSE_TEMPORARILY': 'CLOSE_NODE',
        'REDUCE_FLOW': 'REDUCE_FLOW',
        'INCREASE_SIGNAGE': 'REROUTE'
      };

      const response = await fetch(
        `http://localhost:8000/simulation/${simulationId}/execute-action`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action_type: actionMap[rec.action] || 'REDUCE_FLOW',
            target_node: rec.exit,
            duration: 60,
            intensity: 0.5
          })
        }
      );

      const result = await response.json();
      console.log('✅ Action executed:', result);

      // Mark as executed
      setExecutedActions(prev => ({ ...prev, [index]: result }));
      
      // Clear executing state
      setExecutingActions(prev => {
        const newState = { ...prev };
        delete newState[index];
        return newState;
      });

      // Auto-clear executed state after 5 seconds
      setTimeout(() => {
        setExecutedActions(prev => {
          const newState = { ...prev };
          delete newState[index];
          return newState;
        });
      }, 5000);

    } catch (error) {
      console.error('❌ Error executing action:', error);
      setExecutingActions(prev => {
        const newState = { ...prev };
        delete newState[index];
        return newState;
      });
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        🤖 AI Safety Recommendations
      </h2>

      {hasRecommendations ? (
        <div className="space-y-3">
          {stadiumStatus.recommendations.map((rec, index) => {
            const isExecuting = executingActions[index];
            const executedResult = executedActions[index];
            
            const priorityColors = {
              CRITICAL: 'border-red-500 bg-red-50',
              WARNING: 'border-orange-400 bg-orange-50',
              INFO: 'border-blue-400 bg-blue-50'
            };

            return (
              <div
                key={index}
                className={`border-l-4 p-4 ${priorityColors[rec.priority]}`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <span className={`font-bold text-sm px-2 py-1 rounded ${
                      rec.priority === 'CRITICAL' ? 'bg-red-600 text-white' :
                      rec.priority === 'WARNING' ? 'bg-orange-500 text-white' :
                      'bg-blue-500 text-white'
                    }`}>
                      {rec.priority}
                    </span>
                    <span className="ml-2 font-semibold">{rec.exit}</span>
                    
                    <p className="mt-2 text-sm text-gray-700">
                      <strong>Issue:</strong> {rec.reason}
                    </p>
                    <p className="mt-1 text-sm text-gray-700">
                      <strong>💡 Recommendation:</strong> {rec.recommendation}
                    </p>
                  </div>

                  <div className="ml-4">
                    {executedResult ? (
                      <div className="px-3 py-2 bg-green-100 border border-green-500 rounded text-sm">
                        <div className="font-bold text-green-700">✓ EXECUTED</div>
                        <div className="text-xs text-gray-600 mt-1">
                          {executedResult.agents_rerouted || executedResult.agents_affected || 0} agents affected
                        </div>
                      </div>
                    ) : isExecuting ? (
                      <div className="px-3 py-2 bg-yellow-100 border border-yellow-500 rounded text-sm">
                        <div className="font-bold text-yellow-700">⏳ EXECUTING...</div>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleExecuteAction(rec, index)}
                        className={`px-4 py-2 rounded font-semibold text-sm ${
                          rec.priority === 'CRITICAL' 
                            ? 'bg-red-600 hover:bg-red-700 text-white' 
                            : rec.priority === 'WARNING'
                            ? 'bg-orange-500 hover:bg-orange-600 text-white'
                            : 'bg-blue-500 hover:bg-blue-600 text-white'
                        }`}
                      >
                        {rec.action}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8 text-green-600">
          <div className="text-4xl mb-2">✅</div>
          <p className="font-semibold">All Clear!</p>
          <p className="text-sm text-gray-600">No safety issues detected</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
