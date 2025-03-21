// frontend/src/hooks/usePortfolio.ts - Criado em 21/03/2025 15:15
/**
 * Hook para gerenciamento de portfólio.
 */
import { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import { Portfolio, PortfolioToken } from '../types/models';

interface CreatePortfolioData {
  name: string;
  description?: string;
}

interface UpdatePortfolioData {
  name?: string;
  description?: string;
}

interface AddTokenData {
  symbol: string;
  amount: number;
  purchase_price: number;
  purchase_date: string;
  address?: string;
  chain?: string;
}

export function usePortfolio() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getUserPortfolios = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.get<Portfolio[]>('/api/portfolio');
      setPortfolios(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar portfólios');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const getPortfolioById = useCallback(async (portfolioId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.get<Portfolio>(`/api/portfolio/${portfolioId}`);
      setSelectedPortfolio(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar portfólio');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const createPortfolio = useCallback(async (data: CreatePortfolioData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.post<Portfolio>('/api/portfolio', data);
      
      // Atualizar a lista de portfólios
      setPortfolios(prev => [...prev, response.data]);
      
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao criar portfólio');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updatePortfolio = useCallback(async (portfolioId: string, data: UpdatePortfolioData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.put<Portfolio>(`/api/portfolio/${portfolioId}`, data);
      
      // Atualizar a lista de portfólios
      setPortfolios(prev => 
        prev.map(p => p.id === portfolioId ? response.data : p)
      );
      
      // Atualizar o portfólio selecionado se for o mesmo
      if (selectedPortfolio?.id === portfolioId) {
        setSelectedPortfolio(response.data);
      }
      
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao atualizar portfólio');
      return null;
    } finally {
      setLoading(false);
    }
  }, [selectedPortfolio]);

  const deletePortfolio = useCallback(async (portfolioId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      await apiService.delete(`/api/portfolio/${portfolioId}`);
      
      // Remover da lista de portfólios
      setPortfolios(prev => prev.filter(p => p.id !== portfolioId));
      
      // Limpar o portfólio selecionado se for o mesmo
      if (selectedPortfolio?.id === portfolioId) {
        setSelectedPortfolio(null);
      }
      
      return true;
    } catch (err: any) {
      setError(err.message || 'Erro ao excluir portfólio');
      return false;
    } finally {
      setLoading(false);
    }
  }, [selectedPortfolio]);

  const addToken = useCallback(async (portfolioId: string, tokenData: AddTokenData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.post<Portfolio>(
        `/api/portfolio/${portfolioId}/assets`, 
        tokenData
      );
      
      // Atualizar a lista de portfólios
      setPortfolios(prev => 
        prev.map(p => p.id === portfolioId ? response.data : p)
      );
      
      // Atualizar o portfólio selecionado se for o mesmo
      if (selectedPortfolio?.id === portfolioId) {
        setSelectedPortfolio(response.data);
      }
      
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao adicionar token');
      return null;
    } finally {
      setLoading(false);
    }
  }, [selectedPortfolio]);

  const removeToken = useCallback(async (portfolioId: string, tokenId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.delete<Portfolio>(
        `/api/portfolio/${portfolioId}/assets/${tokenId}`
      );
      
      // Atualizar a lista de portfólios
      setPortfolios(prev => 
        prev.map(p => p.id === portfolioId ? response.data : p)
      );
      
      // Atualizar o portfólio selecionado se for o mesmo
      if (selectedPortfolio?.id === portfolioId) {
        setSelectedPortfolio(response.data);
      }
      
      return true;
    } catch (err: any) {
      setError(err.message || 'Erro ao remover token');
      return false;
    } finally {
      setLoading(false);
    }
  }, [selectedPortfolio]);

  return {
    portfolios,
    selectedPortfolio,
    loading,
    error,
    getUserPortfolios,
    getPortfolioById,
    createPortfolio,
    updatePortfolio,
    deletePortfolio,
    addToken,
    removeToken
  };
}