import React from 'react';
import { FaArrowUp, FaArrowDown, FaArrowRight, FaInfoCircle } from 'react-icons/fa';

const TechnicalAnalysis = ({ report }) => {
  if (!report || !report.technical_analysis) {
    return (
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-2">Technical Analysis</h2>
        <p className="text-gray-400">No technical analysis data available.</p>
      </div>
    );
  }

  const { technical_analysis } = report;
  
  const getSignalIcon = (signal) => {
    if (signal === 'bullish') return <FaArrowUp className="text-green-500" />;
    if (signal === 'bearish') return <FaArrowDown className="text-red-500" />;
    return <FaArrowRight className="text-yellow-500" />;
  };

  const getConfidenceIndicator = (confidence) => {
    const rounded = Math.round(confidence / 10) * 10;
    return (
      <div className="flex items-center">
        <div className="w-24 h-1.5 bg-gray-700 rounded-full mr-2">
          <div 
            className={`h-full rounded-full ${
              confidence >= 70 ? 'bg-green-500' : 
              confidence >= 40 ? 'bg-yellow-500' : 'bg-red-500'
            }`} 
            style={{ width: `${rounded}%` }}
          ></div>
        </div>
        <span className="text-sm text-gray-400">{confidence}%</span>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Summary */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Technical Analysis</h2>
        
        <p className="text-gray-300 mb-6">
          Our technical analysis combines multiple strategies including trend following, mean reversion, 
          momentum, volatility analysis, and statistical arbitrage to provide a comprehensive view of price action.
        </p>
        
        <div className="mb-6">
          <h3 className="font-medium mb-3">Overall Technical Signal</h3>
          <div className="flex items-center space-x-3">
            {getSignalIcon(report.signals.technical)}
            <span className={`font-bold ${
              report.signals.technical === 'bullish' ? 'text-green-500' : 
              report.signals.technical === 'bearish' ? 'text-red-500' : 'text-yellow-500'
            }`}>
              {report.signals.technical.toUpperCase()}
            </span>
            {getConfidenceIndicator(report.technical_analysis.trend_following.confidence)}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key Technical Indicators:</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>EMA Crossovers (8/21, 21/55)</li>
              <li>RSI (14): {Math.round(technical_analysis.mean_reversion.metrics.rsi_14)}</li>
              <li>Price vs. Bollinger Bands</li>
              <li>MACD Signal</li>
              <li>Historical Volatility</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key Insights:</h3>
            <ul className="space-y-2">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>{technical_analysis.trend_following.metrics.short_trend ? "Positive" : "Negative"} short-term trend</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>{technical_analysis.trend_following.metrics.medium_trend ? "Positive" : "Negative"} medium-term trend</span>
              </li>
              <li className="flex items-start">
                <span className={technical_analysis.momentum.metrics.momentum_1m > 0 ? "text-green-500" : "text-red-500"} mr-2>•</span>
                <span>
                  {technical_analysis.momentum.metrics.momentum_1m > 0 ? "Positive" : "Negative"} 1-month momentum 
                  ({(technical_analysis.momentum.metrics.momentum_1m * 100).toFixed(1)}%)
                </span>
              </li>
              <li className="flex items-start">
                <span className={technical_analysis.momentum.metrics.momentum_3m > 0 ? "text-green-500" : "text-red-500"} mr-2>•</span>
                <span>
                  {technical_analysis.momentum.metrics.momentum_3m > 0 ? "Positive" : "Negative"} 3-month momentum
                  ({(technical_analysis.momentum.metrics.momentum_3m * 100).toFixed(1)}%)
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Detailed Strategy Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Trend Following */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Trend Following</h3>
            <div className="flex items-center">
              {getSignalIcon(technical_analysis.trend_following.signal)}
              <span className={`ml-2 font-medium ${
                technical_analysis.trend_following.signal === 'bullish' ? 'text-green-500' : 
                technical_analysis.trend_following.signal === 'bearish' ? 'text-red-500' : 'text-yellow-500'
              }`}>
                {technical_analysis.trend_following.signal.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">ADX (Trend Strength)</span>
              <div className="font-medium">
                {technical_analysis.trend_following.metrics.adx.toFixed(1)}
                <span className="ml-2 text-sm text-gray-400">
                  {technical_analysis.trend_following.metrics.adx > 25 ? "Strong" : "Weak"}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Short-term Trend (8/21 EMA)</span>
              <div className="font-medium">
                <span className={technical_analysis.trend_following.metrics.short_trend ? "text-green-500" : "text-red-500"}>
                  {technical_analysis.trend_following.metrics.short_trend ? "Bullish" : "Bearish"}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Medium-term Trend (21/55 EMA)</span>
              <div className="font-medium">
                <span className={technical_analysis.trend_following.metrics.medium_trend ? "text-green-500" : "text-red-500"}>
                  {technical_analysis.trend_following.metrics.medium_trend ? "Bullish" : "Bearish"}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Trend Strength</span>
              <div className="font-medium">
                {(technical_analysis.trend_following.metrics.trend_strength * 100).toFixed(0)}%
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="h-1.5 w-full bg-gray-700 rounded-full">
              <div 
                className="h-full bg-green-500 rounded-full" 
                style={{ width: `${technical_analysis.trend_following.metrics.trend_strength * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        {/* Mean Reversion */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Mean Reversion</h3>
            <div className="flex items-center">
              {getSignalIcon(technical_analysis.mean_reversion.signal)}
              <span className={`ml-2 font-medium ${
                technical_analysis.mean_reversion.signal === 'bullish' ? 'text-green-500' : 
                technical_analysis.mean_reversion.signal === 'bearish' ? 'text-red-500' : 'text-yellow-500'
              }`}>
                {technical_analysis.mean_reversion.signal.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">RSI (14)</span>
              <div className="font-medium">
                {Math.round(technical_analysis.mean_reversion.metrics.rsi_14)}
                <span className="ml-2 text-sm text-gray-400">
                  {technical_analysis.mean_reversion.metrics.rsi_14 > 70 ? "Overbought" : 
                   technical_analysis.mean_reversion.metrics.rsi_14 < 30 ? "Oversold" : "Neutral"}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">RSI (28)</span>
              <div className="font-medium">
                {Math.round(technical_analysis.mean_reversion.metrics.rsi_28)}
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Z-Score</span>
              <div className="font-medium">
                {technical_analysis.mean_reversion.metrics.z_score.toFixed(2)}
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Price vs. Bollinger Bands</span>
              <div className="font-medium">
                {(technical_analysis.mean_reversion.metrics.price_vs_bb * 100).toFixed(0)}%
                <span className="ml-2 text-sm text-gray-400">
                  {technical_analysis.mean_reversion.metrics.price_vs_bb > 0.8 ? "Upper Band" : 
                   technical_analysis.mean_reversion.metrics.price_vs_bb < 0.2 ? "Lower Band" : "Middle"}
                </span>
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="h-1.5 w-full bg-gray-700 rounded-full">
              <div 
                className="h-full bg-blue-500 rounded-full" 
                style={{ width: `${technical_analysis.mean_reversion.metrics.price_vs_bb * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        {/* Momentum */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Momentum</h3>
            <div className="flex items-center">
              {getSignalIcon(technical_analysis.momentum.signal)}
              <span className={`ml-2 font-medium ${
                technical_analysis.momentum.signal === 'bullish' ? 'text-green-500' : 
                technical_analysis.momentum.signal === 'bearish' ? 'text-red-500' : 'text-yellow-500'
              }`}>
                {technical_analysis.momentum.signal.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">1-Month Momentum</span>
              <div className="font-medium">
                <span className={technical_analysis.momentum.metrics.momentum_1m >= 0 ? "text-green-500" : "text-red-500"}>
                  {(technical_analysis.momentum.metrics.momentum_1m * 100).toFixed(1)}%
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">3-Month Momentum</span>
              <div className="font-medium">
                <span className={technical_analysis.momentum.metrics.momentum_3m >= 0 ? "text-green-500" : "text-red-500"}>
                  {(technical_analysis.momentum.metrics.momentum_3m * 100).toFixed(1)}%
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">6-Month Momentum</span>
              <div className="font-medium">
                <span className={technical_analysis.momentum.metrics.momentum_6m >= 0 ? "text-green-500" : "text-red-500"}>
                  {(technical_analysis.momentum.metrics.momentum_6m * 100).toFixed(1)}%
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Volume Momentum</span>
              <div className="font-medium">
                {technical_analysis.momentum.metrics.volume_momentum.toFixed(2)}x
                <span className="ml-2 text-sm text-gray-400">
                  {technical_analysis.momentum.metrics.volume_momentum > 1 ? "Increasing" : "Decreasing"}
                </span>
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="h-1.5 w-full bg-gray-700 rounded-full">
              <div 
                className={`h-full rounded-full ${technical_analysis.momentum.metrics.momentum_score >= 0 ? "bg-green-500" : "bg-red-500"}`}
                style={{ width: `${Math.abs(technical_analysis.momentum.metrics.momentum_score) * 100 * 2}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        {/* Volatility */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium">Volatility</h3>
            <div className="flex items-center">
              {getSignalIcon(technical_analysis.volatility.signal)}
              <span className={`ml-2 font-medium ${
                technical_analysis.volatility.signal === 'bullish' ? 'text-green-500' : 
                technical_analysis.volatility.signal === 'bearish' ? 'text-red-500' : 'text-yellow-500'
              }`}>
                {technical_analysis.volatility.signal.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Historical Volatility</span>
              <div className="font-medium">
                {(technical_analysis.volatility.metrics.historical_volatility * 100).toFixed(2)}%
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Volatility Regime</span>
              <div className="font-medium">
                {technical_analysis.volatility.metrics.volatility_regime.toFixed(2)}
                <span className="ml-2 text-sm text-gray-400">
                  {technical_analysis.volatility.metrics.volatility_regime > 1.2 ? "High" : 
                   technical_analysis.volatility.metrics.volatility_regime < 0.8 ? "Low" : "Normal"}
                </span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">ATR Ratio</span>
              <div className="font-medium">
                {(technical_analysis.volatility.metrics.atr_ratio * 100).toFixed(2)}%
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Volatility Z-Score</span>
              <div className="font-medium">
                {technical_analysis.volatility.metrics.volatility_z_score.toFixed(2)}
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="h-1.5 w-full bg-gray-700 rounded-full">
              <div 
                className="h-full bg-purple-500 rounded-full" 
                style={{ width: `${technical_analysis.volatility.metrics.volatility_regime * 50}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Statistical Arbitrage */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-medium">Statistical Arbitrage</h3>
          <div className="flex items-center">
            {getSignalIcon(technical_analysis.statistical_arbitrage.signal)}
            <span className={`ml-2 font-medium ${
              technical_analysis.statistical_arbitrage.signal === 'bullish' ? 'text-green-500' : 
              technical_analysis.statistical_arbitrage.signal === 'bearish' ? 'text-red-500' : 'text-yellow-500'
            }`}>
              {technical_analysis.statistical_arbitrage.signal.toUpperCase()}
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <h4 className="text-sm text-gray-400">Hurst Exponent</h4>
            <div className="font-medium text-lg">{technical_analysis.statistical_arbitrage.metrics.hurst_exponent.toFixed(2)}</div>
            <div className="text-sm text-gray-400">
              {technical_analysis.statistical_arbitrage.metrics.hurst_exponent < 0.5 ? "Mean-reverting" : 
               technical_analysis.statistical_arbitrage.metrics.hurst_exponent > 0.5 ? "Trending" : "Random Walk"}
            </div>
          </div>
          
          <div className="space-y-2">
            <h4 className="text-sm text-gray-400">Skewness</h4>
            <div className="font-medium text-lg">{technical_analysis.statistical_arbitrage.metrics.skewness.toFixed(2)}</div>
            <div className="text-sm text-gray-400">
              {technical_analysis.statistical_arbitrage.metrics.skewness > 0 ? "Positively Skewed" : "Negatively Skewed"}
            </div>
          </div>
          
          <div className="space-y-2">
            <h4 className="text-sm text-gray-400">Kurtosis</h4>
            <div className="font-medium text-lg">{technical_analysis.statistical_arbitrage.metrics.kurtosis.toFixed(2)}</div>
            <div className="text-sm text-gray-400">
              {technical_analysis.statistical_arbitrage.metrics.kurtosis > 3 ? "Leptokurtic (Fat Tails)" : "Normal Distribution"}
            </div>
          </div>
        </div>
        
        <div className="mt-6">
          <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
            <FaInfoCircle />
            <span>Statistical properties of price movements can indicate potential trading opportunities</span>
          </div>
          <p className="text-gray-300">
            The Hurst exponent of {technical_analysis.statistical_arbitrage.metrics.hurst_exponent.toFixed(2)} indicates 
            {technical_analysis.statistical_arbitrage.metrics.hurst_exponent < 0.5 
              ? " mean-reverting behavior, suggesting potential for prices to return to historical averages." 
              : technical_analysis.statistical_arbitrage.metrics.hurst_exponent > 0.5 
                ? " trend-following behavior, suggesting persistent price movements in one direction."
                : " random walk behavior, suggesting unpredictable price movements."}
            {technical_analysis.statistical_arbitrage.metrics.skewness > 1 
              ? " Positive skewness suggests more frequent small losses but occasional large gains."
              : technical_analysis.statistical_arbitrage.metrics.skewness < -1
                ? " Negative skewness suggests more frequent small gains but occasional large losses."
                : ""}
          </p>
        </div>
      </div>
    </div>
  );
};

export default TechnicalAnalysis;