import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import CryptoForm from '../components/CryptoForm';
import ProgressModal from '../components/ProgressModal';
import { useTokenAnalysis } from '../hooks/useTokenAnalysis';

const HomePage = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState({});
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const navigate = useNavigate();
  const { analyzeToken } = useTokenAnalysis();

  // Efeito para rastrear mouse (blur dinâmico)
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleAnalyze = async (url) => {
    try {
      setIsAnalyzing(true);

      // Inicializa progresso
      setProgress({
        overall: { status: 'in_progress', percent: 0 },
        data_collection: { status: 'in_progress', percent: 0 },
        technical_analysis: { status: 'pending', percent: 0 },
        sentiment_analysis: { status: 'pending', percent: 0 },
        onchain_analysis: { status: 'pending', percent: 0 },
        risk_management: { status: 'pending', percent: 0 },
        portfolio_management: { status: 'pending', percent: 0 },
        report_generation: { status: 'pending', percent: 0 },
      });

      // Exemplo de atualização de progresso
      updateProgress('data_collection', 50);

      // Chama API para análise
      const analysis = await analyzeToken(url, {
        includeOnchain: true,
        includeSentiment: true,
      });

      updateProgress('data_collection', 100, 'completed');

      // Simula progresso das outras etapas
      await simulateRemainingProgress();

      if (analysis) {
        const reportId = analysis.analysis_id || `crypto-${Date.now()}`;
        navigate(`/report/${reportId}`);
      } else {
        throw new Error('Falha ao analisar o token');
      }
    } catch (error) {
      console.error('Análise falhou:', error);
      setProgress((prev) => ({
        ...prev,
        overall: { status: 'error', percent: 0 },
      }));
    }
  };

  const updateProgress = (step, percent, status = 'in_progress') => {
    setProgress((prev) => ({
      ...prev,
      [step]: { status, percent },
      overall: {
        status: status === 'error' ? 'error' : prev.overall.status,
        percent: calculateOverallPercent({ ...prev, [step]: { status, percent } }),
      },
    }));
  };

  const calculateOverallPercent = (progressState) => {
    const steps = [
      'data_collection',
      'technical_analysis',
      'sentiment_analysis',
      'onchain_analysis',
      'risk_management',
      'portfolio_management',
      'report_generation',
    ];

    let total = 0;
    steps.forEach((step) => {
      if (progressState[step]) {
        total += progressState[step].percent || 0;
      }
    });
    return Math.floor(total / steps.length);
  };

  const simulateRemainingProgress = async () => {
    const steps = [
      { key: 'technical_analysis', duration: 1500 },
      { key: 'sentiment_analysis', duration: 1200 },
      { key: 'onchain_analysis', duration: 1400 },
      { key: 'risk_management', duration: 800 },
      { key: 'portfolio_management', duration: 600 },
      { key: 'report_generation', duration: 1000 },
    ];

    for (const step of steps) {
      updateProgress(step.key, 0);
      for (let i = 0; i <= 10; i++) {
        await new Promise((resolve) => setTimeout(resolve, step.duration / 10));
        updateProgress(step.key, i * 10);
      }
      updateProgress(step.key, 100, 'completed');
    }

    setProgress((prev) => ({
      ...prev,
      overall: { status: 'completed', percent: 100 },
    }));

    await new Promise((resolve) => setTimeout(resolve, 500));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-slate-900 relative overflow-hidden">
      {/* Efeito de blur que segue o mouse */}
      <div
        className="pointer-events-none absolute bg-blue-500/20 mix-blend-screen blur-[80px] rounded-full w-[300px] h-[300px] -translate-x-1/2 -translate-y-1/2 z-0 transition-transform duration-200 ease-out animate-pulse-slow"
        style={{
          left: `${mousePosition.x}px`,
          top: `${mousePosition.y}px`,
          opacity: 0.6,
          background:
            'radial-gradient(circle, rgba(56,189,248,0.4) 0%, rgba(124,58,237,0.3) 50%, rgba(0,0,0,0) 70%)',
        }}
      />

      {/* Header */}
      <header className="container mx-auto py-6 px-10 relative z-10 flex items-center justify-between">
        {/* Logo e Nome */}
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-full bg-gradient-to-r from-purple-600 to-blue-500 flex items-center justify-center">
            <span className="text-white font-bold text-xl">D</span>
          </div>
          <h1 className="text-white text-xl font-bold">
          DeFiInsights<span className="text-blue-500">.ai</span>
          </h1>
        </div>
        {/* Navegação ou Botões (exemplo) */}
        <div className="flex items-center gap-4">
          <button className="text-sm text-gray-200 hover:text-white">Resources</button>
          <button className="text-sm text-gray-200 hover:text-white">About</button>
          <button className="border border-blue-500 text-blue-500 hover:bg-blue-500/10 rounded px-3 py-1">
            Sign In
          </button>
          <button className="border border-purple-500 text-purple-300 hover:bg-purple-500/10 rounded px-3 py-1">
            Register
          </button>
        </div>
      </header>

      {/* Conteúdo Principal */}
      <main className="relative z-10">
        {/* Seção Hero */}
        <section className="max-w-7xl mx-auto text-center py-16 px-4">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
  <span className="gradient-text">Análise de Criptomoedas com IA</span>
</h1>
          <p className="text-gray-300 max-w-4xl mx-auto text-center text-lg mb-8">
            Cole qualquer link do CoinGecko ou CoinMarketCap para obter análise completa on-chain,
            de sentimento, social e fundamental utilizando inteligência artificial.
          </p>
          <div className="max-w-2xl mx-auto">
            <CryptoForm onAnalyze={handleAnalyze} />
          </div>
        </section>

        {/* Seção de Recursos */}
        <section className="max-w-5xl mx-auto px-4 pb-16">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Card: Análise On-Chain */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 text-center">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-indigo-900/30 mx-auto mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-indigo-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="font-semibold text-lg mb-2 text-white">Análise On-Chain</h3>
              <p className="text-gray-400 text-sm">
                Analise dados de blockchain, transações e distribuição de carteiras.
              </p>
            </div>

            {/* Card: Análise de Sentimento */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 text-center">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-purple-900/30 mx-auto mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-purple-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-lg mb-2 text-white">Análise de Sentimento</h3>
              <p className="text-gray-400 text-sm">
                Avalie o sentimento do mercado e tendências emocionais de várias fontes.
              </p>
            </div>

            {/* Card: Análise Social */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 text-center">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-pink-900/30 mx-auto mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-pink-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-lg mb-2 text-white">Análise Social</h3>
              <p className="text-gray-400 text-sm">
                Monitore engajamento em redes sociais, menções e crescimento da comunidade.
              </p>
            </div>

            {/* Card: Análise Fundamental */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 text-center">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-teal-900/30 mx-auto mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-teal-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="font-semibold text-lg mb-2 text-white">Análise Fundamental</h3>
              <p className="text-gray-400 text-sm">
                Avalie tokenomics, equipe, roadmap e fundamentos do projeto.
              </p>
            </div>
          </div>
        </section>

        {/* Seção de Relatórios */}
        <section className="text-center mb-16">
          <h2 className="text-2xl font-bold text-white mb-4">
            Relatórios Completos de Criptomoedas
          </h2>
          <p className="text-gray-300">
            Nossa IA gera relatórios detalhados para ajudar você a tomar decisões de investimento informadas
          </p>
        </section>
      </main>

      {/* Modal de Progresso */}
      {isAnalyzing && (
        <ProgressModal
          progress={progress}
          onClose={() => setIsAnalyzing(false)}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-10 relative z-10">
  <div className="container mx-auto px-4 py-8 flex items-center justify-center">
    <p className="text-gray-400 text-sm text-center">
      © 2025 DeFiInsights.ai. All rights reserved.
    </p>
  </div>
</footer>
    </div>
  );
};

export default HomePage;
