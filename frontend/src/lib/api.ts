import axios from 'axios';

// Configuração da API
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Serviço de autenticação
const auth = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  register: async (email: string, password: string, name: string) => {
    const response = await api.post('/auth/register', { email, password, name });
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('token');
  },
  getUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Serviço de análise
const analysis = {
  getTechnicalAnalysis: async (params: {
    symbol: string;
    contract_address?: string;
    blockchain?: string;
  }) => {
    const response = await api.get('/analysis/technical', { params });
    return response.data;
  },
  getSentimentAnalysis: async (params: {
    symbol: string;
    contract_address?: string;
    blockchain?: string;
  }) => {
    const response = await api.get('/analysis/sentiment', { params });
    return response.data;
  },
  getOnchainAnalysis: async (params: {
    symbol: string;
    contract_address: string;
    blockchain: string;
  }) => {
    const response = await api.get('/analysis/onchain', { params });
    return response.data;
  },
};

// Serviço de portfólio
const portfolio = {
  getUserPortfolios: async () => {
    const response = await api.get('/portfolio');
    return response.data;
  },
  getPortfolioById: async (id: string) => {
    const response = await api.get(`/portfolio/${id}`);
    return response.data;
  },
  createPortfolio: async (data: { name: string }) => {
    const response = await api.post('/portfolio', data);
    return response.data;
  },
  updatePortfolio: async (id: string, data: { name: string }) => {
    const response = await api.put(`/portfolio/${id}`, data);
    return response.data;
  },
  deletePortfolio: async (id: string) => {
    const response = await api.delete(`/portfolio/${id}`);
    return response.data;
  },
  addAsset: async (portfolioId: string, data: { symbol: string; amount: number }) => {
    const response = await api.post(`/portfolio/${portfolioId}/assets`, data);
    return response.data;
  },
  updateAsset: async (portfolioId: string, assetId: string, data: { amount: number }) => {
    const response = await api.put(`/portfolio/${portfolioId}/assets/${assetId}`, data);
    return response.data;
  },
  removeAsset: async (portfolioId: string, assetId: string) => {
    const response = await api.delete(`/portfolio/${portfolioId}/assets/${assetId}`);
    return response.data;
  },
};

// Serviço de dados DeFi
const defiData = {
  getOverview: async () => {
    const response = await api.get('/defi-data/overview');
    return response.data;
  },
  getTVL: async () => {
    const response = await api.get('/defi-data/tvl');
    return response.data;
  },
  getProtocolData: async (protocol: string) => {
    const response = await api.get(`/defi-data/protocol/${protocol}`);
    return response.data;
  },
  getYields: async () => {
    const response = await api.get('/defi-data/yields');
    return response.data;
  },
  getFearGreedIndex: async () => {
    const response = await api.get('/defi-data/fear-greed');
    return response.data;
  },
  getMarketSentiment: async () => {
    const response = await api.get('/defi-data/market-sentiment');
    return response.data;
  },
};

export default {
  auth,
  analysis,
  portfolio,
  defiData,
}; 