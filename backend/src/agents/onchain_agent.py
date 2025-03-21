"""
Agente de análise on-chain para tokens.
"""
import asyncio
import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
import re
import json
import logging

from ..core.base_agent import BaseAgent
from ..integrations.blockchain_explorer import BlockchainExplorerClient
from ..integrations.coingecko import CoinGeckoClient
from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class OnchainAgent(BaseAgent):
    """
    Agente responsável por analisar dados on-chain de contratos inteligentes em diferentes blockchains.
    Fornece análises detalhadas sobre tokens, holders, transações e métricas on-chain.
    """
    
    def __init__(self):
        """Inicializa o OnchainAgent com clientes de blockchain e APIs."""
        super().__init__()
        self.name = "onchain_agent"
        self.blockchain_explorer = BlockchainExplorerClient()
        self.coingecko = CoinGeckoClient()
        self.description = "Agente responsável por analisar dados on-chain de contratos inteligentes em diferentes blockchains."
        logger.info("OnchainAgent inicializado com sucesso")
        
    async def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa um token com base em dados on-chain.
        
        Args:
            input_data: Dicionário contendo 'address' e 'chain' do token
            
        Returns:
            Dicionário com análise detalhada do token, incluindo informações do contrato,
            análise de holders, análise de transações, análise de liquidez e riscos.
        """
        try:
            # Extrair e validar dados de entrada
            address = input_data.get("address")
            chain = input_data.get("chain", "ethereum")
            
            if not address:
                logger.error("Endereço do token não fornecido")
                return {"error": "Endereço do token é obrigatório"}
                
            # Validar formato do endereço
            if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
                logger.error(f"Formato de endereço inválido: {address}")
                return {"error": "Formato de endereço inválido"}
                
            logger.info(f"Iniciando análise do token {address} na chain {chain}")
                
            # Obter informações do contrato
            contract_info = await self.blockchain_explorer.get_address_info(address, chain)
            
            if contract_info.get("error"):
                logger.error(f"Erro ao obter informações do contrato: {contract_info['error']}")
                return {"error": contract_info['error']}
                
            # Obter holders do token
            holders_info = await self.blockchain_explorer.get_token_holders(address, chain)
            
            # Obter transações recentes do token
            transactions = await self.blockchain_explorer.get_token_transactions(address, chain)
            
            # Obter dados do mercado (CoinGecko)
            market_data = await self._get_market_data(address, chain)
            
            # Analisar distribuição de holders
            holder_analysis = self._analyze_holders(holders_info)
            
            # Analisar transações
            transaction_analysis = self._analyze_transactions(transactions)
            
            # Calcular métricas de liquidez e risco
            liquidity_analysis = self._analyze_liquidity(holder_analysis, market_data)
            risk_analysis = self._analyze_risk(holder_analysis, transaction_analysis, liquidity_analysis)
            
            # Compilar resultados
            return {
                "token_address": address,
                "chain": chain,
                "contract_info": contract_info,
                "holder_analysis": holder_analysis,
                "transaction_analysis": transaction_analysis,
                "liquidity_analysis": liquidity_analysis,
                "risk_analysis": risk_analysis,
                "price_data": market_data.get("price_data", {}),
                "analysis_timestamp": self.blockchain_explorer._get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Erro durante análise on-chain: {str(e)}")
            return {"error": f"Falha na análise on-chain: {str(e)}"}
            
    async def _get_market_data(self, address: str, chain: str) -> Dict[str, Any]:
        """
        Obtém dados de mercado do token utilizando o CoinGecko.
        
        Args:
            address: Endereço do contrato do token
            chain: Blockchain onde o token está listado
            
        Returns:
            Dados de mercado do token
        """
        try:
            # Tentar encontrar o token_id baseado no endereço e chain
            token_info = await self.coingecko.get_coin_by_contract(address, chain)
            
            if not token_info or "error" in token_info:
                logger.warning(f"Token {address} não encontrado no CoinGecko. Retornando dados limitados.")
                return {
                    "price_data": {
                        "current_price_usd": None,
                        "market_cap_usd": None,
                        "price_change_24h": None
                    },
                    "symbol": contract_info.get("token_symbol", ""),
                    "name": contract_info.get("token_name", "")
                }
                
            token_id = token_info.get("id")
            
            # Obter dados completos do token
            full_token_data = await self.coingecko.get_token_info(token_id)
            
            return full_token_data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {str(e)}")
            return {"price_data": {}, "error": str(e)}
            
    def _analyze_holders(self, holders_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa a distribuição de holders do token.
        
        Args:
            holders_data: Lista de holders com seus respectivos saldos
            
        Returns:
            Análise da distribuição de holders
        """
        try:
            total_holders = len(holders_data)
            
            if total_holders == 0:
                return {
                    "total_holders": 0,
                    "concentration_risk": "Alto",
                    "distribution_score": 0,
                    "top_holders": []
                }
                
            # Ordenar holders por saldo
            sorted_holders = sorted(holders_data, key=lambda x: float(x.get("balance", 0)), reverse=True)
            
            # Calcular balanço total
            try:
                total_balance = sum(float(holder.get("balance", 0)) for holder in holders_data)
            except (ValueError, TypeError):
                total_balance = 0
                
            # Analisar top holders
            top_10_holders = sorted_holders[:10] if len(sorted_holders) >= 10 else sorted_holders
            
            # Calcular concentração dos top 10
            top_10_concentration = 0
            if total_balance > 0:
                top_10_balance = sum(float(holder.get("balance", 0)) for holder in top_10_holders)
                top_10_concentration = (top_10_balance / total_balance) * 100
                
            # Determinar risco de concentração
            concentration_risk = "Alto" if top_10_concentration > 80 else "Médio" if top_10_concentration > 50 else "Baixo"
            
            # Calcular score de distribuição (0-100)
            distribution_score = 100 - top_10_concentration
            
            return {
                "total_holders": total_holders,
                "top_10_concentration_percent": round(top_10_concentration, 2),
                "concentration_risk": concentration_risk,
                "distribution_score": round(distribution_score, 2),
                "top_holders": top_10_holders
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar holders: {str(e)}")
            return {"error": str(e), "total_holders": 0}
            
    def _analyze_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa as transações recentes do token.
        
        Args:
            transactions: Lista de transações do token
            
        Returns:
            Análise das transações do token
        """
        try:
            total_txs = len(transactions)
            
            if total_txs == 0:
                return {
                    "total_transactions": 0,
                    "unique_addresses": 0,
                    "avg_transaction_value": 0,
                    "transaction_frequency": "Baixa",
                    "recent_transactions": []
                }
                
            # Extrair endereços únicos
            unique_addresses = set()
            for tx in transactions:
                unique_addresses.add(tx.get("from_address", ""))
                unique_addresses.add(tx.get("to_address", ""))
                
            # Calcular valor médio das transações (excluindo zeros)
            try:
                tx_values = [float(tx.get("value", 0)) for tx in transactions if float(tx.get("value", 0)) > 0]
                avg_value = sum(tx_values) / len(tx_values) if tx_values else 0
            except (ValueError, TypeError, ZeroDivisionError):
                avg_value = 0
                
            # Determinar frequência de transações
            transaction_frequency = "Alta" if total_txs > 100 else "Média" if total_txs > 50 else "Baixa"
            
            return {
                "total_transactions": total_txs,
                "unique_addresses": len(unique_addresses),
                "avg_transaction_value": round(avg_value, 6),
                "transaction_frequency": transaction_frequency,
                "recent_transactions": transactions[:5] if transactions else []
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar transações: {str(e)}")
            return {"error": str(e), "total_transactions": 0}
            
    def _analyze_liquidity(self, holder_analysis: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa métricas de liquidez do token.
        
        Args:
            holder_analysis: Análise dos holders do token
            market_data: Dados de mercado do token
            
        Returns:
            Análise de liquidez do token
        """
        try:
            # Extrair dados relevantes
            price_data = market_data.get("price_data", {})
            liquidity_data = market_data.get("liquidity_data", {})
            
            market_cap = price_data.get("market_cap_usd")
            volume_24h = price_data.get("total_volume_usd")
            fdv_to_mcap = liquidity_data.get("fdv_to_mcap_ratio")
            
            # Calcular score de liquidez (0-100)
            liquidity_score = 0
            
            # Fator 1: Volume/Market Cap ratio (quanto maior, melhor)
            vol_to_mcap_ratio = (volume_24h / market_cap) if all([volume_24h, market_cap]) and market_cap > 0 else 0
            vol_score = min(50, vol_to_mcap_ratio * 100) 
            
            # Fator 2: Distribuição de holders (de holder_analysis)
            distribution_score = holder_analysis.get("distribution_score", 0)
            
            # Calcular score final
            liquidity_score = vol_score * 0.6 + distribution_score * 0.4
            
            # Determinar nível de liquidez
            liquidity_level = "Alta" if liquidity_score > 70 else "Média" if liquidity_score > 40 else "Baixa"
            
            return {
                "liquidity_score": round(liquidity_score, 2),
                "liquidity_level": liquidity_level,
                "volume_to_mcap_ratio": round(vol_to_mcap_ratio, 6) if vol_to_mcap_ratio else None,
                "market_cap_usd": market_cap,
                "volume_24h_usd": volume_24h,
                "fdv_to_mcap_ratio": fdv_to_mcap
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar liquidez: {str(e)}")
            return {"liquidity_score": 0, "liquidity_level": "Desconhecida", "error": str(e)}
            
    def _analyze_risk(self, holder_analysis: Dict[str, Any], tx_analysis: Dict[str, Any], 
                      liquidity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia o perfil de risco do token com base nas análises anteriores.
        
        Args:
            holder_analysis: Análise dos holders do token
            tx_analysis: Análise das transações do token
            liquidity_analysis: Análise de liquidez do token
            
        Returns:
            Perfil de risco do token
        """
        try:
            # Extrair métricas relevantes
            concentration_risk = holder_analysis.get("concentration_risk", "Alto")
            liquidity_level = liquidity_analysis.get("liquidity_level", "Baixa")
            liquidity_score = liquidity_analysis.get("liquidity_score", 0)
            distribution_score = holder_analysis.get("distribution_score", 0)
            
            # Calcular score de risco (0-100, onde maior = mais arriscado)
            risk_score = 0
            
            # Fator 1: Concentração de holders (maior concentração = maior risco)
            risk_from_concentration = 100 - distribution_score
            
            # Fator 2: Liquidez (menor liquidez = maior risco)
            risk_from_liquidity = 100 - liquidity_score
            
            # Fator 3: Atividade de transações
            tx_frequency = tx_analysis.get("transaction_frequency", "Baixa")
            risk_from_tx = 80 if tx_frequency == "Baixa" else 40 if tx_frequency == "Média" else 20
            
            # Calcular score composto
            risk_score = risk_from_concentration * 0.4 + risk_from_liquidity * 0.4 + risk_from_tx * 0.2
            
            # Determinar nível de risco
            risk_level = "Alto" if risk_score > 70 else "Médio" if risk_score > 40 else "Baixo"
            
            # Identificar principais riscos
            risk_factors = []
            
            if risk_from_concentration > 70:
                risk_factors.append("Alta concentração de tokens em poucos holders")
                
            if risk_from_liquidity > 70:
                risk_factors.append("Baixa liquidez pode dificultar entradas e saídas")
                
            if tx_frequency == "Baixa":
                risk_factors.append("Baixa atividade de transações indica pouco interesse")
                
            return {
                "risk_score": round(risk_score, 2),
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "concentration_risk": concentration_risk,
                "liquidity_risk": "Alto" if liquidity_level == "Baixa" else "Médio" if liquidity_level == "Média" else "Baixo"
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar risco: {str(e)}")
            return {"risk_score": 100, "risk_level": "Desconhecido", "error": str(e)}

    async def validate_input(self, token_data: Dict[str, Any]) -> bool:
        """
        Valida os dados de entrada para análise onchain.
        
        Args:
            token_data: Dados do token para validação
            
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        if not token_data:
            logger.error("Dados de entrada estão vazios")
            return False
            
        # Verificar se temos o endereço ou o símbolo do token
        address = token_data.get("address")
        symbol = token_data.get("symbol")
        
        if not address and not symbol:
            logger.error("Nem o endereço nem o símbolo do token foram fornecidos")
            return False
            
        # Se o endereço foi fornecido, validar o formato
        if address:
            if not isinstance(address, str):
                logger.error(f"Endereço do token deve ser uma string, recebido: {type(address)}")
                return False
                
            # Verifica se parece um endereço Ethereum ou similar (0x seguido de 40 caracteres hex)
            if not (address.startswith("0x") and len(address) == 42 and all(c in "0123456789abcdefABCDEF" for c in address[2:])):
                logger.warning(f"Formato de endereço potencialmente inválido: {address}")
                # Não retornamos False aqui para permitir outros formatos de endereços em outras chains
        
        # Verificar chain (opcional)
        chain = token_data.get("chain", "ethereum")
        supported_chains = ["ethereum", "binance-smart-chain", "polygon", "avalanche", "solana", "arbitrum"]
        
        if chain not in supported_chains:
            logger.warning(f"Chain não suportada: {chain}. Usando ethereum como padrão.")
            # Não retornamos False, apenas alertamos
        
        return True
