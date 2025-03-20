import { useState, useEffect } from 'react';
import Head from 'next/head';
import api from '../lib/api';

// Tipo para os ativos do portfólio
interface Asset {
  id: string;
  symbol: string;
  name: string;
  amount: number;
  price_usd: number;
  value_usd: number;
  allocation_percentage: number;
  price_change_24h: number;
}

// Tipo para o portfólio
interface Portfolio {
  id: string;
  name: string;
  created_at: string;
  total_value_usd: number;
  change_24h_usd: number;
  change_24h_percentage: number;
  assets: Asset[];
}

export default function PortfolioPage() {
  // Estados
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  
  // Estados para adicionar ativos
  const [showAddAssetForm, setShowAddAssetForm] = useState(false);
  const [newAsset, setNewAsset] = useState({
    symbol: '',
    amount: ''
  });

  // Buscar portfólios ao carregar a página
  useEffect(() => {
    fetchPortfolios();
  }, []);

  // Buscar todos os portfólios do usuário
  const fetchPortfolios = async () => {
    try {
      setIsLoading(true);
      setError('');
      // Em uma implementação real, isso seria obtido da API
      // const data = await api.portfolio.getUserPortfolios();
      
      // Dados simulados para o exemplo
      const data = getMockPortfolios();
      setPortfolios(data);
      
      if (data.length > 0 && !selectedPortfolio) {
        setSelectedPortfolio(data[0]);
      }
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar portfólios');
    } finally {
      setIsLoading(false);
    }
  };

  // Criar novo portfólio
  const createPortfolio = async () => {
    if (!newPortfolioName.trim()) {
      setError('Digite um nome para o portfólio');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      
      // Em uma implementação real, isso seria enviado para a API
      // const data = await api.portfolio.createPortfolio({
      //   name: newPortfolioName
      // });
      
      // Simular criação para o exemplo
      const newId = `portfolio-${Date.now()}`;
      const newPortfolio: Portfolio = {
        id: newId,
        name: newPortfolioName,
        created_at: new Date().toISOString(),
        total_value_usd: 0,
        change_24h_usd: 0,
        change_24h_percentage: 0,
        assets: []
      };
      
      setPortfolios([...portfolios, newPortfolio]);
      setSelectedPortfolio(newPortfolio);
      setNewPortfolioName('');
      setShowAddForm(false);
    } catch (err: any) {
      setError(err.message || 'Erro ao criar portfólio');
    } finally {
      setIsLoading(false);
    }
  };

  // Adicionar ativo ao portfólio
  const addAsset = async () => {
    if (!selectedPortfolio) return;
    
    if (!newAsset.symbol.trim()) {
      setError('Digite o símbolo do token');
      return;
    }
    
    if (!newAsset.amount || parseFloat(newAsset.amount) <= 0) {
      setError('Digite uma quantidade válida');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      
      // Em uma implementação real, isso seria enviado para a API
      // const data = await api.portfolio.addAsset(selectedPortfolio.id, {
      //   symbol: newAsset.symbol,
      //   amount: parseFloat(newAsset.amount)
      // });
      
      // Simular adição para o exemplo
      const mockPrice = Math.random() * 1000 + 10;
      const amount = parseFloat(newAsset.amount);
      const value = mockPrice * amount;
      
      const newAssetObj: Asset = {
        id: `asset-${Date.now()}`,
        symbol: newAsset.symbol.toUpperCase(),
        name: getMockName(newAsset.symbol),
        amount: amount,
        price_usd: mockPrice,
        value_usd: value,
        allocation_percentage: selectedPortfolio.total_value_usd > 0 
          ? (value / (selectedPortfolio.total_value_usd + value)) * 100
          : 100,
        price_change_24h: (Math.random() * 10) - 5 // -5% a +5%
      };
      
      const updatedPortfolio = {
        ...selectedPortfolio,
        total_value_usd: selectedPortfolio.total_value_usd + value,
        change_24h_usd: selectedPortfolio.change_24h_usd + (value * newAssetObj.price_change_24h / 100),
        assets: [...selectedPortfolio.assets, newAssetObj]
      };
      
      // Recalcular as porcentagens de alocação
      updatedPortfolio.assets = updatedPortfolio.assets.map(asset => ({
        ...asset,
        allocation_percentage: (asset.value_usd / updatedPortfolio.total_value_usd) * 100
      }));
      
      updatedPortfolio.change_24h_percentage = 
        updatedPortfolio.total_value_usd > 0 
          ? (updatedPortfolio.change_24h_usd / updatedPortfolio.total_value_usd) * 100
          : 0;
      
      // Atualizar o portfólio na lista
      const updatedPortfolios = portfolios.map(p => 
        p.id === selectedPortfolio.id ? updatedPortfolio : p
      );
      
      setPortfolios(updatedPortfolios);
      setSelectedPortfolio(updatedPortfolio);
      setNewAsset({ symbol: '', amount: '' });
      setShowAddAssetForm(false);
    } catch (err: any) {
      setError(err.message || 'Erro ao adicionar ativo');
    } finally {
      setIsLoading(false);
    }
  };

  // Remover ativo do portfólio
  const removeAsset = async (assetId: string) => {
    if (!selectedPortfolio) return;

    try {
      setIsLoading(true);
      setError('');
      
      // Em uma implementação real, isso seria enviado para a API
      // await api.portfolio.removeAsset(selectedPortfolio.id, assetId);
      
      // Simular remoção para o exemplo
      const assetToRemove = selectedPortfolio.assets.find(a => a.id === assetId);
      if (!assetToRemove) return;
      
      const updatedPortfolio = {
        ...selectedPortfolio,
        total_value_usd: selectedPortfolio.total_value_usd - assetToRemove.value_usd,
        change_24h_usd: selectedPortfolio.change_24h_usd - (assetToRemove.value_usd * assetToRemove.price_change_24h / 100),
        assets: selectedPortfolio.assets.filter(a => a.id !== assetId)
      };
      
      // Recalcular as porcentagens de alocação
      if (updatedPortfolio.total_value_usd > 0) {
        updatedPortfolio.assets = updatedPortfolio.assets.map(asset => ({
          ...asset,
          allocation_percentage: (asset.value_usd / updatedPortfolio.total_value_usd) * 100
        }));
        
        updatedPortfolio.change_24h_percentage = 
          (updatedPortfolio.change_24h_usd / updatedPortfolio.total_value_usd) * 100;
      } else {
        updatedPortfolio.change_24h_percentage = 0;
      }
      
      // Atualizar o portfólio na lista
      const updatedPortfolios = portfolios.map(p => 
        p.id === selectedPortfolio.id ? updatedPortfolio : p
      );
      
      setPortfolios(updatedPortfolios);
      setSelectedPortfolio(updatedPortfolio);
    } catch (err: any) {
      setError(err.message || 'Erro ao remover ativo');
    } finally {
      setIsLoading(false);
    }
  };

  // Excluir portfólio
  const deletePortfolio = async (portfolioId: string) => {
    try {
      setIsLoading(true);
      setError('');
      
      // Em uma implementação real, isso seria enviado para a API
      // await api.portfolio.deletePortfolio(portfolioId);
      
      // Simular exclusão para o exemplo
      const updatedPortfolios = portfolios.filter(p => p.id !== portfolioId);
      setPortfolios(updatedPortfolios);
      
      if (selectedPortfolio?.id === portfolioId) {
        setSelectedPortfolio(updatedPortfolios.length > 0 ? updatedPortfolios[0] : null);
      }
    } catch (err: any) {
      setError(err.message || 'Erro ao excluir portfólio');
    } finally {
      setIsLoading(false);
    }
  };

  // Formatar valor como moeda
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  // Obter dados simulados de portfólios
  const getMockPortfolios = (): Portfolio[] => {
    return [
      {
        id: 'portfolio-1',
        name: 'Portfólio Principal',
        created_at: '2023-01-15T10:30:00Z',
        total_value_usd: 15750.42,
        change_24h_usd: 320.15,
        change_24h_percentage: 2.08,
        assets: [
          {
            id: 'asset-1',
            symbol: 'BTC',
            name: 'Bitcoin',
            amount: 0.25,
            price_usd: 43200.50,
            value_usd: 10800.13,
            allocation_percentage: 68.57,
            price_change_24h: 2.3
          },
          {
            id: 'asset-2',
            symbol: 'ETH',
            name: 'Ethereum',
            amount: 2.5,
            price_usd: 1850.30,
            value_usd: 4625.75,
            allocation_percentage: 29.37,
            price_change_24h: 1.5
          },
          {
            id: 'asset-3',
            symbol: 'SOL',
            name: 'Solana',
            amount: 5.0,
            price_usd: 64.90,
            value_usd: 324.50,
            allocation_percentage: 2.06,
            price_change_24h: 4.2
          }
        ]
      },
      {
        id: 'portfolio-2',
        name: 'DeFi',
        created_at: '2023-03-22T14:15:00Z',
        total_value_usd: 8320.75,
        change_24h_usd: -145.30,
        change_24h_percentage: -1.72,
        assets: [
          {
            id: 'asset-4',
            symbol: 'AAVE',
            name: 'Aave',
            amount: 10.0,
            price_usd: 320.45,
            value_usd: 3204.50,
            allocation_percentage: 38.51,
            price_change_24h: -2.1
          },
          {
            id: 'asset-5',
            symbol: 'UNI',
            name: 'Uniswap',
            amount: 100.0,
            price_usd: 18.75,
            value_usd: 1875.00,
            allocation_percentage: 22.53,
            price_change_24h: -1.8
          },
          {
            id: 'asset-6',
            symbol: 'MKR',
            name: 'Maker',
            amount: 2.0,
            price_usd: 1620.60,
            value_usd: 3241.20,
            allocation_percentage: 38.95,
            price_change_24h: -1.3
          }
        ]
      }
    ];
  };

  // Obter nome fictício para um símbolo
  const getMockName = (symbol: string): string => {
    const names: {[key: string]: string} = {
      'BTC': 'Bitcoin',
      'ETH': 'Ethereum',
      'SOL': 'Solana',
      'ADA': 'Cardano',
      'DOT': 'Polkadot',
      'AVAX': 'Avalanche',
      'MATIC': 'Polygon',
      'LINK': 'Chainlink',
      'UNI': 'Uniswap',
      'AAVE': 'Aave',
      'MKR': 'Maker',
      'CRV': 'Curve',
      'SNX': 'Synthetix',
      'COMP': 'Compound'
    };
    
    return names[symbol.toUpperCase()] || `Token ${symbol.toUpperCase()}`;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Head>
        <title>Gerenciar Portfólio | DeFi Insight</title>
        <meta name="description" content="Gerencie seus portfólios de criptomoedas" />
      </Head>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Gerenciar Portfólio</h1>

        {/* Seleção de portfólios */}
        <div className="mb-8">
          <div className="flex flex-wrap items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Meus Portfólios</h2>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
            >
              {showAddForm ? 'Cancelar' : 'Novo Portfólio'}
            </button>
          </div>

          {/* Formulário para adicionar portfólio */}
          {showAddForm && (
            <div className="mb-6 p-4 bg-gray-800 rounded-lg">
              <div className="flex flex-col sm:flex-row gap-4">
                <input
                  type="text"
                  value={newPortfolioName}
                  onChange={(e) => setNewPortfolioName(e.target.value)}
                  placeholder="Nome do portfólio"
                  className="w-full sm:w-2/3 px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={createPortfolio}
                  disabled={isLoading || !newPortfolioName.trim()}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Criar Portfólio
                </button>
              </div>
            </div>
          )}

          {/* Lista de portfólios */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {portfolios.map((portfolio) => (
              <div 
                key={portfolio.id}
                onClick={() => setSelectedPortfolio(portfolio)}
                className={`p-4 rounded-lg cursor-pointer transition-all ${
                  selectedPortfolio?.id === portfolio.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 hover:bg-gray-700'
                }`}
              >
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-medium mb-2">{portfolio.name}</h3>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deletePortfolio(portfolio.id);
                    }}
                    className="text-gray-400 hover:text-red-400"
                    title="Excluir portfólio"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
                <p className="text-2xl font-bold">{formatCurrency(portfolio.total_value_usd)}</p>
                <p className={`text-sm ${
                  portfolio.change_24h_percentage > 0 
                    ? 'text-green-400' 
                    : portfolio.change_24h_percentage < 0 
                      ? 'text-red-400' 
                      : 'text-gray-400'
                }`}>
                  {portfolio.change_24h_percentage > 0 ? '+' : ''}
                  {portfolio.change_24h_percentage.toFixed(2)}% (24h)
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  {portfolio.assets.length} ativos
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Mensagem de erro */}
        {error && (
          <div className="mb-8 p-4 bg-red-800/50 border border-red-600 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {/* Detalhes do portfólio selecionado */}
        {selectedPortfolio && (
          <div className="mt-8">
            <div className="flex flex-wrap items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">{selectedPortfolio.name}</h2>
              <button
                onClick={() => setShowAddAssetForm(!showAddAssetForm)}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm"
              >
                {showAddAssetForm ? 'Cancelar' : 'Adicionar Ativo'}
              </button>
            </div>

            {/* Formulário para adicionar ativo */}
            {showAddAssetForm && (
              <div className="mb-6 p-4 bg-gray-800 rounded-lg">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Símbolo</label>
                    <input
                      type="text"
                      value={newAsset.symbol}
                      onChange={(e) => setNewAsset({...newAsset, symbol: e.target.value.toUpperCase()})}
                      placeholder="BTC, ETH, etc."
                      className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Quantidade</label>
                    <input
                      type="number"
                      value={newAsset.amount}
                      onChange={(e) => setNewAsset({...newAsset, amount: e.target.value})}
                      placeholder="0.00"
                      step="0.000001"
                      min="0"
                      className="w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 focus:outline-none focus:border-blue-500"
                    />
                  </div>
                  <div className="flex items-end">
                    <button
                      onClick={addAsset}
                      disabled={isLoading || !newAsset.symbol.trim() || !newAsset.amount}
                      className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Adicionar
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Resumo do portfólio */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-medium mb-2">Valor Total</h3>
                <p className="text-3xl font-bold">{formatCurrency(selectedPortfolio.total_value_usd)}</p>
              </div>
              
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-medium mb-2">Variação 24h</h3>
                <p className={`text-3xl font-bold ${
                  selectedPortfolio.change_24h_usd > 0 
                    ? 'text-green-400' 
                    : selectedPortfolio.change_24h_usd < 0 
                      ? 'text-red-400' 
                      : ''
                }`}>
                  {selectedPortfolio.change_24h_usd > 0 ? '+' : ''}
                  {formatCurrency(selectedPortfolio.change_24h_usd)}
                </p>
                <p className={`text-sm ${
                  selectedPortfolio.change_24h_percentage > 0 
                    ? 'text-green-400' 
                    : selectedPortfolio.change_24h_percentage < 0 
                      ? 'text-red-400' 
                      : 'text-gray-400'
                }`}>
                  {selectedPortfolio.change_24h_percentage > 0 ? '+' : ''}
                  {selectedPortfolio.change_24h_percentage.toFixed(2)}%
                </p>
              </div>
              
              <div className="bg-gray-800 p-6 rounded-lg">
                <h3 className="text-lg font-medium mb-2">Ativos</h3>
                <p className="text-3xl font-bold">{selectedPortfolio.assets.length}</p>
              </div>
            </div>

            {/* Lista de ativos */}
            {selectedPortfolio.assets.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left border-b border-gray-700">
                      <th className="py-3 px-4">Ativo</th>
                      <th className="py-3 px-4 text-right">Preço</th>
                      <th className="py-3 px-4 text-right">Quantidade</th>
                      <th className="py-3 px-4 text-right">Valor</th>
                      <th className="py-3 px-4 text-right">Alocação</th>
                      <th className="py-3 px-4 text-right">24h</th>
                      <th className="py-3 px-4 text-center">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPortfolio.assets.map((asset) => (
                      <tr key={asset.id} className="border-b border-gray-700 hover:bg-gray-800">
                        <td className="py-3 px-4">
                          <div className="flex items-center">
                            <div className="mr-3 w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center font-bold">
                              {asset.symbol.substring(0, 1)}
                            </div>
                            <div>
                              <div className="font-medium">{asset.symbol}</div>
                              <div className="text-sm text-gray-400">{asset.name}</div>
                            </div>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-right">{formatCurrency(asset.price_usd)}</td>
                        <td className="py-3 px-4 text-right">{asset.amount.toLocaleString('pt-BR')}</td>
                        <td className="py-3 px-4 text-right font-medium">{formatCurrency(asset.value_usd)}</td>
                        <td className="py-3 px-4 text-right">{asset.allocation_percentage.toFixed(2)}%</td>
                        <td className={`py-3 px-4 text-right ${
                          asset.price_change_24h > 0 
                            ? 'text-green-400' 
                            : asset.price_change_24h < 0 
                              ? 'text-red-400' 
                              : ''
                        }`}>
                          {asset.price_change_24h > 0 ? '+' : ''}
                          {asset.price_change_24h.toFixed(2)}%
                        </td>
                        <td className="py-3 px-4 text-center">
                          <button
                            onClick={() => removeAsset(asset.id)}
                            className="text-gray-400 hover:text-red-400"
                            title="Remover ativo"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center bg-gray-800 rounded-lg">
                <p className="text-gray-400 mb-4">Nenhum ativo no portfólio</p>
                <button
                  onClick={() => setShowAddAssetForm(true)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
                >
                  Adicionar Primeiro Ativo
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
} 