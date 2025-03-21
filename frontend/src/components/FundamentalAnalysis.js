import React from 'react';
import { FaArrowUp, FaArrowDown, FaArrowRight, FaInfoCircle, FaUsers, FaCode, FaGlobe, FaBuilding } from 'react-icons/fa';

const FundamentalAnalysis = ({ report }) => {
  // Since we don't have actual fundamental analysis data in the mock report,
  // we'll create a simulated version here
  const simulatedFundamentalData = {
    technology: {
      score: 4.5,
      decentralization: 4.2,
      security: 4.8,
      scalability: 3.5,
      interoperability: 3.8,
      development_activity: 4.3
    },
    tokenomics: {
      score: 4.2,
      supply_distribution: 4.0,
      inflation_rate: 1.8,
      token_utility: 4.5,
      token_model: 4.3
    },
    team: {
      score: 4.7,
      experience: 4.8,
      track_record: 4.7,
      transparency: 4.6,
      community_engagement: 4.5
    },
    adoption: {
      score: 4.0,
      current_usage: 3.8,
      growth_trend: 4.2,
      ecosystem_size: 4.0,
      institutional_adoption: 4.1
    },
    competition: {
      score: 3.9,
      market_position: 4.5,
      unique_value: 4.0,
      competitive_advantage: 3.5,
      threat_level: 3.5
    }
  };

  const getScoreColor = (score) => {
    if (score >= 4.5) return 'text-green-500';
    if (score >= 4.0) return 'text-green-400';
    if (score >= 3.5) return 'text-yellow-500';
    if (score >= 3.0) return 'text-yellow-400';
    if (score >= 2.5) return 'text-orange-400';
    return 'text-red-500';
  };

  const renderScoreStars = (score) => {
    const fullStars = Math.floor(score);
    const halfStar = score % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    
    return (
      <div className="flex">
        {[...Array(fullStars)].map((_, i) => (
          <span key={`full-${i}`} className="text-yellow-500">★</span>
        ))}
        {halfStar && <span className="text-yellow-500">★</span>}
        {[...Array(emptyStars)].map((_, i) => (
          <span key={`empty-${i}`} className="text-gray-600">★</span>
        ))}
        <span className={`ml-2 ${getScoreColor(score)}`}>{score.toFixed(1)}/5</span>
      </div>
    );
  };

  const renderScoreBar = (score) => {
    return (
      <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full ${
            score >= 4.5 ? 'bg-green-500' :
            score >= 4.0 ? 'bg-green-400' :
            score >= 3.5 ? 'bg-yellow-500' :
            score >= 3.0 ? 'bg-yellow-400' :
            score >= 2.5 ? 'bg-orange-400' :
            'bg-red-500'
          }`}
          style={{ width: `${(score / 5) * 100}%` }}
        ></div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Summary */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Fundamental Analysis</h2>
        
        <p className="text-gray-300 mb-6">
          Our fundamental analysis evaluates {report.name} ({report.symbol}) from multiple perspectives: technology,
          tokenomics, team quality, adoption metrics, and competitive positioning. These factors provide insights
          into the project's long-term viability and growth potential.
        </p>
        
        <div className="mb-6">
          <h3 className="font-medium mb-3">Overall Fundamental Rating</h3>
          <div className="flex items-center">
            {renderScoreStars(4.3)}
          </div>
          <div className="mt-2">
            {renderScoreBar(4.3)}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Strengths:</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>Strong network security and decentralization</li>
              <li>Well-established market position and brand recognition</li>
              <li>Experienced development team with proven track record</li>
              <li>Growing institutional adoption and infrastructure</li>
              <li>Clear token utility and value accrual mechanisms</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-200 mb-2">Weaknesses:</h3>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>Scalability challenges during peak network usage</li>
              <li>Competitive pressure from newer protocols</li>
              <li>Development progress sometimes slower than roadmap</li>
              <li>Regulatory uncertainty in key markets</li>
              <li>High correlation with broader crypto market movements</li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Technology Assessment */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <div className="flex items-center mb-4">
          <FaCode className="text-indigo-400 mr-2" />
          <h3 className="font-medium">Technology Assessment</h3>
          <div className="ml-auto">
            {renderScoreStars(simulatedFundamentalData.technology.score)}
          </div>
        </div>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-1 text-sm">
              <span>Decentralization</span>
              <span className={getScoreColor(simulatedFundamentalData.technology.decentralization)}>
                {simulatedFundamentalData.technology.decentralization.toFixed(1)}/5
              </span>
            </div>
            {renderScoreBar(simulatedFundamentalData.technology.decentralization)}
          </div>
          
          <div>
            <div className="flex justify-between mb-1 text-sm">
              <span>Security</span>
              <span className={getScoreColor(simulatedFundamentalData.technology.security)}>
                {simulatedFundamentalData.technology.security.toFixed(1)}/5
              </span>
            </div>
            {renderScoreBar(simulatedFundamentalData.technology.security)}
          </div>
          
          <div>
            <div className="flex justify-between mb-1 text-sm">
              <span>Scalability</span>
              <span className={getScoreColor(simulatedFundamentalData.technology.scalability)}>
                {simulatedFundamentalData.technology.scalability.toFixed(1)}/5
              </span>
            </div>
            {renderScoreBar(simulatedFundamentalData.technology.scalability)}
          </div>
          
          <div>
            <div className="flex justify-between mb-1 text-sm">
              <span>Interoperability</span>
              <span className={getScoreColor(simulatedFundamentalData.technology.interoperability)}>
                {simulatedFundamentalData.technology.interoperability.toFixed(1)}/5
              </span>
            </div>
            {renderScoreBar(simulatedFundamentalData.technology.interoperability)}
          </div>
          
          <div>
            <div className="flex justify-between mb-1 text-sm">
              <span>Development Activity</span>
              <span className={getScoreColor(simulatedFundamentalData.technology.development_activity)}>
                {simulatedFundamentalData.technology.development_activity.toFixed(1)}/5
              </span>
            </div>
            {renderScoreBar(simulatedFundamentalData.technology.development_activity)}
          </div>
        </div>
        
        <div className="mt-4 bg-[#12141f] p-3 rounded border border-gray-700">
          <p className="text-sm text-gray-300">
            {report.symbol} demonstrates exceptional security characteristics with robust consensus mechanisms
            and a strong track record of withstanding attacks. Decentralization remains high with a well-distributed
            network of nodes. Scalability presents some challenges during peak demand, though ongoing development
            efforts are addressing these limitations through layer-2 solutions and protocol upgrades.
          </p>
        </div>
      </div>
      
      {/* Tokenomics */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <div className="flex items-center mb-4">
          <FaGlobe className="text-indigo-400 mr-2" />
          <h3 className="font-medium">Tokenomics</h3>
          <div className="ml-auto">
            {renderScoreStars(simulatedFundamentalData.tokenomics.score)}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Supply Distribution</span>
                <span className={getScoreColor(simulatedFundamentalData.tokenomics.supply_distribution)}>
                  {simulatedFundamentalData.tokenomics.supply_distribution.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.tokenomics.supply_distribution)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Inflation Rate</span>
                <span className={getScoreColor(5 - simulatedFundamentalData.tokenomics.inflation_rate)}>
                  {simulatedFundamentalData.tokenomics.inflation_rate.toFixed(1)}% (Good)
                </span>
              </div>
              {renderScoreBar(5 - simulatedFundamentalData.tokenomics.inflation_rate)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Token Utility</span>
                <span className={getScoreColor(simulatedFundamentalData.tokenomics.token_utility)}>
                  {simulatedFundamentalData.tokenomics.token_utility.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.tokenomics.token_utility)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Token Model</span>
                <span className={getScoreColor(simulatedFundamentalData.tokenomics.token_model)}>
                  {simulatedFundamentalData.tokenomics.token_model.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.tokenomics.token_model)}
            </div>
          </div>
          
          <div>
            <div className="bg-[#12141f] p-3 rounded border border-gray-700 mb-4">
              <h4 className="text-sm font-medium mb-2">Supply Overview</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span className="text-gray-400">Circulating Supply:</span>
                  <span>{(report.price_data.market_cap / report.price_data.current_price).toLocaleString()} {report.symbol}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Total Supply:</span>
                  <span>21,000,000 {report.symbol}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Max Supply:</span>
                  <span>21,000,000 {report.symbol}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-400">Current Inflation:</span>
                  <span>{simulatedFundamentalData.tokenomics.inflation_rate}% annually</span>
                </li>
              </ul>
            </div>
            
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm font-medium mb-2">Value Accrual Analysis</h4>
              <p className="text-sm text-gray-300">
                {report.symbol}'s tokenomics model features a fixed maximum supply with a diminishing issuance rate,
                creating natural scarcity. The token serves multiple utilities including network security, transaction fees,
                and store of value. Its stock-to-flow ratio continues to increase, strengthening its monetary premium.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Team Assessment */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaUsers className="text-indigo-400 mr-2" />
            <h3 className="font-medium">Team & Governance</h3>
            <div className="ml-auto">
              {renderScoreStars(simulatedFundamentalData.team.score)}
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Experience</span>
                <span className={getScoreColor(simulatedFundamentalData.team.experience)}>
                  {simulatedFundamentalData.team.experience.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.team.experience)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Track Record</span>
                <span className={getScoreColor(simulatedFundamentalData.team.track_record)}>
                  {simulatedFundamentalData.team.track_record.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.team.track_record)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Transparency</span>
                <span className={getScoreColor(simulatedFundamentalData.team.transparency)}>
                  {simulatedFundamentalData.team.transparency.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.team.transparency)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Community Engagement</span>
                <span className={getScoreColor(simulatedFundamentalData.team.community_engagement)}>
                  {simulatedFundamentalData.team.community_engagement.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.team.community_engagement)}
            </div>
          </div>
          
          <div className="mt-4 bg-[#12141f] p-3 rounded border border-gray-700">
            <p className="text-sm text-gray-300">
              The development ecosystem around {report.symbol} features numerous experienced contributors with strong
              technical backgrounds. The governance model demonstrates high decentralization with a transparent development
              process and active community participation in decision-making. Regular communications and clear roadmaps
              enhance accountability.
            </p>
          </div>
        </div>
        
        {/* Adoption Metrics */}
        <div className="bg-[#1A1C31] rounded-lg p-6">
          <div className="flex items-center mb-4">
            <FaBuilding className="text-indigo-400 mr-2" />
            <h3 className="font-medium">Adoption & Market Position</h3>
            <div className="ml-auto">
              {renderScoreStars(simulatedFundamentalData.adoption.score)}
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Current Usage</span>
                <span className={getScoreColor(simulatedFundamentalData.adoption.current_usage)}>
                  {simulatedFundamentalData.adoption.current_usage.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.adoption.current_usage)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Growth Trend</span>
                <span className={getScoreColor(simulatedFundamentalData.adoption.growth_trend)}>
                  {simulatedFundamentalData.adoption.growth_trend.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.adoption.growth_trend)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Ecosystem Size</span>
                <span className={getScoreColor(simulatedFundamentalData.adoption.ecosystem_size)}>
                  {simulatedFundamentalData.adoption.ecosystem_size.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.adoption.ecosystem_size)}
            </div>
            
            <div>
              <div className="flex justify-between mb-1 text-sm">
                <span>Institutional Adoption</span>
                <span className={getScoreColor(simulatedFundamentalData.adoption.institutional_adoption)}>
                  {simulatedFundamentalData.adoption.institutional_adoption.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.adoption.institutional_adoption)}
            </div>
          </div>
          
          <div className="mt-4 bg-[#12141f] p-3 rounded border border-gray-700">
            <p className="text-sm text-gray-300">
              {report.symbol} has achieved substantial adoption with an expanding ecosystem of applications, services,
              and integrations. Recent institutional adoption trends are particularly promising, with growing
              corporate treasury allocations and financial product offerings. Retail adoption continues to broaden, 
              with increasing user-friendly solutions reducing barriers to entry.
            </p>
          </div>
        </div>
      </div>
      
      {/* Competitive Analysis */}
      <div className="bg-[#1A1C31] rounded-lg p-6">
        <h3 className="font-medium mb-4">Competitive Analysis</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <div className="flex justify-between mb-1 text-sm">
              <span>Market Position</span>
              <span className={getScoreColor(simulatedFundamentalData.competition.market_position)}>
                {simulatedFundamentalData.competition.market_position.toFixed(1)}/5
              </span>
            </div>
            {renderScoreBar(simulatedFundamentalData.competition.market_position)}
            
            <div className="mt-4">
              <div className="flex justify-between mb-1 text-sm">
                <span>Unique Value Proposition</span>
                <span className={getScoreColor(simulatedFundamentalData.competition.unique_value)}>
                  {simulatedFundamentalData.competition.unique_value.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.competition.unique_value)}
            </div>
            
            <div className="mt-4">
              <div className="flex justify-between mb-1 text-sm">
                <span>Competitive Advantage</span>
                <span className={getScoreColor(simulatedFundamentalData.competition.competitive_advantage)}>
                  {simulatedFundamentalData.competition.competitive_advantage.toFixed(1)}/5
                </span>
              </div>
              {renderScoreBar(simulatedFundamentalData.competition.competitive_advantage)}
            </div>
            
            <div className="mt-4">
              <div className="flex justify-between mb-1 text-sm">
                <span>Competitive Threat Level</span>
                <span className={getScoreColor(6 - simulatedFundamentalData.competition.threat_level)}>
                  {simulatedFundamentalData.competition.threat_level.toFixed(1)} (Moderate)
                </span>
              </div>
              {renderScoreBar(6 - simulatedFundamentalData.competition.threat_level)}
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm font-medium mb-2">Competitive Position Summary</h4>
              <p className="text-sm text-gray-300">
                {report.symbol} maintains a dominant position in its primary use case as a store of value and
                settlement network. Its first-mover advantage, brand recognition, security track record, and
                network effects provide significant moats against competitors. Newer protocols offer enhanced
                functionality or scalability but have not yet achieved comparable network security or liquidity.
              </p>
            </div>
            
            <div className="bg-[#12141f] p-3 rounded border border-gray-700">
              <h4 className="text-sm font-medium mb-2">Key Competitors</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <div className="font-medium">Ethereum (ETH)</div>
                  <div className="text-gray-400">Smart contract platform with broader functionality</div>
                </li>
                <li>
                  <div className="font-medium">Solana (SOL)</div>
                  <div className="text-gray-400">High-throughput blockchain with lower fees</div>
                </li>
                <li>
                  <div className="font-medium">Polkadot (DOT)</div>
                  <div className="text-gray-400">Multi-chain interoperability protocol</div>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div className="mt-6">
          <div className="flex items-center space-x-2 text-sm text-gray-400 mb-2">
            <FaInfoCircle />
            <span>Fundamental analysis provides insight into long-term value potential</span>
          </div>
          <p className="text-gray-300">
            {report.symbol}'s fundamental analysis reveals a strong overall position with particular strengths in network
            security, brand recognition, and institutional adoption. The fixed supply model and diminishing inflation rate
            create favorable tokenomics. Development activity remains robust with ongoing improvements to scalability.
            While facing competition from alternative protocols, its network effects and first-mover advantages provide
            significant defensive moats. The strong fundamentals position {report.symbol} well for long-term value accrual.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FundamentalAnalysis;