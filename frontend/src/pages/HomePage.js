// frontend/src/pages/HomePage.js - Atualizado em 21/03/2025 16:10
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CryptoForm from '../components/CryptoForm';
import ProgressModal from '../components/ProgressModal';
import { useTokenAnalysis } from '../hooks/useTokenAnalysis';

/**
 * Página inicial da aplicação BaseMind.ai
 * Contém formulário para análise de criptomoedas e informações sobre o serviço
 */
const HomePage = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState({});
  const navigate = useNavigate();
  const { analyzeToken, loading, error } = useTokenAnalysis();

  const handleAnalyze = async (url) => {
    try {
      setIsAnalyzing(true);
      
      // Inicializar progresso
      setProgress({
        overall: { status: 'in_progress', percent: 0 },
        data_collection: { status: 'in_progress', percent: 0 },
        technical_analysis: { status: 'pending', percent: 0 },
        sentiment_analysis: { status: 'pending', percent: 0 },
        onchain_analysis: { status: 'pending', percent: 0 },
        risk_management: { status: 'pending', percent: 0 },
        portfolio_management: { status: 'pending', percent: 0 },
        report_generation: { status: 'pending', percent: 0 }
      });

      // Atualizar progresso (data_collection)
      updateProgress('data_collection', 50);
      
      // Chamar API para análise do token com opções para incluir análises adicionais
      const analysis = await analyzeToken(url, {
        includeOnchain: true,
        includeSentiment: true
      });
      
      // Atualizar progresso (data_collection completo)
      updateProgress('data_collection', 100, 'completed');
      
      // Simular progresso das outras etapas, mas com delays menores
      // Em uma implementação real, o backend poderia fornecer atualizações de status
      await simulateRemainingProgress();
      
      if (analysis) {
        // Uma vez que a análise estiver completa, redirecionar para a página de relatório
        const reportId = analysis.analysis_id || ('crypto-' + Date.now());
        navigate(`/report/${reportId}`);
      } else {
        throw new Error('Falha ao analisar o token');
      }
    } catch (error) {
      console.error('Análise falhou:', error);
      setProgress(prev => ({
        ...prev,
        overall: { status: 'error', percent: 0 }
      }));
    } finally {
      // Não fechamos a modal aqui, deixamos o usuário fechar ou redirecionamos ao concluir
    }
  };

  // Função para atualizar o estado de progresso
  const updateProgress = (step, percent, status = 'in_progress') => {
    setProgress(prev => ({
      ...prev,
      [step]: { status, percent },
      // Calcular o progresso geral com base em todos os passos
      overall: { 
        status: status === 'error' ? 'error' : prev.overall.status, 
        percent: calculateOverallPercent({ ...prev, [step]: { status, percent } })
      }
    }));
  };

  // Calcula a porcentagem geral de progresso
  const calculateOverallPercent = (progressState) => {
    const steps = [
      'data_collection', 
      'technical_analysis', 
      'sentiment_analysis', 
      'onchain_analysis', 
      'risk_management', 
      'portfolio_management', 
      'report_generation'
    ];
    
    let total = 0;
    steps.forEach(step => {
      if (progressState[step]) {
        total += progressState[step].percent || 0;
      }
    });
    
    return Math.floor(total / steps.length);
  };

  // Simula o progresso das etapas restantes após a coleta de dados
  const simulateRemainingProgress = async () => {
    const steps = [
      { key: 'technical_analysis', name: 'Technical Analysis', duration: 1500 },
      { key: 'sentiment_analysis', name: 'Sentiment Analysis', duration: 1200 },
      { key: 'onchain_analysis', name: 'On-Chain Analysis', duration: 1400 },
      { key: 'risk_management', name: 'Risk Management', duration: 800 },
      { key: 'portfolio_management', name: 'Portfolio Management', duration: 600 },
      { key: 'report_generation', name: 'Report Generation', duration: 1000 }
    ];

    for (const step of steps) {
      // Atualizar step para "in_progress"
      updateProgress(step.key, 0);

      // Simular progresso desta etapa
      for (let i = 0; i <= 10; i++) {
        await new Promise(resolve => setTimeout(resolve, step.duration / 10));
        updateProgress(step.key, i * 10);
      }

      // Marcar esta etapa como concluída
      updateProgress(step.key, 100, 'completed');
    }

    // Garantir que o progresso geral esteja completo
    setProgress(prev => ({
      ...prev,
      overall: { status: 'completed', percent: 100 }
    }));

    // Aguardar um momento antes de prosseguir
    await new Promise(resolve => setTimeout(resolve, 500));
  };

  return (
    <div className="min-h-screen flex flex-col">
      <div className="flex-grow flex flex-col items-center justify-center px-4 py-12">
        <div className="max-w-3xl w-full text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="gradient-text">Análise de Criptomoedas com IA</span>
          </h1>
          <p className="text-gray-300 text-lg mb-8">
            Cole qualquer link do CoinGecko ou CoinMarketCap para obter análise completa on-chain,
            de sentimento, social e fundamental utilizando inteligência artificial.
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
            <h3 className="font-semibold text-lg mb-2">Análise On-Chain</h3>
            <p className="text-gray-400 text-sm">
              Analise dados de blockchain, transações e distribuição de carteiras.
            </p>
          </div>
          
          <div className="card">
            <div className="bg-purple-900/30 rounded-full w-10 h-10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg mb-2">Análise de Sentimento</h3>
            <p className="text-gray-400 text-sm">
              Avalie o sentimento do mercado e tendências emocionais de várias fontes.
            </p>
          </div>
          
          <div className="card">
            <div className="bg-pink-900/30 rounded-full w-10 h-10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg mb-2">Análise Social</h3>
            <p className="text-gray-400 text-sm">
              Monitore engajamento em redes sociais, menções e crescimento da comunidade.
            </p>
          </div>
          
          <div className="card">
            <div className="bg-teal-900/30 rounded-full w-10 h-10 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-lg mb-2">Análise Fundamental</h3>
            <p className="text-gray-400 text-sm">
              Avalie tokenomics, equipe, roadmap e fundamentos do projeto.
            </p>
          </div>
        </div>
        
        <div className="mt-20 text-center">
          <h2 className="text-2xl font-bold mb-4">Relatórios Completos de Criptomoedas</h2>
          <p className="text-gray-300 mb-6">
            Nossa IA gera relatórios detalhados para ajudar você a tomar decisões de investimento informadas
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