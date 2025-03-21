"""
Modelos para a análise on-chain de tokens na blockchain.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class OnchainRequest(BaseModel):
    """
    Solicitação para análise on-chain de um token.
    """
    address: str = Field(..., description="Endereço do contrato do token na blockchain")
    chain: str = Field("eth", description="Blockchain onde o token está (eth, bsc, polygon, etc.)")
    user_id: str = Field(..., description="ID do usuário que solicitou a análise")

class ContractInfo(BaseModel):
    """
    Informações básicas do contrato do token.
    """
    address: str
    chain: str
    is_contract: bool = True
    token_name: Optional[str] = None
    token_symbol: Optional[str] = None
    balance: Optional[float] = None
    token_data: Dict[str, Any] = {}
    
class HolderInfo(BaseModel):
    """
    Informações de um detentor do token.
    """
    address: str
    balance: float
    percentage: float
    rank: Optional[int] = None
    address_label: Optional[str] = None

class HolderAnalysis(BaseModel):
    """
    Análise da distribuição de holders do token.
    """
    total_holders: int
    top_10_concentration_percent: float
    concentration_risk: str
    distribution_score: float
    top_holders: List[Dict[str, Any]] = []
    
class TransactionAnalysis(BaseModel):
    """
    Análise das transações do token.
    """
    total_transactions: int
    unique_addresses: int
    avg_transaction_value: float
    transaction_frequency: str
    recent_transactions: List[Dict[str, Any]] = []
    
class LiquidityAnalysis(BaseModel):
    """
    Análise de liquidez do token.
    """
    liquidity_score: float
    liquidity_level: str
    volume_to_mcap_ratio: Optional[float] = None
    market_cap_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    fdv_to_mcap_ratio: Optional[float] = None
    
class RiskAnalysis(BaseModel):
    """
    Análise de risco do token.
    """
    risk_score: float
    risk_level: str
    risk_factors: List[str] = []
    concentration_risk: str
    liquidity_risk: str
    
class PriceData(BaseModel):
    """
    Dados de preço do token.
    """
    current_price_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None
    total_volume_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_7d: Optional[float] = None
    all_time_high: Optional[float] = None
    all_time_low: Optional[float] = None
    
class OnchainResponse(BaseModel):
    """
    Resposta da análise on-chain de um token.
    """
    analysis_id: str
    token_address: str
    chain: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    result: Dict[str, Any] = {}
    
    class Config:
        """Configuração do modelo."""
        json_schema_extra = {
            "example": {
                "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                "token_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                "chain": "eth",
                "timestamp": "2023-11-09T14:57:23.123456",
                "result": {
                    "token_address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                    "chain": "eth",
                    "contract_info": {
                        "address": "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984",
                        "chain": "eth",
                        "is_contract": True,
                        "token_name": "Uniswap",
                        "token_symbol": "UNI"
                    },
                    "holder_analysis": {
                        "total_holders": 5000,
                        "top_10_concentration_percent": 45.8,
                        "concentration_risk": "Médio",
                        "distribution_score": 54.2
                    },
                    "transaction_analysis": {
                        "total_transactions": 12500,
                        "unique_addresses": 3200,
                        "avg_transaction_value": 125.45,
                        "transaction_frequency": "Alta"
                    },
                    "liquidity_analysis": {
                        "liquidity_score": 78.5,
                        "liquidity_level": "Alta",
                        "volume_to_mcap_ratio": 0.15,
                        "market_cap_usd": 4500000000,
                        "volume_24h_usd": 675000000
                    },
                    "risk_analysis": {
                        "risk_score": 35.2,
                        "risk_level": "Baixo",
                        "risk_factors": []
                    },
                    "price_data": {
                        "current_price_usd": 7.85,
                        "market_cap_usd": 4500000000,
                        "price_change_24h": 2.5
                    }
                }
            }
        } 