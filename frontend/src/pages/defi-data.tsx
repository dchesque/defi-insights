import { useState, useEffect } from 'react';
import Head from 'next/head';
import api from '../lib/api';

export default function DefiData() {
  // Estados para os diferentes tipos de dados
  const [overview, setOverview] = useState<any>(null);
  const [tvlData, setTvlData] = useState<any>(null);
  const [yieldData, setYieldData] = useState<any>(null);
  const [fearGreedIndex, setFearGreedIndex] = useState<any>(null);
  const [marketSentiment, setMarketSentiment] = useState<any>(null);
  const [selectedProtocol, setSelectedProtocol] = useState('');
  const [protocolData, setProtocolData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // Buscar dados de visão geral ao carregar a página
  useEffect(() => {
    fetchOverview();
    fetchFearGreedIndex();
  }, []);

  // Buscar visão geral dos dados DeFi
  const fetchOverview = async () => {
    try {
      setIsLoading(true);
      setError('');
      const data = await api.defi.getOverview();
      setOverview(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar dados de visão geral');
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar dados de TVL
  const fetchTvlData = async () => {
    if (tvlData) return; // Evitar buscar novamente se já tivermos os dados
    
    try {
      setIsLoading(true);
      setError('');
      const data = await api.defi.getTvl();
      setTvlData(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar dados de TVL');
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar dados de rendimentos
  const fetchYieldData = async () => {
    if (yieldData) return; // Evitar buscar novamente se já tivermos os dados
    
    try {
      setIsLoading(true);
      setError('');
      const data = await api.defi.getYields();
      setYieldData(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar dados de rendimentos');
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar índice de medo e ganância
  const fetchFearGreedIndex = async () => {
    try {
      setIsLoading(true);
      const data = await api.defi.getFearGreedIndex();
      setFearGreedIndex(data);
    } catch (err: any) {
      console.error('Erro ao buscar índice de medo e ganância:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar sentimento de mercado
  const fetchMarketSentiment = async () => {
    if (marketSentiment) return; // Evitar buscar novamente se já tivermos os dados
    
    try {
      setIsLoading(true);
      setError('');
      const data = await api.defi.getMarketSentiment();
      setMarketSentiment(data);
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar sentimento de mercado');
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar dados de um protocolo específico
  const fetchProtocolData = async () => {
    if (!selectedProtocol) {
      setError('Selecione um protocolo');
      return;
    }
    
    try {
      setIsLoading(true);
      setError('');
      const data = await api.defi.getProtocol(selectedProtocol);
      setProtocolData(data);
    } catch (err: any) {
      setError(err.message || `Erro ao buscar dados do protocolo ${selectedProtocol}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Mudar guia ativa e carregar os dados correspondentes
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setError('');
    
    switch (tab) {
      case 'overview':
        fetchOverview();
        break;
      case 'tvl':
        fetchTvlData();
        break;
      case 'yields':
        fetchYieldData();
        break;
      case 'protocol':
        setProtocolData(null);
        break;
      case 'sentiment':
        fetchMarketSentiment();
        break;
    }
  };

  // Formatar valor como moeda
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value);
  };

  // Formatar valor de TVL para melhor legibilidade
  const formatTVL = (value: number) => {
    if (value >= 1_000_000_000) {
      return `$${(value / 1_000_000_000).toFixed(2)} bilhões`;
    }
    if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toFixed(2)} milhões`;
    }
    return formatCurrency(value);
  };

  // Renderiza a classe CSS para o indicador de Fear & Greed
  const getFearGreedClass = (value: number) => {
    if (value <= 20) return 'bg-red-600'; // Medo extremo
    if (value <= 40) return 'bg-orange-500'; // Medo
    if (value <= 60) return 'bg-yellow-500'; // Neutro
    if (value <= 80) return 'bg-green-500'; // Ganância
    return 'bg-green-700'; // Ganância extrema
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Head>
        <title>Dados DeFi | DeFi Insight</title>
        <meta name="description" content="Dados e métricas do ecossistema DeFi" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Dados DeFi</h1>

        {/* Índice de Medo e Ganância */}
        {fearGreedIndex && (
          <div className="mb-8 p-6 bg-gray-800 rounded-lg">
            <h2 className="text-2xl font-bold mb-4">Índice de Medo e Ganância</h2>
            <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
              <div className="text-center">
                <div className="text-5xl font-bold mb-2">{fearGreedIndex.value}</div>
                <div className="text-xl">{fearGreedIndex.value_classification}</div>
              </div>
              
              <div className="w-full sm:w-2/3">
                <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${getFearGreedClass(fearGreedIndex.value)}`} 
                    style={{ width: `${fearGreedIndex.value}%` }}
                  ></div>
                </div>
                <div className="flex justify-between mt-1 text-sm text-gray-400">
                  <span>Medo Extremo</span>
                  <span>Medo</span>
                  <span>Neutro</span>
                  <span>Ganância</span>
                  <span>Ganância Extrema</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navegação por abas */}
        <div className="mb-8">
          <div className="flex flex-wrap border-b border-gray-700">
            <button
              onClick={() => handleTabChange('overview')}
              className={`px-4 py-2 ${activeTab === 'overview' ? 'border-b-2 border-blue-500 text-blue-400' : 'text-gray-400 hover:text-white'}`}
            >
              Visão Geral
            </button>
            <button
              onClick={() => handleTabChange('tvl')}
              className={`px-4 py-2 ${activeTab === 'tvl' ? 'border-b-2 border-blue-500 text-blue-400' : 'text-gray-400 hover:text-white'}`}
            >
              TVL Global
            </button>
            <button
              onClick={() => handleTabChange('yields')}
              className={`px-4 py-2 ${activeTab === 'yields' ? 'border-b-2 border-blue-500 text-blue-400' : 'text-gray-400 hover:text-white'}`}
            >
              Rendimentos
            </button>
            <button
              onClick={() => handleTabChange('protocol')}
              className={`px-4 py-2 ${activeTab === 'protocol' ? 'border-b-2 border-blue-500 text-blue-400' : 'text-gray-400 hover:text-white'}`}
            >
              Protocolo Específico
            </button>
            <button
              onClick={() => handleTabChange('sentiment')}
              className={`px-4 py-2 ${activeTab === 'sentiment' ? 'border-b-2 border-blue-500 text-blue-400' : 'text-gray-400 hover:text-white'}`}
            >
              Sentimento de Mercado
            </button>
          </div>
        </div>

        {/* Indicador de carregamento */}
        {isLoading && (
          <div className="flex justify-center my-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        )}

        {/* Mensagem de erro */}
        {error && (
          <div className="my-8 p-4 bg-red-800/50 border border-red-600 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {/* Conteúdo da aba Visão Geral */}
        {activeTab === 'overview' && overview && !isLoading && (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3">TVL Total</h3>
                <p className="text-3xl font-bold text-blue-400">{formatTVL(overview.tvl)}</p>
              </div>
              
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3">Protocolos</h3>
                <p className="text-3xl font-bold text-purple-400">{overview.protocols_count}</p>
              </div>
              
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-3">Sentimento</h3>
                <p className="text-3xl font-bold text-yellow-400">{overview.fear_greed_index?.classification || 'N/A'}</p>
              </div>
            </div>
            
            {overview.top_protocols && (
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-xl font-semibold mb-4">Top Protocolos por TVL</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left border-b border-gray-700">
                        <th className="py-2 px-4">#</th>
                        <th className="py-2 px-4">Protocolo</th>
                        <th className="py-2 px-4">TVL</th>
                        <th className="py-2 px-4">Categoria</th>
                        <th className="py-2 px-4">Variação 1d</th>
                      </tr>
                    </thead>
                    <tbody>
                      {overview.top_protocols.map((protocol: any, index: number) => (
                        <tr key={protocol.name} className="border-b border-gray-700 hover:bg-gray-700">
                          <td className="py-3 px-4">{index + 1}</td>
                          <td className="py-3 px-4 font-medium">{protocol.name}</td>
                          <td className="py-3 px-4">{formatTVL(protocol.tvl)}</td>
                          <td className="py-3 px-4">{protocol.category}</td>
                          <td className={`py-3 px-4 ${protocol.change_1d > 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {protocol.change_1d > 0 ? '+' : ''}{protocol.change_1d?.toFixed(2)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Conteúdo da aba TVL Global */}
        {activeTab === 'tvl' && tvlData && !isLoading && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Histórico de TVL Global</h3>
            
            {/* Aqui você poderia adicionar um gráfico com os dados */}
            <div className="mb-4">
              <p className="text-gray-300">TVL Atual: {formatTVL(tvlData.currentTvl)}</p>
              <p className="text-gray-300">Pico Histórico: {formatTVL(tvlData.allTimeHigh)}</p>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b border-gray-700">
                    <th className="py-2 px-4">Data</th>
                    <th className="py-2 px-4">TVL</th>
                    <th className="py-2 px-4">Variação</th>
                  </tr>
                </thead>
                <tbody>
                  {tvlData.tvlHistory && tvlData.tvlHistory.map((entry: any) => (
                    <tr key={entry.date} className="border-b border-gray-700 hover:bg-gray-700">
                      <td className="py-3 px-4">{entry.date}</td>
                      <td className="py-3 px-4">{formatTVL(entry.tvl)}</td>
                      <td className={`py-3 px-4 ${entry.change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {entry.change > 0 ? '+' : ''}{entry.change?.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Conteúdo da aba Rendimentos */}
        {activeTab === 'yields' && yieldData && !isLoading && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Melhores Rendimentos</h3>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b border-gray-700">
                    <th className="py-2 px-4">Pool</th>
                    <th className="py-2 px-4">Protocolo</th>
                    <th className="py-2 px-4">Blockchain</th>
                    <th className="py-2 px-4">APY</th>
                    <th className="py-2 px-4">TVL</th>
                  </tr>
                </thead>
                <tbody>
                  {yieldData.map((pool: any) => (
                    <tr key={pool.id} className="border-b border-gray-700 hover:bg-gray-700">
                      <td className="py-3 px-4 font-medium">{pool.name}</td>
                      <td className="py-3 px-4">{pool.project}</td>
                      <td className="py-3 px-4">{pool.chain}</td>
                      <td className="py-3 px-4 text-green-400">{pool.apy.toFixed(2)}%</td>
                      <td className="py-3 px-4">{formatTVL(pool.tvl)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Conteúdo da aba Protocolo Específico */}
        {activeTab === 'protocol' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Pesquisar Protocolo</h3>
            
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <input
                type="text"
                value={selectedProtocol}
                onChange={(e) => setSelectedProtocol(e.target.value.toLowerCase())}
                placeholder="Nome do protocolo (ex: aave, uniswap)"
                className="w-full sm:w-2/3 px-4 py-3 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500"
              />
              
              <button
                onClick={fetchProtocolData}
                disabled={isLoading || !selectedProtocol}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Buscar Dados
              </button>
            </div>
            
            {protocolData && (
              <div className="mt-6">
                <div className="flex items-center mb-4">
                  {protocolData.logo && (
                    <img 
                      src={protocolData.logo} 
                      alt={protocolData.name} 
                      className="w-10 h-10 mr-3 rounded-full"
                    />
                  )}
                  <h4 className="text-2xl font-bold">{protocolData.name}</h4>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h5 className="text-lg font-medium mb-2">Informações Gerais</h5>
                    <ul className="space-y-2">
                      <li><span className="text-gray-400">Categoria:</span> {protocolData.category}</li>
                      <li><span className="text-gray-400">TVL:</span> {formatTVL(protocolData.tvl)}</li>
                      <li><span className="text-gray-400">Variação 1d:</span> <span className={protocolData.change_1d > 0 ? 'text-green-400' : 'text-red-400'}>{protocolData.change_1d?.toFixed(2)}%</span></li>
                      <li><span className="text-gray-400">Variação 7d:</span> <span className={protocolData.change_7d > 0 ? 'text-green-400' : 'text-red-400'}>{protocolData.change_7d?.toFixed(2)}%</span></li>
                    </ul>
                  </div>
                  
                  <div>
                    <h5 className="text-lg font-medium mb-2">Chains Suportadas</h5>
                    <div className="flex flex-wrap gap-2">
                      {protocolData.chains?.map((chain: string) => (
                        <span key={chain} className="px-3 py-1 bg-gray-700 rounded-full text-sm">{chain}</span>
                      ))}
                    </div>
                  </div>
                </div>
                
                {protocolData.description && (
                  <div className="mb-6">
                    <h5 className="text-lg font-medium mb-2">Descrição</h5>
                    <p className="text-gray-300">{protocolData.description}</p>
                  </div>
                )}
                
                {protocolData.tvlHistory && (
                  <div>
                    <h5 className="text-lg font-medium mb-2">Histórico de TVL</h5>
                    {/* Aqui você poderia adicionar um gráfico */}
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="text-left border-b border-gray-700">
                            <th className="py-2 px-4">Data</th>
                            <th className="py-2 px-4">TVL</th>
                          </tr>
                        </thead>
                        <tbody>
                          {protocolData.tvlHistory.slice(0, 7).map((entry: any) => (
                            <tr key={entry.date} className="border-b border-gray-700 hover:bg-gray-700">
                              <td className="py-3 px-4">{entry.date}</td>
                              <td className="py-3 px-4">{formatTVL(entry.tvl)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Conteúdo da aba Sentimento de Mercado */}
        {activeTab === 'sentiment' && marketSentiment && !isLoading && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Sentimento de Mercado</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gray-700 p-4 rounded-lg">
                <h4 className="text-lg font-medium mb-3">Sentimento Atual</h4>
                <p className="text-2xl font-bold">
                  {marketSentiment.current_sentiment}
                </p>
                <p className="text-gray-300 mt-2">
                  Baseado em dados de redes sociais, notícias e métricas on-chain.
                </p>
              </div>
              
              <div className="bg-gray-700 p-4 rounded-lg">
                <h4 className="text-lg font-medium mb-3">Tendência</h4>
                <p className={`text-2xl font-bold ${
                  marketSentiment.trend === 'positiva' ? 'text-green-400' : 
                  marketSentiment.trend === 'negativa' ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  {marketSentiment.trend}
                </p>
                <p className="text-gray-300 mt-2">
                  Comparado às últimas 24 horas.
                </p>
              </div>
            </div>
            
            <div className="mb-6">
              <h4 className="text-lg font-medium mb-3">Sentimento por Fonte</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {marketSentiment.sentiment_by_source && Object.entries(marketSentiment.sentiment_by_source).map(([source, sentiment]: [string, any]) => (
                  <div key={source} className="bg-gray-700 p-4 rounded-lg">
                    <h5 className="font-medium mb-2 capitalize">{source}</h5>
                    <p className={`text-xl font-bold ${
                      sentiment > 60 ? 'text-green-400' : 
                      sentiment < 40 ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {sentiment}%
                    </p>
                  </div>
                ))}
              </div>
            </div>
            
            {marketSentiment.recent_events && (
              <div>
                <h4 className="text-lg font-medium mb-3">Eventos Recentes que Afetam o Sentimento</h4>
                <ul className="space-y-2">
                  {marketSentiment.recent_events.map((event: any, index: number) => (
                    <li key={index} className="p-3 bg-gray-700 rounded-lg">
                      <div className="font-medium">{event.title}</div>
                      <div className="text-gray-300 text-sm mt-1">{event.description}</div>
                      <div className="flex justify-between mt-2">
                        <span className="text-sm text-gray-400">{event.date}</span>
                        <span className={`text-sm ${
                          event.impact === 'positivo' ? 'text-green-400' : 
                          event.impact === 'negativo' ? 'text-red-400' : 'text-yellow-400'
                        }`}>
                          Impacto: {event.impact}
                        </span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
} 