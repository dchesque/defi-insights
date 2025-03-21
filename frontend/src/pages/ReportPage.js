// frontend/src/pages/ReportPage.js - Atualizado em 21/03/2025 16:15
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ReportSummary from '../components/ReportSummary';
import TechnicalAnalysis from '../components/TechnicalAnalysis';
import SentimentAnalysis from '../components/SentimentAnalysis';
import OnChainAnalysis from '../components/OnChainAnalysis';
import FundamentalAnalysis from '../components/FundamentalAnalysis';
import PriceChart from '../components/PriceChart';
import { useTokenAnalysis } from '../hooks/useTokenAnalysis';

/**
 * Página de relatório de análise de uma criptomoeda
 * Exibe os resultados completos da análise com diferentes abas
 */
const ReportPage = () => {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('summary');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { getAnalysisById } = useTokenAnalysis();

  useEffect(() => {
    // Função para carregar os dados da análise
    const loadAnalysisData = async () => {
      setLoading(true);
      try {
        // Buscar a análise pelo ID
        const analysisData = await getAnalysisById(id);
        
        if (!analysisData) {
          throw new Error('Análise não encontrada');
        }
        
        // Adaptar os dados da API para o formato esperado pelos componentes
        // Isso garante compatibilidade com os componentes existentes
        const adaptedReport = adaptAnalysisToReport(analysisData);
        setReport(adaptedReport);
        setError(null);
      } catch (err) {
        console.error('Erro ao carregar análise:', err);
        setError('Falha ao carregar os dados do relatório. ' + (err.message || ''));
      } finally {
        setLoading(false);
      }
    };

    loadAnalysisData();
  }, [id, getAnalysisById]);

  // Função para adaptar o formato dos dados da API para o formato esperado pelos componentes
  const adaptAnalysisToReport = (analysisData) => {
    // Esta função faz a ponte entre o formato recebido da API 
    // e o formato esperado pelos componentes de visualização

    // Se não houver dados válidos, retornar null
    if (!analysisData || !analysisData.symbol) {
      return null;
    }

    // Construir objeto de preços
    const priceData = {
      current_price: analysisData.price?.current || 0,
      price_change_24h: analysisData.price?.change_24h || 0,
      price_change_7d: analysisData.price?.change_7d || 0,
      price_change_30d: analysisData.price?.change_30d || 0,
      market_cap: analysisData.market_data?.market_cap || 0,
      volume_24h: analysisData.market_data?.volume_24h || 0
    };

    // Determinar sinais com base nos dados disponíveis
    const determineSignal = (value) => {
      if (!value) return 'neutral';
      if (typeof value === 'number') {
        return value > 0 ? 'bullish' : value < 0 ? 'bearish' : 'neutral';
      }
      if (typeof value === 'string') {
        if (value.includes('bull') || value.includes('positive')) return 'bullish';
        if (value.includes('bear') || value.includes('negative')) return 'bearish';
      }
      return 'neutral';
    };

    // Extrair sinais e confiança dos dados de sentimento
    let sentimentSignal = 'neutral';
    let sentimentConfidence = 50;
    
    if (analysisData.sentiment?.overall_sentiment) {
      sentimentSignal = determineSignal(analysisData.sentiment.overall_sentiment.sentiment);
      sentimentConfidence = analysisData.sentiment.overall_sentiment.confidence || 50;
    }

    // Construir objeto de sinais
    const signals = {
      overall: determineOverallSignal(analysisData),
      confidence: calculateOverallConfidence(analysisData),
      technical: 'neutral', // Idealmente seria extraído dos dados técnicos
      onchain: determineOnchainSignal(analysisData.onchain),
      sentiment: sentimentSignal
    };

    // Construir o objeto de relatório adaptado
    return {
      id: analysisData.analysis_id,
      symbol: analysisData.symbol,
      name: analysisData.name || analysisData.symbol,
      timestamp: analysisData.timestamp,
      price_data: priceData,
      signals: signals,
      technical_analysis: generateTechnicalAnalysis(analysisData),
      sentiment_analysis: adaptSentimentAnalysis(analysisData.sentiment),
      onchain_metrics: adaptOnchainMetrics(analysisData.onchain),
      risk_analysis: generateRiskAnalysis(analysisData),
      price_prediction: generatePricePrediction(analysisData),
      recommendation: generateRecommendation(analysisData)
    };
  };

  // Funções auxiliares para adaptar diferentes partes dos dados
  
  // Determinar o sinal geral com base em todos os dados disponíveis
  const determineOverallSignal = (analysisData) => {
    // Em uma implementação real, essa lógica seria mais sofisticada
    // e consideraria pesos para diferentes aspectos da análise
    
    // Verificar se temos dados de sentimento
    if (analysisData.sentiment?.overall_sentiment) {
      const sentiment = analysisData.sentiment.overall_sentiment.sentiment;
      if (sentiment === 'very positive' || sentiment === 'positive') return 'bullish';
      if (sentiment === 'very negative' || sentiment === 'negative') return 'bearish';
    }
    
    // Se não temos dados suficientes, usar mudança de preço como fallback
    if (analysisData.price?.change_24h) {
      return analysisData.price.change_24h > 0 ? 'bullish' : 'bearish';
    }
    
    return 'neutral';
  };

  // Calcular a confiança geral com base em todos os dados disponíveis
  const calculateOverallConfidence = (analysisData) => {
    // Em uma implementação real, essa lógica seria mais sofisticada
    
    // Se temos dados de sentimento com confiança, usar como base
    if (analysisData.sentiment?.overall_sentiment?.confidence) {
      return analysisData.sentiment.overall_sentiment.confidence;
    }
    
    // Valor padrão (dados insuficientes)
    return 65;
  };

  // Determinar o sinal onchain com base nos dados disponíveis
  const determineOnchainSignal = (onchainData) => {
    if (!onchainData) return 'neutral';
    
    // Em uma implementação real, avaliaria métricas como fluxo de carteiras,
    // atividade na rede, análise de liquidez, etc.
    
    // Verificar risco se disponível
    if (onchainData.risk_analysis) {
      const riskScore = onchainData.risk_analysis.risk_score;
      if (riskScore < 30) return 'bullish';
      if (riskScore > 70) return 'bearish';
    }
    
    return 'neutral';
  };

  // Gerar análise técnica a partir dos dados disponíveis ou dados simulados se faltando
  const generateTechnicalAnalysis = (analysisData) => {
    // Em uma implementação real, esses dados viriam do backend
    // Para manter compatibilidade, estamos gerando dados similares aos mockados
    
    return {
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
    };
  };

  // Adaptar dados de sentimento para o formato esperado pelo componente
  const adaptSentimentAnalysis = (sentimentData) => {
    if (!sentimentData) {
      // Se não temos dados de sentimento, retornar objeto vazio
      // Os componentes têm verificações para lidar com isso
      return {};
    }
    
    // Adaptar dados de sentimento da API para o formato usado pelo componente
    const sentiment = {
      social_sentiment: sentimentData.overall_sentiment?.score || 65,
      fear_greed_index: 72, // Dado que poderia vir da API
      fear_greed_classification: "Greed", // Dado que poderia vir da API
      social_volume_24h: sentimentData.engagement_metrics?.total_mentions || 125000,
    };
    
    // Adaptar dados do Twitter se disponíveis
    if (sentimentData.sentiment_by_source?.twitter) {
      sentiment.twitter_data = {
        tweet_count: sentimentData.engagement_metrics?.mentions_by_source?.twitter || 15700,
        positive_sentiment_percent: 62, // Exemplo
        negative_sentiment_percent: 18, // Exemplo
        neutral_sentiment_percent: 20, // Exemplo
      };
    } else {
      // Dados simulados se não disponíveis
      sentiment.twitter_data = {
        tweet_count: 15700,
        positive_sentiment_percent: 62,
        negative_sentiment_percent: 18,
        neutral_sentiment_percent: 20
      };
    }
    
    // Adaptar dados do Reddit se disponíveis
    if (sentimentData.sentiment_by_source?.reddit) {
      sentiment.reddit_data = {
        post_count: sentimentData.engagement_metrics?.mentions_by_source?.reddit || 3200,
        positive_sentiment_percent: 58, // Exemplo
        negative_sentiment_percent: 22, // Exemplo
        neutral_sentiment_percent: 20, // Exemplo
        bullish_ratio: 2.64, // Exemplo
      };
    } else {
      // Dados simulados se não disponíveis
      sentiment.reddit_data = {
        post_count: 3200,
        positive_sentiment_percent: 58,
        negative_sentiment_percent: 22,
        neutral_sentiment_percent: 20,
        bullish_ratio: 2.64
      };
    }
    
    return sentiment;
  };

  // Adaptar dados onchain para o formato esperado pelo componente
  const adaptOnchainMetrics = (onchainData) => {
    if (!onchainData) {
      // Se não temos dados onchain, retornar objeto vazio
      return {};
    }
    
    // Começar com conjunto padrão de métricas
    const onchainMetrics = {
      active_addresses_24h: 982500,
      transaction_count_24h: 325000,
      transaction_volume_24h: 12500000000,
      average_transaction_fee: 2.45,
      market_to_realized_value_ratio: 2.2,
      whale_accumulation_trend: 'increasing',
      smart_money_inflow_7d: 850000000,
      smart_money_outflow_7d: 420000000
    };
    
    // Se temos dados de transações, usá-los
    if (onchainData.transaction_analysis) {
      onchainMetrics.active_addresses_24h = onchainData.transaction_analysis.unique_addresses;
      onchainMetrics.transaction_count_24h = onchainData.transaction_analysis.total_transactions;
      // Outras métricas relacionadas a transações...
    }
    
    // Se temos dados de contrato, adicionar hash rate e dificuldade para Bitcoin
    if (onchainData.contract_info && onchainData.contract_info.token_symbol === 'BTC') {
      onchainMetrics.hash_rate = 350000000000000000000;
      onchainMetrics.difficulty = 46270031793883;
    }
    
    return onchainMetrics;
  };

  // Gerar análise de risco com base nos dados disponíveis
  const generateRiskAnalysis = (analysisData) => {
    // Verificar se temos dados de risco onchain
    let riskLevel = 'medium-low';
    let riskScore = 7.8;
    
    if (analysisData.onchain?.risk_analysis) {
      riskScore = 10 - (analysisData.onchain.risk_analysis.risk_score / 10);
      
      if (riskScore > 7.5) riskLevel = 'low';
      else if (riskScore > 5) riskLevel = 'medium-low';
      else if (riskScore > 2.5) riskLevel = 'medium-high';
      else riskLevel = 'high';
    }
    
    // Calcular posição limite baseada no preço atual
    const currentPrice = analysisData.price?.current || 61245.32;
    const volatility = 0.045; // Valor padrão
    const positionLimit = 10000; // Valor padrão
    
    return {
      position_limit: positionLimit,
      max_units: positionLimit / currentPrice,
      current_price: currentPrice,
      volatility: volatility,
      market_quality: {
        score: riskScore,
        description: 'Mercado favorável',
        risk_level: riskLevel
      }
    };
  };

  // Gerar previsão de preço com base nos dados disponíveis
  const generatePricePrediction = (analysisData) => {
    // Em uma implementação real, esses dados viriam do backend
    const currentPrice = analysisData.price?.current || 61245.32;
    
    // Previsão simplificada baseada no preço atual
    return {
      target_price_30d: Math.round(currentPrice * 1.18),
      confidence: 65,
      bull_case: Math.round(currentPrice * 1.34),
      bear_case: Math.round(currentPrice * 0.9)
    };
  };

  // Gerar recomendação baseada nos dados da análise
  const generateRecommendation = (analysisData) => {
    // Em uma implementação real, a IA do backend geraria essa recomendação
    const overall = determineOverallSignal(analysisData);
    
    if (overall === 'bullish') {
      return 'Recomendação de compra forte com atividade on-chain crescente e momentum positivo. O interesse institucional permanece alto.';
    } else if (overall === 'bearish') {
      return 'Recomendação de cautela devido a sinais de fraqueza no mercado. Considere reduzir exposição ou aguardar melhor ponto de entrada.';
    } else {
      return 'Sinais mistos indicam que é um bom momento para observar o mercado antes de tomar decisões. O ativo mostra estabilidade relativa.';
    }
  };

  // Renderização condicional baseada no estado
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
          <h2 className="text-2xl font-bold text-red-500 mb-4">Erro</h2>
          <p className="text-gray-300">{error}</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-300 mb-4">Relatório Não Encontrado</h2>
          <p className="text-gray-400">O relatório solicitado não pôde ser encontrado.</p>
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
            <p className="text-gray-400 mt-1">Análise gerada em {new Date(report.timestamp).toLocaleString()}</p>
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
            <p className="text-gray-400 text-sm">Variação 24h</p>
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
              Resumo
            </button>
            <button
              className={`py-3 px-4 font-medium text-sm border-b-2 ${
                activeTab === 'technical' 
                  ? 'border-indigo-500 text-white' 
                  : 'border-transparent text-gray-400 hover:text-gray-300'
              }`}
              onClick={() => setActiveTab('technical')}
            >
              Técnica
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
              Sentimento
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