// frontend/src/hooks/useTokenAnalysis.ts - Criado em 21/03/2025 14:55
/**
 * Hook para análise de tokens.
 * Encapsula a lógica de chamadas à API para análise de tokens.
 */
import { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import { TokenAnalysis } from '../types/models';

interface TokenAnalysisOptions {
  includeOnchain?: boolean;
  includeSentiment?: boolean;
}

export function useTokenAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<TokenAnalysis | null>(null);

  const analyzeToken = useCallback(async (
    symbolOrUrl: string, 
    options: TokenAnalysisOptions = {}
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      // Determinar se é um símbolo ou URL
      const isUrl = symbolOrUrl.startsWith('http');
      
      const requestData = {
        [isUrl ? 'url' : 'symbol']: symbolOrUrl,
        include_onchain: !!options.includeOnchain,
        include_sentiment: !!options.includeSentiment,
        user_id: 'current' // API irá extrair do token JWT
      };
      
      const response = await apiService.post<TokenAnalysis>('/api/analysis', requestData);
      setAnalysis(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao analisar token');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getAnalysisById = useCallback(async (analysisId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.get<TokenAnalysis>(`/api/analysis/${analysisId}`);
      setAnalysis(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar análise');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getUserAnalyses = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.get<TokenAnalysis[]>('/api/analysis/user/current');
      return response.data;
    } catch (err: any) {
      setError(err.message || 'Erro ao buscar análises do usuário');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    analyzeToken,
    getAnalysisById,
    getUserAnalyses,
    analysis,
    loading,
    error,
  };
}