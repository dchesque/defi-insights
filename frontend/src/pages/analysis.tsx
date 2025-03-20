import { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import api from '../lib/api';

// Tipos de análise disponíveis
type AnalysisType = 'technical' | 'sentiment' | 'onchain';

export default function Analysis() {
  const router = useRouter();
  const [symbol, setSymbol] = useState('');
  const [analysisType, setAnalysisType] = useState<AnalysisType>('technical');
  const [timeframe, setTimeframe] = useState('1d');
  const [address, setAddress] = useState('');
  const [chain, setChain] = useState('eth');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState<any>(null);

  // Lista de tokens populares
  const popularTokens = [
    { symbol: 'BTC', name: 'Bitcoin' },
    { symbol: 'ETH', name: 'Ethereum' },
    { symbol: 'BNB', name: 'Binance Coin' },
    { symbol: 'SOL', name: 'Solana' },
    { symbol: 'ADA', name: 'Cardano' },
    { symbol: 'DOT', name: 'Polkadot' },
    { symbol: 'AVAX', name: 'Avalanche' },
  ];

  // Lista de blockchains suportadas
  const supportedChains = [
    { value: 'eth', name: 'Ethereum' },
    { value: 'bsc', name: 'Binance Smart Chain' },
    { value: 'polygon', name: 'Polygon' },
    { value: 'arbitrum', name: 'Arbitrum' },
    { value: 'optimism', name: 'Optimism' },
  ];

  // Manipular mudança no tipo de análise
  const handleTypeChange = (type: AnalysisType) => {
    setAnalysisType(type);
    setResults(null);
    setError('');
  };

  // Manipular seleção de token popular
  const handleSelectToken = (selectedSymbol: string) => {
    setSymbol(selectedSymbol);
    setError('');
  };

  // Realizar análise
  const handleAnalyze = async () => {
    if (!symbol) {
      setError('Por favor, insira o símbolo do token');
      return;
    }

    setIsLoading(true);
    setError('');
    setResults(null);

    try {
      let response;

      switch (analysisType) {
        case 'technical':
          response = await api.technical.analyze(symbol, timeframe);
          break;
        case 'sentiment':
          response = await api.sentiment.analyze(symbol);
          break;
        case 'onchain':
          if (!address) {
            setError('Por favor, insira o endereço do contrato');
            setIsLoading(false);
            return;
          }
          response = await api.onchain.analyze(symbol, address, chain);
          break;
      }

      setResults(response);
    } catch (err: any) {
      setError(err.message || 'Erro ao realizar análise');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Head>
        <title>Análise de Tokens | DeFi Insight</title>
        <meta name="description" content="Realize análises avançadas de tokens cripto" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Análise de Tokens</h1>

        {/* Seleção de tipo de análise */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Tipo de Análise</h2>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => handleTypeChange('technical')}
              className={`px-6 py-3 rounded-lg text-lg transition-colors ${
                analysisType === 'technical'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Análise Técnica
            </button>
            <button
              onClick={() => handleTypeChange('sentiment')}
              className={`px-6 py-3 rounded-lg text-lg transition-colors ${
                analysisType === 'sentiment'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Análise de Sentimento
            </button>
            <button
              onClick={() => handleTypeChange('onchain')}
              className={`px-6 py-3 rounded-lg text-lg transition-colors ${
                analysisType === 'onchain'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Análise On-Chain
            </button>
          </div>
        </div>

        {/* Seleção de token */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Token</h2>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="w-full sm:w-2/3">
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="Digite o símbolo do token (ex: BTC, ETH)"
                className="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:border-blue-500"
              />
            </div>
            {analysisType === 'technical' && (
              <div className="w-full sm:w-1/3">
                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:border-blue-500"
                >
                  <option value="1h">1 hora</option>
                  <option value="4h">4 horas</option>
                  <option value="1d">1 dia</option>
                  <option value="1w">1 semana</option>
                  <option value="1m">1 mês</option>
                </select>
              </div>
            )}
          </div>

          {/* Tokens populares */}
          <div className="mt-4">
            <h3 className="text-lg font-medium mb-2">Tokens Populares</h3>
            <div className="flex flex-wrap gap-2">
              {popularTokens.map((token) => (
                <button
                  key={token.symbol}
                  onClick={() => handleSelectToken(token.symbol)}
                  className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                    symbol === token.symbol
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {token.symbol} - {token.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Campos específicos para análise on-chain */}
        {analysisType === 'onchain' && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Detalhes On-Chain</h2>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="w-full sm:w-2/3">
                <label className="block mb-1 text-gray-300">Endereço do Contrato</label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="0x..."
                  className="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="w-full sm:w-1/3">
                <label className="block mb-1 text-gray-300">Blockchain</label>
                <select
                  value={chain}
                  onChange={(e) => setChain(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:border-blue-500"
                >
                  {supportedChains.map((chain) => (
                    <option key={chain.value} value={chain.value}>
                      {chain.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Botão de análise */}
        <div className="mb-8">
          <button
            onClick={handleAnalyze}
            disabled={isLoading}
            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white text-lg font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Analisando...' : 'Analisar Token'}
          </button>
        </div>

        {/* Mensagem de erro */}
        {error && (
          <div className="mb-8 p-4 bg-red-800/50 border border-red-600 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {/* Resultados da análise */}
        {results && (
          <div className="mt-8 p-6 bg-gray-800 rounded-lg">
            <h2 className="text-2xl font-bold mb-4">Resultados da Análise</h2>
            
            {/* Aqui você pode personalizar a exibição dos resultados dependendo do tipo de análise */}
            {analysisType === 'technical' && (
              <div>
                <h3 className="text-xl font-semibold mb-2">Análise Técnica para {results.symbol}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Indicadores</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.indicators, null, 2)}
                    </pre>
                  </div>
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Sinais</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.signals, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {analysisType === 'sentiment' && (
              <div>
                <h3 className="text-xl font-semibold mb-2">Análise de Sentimento para {results.symbol}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Sentimento Geral</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.overall_sentiment, null, 2)}
                    </pre>
                  </div>
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Sentimento por Fonte</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.sentiment_by_source, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}

            {analysisType === 'onchain' && (
              <div>
                <h3 className="text-xl font-semibold mb-2">Análise On-Chain para {results.symbol}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Distribuição de Holders</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.holder_distribution, null, 2)}
                    </pre>
                  </div>
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Métricas de Transação</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.transaction_metrics, null, 2)}
                    </pre>
                  </div>
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Análise de Liquidez</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.liquidity_analysis, null, 2)}
                    </pre>
                  </div>
                  <div className="p-4 bg-gray-700 rounded-lg">
                    <h4 className="text-lg font-medium mb-2">Avaliação de Risco</h4>
                    <pre className="text-sm overflow-auto p-2 bg-gray-800 rounded">
                      {JSON.stringify(results.risk_assessment, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
} 