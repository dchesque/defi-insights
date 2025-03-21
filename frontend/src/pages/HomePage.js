import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CryptoForm from '../components/CryptoForm';
import ProgressModal from '../components/ProgressModal';

const HomePage = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState({});
  const navigate = useNavigate();

  const handleAnalyze = async (url) => {
    try {
      setIsAnalyzing(true);
      
      // Initialize progress
      setProgress({
        overall: { status: 'in_progress', percent: 0 },
        data_collection: { status: 'pending', percent: 0 },
        technical_analysis: { status: 'pending', percent: 0 },
        sentiment_analysis: { status: 'pending', percent: 0 },
        onchain_analysis: { status: 'pending', percent: 0 },
        risk_management: { status: 'pending', percent: 0 },
        portfolio_management: { status: 'pending', percent: 0 },
        report_generation: { status: 'pending', percent: 0 }
      });

      // Simulate progress for demo
      // In a real application, this would be replaced with actual API calls
      // that return progress updates
      await simulateProgress(setProgress);
      
      // Once analysis is complete, redirect to report page
      const reportId = 'btc-' + Date.now(); // In real app, this would come from API
      navigate(`/report/${reportId}`);
    } catch (error) {
      console.error('Analysis failed:', error);
      setIsAnalyzing(false);
    }
  };

  // This function simulates the progress of each analysis step
  // In a real application, you would use WebSockets or polling to get updates
  const simulateProgress = async (setProgress) => {
    const steps = [
      { key: 'data_collection', name: 'Data Collection', duration: 2000 },
      { key: 'technical_analysis', name: 'Technical Analysis', duration: 3000 },
      { key: 'sentiment_analysis', name: 'Sentiment Analysis', duration: 2500 },
      { key: 'onchain_analysis', name: 'On-Chain Analysis', duration: 2800 },
      { key: 'risk_management', name: 'Risk Management', duration: 1500 },
      { key: 'portfolio_management', name: 'Portfolio Management', duration: 1000 },
      { key: 'report_generation', name: 'Report Generation', duration: 1200 }
    ];

    const totalDuration = steps.reduce((total, step) => total + step.duration, 0);
    let elapsedTime = 0;

    for (const step of steps) {
      // Update current step to 'in_progress'
      setProgress(prev => ({
        ...prev,
        [step.key]: { status: 'in_progress', percent: 0 }
      }));

      // Simulate progress within this step
      for (let i = 0; i <= 10; i++) {
        await new Promise(resolve => setTimeout(resolve, step.duration / 10));
        
        // Update progress for this step
        setProgress(prev => ({
          ...prev,
          [step.key]: { 
            status: 'in_progress', 
            percent: i * 10 
          },
          overall: { 
            status: 'in_progress', 
            percent: Math.floor((elapsedTime + (step.duration * (i / 10))) / totalDuration * 100) 
          }
        }));
      }

      elapsedTime += step.duration;
      
      // Mark this step as complete
      setProgress(prev => ({
        ...prev,
        [step.key]: { status: 'completed', percent: 100 }
      }));
    }

    // Ensure overall progress is complete
    setProgress(prev => ({
      ...prev,
      overall: { status: 'completed', percent: 100 }
    }));

    // Wait a moment before proceeding to show the complete progress
    await new Promise(resolve => setTimeout(resolve, 500));
  };

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex-grow flex flex-col items-center justify-center px-4 py-12">
        <div className="max-w-3xl w-full text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="gradient-text">AI-Powered Crypto Analysis</span>
          </h1>
          <p className="text-gray-300 text-lg mb-8">
            Paste any CoinGecko or CoinMarketCap link to get comprehensive on-chain,
            sentiment, social, and fundamental analysis powered by artificial intelligence.
          </p>
          
          <CryptoForm onAnalyze={handleAnalyze} />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 w-full max-w-5xl">
          <div className="card">
            <div className="bg-indigo-900/30 rounded-full w-10 h-10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg mb-2">On-Chain Analysis</h3>
            <p className="text-gray-400 text-sm">
              Analyze blockchain data, transactions, and wallet distributions.
            </p>
          </div>
          
          <div className="card">
            <div className="bg-purple-900/30 rounded-full w-10 h-10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg mb-2">Sentiment Analysis</h3>
            <p className="text-gray-400 text-sm">
              Gauge market sentiment and emotional trends from various sources.
            </p>
          </div>
          
          <div className="card">
            <div className="bg-pink-900/30 rounded-full w-10 h-10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg mb-2">Social Analysis</h3>
            <p className="text-gray-400 text-sm">
              Track social media engagement, mentions, and community growth.
            </p>
          </div>
          
          <div className="card">
            <div className="bg-teal-900/30 rounded-full w-10 h-10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg mb-2">Fundamental Analysis</h3>
            <p className="text-gray-400 text-sm">
              Evaluate tokenomics, team, roadmap, and project fundamentals.
            </p>
          </div>
        </div>
        
        <div className="mt-20 text-center">
          <h2 className="text-2xl font-bold mb-4">Comprehensive Crypto Reports</h2>
          <p className="text-gray-300 mb-6">
            Our AI generates detailed reports to help you make informed investment decisions
          </p>
        </div>
      </div>
      
      {isAnalyzing && (
        <ProgressModal 
          progress={progress} 
          onClose={() => setIsAnalyzing(false)}
        />
      )}
    </div>
  );
};

export default HomePage;