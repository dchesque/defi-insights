// frontend/src/types/models.ts - Criado em 21/03/2025 14:45
/**
 * Definições de tipos para os modelos de dados da API.
 * Facilita o trabalho com TypeScript e proporciona autocompletar nos editores.
 */

// Modelos de usuário e autenticação
export interface User {
    id: string;
    email: string;
    name: string;
    created_at: string;
  }
  
  export interface AuthToken {
    access_token: string;
    token_type: string;
    expires_in: number;
    refresh_token?: string;
  }
  
  // Modelos para análise de tokens
  export interface TokenPrice {
    current: number;
    change_24h: number;
    change_7d?: number;
    change_30d?: number;
  }
  
  export interface MarketData {
    market_cap: number;
    volume_24h: number;
    circulating_supply: number;
    total_supply?: number;
    max_supply?: number;
    rank?: number;
  }
  
  export interface TokenAdditionalInfo {
    description?: string;
    homepage?: string;
    github?: string[];
    twitter?: string;
    telegram?: string;
    blockchain_explorers?: string[];
    categories?: string[];
  }
  
  export interface TokenAnalysis {
    analysis_id: string;
    symbol: string;
    name?: string;
    price?: TokenPrice;
    market_data?: MarketData;
    sentiment?: SentimentAnalysis;
    onchain?: OnchainAnalysis;
    additional_info?: TokenAdditionalInfo;
    timestamp: string;
  }
  
  // Modelos para análise de sentimento
  export interface SentimentSource {
    score: number;
    sentiment: string;
    confidence: number;
    no_data?: boolean;
  }
  
  export interface EngagementMetrics {
    total_mentions: number;
    mentions_by_source: Record<string, number>;
    activity_level: string;
    trend: string;
  }
  
  export interface DiscussionTrend {
    theme: string;
    relevance: string;
    sentiment: string;
    keywords: string[];
  }
  
  export interface SentimentAnalysis {
    overall_sentiment: {
      score: number;
      sentiment: string;
      confidence: number;
      sources_count: number;
    };
    sentiment_by_source: Record<string, SentimentSource>;
    engagement_metrics: EngagementMetrics;
    discussion_trends: DiscussionTrend[];
  }
  
  // Modelos para análise on-chain
  export interface ContractInfo {
    address: string;
    chain: string;
    is_contract: boolean;
    token_name?: string;
    token_symbol?: string;
    balance?: number;
    token_data?: any;
  }
  
  export interface HolderAnalysis {
    total_holders: number;
    top_10_concentration_percent: number;
    concentration_risk: string;
    distribution_score: number;
    top_holders: any[];
  }
  
  export interface TransactionAnalysis {
    total_transactions: number;
    unique_addresses: number;
    avg_transaction_value: number;
    transaction_frequency: string;
    recent_transactions: any[];
  }
  
  export interface LiquidityAnalysis {
    liquidity_score: number;
    liquidity_level: string;
    volume_to_mcap_ratio?: number;
    market_cap_usd?: number;
    volume_24h_usd?: number;
    fdv_to_mcap_ratio?: number;
  }
  
  export interface RiskAnalysis {
    risk_score: number;
    risk_level: string;
    risk_factors: string[];
    concentration_risk: string;
    liquidity_risk: string;
  }
  
  export interface OnchainAnalysis {
    token_address: string;
    chain: string;
    contract_info?: ContractInfo;
    holder_analysis?: HolderAnalysis;
    transaction_analysis?: TransactionAnalysis;
    liquidity_analysis?: LiquidityAnalysis;
    risk_analysis?: RiskAnalysis;
    price_data?: any;
    analysis_timestamp: string;
  }
  
  // Modelos para portfólio
  export interface PortfolioToken {
    id: string;
    symbol: string;
    name: string;
    amount: number;
    purchase_price: number;
    purchase_date: string;
    current_price?: number;
    current_value?: number;
    profit_loss?: number;
    profit_loss_percentage?: number;
  }
  
  export interface Portfolio {
    id: string;
    name: string;
    description?: string;
    user_id: string;
    tokens: PortfolioToken[];
    total_value?: number;
    total_invested?: number;
    profit_loss?: number;
    profit_loss_percentage?: number;
    created_at: string;
    updated_at: string;
  }

  export interface ApiErrorResponse {
    success: false;
    message: string;
    timestamp: string;
    request_id: string;
    error_code?: string;
    details?: any;
    path?: string;
  }

  export interface ApiResponse<T> {
    success: boolean;
    message: string;
    data: T;
    timestamp: string;
    request_id: string;
    metadata?: any;
  }
  
  export interface PaginatedResponse<T> extends ApiResponse<T[]> {
    pagination: {
      page: number;
      page_size: number;
      total_items: number;
      total_pages: number;
      has_next: boolean;
      has_previous: boolean;
    };
  }