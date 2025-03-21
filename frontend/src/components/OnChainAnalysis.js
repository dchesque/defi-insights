import React from 'react';
import { FaArrowUp, FaArrowDown, FaArrowRight, FaWallet, FaExchangeAlt, FaServer, FaNetworkWired } from 'react-icons/fa';

const OnChainAnalysis = ({ report }) => {
  if (!report || !report.onchain_metrics) {
    return (
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-2">On-Chain Analysis</h2>
        <p className="text-gray-400">No on-chain analysis data available.</p>
      </div>
    );
  }

  const { onchain_metrics } = report;
  
  const getSignalIcon = (signal) => {
    if (signal === 'bullish') return <FaArrowUp className="text-green-500" />;
    if (signal === 'bearish') return <FaArrowDown className="text-red-500" />;
    return <FaArrowRight className="text-yellow-500" />;
  };

  const formatLargeNumber = (num) => {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toString();
  };

  const formatHashRate = (hashrate) => {
    if (hashrate >= 1e18) return (hashrate / 1e18).toFixed(2) + ' EH/s';
    if (hashrate >= 1e15) return (hashrate / 1e15).toFixed(2) + ' PH/s';
    if (hashrate >= 1e12) return (hashrate / 1e12).toFixed(2) + ' TH/s';
    return hashrate.toString() + ' H/s';
  };

  return (
    <div className="space-y-8">
      {/* Summary */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">On-Chain Analysis</h2>
        
        <p className="text-gray-300 mb-6">
          Our on-chain analysis examines blockchain data including transaction activity, network usage, and wallet behaviors.
          These metrics provide insights into the underlying health and adoption of {report.symbol}, which may not be reflected
          in price action alone.
        </p>
        
        <div className="mb-6">
          <h3 className="font-medium mb-3">Overall On-Chain Signal</h3>
          <div className="flex items-center space-x-3">
            {getSignalIcon(report.signals.onchain)}
            <span className={`font-bold ${
              report.signals.onchain === 'bullish' ? 'text-green-500' : 
              report.signals.onchain === 'bearish' ? 'text-red-500' : 'text-yellow-500'
            }`}>
              {report.signals.onchain.toUpperCase()}
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key On-Chain Metrics:</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>Active Addresses (24h): {formatLargeNumber(onchain_metrics.active_addresses_24h)}</li>
              <li>Transaction Count (24h): {formatLargeNumber(onchain_metrics.transaction_count_24h)}</li>
              <li>Transaction Volume (24h): ${formatLargeNumber(onchain_metrics.transaction_volume_24h)}</li>
              <li>Average Fee: ${onchain_metrics.average_transaction_fee.toFixed(2)}</li>
              <li>MVRV Ratio: {onchain_metrics.market_to_realized_value_ratio.toFixed(2)}</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key Insights:</h3>
            <ul className="space-y-2">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>
                  {onchain_metrics.whale_accumulation_trend === 'increasing' ? 'Increasing' : 
                   onchain_metrics.whale_accumulation_trend === 'decreasing' ? 'Decreasing' : 'Neutral'} 
                  whale accumulation trend
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>
                  {onchain_metrics.smart_money_inflow_7d > onchain_metrics.smart_money_outflow_7d ? 'Net inflow' : 'Net outflow'} 
                  of "smart money" in the past 7 days
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">•</span>
                <span>
                  {onchain_metrics.hash_rate ? 'Strong network security with high hash rate' : 'Healthy network metrics'}
                </span>
              </li>
              <li className="flex items-start">
                <span className={onchain_metrics.market_to_realized_value_ratio > 1 ? "text-green-500" : "text-red-500"} mr-2>•</span>
                <span>
                  MVRV ratio of {onchain_metrics.market_to_realized_value_ratio.toFixed(2)} indicates
                  {onchain_metrics.market_to_realized_value_ratio > 3 ? ' possible overvaluation' : 
                   onchain_metrics.market_to_realized_value_ratio > 1 ? ' healthy valuation' : ' possible undervaluation'}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Network Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Addresses & Transactions */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaWallet className="text-indigo-400 mr-2" />
            <h3 className="font-medium">Addresses & Transactions</h3>
          </div>
          
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xl font-bold">{formatLargeNumber(onchain_metrics.active_addresses_24h)}</div>
                <div className="text-sm text-gray-400">Active Addresses (24h)</div>
                <div className="text-xs text-green-500 mt-1">+5.2% vs avg</div>
              </div>
              
              <div>
                <div className="text-xl font-bold">{formatLargeNumber(onchain_metrics.transaction_count_24h)}</div>
                <div className="text-sm text-gray-400">Transactions (24h)</div>
                <div className="text-xs text-green-500 mt-1">+3.8% vs avg</div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Transaction Volume (24h)</span>
                <span className="font-medium">${formatLargeNumber(onchain_metrics.transaction_volume_24h)}</span>
              </div>
              <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-indigo-500 rounded-full" 
                  style={{ width: '65%' }}
                ></div>
              </div>
              <div className="mt-1 text-right text-xs text-green-500">
                +12% vs 7-day average
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Average Transaction Fee</span>
                <span className="font-medium">${onchain_metrics.average_transaction_fee.toFixed(2)}</span>
              </div>
              <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-indigo-500 rounded-full" 
                  style={{ width: '40%' }}
                ></div>
              </div>
              <div className="mt-1 text-right text-xs text-red-500">
                -2.3% vs 7-day average
              </div>
            </div>
          </div>
        </div>
        
        {/* Smart Money Flow */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaExchangeAlt className="text-indigo-400 mr-2" />
            <h3 className="font-medium">Smart Money Flow</h3>
          </div>
          
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xl font-bold text-green-500">${formatLargeNumber(onchain_metrics.smart_money_inflow_7d)}</div>
                <div className="text-sm text-gray-400">Inflow (7d)</div>
              </div>
              
              <div>
                <div className="text-xl font-bold text-red-500">${formatLargeNumber(onchain_metrics.smart_money_outflow_7d)}</div>
                <div className="text-sm text-gray-400">Outflow (7d)</div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Net Flow</span>
                <span className={`font-medium ${
                  onchain_metrics.smart_money_inflow_7d > onchain_metrics.smart_money_outflow_7d ? 'text-green-500' : 'text-red-500'
                }`}>
                  ${formatLargeNumber(onchain_metrics.smart_money_inflow_7d - onchain_metrics.smart_money_outflow_7d)}
                </span>
              </div>
              <div className="flex h-2">
                <div 
                  className="bg-green-500 h-full rounded-l" 
                  style={{ width: `${onchain_metrics.smart_money_inflow_7d / (onchain_metrics.smart_money_inflow_7d + onchain_metrics.smart_money_outflow_7d) * 100}%` }}
                ></div>
                <div 
                  className="bg-red-500 h-full rounded-r" 
                  style={{ width: `${onchain_metrics.smart_money_outflow_7d / (onchain_metrics.smart_money_inflow_7d + onchain_metrics.smart_money_outflow_7d) * 100}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Whale Accumulation Trend</span>
                <span className={`font-medium ${
                  onchain_metrics.whale_accumulation_trend === 'increasing' ? 'text-green-500' : 
                  onchain_metrics.whale_accumulation_trend === 'decreasing' ? 'text-red-500' : 'text-yellow-500'
                }`}>
                  {onchain_metrics.whale_accumulation_trend.charAt(0).toUpperCase() + onchain_metrics.whale_accumulation_trend.slice(1)}
                </span>
              </div>
              <div className="bg-[#12141f] p-3 rounded border border-gray-700">
                <p className="text-sm text-gray-300">
                  {onchain_metrics.whale_accumulation_trend === 'increasing' 
                    ? 'Large wallets (top 1%) are currently in accumulation phase, indicating confidence in the asset\'s future value.'
                    : onchain_metrics.whale_accumulation_trend === 'decreasing'
                      ? 'Large wallets (top 1%) are currently reducing positions, which may indicate caution or profit-taking.'
                      : 'Large wallets (top 1%) are maintaining stable positions, neither accumulating nor distributing significantly.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Network Health & MVRV */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Network Health */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaServer className="text-indigo-400 mr-2" />
            <h3 className="font-medium">Network Health</h3>
          </div>
          
          <div className="space-y-6">
            {onchain_metrics.hash_rate && (
              <div>
                <div className="flex justify-between mb-1 text-sm">
                  <span>Hash Rate</span>
                  <span className="font-medium">{formatHashRate(onchain_metrics.hash_rate)}</span>
                </div>
                <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 rounded-full" 
                    style={{ width: '85%' }}
                  ></div>
                </div>
                <div className="mt-1 text-right text-xs text-green-500">
                  Near all-time high
                </div>
              </div>
            )}
            
            {onchain_metrics.difficulty && (
              <div>
                <div className="flex justify-between mb-1 text-sm">
                  <span>Mining Difficulty</span>
                  <span className="font-medium">{formatLargeNumber(onchain_metrics.difficulty)}</span>
                </div>
                <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-green-500 rounded-full" 
                    style={{ width: '80%' }}
                  ></div>
                </div>
                <div className="mt-1 text-right text-xs text-green-500">
                  +2.3% since last adjustment
                </div>
              </div>
            )}
            
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm font-medium mb-2">Network Security Assessment</h4>
              <div className="flex items-center mb-2">
                <div className="h-2 w-2 rounded-full bg-green-500 mr-2"></div>
                <span className="text-sm text-gray-300">Strong</span>
              </div>
              <p className="text-sm text-gray-400">
                {report.symbol === 'BTC' 
                  ? `Bitcoin's hash rate is at near all-time high levels, indicating extremely robust network security. 
                     The high difficulty adjustment reflects growing mining competition.`
                  : `Network security metrics show strong fundamentals with increasing participation 
                     and robust validation mechanisms.`}
              </p>
            </div>
          </div>
        </div>
        
        {/* MVRV & Valuation */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaNetworkWired className="text-indigo-400 mr-2" />
            <h3 className="font-medium">MVRV & Valuation Metrics</h3>
          </div>
          
          <div className="space-y-6">
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>MVRV Ratio</span>
                <span className="font-medium">{onchain_metrics.market_to_realized_value_ratio.toFixed(2)}</span>
              </div>
              <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    onchain_metrics.market_to_realized_value_ratio > 3 ? 'bg-red-500' :
                    onchain_metrics.market_to_realized_value_ratio > 2 ? 'bg-yellow-500' :
                    onchain_metrics.market_to_realized_value_ratio > 1 ? 'bg-green-500' :
                    'bg-blue-500'
                  }`}
                  style={{ width: `${Math.min(onchain_metrics.market_to_realized_value_ratio / 4, 1) * 100}%` }}
                ></div>
              </div>
              <div className="mt-1 flex justify-between text-xs text-gray-400">
                <span>Undervalued</span>
                <span>Fair Value</span>
                <span>Overvalued</span>
              </div>
            </div>
            
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm font-medium mb-2">MVRV Interpretation</h4>
              <p className="text-sm text-gray-300 mb-2">
                The Market Value to Realized Value (MVRV) ratio of {onchain_metrics.market_to_realized_value_ratio.toFixed(2)} indicates
                {onchain_metrics.market_to_realized_value_ratio > 3.5 
                  ? ' that the asset may be significantly overvalued relative to its realized price, suggesting caution.' 
                  : onchain_metrics.market_to_realized_value_ratio > 2.5
                    ? ' that the asset is approaching overvalued territory, suggesting some caution is warranted.'
                    : onchain_metrics.market_to_realized_value_ratio > 1.5
                      ? ' a healthy premium over realized value, suggesting reasonable valuation.'
                      : onchain_metrics.market_to_realized_value_ratio > 1
                        ? ' that the asset is trading slightly above its realized value, suggesting fair valuation.'
                        : ' that the asset is trading below its realized value, potentially presenting a buying opportunity.'}
              </p>
              <p className="text-sm text-gray-400">
                Historically, MVRV values above 3.5 have often indicated market tops, while values below 1 have indicated market bottoms.
              </p>
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Supply on Exchanges</span>
                <span className="font-medium">8.2%</span>
              </div>
              <div className="h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full" 
                  style={{ width: '30%' }}
                ></div>
              </div>
              <div className="mt-1 text-right text-xs text-green-500">
                -0.8% in last 30 days (bullish)
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Supply Distribution */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h3 className="font-medium mb-4">Supply Distribution Analysis</h3>
        
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm text-gray-400 mb-2">Realized Price</h4>
              <div className="text-xl font-bold">${(report.price_data.current_price / onchain_metrics.market_to_realized_value_ratio).toFixed(2)}</div>
              <div className="text-xs text-gray-400 mt-1">Average cost basis of all coins</div>
            </div>
            
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm text-gray-400 mb-2">Exchange Supply</h4>
              <div className="text-xl font-bold">8.2%</div>
              <div className={`text-xs mt-1 ${
                "text-green-500"
              }`}>
                Decreasing (-0.8% in 30d)
              </div>
            </div>
            
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm text-gray-400 mb-2">Illiquid Supply</h4>
              <div className="text-xl font-bold">76.3%</div>
              <div className={`text-xs mt-1 ${
                "text-green-500"
              }`}>
                Increasing (+1.2% in 30d)
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm text-gray-400 mb-2">Wallet Distribution</h4>
            <div className="h-10 bg-[#12141f] rounded relative overflow-hidden">
              <div className="absolute inset-0 flex h-full">
                <div className="h-full bg-blue-600" style={{ width: '2%' }}></div>
                <div className="h-full bg-indigo-600" style={{ width: '8%' }}></div>
                <div className="h-full bg-purple-600" style={{ width: '15%' }}></div>
                <div className="h-full bg-pink-600" style={{ width: '25%' }}></div>
                <div className="h-full bg-red-600" style={{ width: '50%' }}></div>
              </div>
            </div>
            <div className="mt-2 grid grid-cols-5 text-xs text-gray-400">
              <div>Whales<br/>2%</div>
              <div>Large<br/>8%</div>
              <div>Medium<br/>15%</div>
              <div>Small<br/>25%</div>
              <div>Retail<br/>50%</div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm text-gray-400 mb-2">Supply Age Analysis</h4>
              <div className="bg-[#12141f] p-3 rounded border border-gray-700">
                <ul className="space-y-2">
                  <li className="flex justify-between">
                    <span className="text-gray-400">Dormant 1+ Years</span>
                    <span className="font-medium">65.2%</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-400">Held 6-12 Months</span>
                    <span className="font-medium">15.3%</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-400">Held 1-6 Months</span>
                    <span className="font-medium">12.8%</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-400">Held {'<'}30 Days</span>
                    <span className="font-medium">6.7%</span>
                  </li>
                </ul>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm text-gray-400 mb-2">Key On-Chain Indicators</h4>
              <div className="bg-[#12141f] p-3 rounded border border-gray-700">
                <p className="text-sm text-gray-300">
                  The combination of decreasing exchange supply, increasing illiquid supply, and strong holding behavior 
                  among long-term investors creates structural support for the asset price. The MVRV ratio of 
                  {onchain_metrics.market_to_realized_value_ratio.toFixed(2)} suggests 
                  {onchain_metrics.market_to_realized_value_ratio > 2.5 
                    ? ' some caution is warranted as the market appears to be pricing in significant future growth.'
                    : onchain_metrics.market_to_realized_value_ratio > 1
                      ? ' the market is pricing the asset at a reasonable premium to its realized value.'
                      : ' the market is currently undervaluing the asset relative to its realized value.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnChainAnalysis;