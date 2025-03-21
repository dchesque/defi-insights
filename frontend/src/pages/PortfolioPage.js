// frontend/src/pages/PortfolioPage.js - Criado em 21/03/2025 16:40
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FaPlus, FaTrash, FaEdit, FaChartLine, FaWallet, FaSyncAlt, FaInfoCircle } from 'react-icons/fa';
import { useAuthContext } from '../App';
import { usePortfolio } from '../hooks/usePortfolio';

/**
 * Página de gerenciamento de portfólio
 * Permite ao usuário acompanhar seus investimentos em criptomoedas
 */
const PortfolioPage = () => {
  const { user } = useAuthContext();
  const { 
    portfolios,
    getUserPortfolios, 
    createPortfolio,
    deletePortfolio,
    addToken,
    removeToken,
    loading,
    error 
  } = usePortfolio();
  
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [showAddPortfolioModal, setShowAddPortfolioModal] = useState(false);
  const [showAddTokenModal, setShowAddTokenModal] = useState(false);
  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [newPortfolioDescription, setNewPortfolioDescription] = useState('');
  const [newToken, setNewToken] = useState({
    symbol: '',
    amount: '',
    purchase_price: '',
    purchase_date: new Date().toISOString().split('T')[0]
  });

  // Carregar portfólios ao iniciar
  useEffect(() => {
    const loadPortfolios = async () => {
      try {
        const userPortfolios = await getUserPortfolios();
        if (userPortfolios && userPortfolios.length > 0) {
          setSelectedPortfolio(userPortfolios[0]);
        }
      } catch (err) {
        console.error('Erro ao carregar portfólios:', err);
      }
    };

    loadPortfolios();
  }, [getUserPortfolios]);

  // Criar novo portfólio
  const handleCreatePortfolio = async (e) => {
    e.preventDefault();
    
    if (!newPortfolioName.trim()) {
      return;
    }
    
    try {
      const createdPortfolio = await createPortfolio({
        name: newPortfolioName,
        description: newPortfolioDescription
      });
      
      if (createdPortfolio) {
        setSelectedPortfolio(createdPortfolio);
        setShowAddPortfolioModal(false);
        setNewPortfolioName('');
        setNewPortfolioDescription('');
      }
    } catch (err) {
      console.error('Erro ao criar portfólio:', err);
    }
  };

  // Adicionar novo token ao portfólio
  const handleAddToken = async (e) => {
    e.preventDefault();
    
    if (!newToken.symbol || !newToken.amount || !newToken.purchase_price) {
      return;
    }
    
    try {
      await addToken(selectedPortfolio.id, {
        symbol: newToken.symbol.toUpperCase(),
        amount: parseFloat(newToken.amount),
        purchase_price: parseFloat(newToken.purchase_price),
        purchase_date: newToken.purchase_date
      });
      
      setShowAddTokenModal(false);
      setNewToken({
        symbol: '',
        amount: '',
        purchase_price: '',
        purchase_date: new Date().toISOString().split('T')[0]
      });
    } catch (err) {
      console.error('Erro ao adicionar token:', err);
    }
  };

  // Remover token do portfólio
  const handleRemoveToken = async (tokenId) => {
    if (!selectedPortfolio) return;
    
    if (window.confirm('Tem certeza que deseja remover este token?')) {
      try {
        await removeToken(selectedPortfolio.id, tokenId);
      } catch (err) {
        console.error('Erro ao remover token:', err);
      }
    }
  };

  // Excluir portfólio
  const handleDeletePortfolio = async (portfolioId) => {
    if (window.confirm('Tem certeza que deseja excluir este portfólio?')) {
      try {
        await deletePortfolio(portfolioId);
        
        // Se excluiu o portfólio selecionado, selecionar outro
        if (selectedPortfolio?.id === portfolioId) {
          setSelectedPortfolio(portfolios.find(p => p.id !== portfolioId) || null);
        }
      } catch (err) {
        console.error('Erro ao excluir portfólio:', err);
      }
    }
  };

  // Atualizar portfólio (recarregar preços atuais)
  const handleRefreshPortfolio = () => {
    if (selectedPortfolio) {
      getUserPortfolios();
    }
  };

  return (
    <div className="py-8 px-4 md:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Cabeçalho */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Meu Portfólio
            </h1>
            <p className="text-gray-400">
              Acompanhe seus investimentos em criptomoedas
            </p>
          </div>
          
          <div className="mt-4 md:mt-0 flex space-x-4">
            <button
              onClick={() => setShowAddPortfolioModal(true)}
              className="px-4 py-2 flex items-center bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
            >
              <FaPlus className="mr-2" />
              Novo Portfólio
            </button>
            
            {selectedPortfolio && (
              <button
                onClick={() => setShowAddTokenModal(true)}
                className="px-4 py-2 flex items-center bg-[#1A1C31] border border-indigo-600 rounded-md text-indigo-400 font-medium hover:bg-indigo-900/30 transition-colors"
              >
                <FaPlus className="mr-2" />
                Adicionar Token
              </button>
            )}
          </div>
        </div>
        
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
          </div>
        ) : portfolios && portfolios.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Seletor de Portfólio */}
            <div className="md:col-span-1">
              <div className="bg-[#1A1C31] rounded-lg p-6">
                <h2 className="text-lg font-medium mb-4">Meus Portfólios</h2>
                
                <div className="space-y-2">
                  {portfolios.map(portfolio => (
                    <div
                      key={portfolio.id}
                      className={`p-3 rounded-md cursor-pointer flex justify-between items-center ${
                        selectedPortfolio?.id === portfolio.id
                          ? 'bg-indigo-900/30 border border-indigo-800/30'
                          : 'hover:bg-[#22263E]'
                      }`}
                      onClick={() => setSelectedPortfolio(portfolio)}
                    >
                      <div>
                        <div className="font-medium">{portfolio.name}</div>
                        {portfolio.total_value && (
                          <div className="text-sm text-gray-400">
                            ${portfolio.total_value.toLocaleString()}
                          </div>
                        )}
                      </div>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeletePortfolio(portfolio.id);
                        }}
                        className="text-gray-400 hover:text-red-500"
                        title="Excluir portfólio"
                      >
                        <FaTrash />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Detalhes do Portfólio */}
            <div className="md:col-span-3">
              {selectedPortfolio ? (
                <div className="bg-[#1A1C31] rounded-lg overflow-hidden">
                  {/* Cabeçalho do Portfólio */}
                  <div className="p-6 border-b border-gray-800 flex flex-col md:flex-row md:items-center md:justify-between">
                    <div>
                      <h2 className="text-xl font-bold">{selectedPortfolio.name}</h2>
                      {selectedPortfolio.description && (
                        <p className="text-gray-400 mt-1">{selectedPortfolio.description}</p>
                      )}
                    </div>
                    
                    <div className="mt-4 md:mt-0 flex items-center">
                      <button
                        onClick={handleRefreshPortfolio}
                        className="mr-4 text-indigo-400 hover:text-indigo-300"
                        title="Atualizar preços"
                      >
                        <FaSyncAlt />
                      </button>
                      
                      <button
                        onClick={() => setShowAddTokenModal(true)}
                        className="px-3 py-1 bg-indigo-900/30 text-indigo-400 text-sm rounded hover:bg-indigo-700/30"
                      >
                        <FaPlus className="mr-1 inline-block" />
                        Adicionar Token
                      </button>
                    </div>
                  </div>
                  
                  {/* Resumo do Portfólio */}
                  <div className="p-6 border-b border-gray-800">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                        <div className="text-gray-400 text-sm mb-1">Valor Total</div>
                        <div className="text-2xl font-bold">
                          ${selectedPortfolio.total_value?.toLocaleString() || '0.00'}
                        </div>
                      </div>
                      
                      <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                        <div className="text-gray-400 text-sm mb-1">Investimento</div>
                        <div className="text-2xl font-bold">
                          ${selectedPortfolio.total_invested?.toLocaleString() || '0.00'}
                        </div>
                      </div>
                      
                      <div className="bg-[#12141F] p-4 rounded-lg border border-gray-800">
                        <div className="text-gray-400 text-sm mb-1">Lucro/Perda</div>
                        <div className={`text-2xl font-bold ${
                          (selectedPortfolio.profit_loss || 0) >= 0 
                            ? 'text-green-500' 
                            : 'text-red-500'
                        }`}>
                          {(selectedPortfolio.profit_loss || 0) >= 0 ? '+' : ''}
                          ${Math.abs(selectedPortfolio.profit_loss || 0).toLocaleString()}
                          <span className="text-sm">
                            ({(selectedPortfolio.profit_loss_percentage || 0) >= 0 ? '+' : ''}
                            {selectedPortfolio.profit_loss_percentage?.toFixed(2) || 0}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Lista de Tokens */}
                  <div className="p-6">
                    <h3 className="font-medium mb-4">Tokens</h3>
                    
                    {selectedPortfolio.tokens && selectedPortfolio.tokens.length > 0 ? (
                      <div className="overflow-x-auto">
                        <table className="w-full">
                          <thead>
                            <tr className="text-left text-gray-400 border-b border-gray-800">
                              <th className="pb-3 font-medium">Token</th>
                              <th className="pb-3 font-medium">Quantidade</th>
                              <th className="pb-3 font-medium">Preço Compra</th>
                              <th className="pb-3 font-medium">Preço Atual</th>
                              <th className="pb-3 font-medium">Valor</th>
                              <th className="pb-3 font-medium">Lucro/Perda</th>
                              <th className="pb-3 font-medium text-right">Ações</th>
                            </tr>
                          </thead>
                          <tbody>
                            {selectedPortfolio.tokens.map(token => (
                              <tr key={token.id} className="border-b border-gray-800">
                                <td className="py-4">
                                  <div className="font-medium">{token.symbol}</div>
                                  <div className="text-gray-400 text-sm">{token.name}</div>
                                </td>
                                <td className="py-4">
                                  {token.amount}
                                </td>
                                <td className="py-4">
                                  ${token.purchase_price.toLocaleString()}
                                </td>
                                <td className="py-4">
                                  {token.current_price ? (
                                    <div>${token.current_price.toLocaleString()}</div>
                                  ) : (
                                    <div className="text-gray-400">—</div>
                                  )}
                                </td>
                                <td className="py-4">
                                  {token.current_value ? (
                                    <div>${token.current_value.toLocaleString()}</div>
                                  ) : (
                                    <div>${(token.amount * token.purchase_price).toLocaleString()}</div>
                                  )}
                                </td>
                                <td className="py-4">
                                  {token.profit_loss ? (
                                    <div className={`${
                                      token.profit_loss >= 0 
                                        ? 'text-green-500' 
                                        : 'text-red-500'
                                    }`}>
                                      {token.profit_loss >= 0 ? '+' : ''}
                                      ${Math.abs(token.profit_loss).toLocaleString()}
                                      <span className="block text-xs">
                                        ({token.profit_loss_percentage >= 0 ? '+' : ''}
                                        {token.profit_loss_percentage?.toFixed(2)}%)
                                      </span>
                                    </div>
                                  ) : (
                                    <div className="text-gray-400">—</div>
                                  )}
                                </td>
                                <td className="py-4 text-right">
                                  <button
                                    onClick={() => handleRemoveToken(token.id)}
                                    className="text-gray-400 hover:text-red-500 ml-3"
                                    title="Remover token"
                                  >
                                    <FaTrash />
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-400 mb-4">
                          Você ainda não adicionou tokens a este portfólio.
                        </p>
                        <button
                          onClick={() => setShowAddTokenModal(true)}
                          className="inline-block px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
                        >
                          <FaPlus className="mr-2 inline-block" />
                          Adicionar Primeiro Token
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="bg-[#1A1C31] rounded-lg p-6 text-center">
                  <div className="bg-indigo-900/30 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                    <FaWallet className="text-indigo-400 text-2xl" />
                  </div>
                  <h2 className="text-xl font-bold mb-2">Nenhum Portfólio Selecionado</h2>
                  <p className="text-gray-400 mb-6">
                    Selecione um portfólio existente ou crie um novo para começar.
                  </p>
                  <button
                    onClick={() => setShowAddPortfolioModal(true)}
                    className="inline-block px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
                  >
                    <FaPlus className="mr-2 inline-block" />
                    Criar Portfólio
                  </button>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-[#1A1C31] rounded-lg p-8 text-center">
            <div className="bg-indigo-900/30 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
              <FaWallet className="text-indigo-400 text-3xl" />
            </div>
            <h2 className="text-2xl font-bold mb-3">Bem-vindo ao Gerenciamento de Portfólio</h2>
            <p className="text-gray-400 mb-6 max-w-md mx-auto">
              Acompanhe seus investimentos em criptomoedas, monitore seu desempenho e receba insights baseados em IA.
            </p>
            <button
              onClick={() => setShowAddPortfolioModal(true)}
              className="inline-block px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
            >
              <FaPlus className="mr-2 inline-block" />
              Criar Meu Primeiro Portfólio
            </button>
          </div>
        )}
      </div>
      
      {/* Modal para adicionar portfólio */}
      {showAddPortfolioModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-[#1A1C31] rounded-lg shadow-xl max-w-md w-full p-6 relative">
            <button
              onClick={() => setShowAddPortfolioModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              ×
            </button>
            
            <h2 className="text-xl font-bold mb-6">Novo Portfólio</h2>
            
            <form onSubmit={handleCreatePortfolio}>
              <div className="mb-4">
                <label htmlFor="portfolioName" className="block text-gray-300 mb-2 font-medium">
                  Nome do Portfólio
                </label>
                <input
                  id="portfolioName"
                  type="text"
                  value={newPortfolioName}
                  onChange={(e) => setNewPortfolioName(e.target.value)}
                  className="w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  placeholder="Ex: Meu Portfólio Principal"
                  required
                />
              </div>
              
              <div className="mb-6">
                <label htmlFor="portfolioDescription" className="block text-gray-300 mb-2 font-medium">
                  Descrição (opcional)
                </label>
                <input
                  id="portfolioDescription"
                  type="text"
                  value={newPortfolioDescription}
                  onChange={(e) => setNewPortfolioDescription(e.target.value)}
                  className="w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  placeholder="Ex: Investimentos de longo prazo"
                />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setShowAddPortfolioModal(false)}
                  className="mr-3 px-4 py-2 bg-gray-800 rounded-md text-gray-300 font-medium hover:bg-gray-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
                >
                  Criar Portfólio
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Modal para adicionar token */}
      {showAddTokenModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-[#1A1C31] rounded-lg shadow-xl max-w-md w-full p-6 relative">
            <button
              onClick={() => setShowAddTokenModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              ×
            </button>
            
            <h2 className="text-xl font-bold mb-6">Adicionar Token</h2>
            
            <form onSubmit={handleAddToken}>
              <div className="mb-4">
                <label htmlFor="tokenSymbol" className="block text-gray-300 mb-2 font-medium">
                  Símbolo
                </label>
                <input
                  id="tokenSymbol"
                  type="text"
                  value={newToken.symbol}
                  onChange={(e) => setNewToken({...newToken, symbol: e.target.value})}
                  className="w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  placeholder="Ex: BTC"
                  required
                />
              </div>
              
              <div className="mb-4">
                <label htmlFor="tokenAmount" className="block text-gray-300 mb-2 font-medium">
                  Quantidade
                </label>
                <input
                  id="tokenAmount"
                  type="number"
                  step="any"
                  value={newToken.amount}
                  onChange={(e) => setNewToken({...newToken, amount: e.target.value})}
                  className="w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  placeholder="Ex: 0.5"
                  required
                />
              </div>
              
              <div className="mb-4">
                <label htmlFor="tokenPrice" className="block text-gray-300 mb-2 font-medium">
                  Preço de Compra (USD)
                </label>
                <input
                  id="tokenPrice"
                  type="number"
                  step="any"
                  value={newToken.purchase_price}
                  onChange={(e) => setNewToken({...newToken, purchase_price: e.target.value})}
                  className="w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  placeholder="Ex: 50000"
                  required
                />
              </div>
              
              <div className="mb-6">
                <label htmlFor="purchaseDate" className="block text-gray-300 mb-2 font-medium">
                  Data de Compra
                </label>
                <input
                  id="purchaseDate"
                  type="date"
                  value={newToken.purchase_date}
                  onChange={(e) => setNewToken({...newToken, purchase_date: e.target.value})}
                  className="w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  required
                />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setShowAddTokenModal(false)}
                  className="mr-3 px-4 py-2 bg-gray-800 rounded-md text-gray-300 font-medium hover:bg-gray-700"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md text-white font-medium hover:opacity-90 transition-opacity"
                >
                  Adicionar Token
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioPage;