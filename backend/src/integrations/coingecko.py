"""
Cliente para a API do CoinGecko - uma fonte gratuita de dados de criptomoedas.
"""
import os
import httpx
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class CoinGeckoClient:
    """Cliente para interagir com a API pública do CoinGecko."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        """Inicializa o cliente do CoinGecko."""
        self.api_key = os.getenv("COINGECKO_API_KEY", None)  # API key é opcional para a versão gratuita
        
        self.cache = {}
        self.cache_ttl = {
            "price": 60,  # Cache de 1 minuto para dados de preço
            "coins": 900,  # Cache de 15 minutos para lista de moedas
            "markets": 300,  # Cache de 5 minutos para dados de mercado
            "historical": 3600,  # Cache de 1 hora para dados históricos
        }
        
        self.request_cooldown = 1.5  # Tempo de espera entre requisições (segundos) para respeitar limites da API gratuita
        self.last_request_time = datetime.now() - timedelta(seconds=10)  # Inicializa com um valor no passado
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, cache_category: str = "price") -> Dict[str, Any]:
        """
        Faz uma requisição para a API do CoinGecko respeitando limites de requisição.
        
        Args:
            endpoint: Caminho do endpoint da API.
            params: Parâmetros da query (opcional).
            cache_category: Categoria para determinar TTL do cache.
            
        Returns:
            Resposta da API em formato JSON.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Preparar parâmetros
        request_params = params.copy() if params else {}
        if self.api_key:
            request_params["x_cg_pro_api_key"] = self.api_key
        
        # Verificar se temos dados em cache
        cache_key = f"{endpoint}:{json.dumps(request_params)}"
        if cache_key in self.cache:
            # Verificar se o cache ainda é válido
            cached_data, timestamp = self.cache[cache_key]
            ttl = self.cache_ttl.get(cache_category, 300)  # Default 5 minutos
            if datetime.now() - timestamp < timedelta(seconds=ttl):
                return cached_data
        
        # Implementar cooldown entre requisições para API gratuita
        time_since_last_request = (datetime.now() - self.last_request_time).total_seconds()
        if time_since_last_request < self.request_cooldown:
            cooldown_time = self.request_cooldown - time_since_last_request
            if cooldown_time > 0:
                await asyncio.sleep(cooldown_time)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=request_params
                )
                
                # Atualizar timestamp da última requisição
                self.last_request_time = datetime.now()
                
                # Verificar se houve erro
                response.raise_for_status()
                
                # Armazenar resultado no cache
                result = response.json()
                self.cache[cache_key] = (result, datetime.now())
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao chamar a API do CoinGecko: {e.response.status_code} - {e.response.text}")
            raise
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do CoinGecko: {str(e)}")
            raise
    
    async def ping(self) -> bool:
        """
        Verifica se a API do CoinGecko está respondendo.
        
        Returns:
            True se a API estiver disponível, False caso contrário.
        """
        try:
            response = await self._make_request("ping")
            return "gecko_says" in response
        except Exception as e:
            logger.error(f"Erro ao fazer ping na API do CoinGecko: {str(e)}")
            return False
    
    async def get_coins_list(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de todas as moedas disponíveis na API.
        
        Returns:
            Lista de moedas com id, symbol e name.
        """
        try:
            return await self._make_request("coins/list", cache_category="coins")
        except Exception as e:
            logger.error(f"Erro ao obter lista de moedas: {str(e)}")
            return []
    
    async def search_coins(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca moedas pelo nome ou símbolo.
        
        Args:
            query: Termo de busca.
            
        Returns:
            Lista de moedas correspondentes à busca.
        """
        try:
            result = await self._make_request("search", {"query": query}, cache_category="coins")
            return result.get("coins", [])
        except Exception as e:
            logger.error(f"Erro ao buscar moedas com '{query}': {str(e)}")
            return []
    
    async def get_coin_data(self, coin_id: str, localization: bool = False, tickers: bool = False, 
                          market_data: bool = True, community_data: bool = False, 
                          developer_data: bool = False) -> Dict[str, Any]:
        """
        Obtém dados detalhados de uma moeda específica.
        
        Args:
            coin_id: ID da moeda no CoinGecko.
            localization: Incluir dados de localização.
            tickers: Incluir dados de tickers.
            market_data: Incluir dados de mercado.
            community_data: Incluir dados da comunidade.
            developer_data: Incluir dados de desenvolvimento.
            
        Returns:
            Dados detalhados da moeda.
        """
        params = {
            "localization": str(localization).lower(),
            "tickers": str(tickers).lower(),
            "market_data": str(market_data).lower(),
            "community_data": str(community_data).lower(),
            "developer_data": str(developer_data).lower()
        }
        
        try:
            return await self._make_request(f"coins/{coin_id}", params, cache_category="coins")
        except Exception as e:
            logger.error(f"Erro ao obter dados da moeda {coin_id}: {str(e)}")
            return {}
    
    async def get_coin_price(self, coin_ids: Union[str, List[str]], vs_currencies: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Obtém preços atuais de uma ou mais moedas.
        
        Args:
            coin_ids: ID ou lista de IDs das moedas.
            vs_currencies: Moeda ou lista de moedas de base para converter o preço.
            
        Returns:
            Dicionário com preços atuais.
        """
        if isinstance(coin_ids, list):
            ids = ",".join(coin_ids)
        else:
            ids = coin_ids
            
        if isinstance(vs_currencies, list):
            currencies = ",".join(vs_currencies)
        else:
            currencies = vs_currencies
            
        params = {
            "ids": ids,
            "vs_currencies": currencies
        }
        
        try:
            return await self._make_request("simple/price", params, cache_category="price")
        except Exception as e:
            logger.error(f"Erro ao obter preços para {ids}: {str(e)}")
            return {}
    
    async def get_coin_market_chart(self, coin_id: str, vs_currency: str, days: Union[int, str], 
                                  interval: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém dados históricos de preço, volume e capitalização de mercado.
        
        Args:
            coin_id: ID da moeda no CoinGecko.
            vs_currency: Moeda base para converter o preço.
            days: Número de dias ou string ('max', '1', '14', etc).
            interval: Intervalo de dados ('daily', 'hourly', etc).
            
        Returns:
            Dados históricos da moeda.
        """
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        
        if interval:
            params["interval"] = interval
            
        try:
            return await self._make_request(f"coins/{coin_id}/market_chart", params, cache_category="historical")
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos para {coin_id}: {str(e)}")
            return {}
    
    async def get_markets(self, vs_currency: str = "usd", ids: Optional[List[str]] = None, 
                        category: Optional[str] = None, order: str = "market_cap_desc", 
                        per_page: int = 100, page: int = 1, price_change_percentage: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém dados de mercado para moedas listadas e filtragem.
        
        Args:
            vs_currency: Moeda base para converter o preço.
            ids: Lista de IDs das moedas a serem incluídas.
            category: Filtrar por categoria.
            order: Campo de ordenação.
            per_page: Número de resultados por página.
            page: Número da página.
            price_change_percentage: Períodos para calcular mudança de preço (1h,24h,7d,14d,30d,200d,1y).
            
        Returns:
            Lista de dados de mercado para moedas.
        """
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        
        if ids:
            params["ids"] = ",".join(ids)
            
        if category:
            params["category"] = category
            
        if price_change_percentage:
            params["price_change_percentage"] = price_change_percentage
            
        try:
            return await self._make_request("coins/markets", params, cache_category="markets")
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {str(e)}")
            return []
    
    async def get_global_data(self) -> Dict[str, Any]:
        """
        Obtém dados globais do mercado de criptomoedas.
        
        Returns:
            Dados globais do mercado.
        """
        try:
            result = await self._make_request("global", cache_category="markets")
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Erro ao obter dados globais: {str(e)}")
            return {}
    
    async def get_global_defi_data(self) -> Dict[str, Any]:
        """
        Obtém dados globais do mercado DeFi.
        
        Returns:
            Dados globais do mercado DeFi.
        """
        try:
            result = await self._make_request("global/decentralized_finance_defi", cache_category="markets")
            return result.get("data", {})
        except Exception as e:
            logger.error(f"Erro ao obter dados globais de DeFi: {str(e)}")
            return {}
    
    async def get_trending_coins(self) -> List[Dict[str, Any]]:
        """
        Obtém lista de moedas em tendência (baseado em buscas).
        
        Returns:
            Lista de moedas em tendência.
        """
        try:
            result = await self._make_request("search/trending", cache_category="markets")
            return result.get("coins", [])
        except Exception as e:
            logger.error(f"Erro ao obter moedas em tendência: {str(e)}")
            return []
    
    async def get_coin_ohlc(self, coin_id: str, vs_currency: str, days: Union[int, str]) -> List[List[float]]:
        """
        Obtém dados OHLC (Open, High, Low, Close) para uma moeda.
        
        Args:
            coin_id: ID da moeda no CoinGecko.
            vs_currency: Moeda base para converter o preço.
            days: Número de dias (1/7/14/30/90/180/365).
            
        Returns:
            Lista de dados OHLC [timestamp, open, high, low, close].
        """
        params = {
            "vs_currency": vs_currency,
            "days": days
        }
        
        try:
            return await self._make_request(f"coins/{coin_id}/ohlc", params, cache_category="historical")
        except Exception as e:
            logger.error(f"Erro ao obter dados OHLC para {coin_id}: {str(e)}")
            return []
    
    async def get_top_gainers_losers(self, vs_currency: str = "usd", timeframe: str = "24h", limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtém as moedas com maior ganho e maior perda em um período.
        
        Args:
            vs_currency: Moeda base para converter o preço.
            timeframe: Período para calcular a variação ('1h', '24h', '7d', '14d', '30d').
            limit: Número de moedas para cada categoria.
            
        Returns:
            Dicionário com listas de 'gainers' e 'losers'.
        """
        try:
            # Mapear timeframe para o campo correto da API
            timeframe_map = {
                "1h": "price_change_percentage_1h_in_currency",
                "24h": "price_change_percentage_24h",
                "7d": "price_change_percentage_7d_in_currency",
                "14d": "price_change_percentage_14d_in_currency",
                "30d": "price_change_percentage_30d_in_currency"
            }
            
            price_change_field = timeframe_map.get(timeframe, "price_change_percentage_24h")
            price_change_param = ",".join([field for field in timeframe_map.values()])
            
            # Obter dados de mercado para as 250 principais moedas
            markets = await self.get_markets(
                vs_currency=vs_currency, 
                per_page=250, 
                page=1, 
                price_change_percentage=price_change_param
            )
            
            # Filtrar moedas com dados válidos
            valid_coins = [coin for coin in markets if price_change_field in coin and coin[price_change_field] is not None]
            
            # Ordenar por variação de preço
            valid_coins.sort(key=lambda x: x[price_change_field], reverse=True)
            
            # Selecionar top gainers e top losers
            gainers = valid_coins[:limit]
            losers = valid_coins[-limit:]
            losers.reverse()  # Ordenar dos maiores perdedores para os menores
            
            return {
                "gainers": gainers,
                "losers": losers
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter top gainers e losers: {str(e)}")
            return {"gainers": [], "losers": []}
    
    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Obtém uma estimativa do índice de medo e ganância do mercado baseado em métricas CoinGecko.
        
        Returns:
            Dicionário com valor do índice e classificação.
        """
        try:
            # Obter dados globais
            global_data = await self.get_global_data()
            
            # Verificar se obtivemos dados válidos
            if not global_data:
                return {"value": 50, "classification": "Neutro", "error": "Dados globais não disponíveis"}
                
            # Fatores para calcular o índice
            factors = {}
            
            # Volatilidade (baseada na dominância do BTC)
            btc_dominance = global_data.get("market_cap_percentage", {}).get("btc", 50)
            factors["btc_dominance"] = btc_dominance
            
            # Volume de mercado
            market_cap_change = global_data.get("market_cap_change_percentage_24h_usd", 0)
            factors["market_cap_change"] = market_cap_change
            
            # Tendências de busca
            trending_coins = await self.get_trending_coins()
            trending_factor = min(len(trending_coins) * 5, 100) if trending_coins else 50
            factors["trending_factor"] = trending_factor
            
            # Calcular índice baseado nos fatores (algoritmo simplificado)
            # Alta dominância do BTC geralmente indica medo (exceto quando BTC está subindo muito)
            btc_dominance_factor = 100 - btc_dominance if market_cap_change > 0 else btc_dominance
            
            # Índice final (média ponderada dos fatores)
            fear_greed_value = (
                btc_dominance_factor * 0.25 +
                (market_cap_change + 100) / 2 * 0.5 +  # Converter range (-100 a 100) para (0 a 100)
                trending_factor * 0.25
            )
            
            # Garantir que está no intervalo 0-100
            fear_greed_value = max(0, min(100, fear_greed_value))
            
            # Classificação
            classification = "Medo Extremo"
            if fear_greed_value >= 25:
                classification = "Medo"
            if fear_greed_value >= 45:
                classification = "Neutro"
            if fear_greed_value >= 55:
                classification = "Ganância"
            if fear_greed_value >= 75:
                classification = "Ganância Extrema"
                
            return {
                "value": round(fear_greed_value),
                "classification": classification,
                "timestamp": datetime.now().isoformat(),
                "factors": factors
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular índice de medo e ganância: {str(e)}")
            return {
                "value": 50, 
                "classification": "Neutro",
                "error": str(e)
            }
    
    async def get_market_summary(self, vs_currency: str = "usd") -> Dict[str, Any]:
        """
        Obtém um resumo geral do mercado de criptomoedas.
        
        Args:
            vs_currency: Moeda base para os valores.
            
        Returns:
            Dicionário com resumo do mercado.
        """
        try:
            # Obter dados globais
            global_data = await self.get_global_data()
            
            # Obter dados de DeFi
            defi_data = await self.get_global_defi_data()
            
            # Obter top moedas
            top_coins = await self.get_markets(vs_currency=vs_currency, per_page=10, page=1)
            
            # Calcular índice de medo e ganância
            fear_greed = await self.get_fear_greed_index()
            
            # Obter top gainers e losers
            top_movers = await self.get_top_gainers_losers(vs_currency=vs_currency)
            
            # Obter tendências
            trending = await self.get_trending_coins()
            trending_coins = [item["item"] for item in trending] if trending else []
            
            # Consolidar resumo do mercado
            return {
                "timestamp": datetime.now().isoformat(),
                "global": {
                    "total_market_cap": global_data.get("total_market_cap", {}).get(vs_currency, 0),
                    "total_volume": global_data.get("total_volume", {}).get(vs_currency, 0),
                    "market_cap_change_24h": global_data.get("market_cap_change_percentage_24h_usd", 0),
                    "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                    "markets": global_data.get("markets", 0),
                    "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
                    "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0)
                },
                "defi": {
                    "defi_market_cap": defi_data.get("defi_market_cap", 0),
                    "defi_to_total_market_cap": defi_data.get("defi_to_total_market_cap_percentage", 0),
                    "trading_volume_24h": defi_data.get("trading_volume_24h", 0),
                    "defi_dominance": defi_data.get("defi_dominance", 0),
                    "top_coins_defi": defi_data.get("top_coins_defi", [])
                },
                "top_coins": [
                    {
                        "id": coin.get("id", ""),
                        "symbol": coin.get("symbol", ""),
                        "name": coin.get("name", ""),
                        "image": coin.get("image", ""),
                        "current_price": coin.get("current_price", 0),
                        "market_cap": coin.get("market_cap", 0),
                        "market_cap_rank": coin.get("market_cap_rank", 0),
                        "price_change_24h": coin.get("price_change_percentage_24h", 0)
                    } for coin in top_coins
                ],
                "top_gainers": [
                    {
                        "id": coin.get("id", ""),
                        "symbol": coin.get("symbol", ""),
                        "name": coin.get("name", ""),
                        "image": coin.get("image", ""),
                        "current_price": coin.get("current_price", 0),
                        "price_change_24h": coin.get("price_change_percentage_24h", 0)
                    } for coin in top_movers.get("gainers", [])
                ],
                "top_losers": [
                    {
                        "id": coin.get("id", ""),
                        "symbol": coin.get("symbol", ""),
                        "name": coin.get("name", ""),
                        "image": coin.get("image", ""),
                        "current_price": coin.get("current_price", 0),
                        "price_change_24h": coin.get("price_change_percentage_24h", 0)
                    } for coin in top_movers.get("losers", [])
                ],
                "trending": [
                    {
                        "id": coin.get("id", ""),
                        "name": coin.get("name", ""),
                        "symbol": coin.get("symbol", ""),
                        "market_cap_rank": coin.get("market_cap_rank", 0),
                        "score": coin.get("score", 0)
                    } for coin in trending_coins
                ],
                "fear_greed_index": fear_greed
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo do mercado: {str(e)}")
            return {"error": str(e)}

# Importação obrigatória para o delay entre requisições
import asyncio

# Instância global do cliente
coingecko_client = CoinGeckoClient()
