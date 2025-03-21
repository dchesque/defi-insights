import React from 'react';
import { FaTwitter, FaReddit, FaGlobe, FaChartBar, FaArrowUp, FaArrowDown, FaArrowRight } from 'react-icons/fa';

const SentimentAnalysis = ({ report }) => {
  if (!report || !report.sentiment_analysis) {
    return (
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-2">Sentiment Analysis</h2>
        <p className="text-gray-400">No sentiment analysis data available.</p>
      </div>
    );
  }

  const { sentiment_analysis } = report;
  
  const getSignalIcon = (signal) => {
    if (signal === 'bullish') return <FaArrowUp className="text-green-500" />;
    if (signal === 'bearish') return <FaArrowDown className="text-red-500" />;
    return <FaArrowRight className="text-yellow-500" />;
  };

  const getSentimentGradient = (value) => {
    // Convert 0-100 scale to percentage for the gradient
    return (
      <div className="w-full h-2 bg-gray-700 rounded-full">
        <div 
          className="h-full rounded-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500" 
          style={{ width: `${value}%` }}
        ></div>
      </div>
    );
  };

  const getFearGreedColor = (value) => {
    if (value >= 75) return 'text-green-500';
    if (value >= 50) return 'text-lime-500';
    if (value >= 25) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getFearGreedClass = (classification) => {
    if (classification.includes('Extreme Greed')) return 'bg-green-900/30 text-green-500 border-green-700/30';
    if (classification.includes('Greed')) return 'bg-lime-900/30 text-lime-500 border-lime-700/30';
    if (classification.includes('Neutral')) return 'bg-yellow-900/30 text-yellow-500 border-yellow-700/30';
    if (classification.includes('Fear')) return 'bg-orange-900/30 text-orange-500 border-orange-700/30';
    if (classification.includes('Extreme Fear')) return 'bg-red-900/30 text-red-500 border-red-700/30';
    return 'bg-gray-900/30 text-gray-500 border-gray-700/30';
  };

  return (
    <div className="space-y-8">
      {/* Summary */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Sentiment Analysis</h2>
        
        <p className="text-gray-300 mb-6">
          Our sentiment analysis combines data from social media, news sources, and market indicators to provide
          a comprehensive view of market sentiment for {report.symbol}. This includes Twitter/X sentiment, Reddit discussions,
          and the famous Fear & Greed Index.
        </p>
        
        <div className="mb-6">
          <h3 className="font-medium mb-3">Overall Sentiment Signal</h3>
          <div className="flex items-center space-x-3">
            {getSignalIcon(report.signals.sentiment)}
            <span className={`font-bold ${
              report.signals.sentiment === 'bullish' ? 'text-green-500' : 
              report.signals.sentiment === 'bearish' ? 'text-red-500' : 'text-yellow-500'
            }`}>
              {report.signals.sentiment.toUpperCase()}
            </span>
            <div className="text-sm text-gray-400 ml-2">Confidence: {sentiment_analysis.social_sentiment}%</div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key Sentiment Indicators:</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>Social Sentiment Score: {sentiment_analysis.social_sentiment}/100</li>
              <li>Fear & Greed Index: {sentiment_analysis.fear_greed_index} ({sentiment_analysis.fear_greed_classification})</li>
              <li>Twitter Positive Sentiment: {sentiment_analysis.twitter_data.positive_sentiment_percent}%</li>
              <li>Reddit Bullish Ratio: {sentiment_analysis.reddit_data.bullish_ratio}</li>
              <li>Social Volume: {sentiment_analysis.social_volume_24h.toLocaleString()} mentions</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Key Insights:</h3>
            <ul className="space-y-2">
              <li className="flex items-start">
                <span className={sentiment_analysis.twitter_data.positive_sentiment_percent > 50 ? "text-green-500" : "text-red-500"} mr-2>•</span>
                <span>
                  {sentiment_analysis.twitter_data.positive_sentiment_percent > 50 ? "Positive" : "Negative"} Twitter sentiment 
                  ({sentiment_analysis.twitter_data.positive_sentiment_percent}% positive)
                </span>
              </li>
              <li className="flex items-start">
                <span className={sentiment_analysis.reddit_data.bullish_ratio > 1 ? "text-green-500" : "text-red-500"} mr-2>•</span>
                <span>
                  {sentiment_analysis.reddit_data.bullish_ratio > 1 ? "Bullish" : "Bearish"} Reddit sentiment 
                  (Ratio: {sentiment_analysis.reddit_data.bullish_ratio.toFixed(2)})
                </span>
              </li>
              <li className="flex items-start">
                <span className={sentiment_analysis.fear_greed_index > 50 ? "text-green-500" : "text-red-500"} mr-2>•</span>
                <span>
                  Market in "{sentiment_analysis.fear_greed_classification}" phase
                </span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                <span>
                  High social engagement with {sentiment_analysis.social_volume_24h.toLocaleString()} mentions in 24h
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Fear & Greed Index */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h3 className="font-medium mb-4">Fear & Greed Index</h3>
        
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="mb-4 md:mb-0">
            <div className="flex items-baseline">
              <div className={`text-4xl font-bold ${getFearGreedColor(sentiment_analysis.fear_greed_index)}`}>
                {sentiment_analysis.fear_greed_index}
              </div>
              <div className="ml-3 text-xl text-gray-300">/100</div>
            </div>
            <div className={`mt-2 inline-block px-3 py-1 rounded border ${getFearGreedClass(sentiment_analysis.fear_greed_classification)}`}>
              {sentiment_analysis.fear_greed_classification}
            </div>
            <div className="mt-3 text-sm text-gray-400">
              The Fear & Greed Index measures market sentiment from 0 (Extreme Fear) to 100 (Extreme Greed)
            </div>
          </div>
          
          <div className="w-full md:w-1/2">
            <div className="mb-3">
              {getSentimentGradient(sentiment_analysis.fear_greed_index)}
            </div>
            <div className="flex justify-between text-xs text-gray-400">
              <span>Extreme Fear</span>
              <span>Fear</span>
              <span>Neutral</span>
              <span>Greed</span>
              <span>Extreme Greed</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Social Media Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Twitter */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaTwitter className="text-blue-400 mr-2" />
            <h3 className="font-medium">Twitter/X Sentiment</h3>
          </div>
          
          <div className="space-y-6">
            <div className="flex justify-between">
              <div>
                <div className="text-2xl font-bold">{sentiment_analysis.twitter_data.tweet_count.toLocaleString()}</div>
                <div className="text-sm text-gray-400">Tweets in 24h</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{sentiment_analysis.twitter_data.positive_sentiment_percent}%</div>
                <div className="text-sm text-gray-400">Positive Sentiment</div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Sentiment Distribution</span>
              </div>
              <div className="flex h-4">
                <div 
                  className="bg-green-500 h-full rounded-l" 
                  style={{ width: `${sentiment_analysis.twitter_data.positive_sentiment_percent}%` }}
                ></div>
                <div 
                  className="bg-gray-500 h-full" 
                  style={{ width: `${sentiment_analysis.twitter_data.neutral_sentiment_percent}%` }}
                ></div>
                <div 
                  className="bg-red-500 h-full rounded-r" 
                  style={{ width: `${sentiment_analysis.twitter_data.negative_sentiment_percent}%` }}
                ></div>
              </div>
              <div className="flex justify-between mt-1 text-xs text-gray-400">
                <span>Positive: {sentiment_analysis.twitter_data.positive_sentiment_percent}%</span>
                <span>Neutral: {sentiment_analysis.twitter_data.neutral_sentiment_percent}%</span>
                <span>Negative: {sentiment_analysis.twitter_data.negative_sentiment_percent}%</span>
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-400 mb-1">Engagement Rate</div>
              <div className="h-1.5 w-full bg-gray-700 rounded-full">
                <div 
                  className="h-full bg-blue-500 rounded-full" 
                  style={{ width: '75%' }}
                ></div>
              </div>
              <div className="mt-1 text-right text-xs text-gray-400">
                High
              </div>
            </div>
          </div>
        </div>
        
        {/* Reddit */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaReddit className="text-orange-400 mr-2" />
            <h3 className="font-medium">Reddit Sentiment</h3>
          </div>
          
          <div className="space-y-6">
            <div className="flex justify-between">
              <div>
                <div className="text-2xl font-bold">{sentiment_analysis.reddit_data.post_count.toLocaleString()}</div>
                <div className="text-sm text-gray-400">Posts in 24h</div>
              </div>
              <div>
                <div className="text-2xl font-bold">{sentiment_analysis.reddit_data.bullish_ratio.toFixed(2)}</div>
                <div className="text-sm text-gray-400">Bullish Ratio</div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Sentiment Distribution</span>
              </div>
              <div className="flex h-4">
                <div 
                  className="bg-green-500 h-full rounded-l" 
                  style={{ width: `${sentiment_analysis.reddit_data.positive_sentiment_percent}%` }}
                ></div>
                <div 
                  className="bg-gray-500 h-full" 
                  style={{ width: `${sentiment_analysis.reddit_data.neutral_sentiment_percent}%` }}
                ></div>
                <div 
                  className="bg-red-500 h-full rounded-r" 
                  style={{ width: `${sentiment_analysis.reddit_data.negative_sentiment_percent}%` }}
                ></div>
              </div>
              <div className="flex justify-between mt-1 text-xs text-gray-400">
                <span>Positive: {sentiment_analysis.reddit_data.positive_sentiment_percent}%</span>
                <span>Neutral: {sentiment_analysis.reddit_data.neutral_sentiment_percent}%</span>
                <span>Negative: {sentiment_analysis.reddit_data.negative_sentiment_percent}%</span>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between">
                <div className="text-sm text-gray-400 mb-1">Bullish vs Bearish Posts</div>
                <div className="text-sm font-medium">{sentiment_analysis.reddit_data.bullish_ratio.toFixed(2)}:1</div>
              </div>
              <div className="flex h-1.5">
                <div 
                  className="bg-green-500 h-full rounded-l" 
                  style={{ width: `${sentiment_analysis.reddit_data.bullish_ratio * 50}%` }}
                ></div>
                <div 
                  className="bg-red-500 h-full rounded-r" 
                  style={{ width: `${100 - sentiment_analysis.reddit_data.bullish_ratio * 50}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Social Volume Analysis */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h3 className="font-medium mb-4">Social Volume Analysis</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-[#12141f] p-4 rounded border border-gray-700">
            <div className="flex items-center text-gray-400 mb-2">
              <FaChartBar className="mr-2" />
              <span>Total Social Volume</span>
            </div>
            <div className="text-2xl font-bold">{sentiment_analysis.social_volume_24h.toLocaleString()}</div>
            <div className="text-sm text-gray-400">Mentions in last 24h</div>
          </div>
          
          <div className="bg-[#12141f] p-4 rounded border border-gray-700">
            <div className="flex items-center text-gray-400 mb-2">
              <FaTwitter className="mr-2" />
              <span>Twitter Volume</span>
            </div>
            <div className="text-2xl font-bold">{sentiment_analysis.twitter_data.tweet_count.toLocaleString()}</div>
            <div className="text-sm text-gray-400">Tweets in last 24h</div>
          </div>
          
          <div className="bg-[#12141f] p-4 rounded border border-gray-700">
            <div className="flex items-center text-gray-400 mb-2">
              <FaReddit className="mr-2" />
              <span>Reddit Volume</span>
            </div>
            <div className="text-2xl font-bold">{sentiment_analysis.reddit_data.post_count.toLocaleString()}</div>
            <div className="text-sm text-gray-400">Posts in last 24h</div>
          </div>
        </div>
        
        <div>
          <h4 className="text-gray-300 font-medium mb-2">Social Volume Trend</h4>
          <div className="flex items-center">
            <div className="w-full">
              <div className="flex justify-between mb-1 text-xs text-gray-400">
                <span>7 days ago</span>
                <span>Now</span>
              </div>
              <div className="h-10 bg-gradient-to-r from-indigo-500/20 to-indigo-500/60 rounded relative">
                {/* This would be a chart in a real implementation */}
                <div className="absolute inset-0 flex items-end">
                  <div className="h-40% w-1/7 bg-indigo-500/80"></div>
                  <div className="h-60% w-1/7 bg-indigo-500/80"></div>
                  <div className="h-50% w-1/7 bg-indigo-500/80"></div>
                  <div className="h-70% w-1/7 bg-indigo-500/80"></div>
                  <div className="h-65% w-1/7 bg-indigo-500/80"></div>
                  <div className="h-80% w-1/7 bg-indigo-500/80"></div>
                  <div className="h-100% w-1/7 bg-indigo-500/80"></div>
                </div>
              </div>
            </div>
            <div className="ml-4">
              <div className="text-lg font-bold text-green-500">+25%</div>
              <div className="text-xs text-gray-400">vs last week</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Sentiment Impact */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h3 className="font-medium mb-4">Sentiment Impact Analysis</h3>
        
        <p className="text-gray-300 mb-4">
          Our AI analyzes how sentiment correlates with price movements for {report.symbol}. Historical data shows that
          social sentiment for this asset {sentiment_analysis.social_sentiment > 65 ? "often precedes price movements by 1-2 days" : "has moderate correlation with price action"}.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm text-gray-400 mb-2">Recent Sentiment Impact</h4>
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  <span>Positive sentiment across social platforms correlates with recent price stability</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">•</span>
                  <span>Bullish narratives dominating Twitter discussions</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>Institutional interest remains strong, though retail sentiment is mixed</span>
                </li>
                <li className="flex items-start">
                  <span className="text-yellow-500 mr-2">•</span>
                  <span>Rising social volume indicates growing interest, which typically precedes volatility</span>
                </li>
              </ul>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm text-gray-400 mb-2">Sentiment Interpretation</h4>
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <p className="text-gray-300 mb-2">
                The overall sentiment score of {sentiment_analysis.social_sentiment}/100 is {sentiment_analysis.social_sentiment > 60 ? "bullish" : sentiment_analysis.social_sentiment > 40 ? "neutral" : "bearish"}.
                Fear & Greed Index at {sentiment_analysis.fear_greed_index} indicates market is in
                <span className={`font-medium ${getFearGreedColor(sentiment_analysis.fear_greed_index)}`}> {sentiment_analysis.fear_greed_classification.toLowerCase()} </span>
                territory.
              </p>
              <p className="text-gray-300">
                {sentiment_analysis.fear_greed_index > 75 ? 
                  "Extreme greed can be a contrarian indicator, suggesting caution for new entries." :
                 sentiment_analysis.fear_greed_index > 50 ?
                  "Greed suggests positive momentum may continue in the short term." :
                 sentiment_analysis.fear_greed_index > 25 ?
                  "Neutral sentiment suggests balanced risk/reward for current entries." :
                  "Fear can present buying opportunities as assets may be undervalued."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentAnalysis;