"""
Agente de análise on-chain para tokens.
"""
import asyncio
import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

from ..core.base_agent import BaseAgent
from ..integrations.blockchain_explorer import blockchain_explorer_client
from ..integrations.coingecko import coingecko_client

class OnchainAgent(BaseAgent):
    """
    Agente especializado em análise on-chain de tokens baseado em exploradores de blockchain e APIs gratuitas.
    """
    
    def __init__(self):
        """Inicializa o agente de análise on-chain."""
        super().__init__()
        self.description = "Agente especializado em análise on-chain de tokens"
        # Adicionar nome para o agent_manager
        self.name = "OnchainAgent"
        # Remover a dependência do DataFetcher que foi descontinuado
        # self.data_fetcher = DataFetcher()
        
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Valida os dados de entrada para análise on-chain.
        
        Args:
            data: Dados de entrada contendo o endereço do token e a blockchain.
            
        Returns:
            True se os dados forem válidos, False caso contrário.
        """
        if not data:
            logger.error("Dados de entrada vazios")
            return False
            
        required_fields = ['address', 'chain']
        if not all(field in data for field in required_fields):
            logger.error(f"Campos obrigatórios não fornecidos: {required_fields}")
            return False
            
        # Validar formato do endereço
        address = data.get('address', '')
        if not address.startswith('0x') or len(address) != 42:
            logger.error(f"Endereço do token inválido: {address}")
            return False
            
        # Validar chain suportada
        supported_chains = ['eth', 'bsc', 'polygon', 'arbitrum', 'optimism']
        chain = data.get('chain', '').lower()
        if chain not in supported_chains:
            logger.error(f"Chain não suportada: {chain}. Chains suportadas: {supported_chains}")
            return False
            
        return True
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza a análise on-chain do token.
        
        Args:
            data: Dados de entrada contendo o endereço do token e a blockchain.
            
        Returns:
            Dicionário com os resultados da análise on-chain.
        """
        if not await self.validate_input(data):
            return {"error": "Dados de entrada inválidos"}
            
        try:
            address = data['address']
            chain = data['chain'].lower()
            logger.info(f"Iniciando análise on-chain para o token: {address} na chain {chain}")
            
            # Obter dados on-chain de diferentes fontes em paralelo
            contract_info, holders_data, transactions_data, price_data = await asyncio.gather(
                blockchain_explorer_client.get_token_contract_info(address, chain),
                blockchain_explorer_client.get_token_holders(address, chain),
                blockchain_explorer_client.get_token_transactions(address, chain, limit=50),
                self._get_market_data(address, chain)
            )
            
            # Analisar distribuição de holders
            holder_analysis = self._analyze_holders(holders_data)
            
            # Analisar transações
            transaction_analysis = self._analyze_transactions(transactions_data)
            
            # Analisar liquidez e métricas de mercado
            liquidity_analysis = self._analyze_liquidity(price_data, contract_info)
            
            # Analisar riscos
            risk_assessment = self._analyze_risks(contract_info, holder_analysis, transaction_analysis, liquidity_analysis)
            
            # Compilar resultados
            results = {
                "address": address,
                "chain": chain,
                "token_info": {
                    "name": contract_info.get("name", f"Token_{address[2:8]}"),
                    "symbol": contract_info.get("symbol", address[2:5].upper()),
                    "type": contract_info.get("token_type", "Unknown"),
                    "total_supply": contract_info.get("total_supply", 0),
                    "decimals": contract_info.get("decimals", 18),
                    "creation_date": contract_info.get("creation_date"),
                    "verified": contract_info.get("verified", False)
                },
                "holder_distribution": holder_analysis,
                "transaction_metrics": transaction_analysis,
                "liquidity_analysis": liquidity_analysis,
                "risk_assessment": risk_assessment,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            logger.info(f"Análise on-chain concluída para o token: {address}")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao realizar análise on-chain: {str(e)}")
            return {"error": f"Falha na análise: {str(e)}"}
    
    async def _get_market_data(self, address: str, chain: str) -> Dict[str, Any]:
        """
        Obtém dados de mercado para o token usando a API do CoinGecko.
        
        Args:
            address: Endereço do contrato do token.
            chain: Blockchain em que o token está.
            
        Returns:
            Dicionário com dados de mercado.
        """
        try:
            # Para tokens de grandes blockchains, podemos tentar obter dados do CoinGecko
            # Mapeia a chain para o formato do CoinGecko
            chain_map = {
                "eth": "ethereum",
                "bsc": "binance-smart-chain",
                "polygon": "polygon-pos",
                "arbitrum": "arbitrum-one",
                "optimism": "optimistic-ethereum"
            }
            
            # Tenta encontrar o token pelo endereço
            platform = chain_map.get(chain, "ethereum")
            
            # Infelizmente, a API gratuita do CoinGecko não permite busca direta por endereço
            # Vamos usar um método alternativo com dados de simulação
            
            # Em uma implementação real, usaríamos:
            # token_id = await coingecko_client.get_token_id_by_address(address, platform)
            # if token_id:
            #     return await coingecko_client.get_token_info(token_id)
            
            # Para este exemplo, vamos criar dados simulados baseados no endereço
            symbol = address[2:5].upper()
            
            # Verificar se é um token popular com base no símbolo
            popular_tokens = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "USDT": "tether",
                "BNB": "binancecoin",
                "MATIC": "matic-network"
            }
            
            if symbol in popular_tokens:
                # Para tokens populares, obtemos dados reais do CoinGecko
                return await coingecko_client.get_token_info(popular_tokens[symbol])
            
            # Para outros tokens, usamos dados simulados
            return self._generate_market_data(address, chain)
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {str(e)}")
            return self._generate_market_data(address, chain)
    
    def _generate_market_data(self, address: str, chain: str) -> Dict[str, Any]:
        """
        Gera dados de mercado simulados para demonstração.
        
        Args:
            address: Endereço do contrato do token.
            chain: Blockchain em que o token está.
            
        Returns:
            Dicionário com dados de mercado simulados.
        """
        # Usar o hash do endereço para gerar dados consistentes
        address_hash = sum(ord(c) for c in address)
        
        # Gerar dados simulados  
        current_price = (address_hash % 1000) / 100.0  # Entre 0.01 e 10.00
        market_cap = current_price * (10000000 + (address_hash % 990000000))  # Entre 10M e 1B
        volume_24h = market_cap * (0.05 + (address_hash % 100) / 1000)  # Entre 5% e 15% do market cap
        price_change_24h = ((address_hash % 40) - 20) / 10.0  # Entre -2% e 2%
        
        # Dados sobre DEXs e liquidez
        dexes = ["Uniswap", "SushiSwap", "PancakeSwap", "QuickSwap"]
        liquidity_by_dex = {}
        
        total_liquidity = market_cap * (0.1 + (address_hash % 50) / 100)  # Entre 10% e 60% do market cap
        remaining_liquidity = total_liquidity
        
        for i, dex in enumerate(dexes[:3]):
            if i == len(dexes) - 1:
                # Último DEX recebe o restante
                liquidity_by_dex[dex] = remaining_liquidity
            else:
                # Distribuir liquidez
                dex_liquidity = total_liquidity * ((30 + i * 15 + (address_hash % 20)) / 100)
                liquidity_by_dex[dex] = dex_liquidity
                remaining_liquidity -= dex_liquidity
        
        return {
            "price_data": {
                "current_price_usd": current_price,
                "market_cap_usd": market_cap,
                "volume_24h_usd": volume_24h,
                "price_change_24h_percentage": price_change_24h
            },
            "liquidity_data": {
                "total_liquidity_usd": total_liquidity,
                "liquidity_by_dex": liquidity_by_dex,
                "liquidity_to_marketcap_ratio": total_liquidity / market_cap if market_cap > 0 else 0
            },
            "exchange_data": {
                "listed_on_cex": address_hash % 10 > 6,  # 30% de chance de estar listado em CEX
                "dex_listings": len(liquidity_by_dex)
            }
        }
    
    def _analyze_holders(self, holders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa a distribuição de holders de um token.
        
        Args:
            holders: Lista de holders do token.
            
        Returns:
            Dicionário com a análise da distribuição de holders.
        """
        try:
            if not holders or "error" in holders[0]:
                return {
                    "total_holders": 0,
                    "error": "Dados de holders não disponíveis"
                }
            
            total_holders = len(holders)
            
            # Ordenar holders por quantidade
            sorted_holders = sorted(holders, key=lambda x: x.get("quantity", 0), reverse=True)
            
            # Calcular concentração de tokens
            top_holders = {
                "top_1": sorted_holders[0] if total_holders >= 1 else None,
                "top_5_percentage": sum(h.get("percentage", 0) for h in sorted_holders[:5]) if total_holders >= 5 else 0,
                "top_10_percentage": sum(h.get("percentage", 0) for h in sorted_holders[:10]) if total_holders >= 10 else 0,
                "top_50_percentage": sum(h.get("percentage", 0) for h in sorted_holders[:50]) if total_holders >= 50 else 0
            }
            
            # Calcular distribuição por tipo de holder
            holder_types = {}
            for h in holders:
                h_type = h.get("type", "Unknown")
                if h_type not in holder_types:
                    holder_types[h_type] = 0
                holder_types[h_type] += h.get("percentage", 0)
            
            # Distribuição de tokens por categoria de tamanho
            whale_threshold = 1.0  # Holders com mais de 1% são baleias
            large_holder_threshold = 0.1  # Holders com mais de 0.1% são grandes
            
            whales = [h for h in holders if h.get("percentage", 0) > whale_threshold]
            large_holders = [h for h in holders if whale_threshold >= h.get("percentage", 0) > large_holder_threshold]
            small_holders = [h for h in holders if h.get("percentage", 0) <= large_holder_threshold]
            
            distribution = {
                "whales": {
                    "count": len(whales),
                    "percentage_total": sum(h.get("percentage", 0) for h in whales)
                },
                "large_holders": {
                    "count": len(large_holders),
                    "percentage_total": sum(h.get("percentage", 0) for h in large_holders)
                },
                "small_holders": {
                    "count": len(small_holders),
                    "percentage_total": sum(h.get("percentage", 0) for h in small_holders)
                }
            }
            
            # Avaliar nível de descentralização
            decentralization_level = "alto"
            if top_holders["top_10_percentage"] > 80:
                decentralization_level = "muito baixo"
            elif top_holders["top_10_percentage"] > 60:
                decentralization_level = "baixo"
            elif top_holders["top_10_percentage"] > 40:
                decentralization_level = "médio"
            
            return {
                "total_holders": total_holders,
                "concentration": top_holders,
                "distribution_by_type": holder_types,
                "holder_size_distribution": distribution,
                "decentralization_level": decentralization_level
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar holders: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa as transações de um token.
        
        Args:
            transactions: Lista de transações do token.
            
        Returns:
            Dicionário com a análise das transações.
        """
        try:
            if not transactions or "error" in transactions[0]:
                return {
                    "total_transactions": 0,
                    "error": "Dados de transações não disponíveis"
                }
            
            total_transactions = len(transactions)
            
            # Calcular volume total
            total_volume = sum(tx.get("value", 0) for tx in transactions)
            
            # Contagem por tipo de transação
            buy_count = len([tx for tx in transactions if tx.get("transaction_type") == "Buy"])
            sell_count = len([tx for tx in transactions if tx.get("transaction_type") == "Sell"])
            other_count = total_transactions - buy_count - sell_count
            
            # Calcular proporção de compras vs vendas
            buy_sell_ratio = buy_count / sell_count if sell_count > 0 else float('inf')
            
            # Identificar endereços únicos nas transações
            unique_addresses = set()
            for tx in transactions:
                if "from" in tx:
                    unique_addresses.add(tx["from"])
                if "to" in tx:
                    unique_addresses.add(tx["to"])
            
            # Calcular frequência de transações
            now = datetime.datetime.now()
            tx_timestamps = []
            for tx in transactions:
                if "timestamp" in tx:
                    try:
                        tx_time = datetime.datetime.fromisoformat(tx["timestamp"].replace("Z", "+00:00"))
                        tx_timestamps.append(tx_time)
                    except (ValueError, TypeError):
                        pass
            
            if tx_timestamps:
                tx_timestamps.sort(reverse=True)
                oldest_tx = tx_timestamps[-1]
                newest_tx = tx_timestamps[0]
                
                time_span = (newest_tx - oldest_tx).total_seconds()
                if time_span > 0:
                    tx_frequency = total_transactions / (time_span / 86400)  # Transações por dia
                else:
                    tx_frequency = 0
            else:
                tx_frequency = 0
            
            # Identificar tendências recentes
            if buy_count > sell_count * 2:
                trend = "forte acumulação"
            elif buy_count > sell_count * 1.5:
                trend = "acumulação"
            elif sell_count > buy_count * 2:
                trend = "forte distribuição"
            elif sell_count > buy_count * 1.5:
                trend = "distribuição"
            else:
                trend = "neutral"
            
            return {
                "total_transactions": total_transactions,
                "total_volume": total_volume,
                "transaction_counts": {
                    "buys": buy_count,
                    "sells": sell_count,
                    "other": other_count
                },
                "buy_sell_ratio": buy_sell_ratio,
                "unique_addresses": len(unique_addresses),
                "transaction_frequency_per_day": tx_frequency,
                "recent_trend": trend
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar transações: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_liquidity(self, price_data: Dict[str, Any], contract_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a liquidez e dados de mercado de um token.
        
        Args:
            price_data: Dados de preço e liquidez do token.
            contract_info: Informações do contrato do token.
            
        Returns:
            Dicionário com a análise de liquidez.
        """
        try:
            if "error" in price_data:
                return {"error": "Dados de liquidez não disponíveis"}
            
            price_info = price_data.get("price_data", {})
            liquidity_info = price_data.get("liquidity_data", {})
            exchange_info = price_data.get("exchange_data", {})
            
            current_price = price_info.get("current_price_usd", 0)
            market_cap = price_info.get("market_cap_usd", 0)
            volume_24h = price_info.get("volume_24h_usd", 0)
            price_change = price_info.get("price_change_24h_percentage", 0)
            
            total_liquidity = liquidity_info.get("total_liquidity_usd", 0)
            liquidity_by_dex = liquidity_info.get("liquidity_by_dex", {})
            liquidity_ratio = liquidity_info.get("liquidity_to_marketcap_ratio", 0)
            
            # Calcular métricas de liquidez
            has_sufficient_liquidity = total_liquidity > 100000 or liquidity_ratio > 0.05
            liquidity_level = "alta" if liquidity_ratio > 0.2 else "média" if liquidity_ratio > 0.05 else "baixa"
            
            # Analisar distribuição de liquidez entre DEXs
            primary_dex = max(liquidity_by_dex.items(), key=lambda x: x[1])[0] if liquidity_by_dex else "Unknown"
            primary_dex_percentage = (liquidity_by_dex.get(primary_dex, 0) / total_liquidity * 100) if total_liquidity > 0 else 0
            
            # Verificar concentração de liquidez
            liquidity_concentration = "alta" if primary_dex_percentage > 80 else "média" if primary_dex_percentage > 50 else "baixa"
            
            # Calcular proporção volume/liquidez (V/L)
            volume_liquidity_ratio = volume_24h / total_liquidity if total_liquidity > 0 else 0
            v_l_ratio_healthy = volume_liquidity_ratio < 1.0  # V/L < 1 geralmente é mais saudável
            
            # Analisar listagens em exchanges
            exchange_liquidity_score = 0
            if exchange_info.get("listed_on_cex", False):
                exchange_liquidity_score += 3
            exchange_liquidity_score += min(exchange_info.get("dex_listings", 0), 3)
            
            exchange_access = "amplo" if exchange_liquidity_score >= 4 else "médio" if exchange_liquidity_score >= 2 else "limitado"
            
            return {
                "market_data": {
                    "price_usd": current_price,
                    "market_cap_usd": market_cap,
                    "volume_24h_usd": volume_24h,
                    "price_change_24h": f"{price_change:.2f}%"
                },
                "liquidity_metrics": {
                    "total_liquidity_usd": total_liquidity,
                    "liquidity_to_market_cap_ratio": liquidity_ratio,
                    "volume_to_liquidity_ratio": volume_liquidity_ratio,
                    "has_sufficient_liquidity": has_sufficient_liquidity,
                    "liquidity_level": liquidity_level
                },
                "liquidity_distribution": {
                    "dexes": list(liquidity_by_dex.keys()),
                    "primary_dex": primary_dex,
                    "primary_dex_percentage": primary_dex_percentage,
                    "concentration_level": liquidity_concentration
                },
                "exchange_availability": {
                    "listed_on_cex": exchange_info.get("listed_on_cex", False),
                    "dex_count": exchange_info.get("dex_listings", 0),
                    "access_level": exchange_access
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar liquidez: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_risks(self, contract_info: Dict[str, Any], holder_analysis: Dict[str, Any], 
                       transaction_analysis: Dict[str, Any], liquidity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa os riscos on-chain de um token com base nas análises anteriores.
        
        Args:
            contract_info: Informações do contrato do token.
            holder_analysis: Análise da distribuição de holders.
            transaction_analysis: Análise das transações.
            liquidity_analysis: Análise de liquidez.
            
        Returns:
            Dicionário com a análise de riscos.
        """
        try:
            risks = []
            risk_level = "baixo"
            
            # Verificar riscos relacionados ao contrato
            if not contract_info.get("verified", False):
                risks.append({
                    "category": "contrato",
                    "description": "Contrato não verificado",
                    "severity": "alto"
                })
                risk_level = "alto"
            
            # Verificar riscos de concentração de tokens
            top10_percentage = holder_analysis.get("concentration", {}).get("top_10_percentage", 0)
            if top10_percentage > 80:
                risks.append({
                    "category": "concentração",
                    "description": f"Alta concentração de tokens ({top10_percentage:.1f}% nos top 10 endereços)",
                    "severity": "alto"
                })
                risk_level = max(risk_level, "alto", key=lambda x: {"baixo": 0, "médio": 1, "alto": 2}[x])
            elif top10_percentage > 60:
                risks.append({
                    "category": "concentração",
                    "description": f"Concentração moderada de tokens ({top10_percentage:.1f}% nos top 10 endereços)",
                    "severity": "médio"
                })
                risk_level = max(risk_level, "médio", key=lambda x: {"baixo": 0, "médio": 1, "alto": 2}[x])
            
            # Verificar riscos de liquidez
            liquidity_metrics = liquidity_analysis.get("liquidity_metrics", {})
            if not liquidity_metrics.get("has_sufficient_liquidity", True):
                risks.append({
                    "category": "liquidez",
                    "description": "Liquidez insuficiente para trading seguro",
                    "severity": "alto"
                })
                risk_level = max(risk_level, "alto", key=lambda x: {"baixo": 0, "médio": 1, "alto": 2}[x])
            
            liquidity_concentration = liquidity_analysis.get("liquidity_distribution", {}).get("concentration_level", "")
            if liquidity_concentration == "alta":
                risks.append({
                    "category": "liquidez",
                    "description": "Liquidez altamente concentrada em uma única DEX",
                    "severity": "médio"
                })
                risk_level = max(risk_level, "médio", key=lambda x: {"baixo": 0, "médio": 1, "alto": 2}[x])
            
            # Verificar riscos de transações
            buy_sell_ratio = transaction_analysis.get("buy_sell_ratio", 1.0)
            recent_trend = transaction_analysis.get("recent_trend", "")
            
            if buy_sell_ratio > 5:
                risks.append({
                    "category": "transações",
                    "description": "Padrão de compras anormalmente alto - possível pump",
                    "severity": "médio"
                })
                risk_level = max(risk_level, "médio", key=lambda x: {"baixo": 0, "médio": 1, "alto": 2}[x])
            elif buy_sell_ratio < 0.2:
                risks.append({
                    "category": "transações",
                    "description": "Padrão de vendas anormalmente alto - possível dump",
                    "severity": "alto"
                })
                risk_level = max(risk_level, "alto", key=lambda x: {"baixo": 0, "médio": 1, "alto": 2}[x])
            
            # Consolidar análise de risco
            total_severity = len([r for r in risks if r["severity"] == "alto"]) * 3 + len([r for r in risks if r["severity"] == "médio"]) * 1
            
            if total_severity >= 4:
                summary = "Alto risco - Recomenda-se extrema cautela"
            elif total_severity >= 2:
                summary = "Risco moderado - Realize diligência adicional"
            else:
                summary = "Risco baixo - Métricas on-chain saudáveis"
            
            # Identificar pontos positivos
            strengths = []
            
            if contract_info.get("verified", False):
                strengths.append("Contrato verificado")
                
            if top10_percentage < 40:
                strengths.append("Boa distribuição de tokens")
                
            if liquidity_metrics.get("has_sufficient_liquidity", False) and liquidity_metrics.get("liquidity_level", "") == "alta":
                strengths.append("Liquidez robusta")
                
            if liquidity_analysis.get("exchange_availability", {}).get("listed_on_cex", False):
                strengths.append("Listado em exchanges centralizadas")
                
            if 0.8 <= buy_sell_ratio <= 1.2:
                strengths.append("Padrão de transações equilibrado")
                
            return {
                "overall_risk_level": risk_level,
                "risk_summary": summary,
                "risk_factors": risks,
                "strengths": strengths,
                "risk_count": {
                    "alto": len([r for r in risks if r["severity"] == "alto"]),
                    "médio": len([r for r in risks if r["severity"] == "médio"]),
                    "baixo": len([r for r in risks if r["severity"] == "baixo"])
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar riscos: {str(e)}")
            return {"error": str(e)}
