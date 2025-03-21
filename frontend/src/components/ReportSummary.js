import React from 'react';
import { FaArrowUp, FaArrowDown, FaArrowRight, FaInfoCircle } from 'react-icons/fa';

const ReportSummary = ({ report }) => {
  const getSignalIcon = (signal) => {
    if (signal === 'bullish') return <FaArrowUp className="text-green-500" />;
    if (signal === 'bearish') return <FaArrowDown className="text-red-500" />;
    return <FaArrowRight className="text-yellow-500" />;
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 75) return 'text-green-500';
    if (confidence >= 50) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="space-y-8">
      {/* AI Analysis Summary */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">AI Analysis Summary</h2>
        
        <p className="text-gray-300 mb-6">
          {report.symbol} is showing strong on-chain fundamentals with increasing adoption and decreasing supply on exchanges. 
          The recent price action suggests a consolidation phase before potential upward movement.
          Social sentiment analysis indicates growing positive momentum across Twitter, Reddit, and other platforms.
          Institutional interest remains high with continued accumulation from large entities.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key metrics to watch:</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>Active addresses (daily)</li>
              <li>Exchange outflows</li>
              <li>MVRV ratio</li>
              <li>Social volume trends</li>
              <li>Institutional accumulation patterns</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key insights:</h3>
            <ul className="space-y-2">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>Strong accumulation by long-term holders</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>Decreasing exchange reserves (bullish)</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>Increasing hash rate indicating network security</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>Growing institutional adoption</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Analysis Signals */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Signal Analysis</h3>
            <div className="flex items-center">
              <span className={`font-bold ${
                report.signals.overall === 'bullish' 
                  ? 'text-green-500' 
                  : report.signals.overall === 'bearish'
                    ? 'text-red-500'
                    : 'text-yellow-500'
              }`}>
                {report.signals.overall.toUpperCase()}
              </span>
              <span className="ml-2 text-sm text-gray-400">
                {report.signals.confidence}% confidence
              </span>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Technical</span>
              <div className="flex items-center">
                {getSignalIcon(report.signals.technical)}
                <span className="ml-2 font-medium">
                  {report.signals.technical.toUpperCase()}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">On-Chain</span>
              <div className="flex items-center">
                {getSignalIcon(report.signals.onchain)}
                <span className="ml-2 font-medium">
                  {report.signals.onchain.toUpperCase()}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Sentiment</span>
              <div className="flex items-center">
                {getSignalIcon(report.signals.sentiment)}
                <span className="ml-2 font-medium">
                  {report.signals.sentiment.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <h3 className="font-medium mb-4">Price Prediction</h3>
          
          <div className="mb-4">
            <div className="text-2xl font-bold">${report.price_prediction.target_price_30d.toLocaleString()}</div>
            <div className="text-sm text-gray-400">30-day forecast</div>
          </div>
          
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-400">Current</span>
            <span className="text-gray-400">Target</span>
          </div>
          
          <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden mb-3">
            <div className="h-full bg-gradient-to-r from-green-500 to-blue-500 rounded-full" style={{ width: '65%' }}></div>
          </div>
          
          <div className="flex justify-between text-sm mb-4">
            <span className="font-medium">${report.price_data.current_price.toLocaleString()}</span>
            <span className="font-medium">${report.price_prediction.target_price_30d.toLocaleString()}</span>
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-red-900/20 p-2 rounded border border-red-700/20">
              <div className="text-gray-400">Bear Case</div>
              <div className="font-medium">${report.price_prediction.bear_case.toLocaleString()}</div>
            </div>
            
            <div className="bg-green-900/20 p-2 rounded border border-green-700/20">
              <div className="text-gray-400">Bull Case</div>
              <div className="font-medium">${report.price_prediction.bull_case.toLocaleString()}</div>
            </div>
          </div>
        </div>
        
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <h3 className="font-medium mb-4">Investment Rating</h3>
          
          <div className="flex items-center justify-center mb-4">
            <div className="bg-green-900/30 text-green-500 font-bold text-xl py-2 px-6 rounded-lg border border-green-600/30">
              BUY
            </div>
          </div>
          
          <div className="flex justify-center mb-3">
            <div className="flex items-center">
              <span className="text-yellow-500">★</span>
              <span className="text-yellow-500">★</span>
              <span className="text-yellow-500">★</span>
              <span className="text-yellow-500">★</span>
              <span className="text-gray-600">★</span>
            </div>
          </div>
          
          <div className="text-center text-sm text-gray-400 mb-4">
            Strong fundamentals
          </div>
          
          <div className="border-t border-gray-700 pt-4">
            <div className="mb-2">
              <div className="flex justify-between mb-1">
                <span className="text-xs text-gray-400">Risk</span>
                <span className="text-xs font-medium text-green-500">Low</span>
              </div>
              <div className="h-1.5 w-full bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 rounded-full" style={{ width: '25%' }}></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-xs text-gray-400">Reward Potential</span>
                <span className="text-xs font-medium text-green-500">High</span>
              </div>
              <div className="h-1.5 w-full bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 rounded-full" style={{ width: '85%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Risk Assessment */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Risk Assessment</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-gray-300 font-medium mb-2">Risk Level</h3>
            <div className="p-3 rounded-lg bg-[#12141f] border border-gray-700">
              <div className="flex items-center justify-between">
                <span className="font-medium">{report.risk_analysis.market_quality.risk_level}</span>
                <span className={`text-sm ${
                  report.risk_analysis.market_quality.risk_level.includes('low') 
                    ? 'text-green-500' 
                    : report.risk_analysis.market_quality.risk_level.includes('medium')
                      ? 'text-yellow-500'
                      : 'text-red-500'
                }`}>
                  {report.risk_analysis.market_quality.score}/10
                </span>
              </div>
              
              <div className="mt-2 h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full" 
                  style={{ width: `${report.risk_analysis.market_quality.score * 10}%` }}
                ></div>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-gray-300 font-medium mb-2">Volatility</h3>
            <div className="p-3 rounded-lg bg-[#12141f] border border-gray-700">
              <div className="flex items-center justify-between">
                <span className="font-medium">Low</span>
                <span className="text-sm text-green-500">
                  {(report.risk_analysis.volatility * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="mt-2 h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full" 
                  style={{ width: `${report.risk_analysis.volatility * 20 * 100}%` }}
                ></div>
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-gray-300 font-medium mb-2">Max Position Size</h3>
            <div className="p-3 rounded-lg bg-[#12141f] border border-gray-700">
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-400 text-sm">Position Limit</span>
                <span className="font-medium">${report.risk_analysis.position_limit.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-400 text-sm">Current Price</span>
                <span className="font-medium">${report.risk_analysis.current_price.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400 text-sm">Max Units</span>
                <span className="font-medium">{report.risk_analysis.max_units.toFixed(4)} {report.symbol}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-6">
          <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
            <FaInfoCircle />
            <span>Risk assessment based on volatility, market conditions, and on-chain metrics</span>
          </div>
          <p className="text-gray-300">
            {report.recommendation}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ReportSummary;