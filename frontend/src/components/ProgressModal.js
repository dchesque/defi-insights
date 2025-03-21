import React from 'react';
import { FaCheckCircle, FaSpinner, FaClock, FaTimes } from 'react-icons/fa';

const ProgressModal = ({ progress, onClose }) => {
  const steps = [
    { id: 'data_collection', name: 'Data Collection', description: 'Gathering market data' },
    { id: 'technical_analysis', name: 'Technical Analysis', description: 'Analyzing price patterns and indicators' },
    { id: 'sentiment_analysis', name: 'Sentiment Analysis', description: 'Evaluating market sentiment and social trends' },
    { id: 'onchain_analysis', name: 'On-Chain Analysis', description: 'Examining blockchain metrics and wallet activity' },
    { id: 'risk_management', name: 'Risk Management', description: 'Assessing investment risks and parameters' },
    { id: 'portfolio_management', name: 'Portfolio Management', description: 'Optimizing allocation based on signals' },
    { id: 'report_generation', name: 'Report Generation', description: 'Creating comprehensive analysis report' }
  ];

  const getStepIcon = (stepId) => {
    const step = progress[stepId];
    
    if (!step) return <FaClock className="text-gray-400" />;
    
    switch (step.status) {
      case 'completed':
        return <FaCheckCircle className="text-green-500" />;
      case 'in_progress':
        return <FaSpinner className="text-blue-500 animate-spin" />;
      case 'error':
        return <FaTimes className="text-red-500" />;
      default:
        return <FaClock className="text-gray-400" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1A1C31] rounded-lg shadow-xl max-w-2xl w-full p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white"
        >
          <FaTimes />
        </button>
        
        <h2 className="text-xl font-bold mb-6">Analyzing Cryptocurrency</h2>
        
        <div className="mb-6">
          <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full transition-all duration-300"
              style={{ width: `${progress.overall?.percent || 0}%` }}
            ></div>
          </div>
          <div className="mt-2 text-right text-sm text-gray-300">
            {progress.overall?.percent || 0}% Complete
          </div>
        </div>
        
        <div className="space-y-4">
          {steps.map((step) => (
            <div 
              key={step.id}
              className={`flex items-start p-3 rounded-md ${
                progress[step.id]?.status === 'in_progress' 
                  ? 'bg-blue-900/20 border border-blue-800/30' 
                  : progress[step.id]?.status === 'completed'
                    ? 'bg-green-900/10 border border-green-800/20'
                    : 'bg-gray-800/20'
              }`}
            >
              <div className="mr-3 mt-1">
                {getStepIcon(step.id)}
              </div>
              <div className="flex-grow">
                <h3 className="font-medium">{step.name}</h3>
                <p className="text-sm text-gray-400">{step.description}</p>
                
                {progress[step.id]?.status === 'in_progress' && (
                  <div className="mt-2 h-1 w-full bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 rounded-full transition-all duration-300"
                      style={{ width: `${progress[step.id]?.percent || 0}%` }}
                    ></div>
                  </div>
                )}
              </div>
              
              <div className="ml-2 text-sm">
                {progress[step.id]?.status === 'completed' && (
                  <span className="text-green-400">Complete</span>
                )}
                {progress[step.id]?.status === 'in_progress' && (
                  <span className="text-blue-400">In Progress</span>
                )}
                {progress[step.id]?.status === 'error' && (
                  <span className="text-red-400">Error</span>
                )}
                {progress[step.id]?.status === 'pending' && (
                  <span className="text-gray-400">Pending</span>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {progress.overall?.status === 'completed' && (
          <div className="mt-6 text-center">
            <p className="text-green-400 mb-4">Analysis completed successfully!</p>
            <button
              onClick={onClose}
              className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
            >
              View Report
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressModal;