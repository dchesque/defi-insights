// frontend/src/pages/DashboardPage.js - Criado em 21/03/2025 16:35
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaPlus, FaChartLine, FaWallet, FaBell, FaSearch, FaClock, FaArrowUp, FaArrowDown } from 'react-icons/fa';
import { useAuthContext } from '../App';
import { useTokenAnalysis } from '../hooks/useTokenAnalysis';

/**
 * Página de dashboard do usuário
 * Exibe resumo das análises recentes e acesso às funcionalidades principais
 */
const DashboardPage = () => {
  const { user } = useAuthContext();
  const { getUserAnalyses, loading, error } = useTokenAnalysis();
  const [analyses, setAnalyses] = useState([]);
  const [loadingAnalyses, setLoadingAnalyses] = useState(true);
  const navigate = useNavigate();

  // Efeito para carregar análises do usuário
  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        setLoadingAnalyses(true);
        const userAnalyses = await getUserAnalyses();
        setAnalyses(userAnalyses);
      } catch (err) {
        console.error('Erro ao carregar análises:', err);
      } finally {
        setLoadingAnalyses(false);
      }
    };

    fetchAnalyses();
  }, [getUserAnalyses]);

  // Função para formatar data relativa (ex: "há 2 dias")
  const formatRelativeTime = (timestamp) => {
    const now = new Date();
    const analysisDate = new Date(timestamp);
    const diffInSeconds = Math.floor((now - analysisDate) / 1000);
    
    if (diffInSeconds < 60) {
      return 'Agora mesmo';
    }
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
      return `Há ${diffInMinutes} ${diffInMinutes === 1 ? 'minuto' : 'minutos'}`;
    }
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
      return `Há ${diffInHours} ${diffInHours === 1 ? 'hora' : 'horas'}`;
    }
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 30) {
      return `Há ${diffInDays} ${diffInDays === 1 ? 'dia' : 'dias'}`;
    }
    
    const diffInMonths = Math.floor(diffInDays / 30);
    return `Há ${diffInMonths} ${diffInMonths === 1 ? 'mês' : 'meses'}`;
  };

  // Função para determinar a cor do indicador de sentimento
  const getSentimentColor = (sentiment) => {
    if (!sentiment) return 'text-gray-400';
    
    if (sentiment.includes('positive') || sentiment.includes('bull')) {
      return 'text-green-500';
    }
    
    if (sentiment.includes('negative') || sentiment.includes('bear')) {
      return 'text-red-500';
    }
    
    return 'text-yellow-500';
  };

  // Função para obter ícone de sentimento
  const getSentimentIcon = (sentiment) => {
    if (!sentiment) return <FaChartLine className="text-gray-400" />;
    
    if (sentiment.includes('positive') || sentiment.includes('bull')) {
      return <FaArrowUp className="text-green-500" />;
    }
    
    if (sentiment.includes('negative') || sentiment.includes('bear')) {
      return <FaArrowDown className="text-red-500" />;
    }
    
    return <FaChartLine className="text-yellow-500" />;
  };

  return (
    <div className="py-8 px-4 md:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Cabeçalho */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Olá, {user?.name || 'Investidor'}!
          </h1>
          <p className="text-gray-400">
            Bem-vindo ao seu dashboard de análises cripto com IA
          </p>
        </div>
        
        {/* Cards de Ações Rápidas */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mb-8">
          <div 
            className="bg-[#1A1C31] rounded-lg p-6 hover:bg-[#22263E] transition-colors cursor-pointer"
            onClick={() => navigate('/')}
          >
            <div className="bg-indigo-900/30 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <FaPlus className="text-indigo-400" />
            </div>
            <h3 className="font-semibold text-lg mb-1">Nova Análise</h3>
            <p className="text-gray-400 text-sm">
              Analisar uma nova criptomoeda
            </p>
          </div>
          
          <div 
            className="bg-[#1A1C31] rounded-lg p-6 hover:bg-[#22263E] transition-colors cursor-pointer"
            onClick={() => navigate('/portfolio')}
          >
            <div className="bg-green-900/30 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <FaWallet className="text-green-400" />
            </div>
            <h3 className="font-semibold text-lg mb-1">Portfólio</h3>
            <p className="text-gray-400 text-sm">
              Gerenciar seus investimentos
            </p>
          </div>
          
          <div className="bg-[#1A1C31] rounded-lg p-6 hover:bg-[#22263E] transition-colors cursor-pointer">
            <div className="bg-purple-900/30 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <FaChartLine className="text-purple-400" />
            </div>
            <h3 className="font-semibold text-lg mb-1">Mercados</h3>
            <p className="text-gray-400 text-sm">
              Explorar tendências de mercado
            </p>
          </div>
          
          <div className="bg-[#1A1C31] rounded-lg p-6 hover:bg-[#22263E] transition-colors cursor-pointer">
            <div className="bg-blue-900/30 rounded-full w-12 h-12 flex items-center justify-center mb-4">
              <FaBell className="text-blue-400" />
            </div>
            <h3 className="font-semibold text-lg mb-1">Alertas</h3>
            <p className="text-gray-400 text-sm">
              Configurar notificações
            </p>
            <div className="mt-3 inline-block px-2 py-1 bg-blue-900/30 text-blue-400 text-xs rounded">
              Em breve
            </div>
          </div>
        </div>
        
        {/* Pesquisa de Análises (opcional) */}
        <div className="mb-8">
          <div className="relative max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FaSearch className="text-gray-500" />
            </div>
            <input
              type="text"
              placeholder="Buscar análises por símbolo ou nome..."
              className="pl-10 w-full rounded-md bg-[#1A1C31] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>
        
        {/* Análises Recentes */}
        <div className="bg-[#1A1C31] rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">Análises Recentes</h2>
            <Link 
              to="/" 
              className="text-indigo-400 hover:text-indigo-300 text-sm flex items-center"
            >
              <FaPlus className="mr-1" />
              Nova Análise
            </Link>
          </div>
          
          {loadingAnalyses ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
          ) : analyses && analyses.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left text-gray-400 border-b border-gray-800">
                    <th className="pb-3 font-medium">Criptomoeda</th>
                    <th className="pb-3 font-medium">Preço</th>
                    <th className="pb-3 font-medium">Sentiment</th>
                    <th className="pb-3 font-medium">Data</th>
                    <th className="pb-3 font-medium text-right">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {analyses.map((analysis) => (
                    <tr 
                      key={analysis.analysis_id} 
                      className="border-b border-gray-800 hover:bg-[#22263E]"
                    >
                      <td className="py-4">
                        <div className="flex items-center">
                          {/* Aqui poderia ter um ícone/logo da criptomoeda */}
                          <div>
                            <div className="font-medium">{analysis.name || analysis.symbol}</div>
                            <div className="text-gray-400 text-sm">{analysis.symbol}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4">
                        {analysis.price?.current ? (
                          <div>
                            <div className="font-medium">${analysis.price.current.toLocaleString()}</div>
                            <div className={`text-sm ${
                              (analysis.price.change_24h || 0) >= 0 
                                ? 'text-green-500' 
                                : 'text-red-500'
                            }`}>
                              {(analysis.price.change_24h || 0) >= 0 ? '+' : ''}
                              {(analysis.price.change_24h || 0)}%
                            </div>
                          </div>
                        ) : (
                          <span className="text-gray-400">N/A</span>
                        )}
                      </td>
                      <td className="py-4">
                        <div className="flex items-center">
                          {getSentimentIcon(analysis.sentiment?.overall_sentiment?.sentiment)}
                          <span 
                            className={`ml-2 ${getSentimentColor(analysis.sentiment?.overall_sentiment?.sentiment)}`}
                          >
                            {analysis.sentiment?.overall_sentiment?.sentiment || 'Neutro'}
                          </span>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-center text-gray-400 text-sm">
                          <FaClock className="mr-2" />
                          {formatRelativeTime(analysis.timestamp)}
                        </div>
                      </td>
                      <td className="py-4 text-right">
                        <Link 
                          to={`/report/${analysis.analysis_id}`}
                          className="inline-block px-3 py-1 bg-indigo-900/30 text-indigo-400 text-sm rounded hover:bg-indigo-700/30"
                        >
                          Ver Relatório
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">
                Você ainda não tem análises de criptomoedas.
              </p>
              <Link 
                to="/"
                className="inline-block px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
              >
                Criar Primeira Análise
              </Link>
            </div>
          )}
        </div>
        
        {/* Estatísticas e Dicas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="col-span-1 md:col-span-2 bg-[#1A1C31] rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Estatísticas do Mercado</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                <div className="text-gray-400 text-sm mb-1">Fear & Greed Index</div>
                <div className="text-xl font-bold text-green-500">65</div>
                <div className="text-green-400 text-sm">Greed</div>
              </div>
              
              <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                <div className="text-gray-400 text-sm mb-1">Dominância BTC</div>
                <div className="text-xl font-bold">52.4%</div>
                <div className="text-green-500 text-sm">+0.8%</div>
              </div>
              
              <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                <div className="text-gray-400 text-sm mb-1">Market Cap Total</div>
                <div className="text-xl font-bold">$2.45T</div>
                <div className="text-green-500 text-sm">+1.2%</div>
              </div>
              
              <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                <div className="text-gray-400 text-sm mb-1">Volume 24h</div>
                <div className="text-xl font-bold">$98.7B</div>
                <div className="text-red-500 text-sm">-3.5%</div>
              </div>
            </div>
          </div>
          
          <div className="bg-[#1A1C31] rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Dicas Rápidas</h2>
            
            <div className="space-y-4">
              <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                <div className="text-sm mb-2">
                  <span className="text-indigo-400 font-medium">Análise on-chain</span> oferece insights valiosos sobre fluxos de carteira e atividade de rede.
                </div>
              </div>
              
              <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                <div className="text-sm mb-2">
                  <span className="text-indigo-400 font-medium">Relatórios de sentimento</span> podem antecipar movimentos de preço em 24-48 horas.
                </div>
              </div>
              
              <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                <div className="text-sm mb-2">
                  <span className="text-indigo-400 font-medium">Diversificação</span> entre diferentes classes de ativos cripto pode reduzir riscos.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;