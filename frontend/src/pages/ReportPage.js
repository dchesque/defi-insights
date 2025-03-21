import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ReportSummary from '../components/ReportSummary';
import TechnicalAnalysis from '../components/TechnicalAnalysis';
import SentimentAnalysis from '../components/SentimentAnalysis';
import OnChainAnalysis from '../components/OnChainAnalysis';
import FundamentalAnalysis from '../components/FundamentalAnalysis';
import PriceChart from '../components/PriceChart';

const ReportPage = () => {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('summary');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // In a real application, you would fetch the report data from your API
    // For this demo, we'll use a mock report
    setLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      try {
        const mockReport = getMockReport(id);
        setReport(mockReport);
        setLoading(false);
      } catch (err) {
        setError('Failed to load report data');
        setLoading(false);
      }
    }, 1000);
  }, [id]);

  const getMockReport = (reportId) => {
    // This is mock data. In a real app, this would come from your API/backend
    return {
      id: reportId,
      symbol: 'BTC',
      name: 'Bitcoin',
      timestamp: new Date().toISOString(),
      price_data: {
        current_price: 61245.32,
        price_change_24h: 2.4,
        price_change_7d: -1.2,
        price_change_30d: 15.7,
        market_cap: 1192876543210,
        volume_24h: 38765432100
      },
      signals: {
        overall: 'bullish',
        confidence: 75.8,
        technical: 'bullish',
        onchain: 'bullish',
        sentiment: 'neutral'
      },
      technical_analysis: {
        trend_following: {
          signal: 'bullish',
          confidence: 82,
          metrics: {
            adx: 28.5,
            trend_strength: 0.78,
            short_trend: true,
            medium_trend: true
          }
        },
        mean_reversion: {
          signal: 'neutral',
          confidence: 55,
          metrics: {
            z_score: 0.8,
            price_vs_bb: 0.65,
            rsi_14: 58.2,
            rsi_28: 62.5
          }
        },
        momentum: {
          signal: 'bullish',
          confidence: 76,
          metrics: {
            momentum_1m: 0.12,
            momentum_3m: 0.18,
            momentum_6m: 0.42,
            momentum_score: 0.24,
            volume_momentum: 1.2
          }
        },
        volatility: {
          signal: 'neutral',
          confidence: 45,
          metrics: {
            historical_volatility: 0.045,
            volatility_regime: 0.92,
            volatility_z_score: -0.5,
            atr_ratio: 0.025
          }
        },
        statistical_arbitrage: {
          signal: 'bullish',
          confidence: 68,
          metrics: {
            hurst_exponent: 0.35,
            skewness: 1.2,
            kurtosis: 3.8
          }
        }
      },
      sentiment_analysis: {
        social_sentiment: 65,
        fear_greed_index: 72,
        fear_greed_classification: 'Greed',
        social_volume_24h: 125000,
        twitter_data: {
          tweet_count: 15700,
          positive_sentiment_percent: 62,
          negative_sentiment_percent: 18,
          neutral_sentiment_percent: 20
        },
        reddit_data: {
          post_count: 3200,
          positive_sentiment_percent: 58,
          negative_sentiment_percent: 22,
          neutral_sentiment_percent: 20,
          bullish_ratio: 2.64
        }
      },
      onchain_metrics: {
        active_addresses_24h: 982500,
        transaction_count_24h: 325000,
        transaction_volume_24h: 12500000000,
        average_transaction_fee: 2.45,
        market_to_realized_value_ratio: 2.2,
        hash_rate: 350000000000000000000,
        difficulty: 46270031793883,
        whale_accumulation_trend: 'increasing',
        smart_money_inflow_7d: 850000000,
        smart_money_outflow_7d: 420000000
      },
      risk_analysis: {
        position_limit: 10000,
        max_units: 0.163,
        current_price: 61245.32,
        volatility: 0.045,
        market_quality: {
          score: 7.8,
          description: 'Favorable market',
          risk_level: 'medium-low'
        }
      },
      price_prediction: {
        target_price_30d: 72500,
        confidence: 65,
        bull_case: 82000,
        bear_case: 55000
      },
      recommendation: 'Strong buy recommendation with increasing on-chain activity and positive momentum. Institutional interest remains high.'
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-500 mb-4">Error</h2>
          <p className="text-gray-300">{error}</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-300 mb-4">Report Not Found</h2>
          <p className="text-gray-400">The requested report could not be found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="py-8 px-4 md:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center">
              <h1 className="text-3xl font-bold">
                {report.name} ({report.symbol})
              </h1>
              <span className={`ml-4 px-3 py-1 rounded-full text-sm font-medium ${
                report.signals.overall === 'bullish' 
                  ? 'bg-green-900/40 text-green-400 border border-green-600/30' 
                  : report.signals.overall === 'bearish'
                    ? 'bg-red-900/40 text-red-400 border border-red-600/30'
                    : 'bg-yellow-900/40 text-yellow-400 border border-yellow-600/30'
              }`}>
                {report.signals.overall.toUpperCase()} ({report.signals.confidence}%)
              </span>
            </div>
            <p className="text-gray-400 mt-1">Analysis generated on {new Date(report.timestamp).toLocaleString()}</p>
          </div>
          
          <div className="mt-4 md:mt-0">
            <div className="flex items-center">
              <div className="text-3xl font-bold">${report.price_data.current_price.toLocaleString()}</div>
              <span className={`ml-2 ${
                report.price_data.price_change_24h >= 0 
                  ? 'text-green-500' 
                  : 'text-red-500'
              }`}>
                {report.price_data.price_change_24h >= 0 ? '+' : ''}
                {report.price_data.price_change_24h}%
              </span>
            </div>
            <p className="text-gray-400 text-sm">24h Change</p>
          </div>
        </div>
        
        {/* Price Chart */}
        <div className="bg-[#1A1C31] rounded-lg p-4 mb-8">
          <PriceChart symbol={report.symbol} />
        </div>
        
        {/* Tabs */}
        <div className="mb-6 border-b border-gray-800">
          <div className="flex overflow-x-auto">
            <button
              className={`py-3 px-4 font-medium text-sm border-b-2 ${
                activeTab === 'summary' 
                  ? 'border-indigo-500 text-white' 
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('summary')}
            >
              Summary
            </button>
            <button
              className={`py-3 px-4 font-medium text-sm border-b-2 ${
                activeTab === 'technical' 
                  ? 'border-indigo-500 text-white' 
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('technical')}
            >
              Technical
            </button>
            <button
              className={`py-3 px-4 font-medium text-sm border-b-2 ${
                activeTab === 'onchain' 
                  ? 'border-indigo-500 text-white' 
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('onchain')}
            >
              On-Chain
            </button>
            <button
              className={`py-3 px-4 font-medium text-sm border-b-2 ${
                activeTab === 'sentiment' 
                  ? 'border-indigo-500 text-white' 
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('sentiment')}
            >
              Sentiment
            </button>
            <button
              className={`py-3 px-4 font-medium text-sm border-b-2 ${
                activeTab === 'fundamental' 
                  ? 'border-indigo-500 text-white' 
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('fundamental')}
            >
              Fundamental
            </button>
          </div>
        </div>
        
        {/* Tab Content */}
        <div>
          {activeTab === 'summary' && <ReportSummary report={report} />}
          {activeTab === 'technical' && <TechnicalAnalysis report={report} />}
          {activeTab === 'onchain' && <OnChainAnalysis report={report} />}
          {activeTab === 'sentiment' && <SentimentAnalysis report={report} />}
          {activeTab === 'fundamental' && <FundamentalAnalysis report={report} />}
        </div>
      </div>
    </div>
  );
};

export default ReportPage;