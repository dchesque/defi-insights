"""
Cliente para a API do CoinGecko - uma fonte gratuita de dados de criptomoedas.
"""
import os
import httpx
import json
import asyncio
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
    
    async def get_token_history(self, symbol: str, days: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos de preço para um token específico.
        
        Args:
            symbol: Símbolo do token (ex: BTC)
            days: Número de dias de histórico (default: 100)
            
        Returns:
            Lista de pontos de dados históricos formatados para compatibilidade
        """
        try:
            # Primeiro precisamos converter o símbolo para o ID do CoinGecko
            coins = await self.search_coins(symbol)
            
            if not coins:
                logger.warning(f"Token {symbol} não encontrado no CoinGecko")
                return []
                
            # Pegar o primeiro resultado da busca
            coin_id = coins[0]['id']
            
            # Obter dados históricos
            market_data = await self.get_coin_market_chart(
                coin_id=coin_id,
                vs_currency="usd",
                days=days
            )
            
            if not market_data or "prices" not in market_data:
                logger.warning(f"Dados históricos não disponíveis para {symbol}")
                return []
                
            # Converter para o formato esperado pelo technical_agent
            result = []
            for i, (timestamp, price) in enumerate(market_data.get("prices", [])):
                # Timestamp está em milissegundos
                dt = datetime.fromtimestamp(timestamp / 1000)
                
                # Pegar volumes do mesmo período
                volume = 0
                if i < len(market_data.get("total_volumes", [])):
                    _, volume = market_data["total_volumes"][i]
                
                entry = {
                    "timestamp": dt,
                    "prices": price,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": volume,
                    "total_volumes": volume
                }
                result.append(entry)
                
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico para {symbol}: {str(e)}")
            return []
    
    async def get_coin_news(self, coin_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém notícias recentes relacionadas a uma criptomoeda.
        Documentação: https://www.coingecko.com/api/documentation
        
        Args:
            coin_id: ID da moeda no CoinGecko (ex: 'bitcoin')
            limit: Número máximo de notícias a retornar
            
        Returns:
            Lista de notícias relacionadas à moeda
        """
        logger.info(f"Obtendo notícias para {coin_id}")
        
        # Primeiro, buscar o ID exato no CoinGecko se for um símbolo
        if len(coin_id) < 5:  # Provavelmente é um símbolo como BTC, ETH
            coins_list = await self.get_coins_list()
            for coin in coins_list:
                if coin.get('symbol', '').lower() == coin_id.lower():
                    coin_id = coin.get('id')
                    break
        
        # Buscar notícias usando a API de status do mercado (inclui notícias)
        try:
            endpoint = "search/trending"
            trending_data = await self._make_request(endpoint, cache_category="news")
            
            # A API do CoinGecko não fornece uma endpoint específica para notícias
            # Vamos usar a API de busca/tendências como alternativa
            
            # Obter dados da moeda para mais informações
            coin_data = await self.get_coin_data(coin_id)
            coin_name = coin_data.get('name', '').lower()
            
            # Buscar também dados atuais de mercado
            endpoint = "coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": coin_id,
                "order": "market_cap_desc",
                "per_page": 1,
                "page": 1,
                "sparkline": "false"
            }
            market_data = await self._make_request(endpoint, params, cache_category="markets")
            
            # Coletar todas as notícias de tendências
            all_news = []
            
            # Adicionar notícias baseadas em tendências
            if trending_data and "coins" in trending_data:
                trending_coins = trending_data.get("coins", [])
                
                # Verificar se a moeda está nas tendências
                is_trending = any(item.get("item", {}).get("id") == coin_id for item in trending_coins)
                
                if is_trending:
                    all_news.append({
                        "title": f"{coin_name.title()} está em tendência no CoinGecko",
                        "description": f"{coin_name.title()} está entre as criptomoedas mais pesquisadas nas últimas 24 horas.",
                        "url": f"https://www.coingecko.com/en/coins/{coin_id}",
                        "source": "CoinGecko",
                        "date": datetime.now().isoformat()
                    })
            
            # Adicionar notícias baseadas em dados de mercado
            if market_data and len(market_data) > 0:
                market_item = market_data[0]
                
                price = market_item.get("current_price")
                price_change_24h = market_item.get("price_change_percentage_24h")
                market_cap = market_item.get("market_cap")
                market_cap_rank = market_item.get("market_cap_rank")
                
                if price and price_change_24h:
                    change_type = "subiu" if price_change_24h > 0 else "caiu"
                    all_news.append({
                        "title": f"Preço de {coin_name.title()} {change_type} {abs(price_change_24h):.2f}% nas últimas 24h",
                        "description": f"{coin_name.title()} está sendo negociado a ${price:.2f} com capitalização de mercado de ${market_cap:,}.",
                        "url": f"https://www.coingecko.com/en/coins/{coin_id}",
                        "source": "CoinGecko Market Data",
                        "date": datetime.now().isoformat()
                    })
                    
                if market_cap_rank:
                    all_news.append({
                        "title": f"{coin_name.title()} está na posição #{market_cap_rank} por capitalização de mercado",
                        "description": f"Com uma capitalização de mercado de ${market_cap:,}, {coin_name.title()} é a #{market_cap_rank} criptomoeda.",
                        "url": f"https://www.coingecko.com/en/coins/{coin_id}",
                        "source": "CoinGecko Rankings",
                        "date": datetime.now().isoformat()
                    })
            
            # Adicionar dados de desenvolvedores se disponível
            if "developer_data" in coin_data:
                dev_data = coin_data.get("developer_data", {})
                
                if dev_data.get("pull_request_contributors"):
                    all_news.append({
                        "title": f"{coin_name.title()} conta com {dev_data.get('pull_request_contributors')} contribuidores",
                        "description": f"O projeto {coin_name.title()} tem {dev_data.get('forks', 0)} forks, {dev_data.get('stars', 0)} estrelas no GitHub e {dev_data.get('subscribers', 0)} assinantes.",
                        "url": f"https://www.coingecko.com/en/coins/{coin_id}/developers",
                        "source": "CoinGecko Developer Data",
                        "date": datetime.now().isoformat()
                    })
            
            # Adicionar dados da comunidade se disponível
            if "community_data" in coin_data:
                community = coin_data.get("community_data", {})
                
                if community.get("twitter_followers"):
                    all_news.append({
                        "title": f"{coin_name.title()} tem {community.get('twitter_followers'):,} seguidores no Twitter",
                        "description": f"A comunidade de {coin_name.title()} inclui {community.get('reddit_subscribers', 0):,} assinantes no Reddit.",
                        "url": f"https://www.coingecko.com/en/coins/{coin_id}/social_media",
                        "source": "CoinGecko Community Data",
                        "date": datetime.now().isoformat()
                    })
            
            # Adicionar dados de liquidez de mercado
            if "tickers" in coin_data:
                tickers = coin_data.get("tickers", [])
                active_exchanges = len(set(ticker.get("market", {}).get("name") for ticker in tickers if ticker.get("market")))
                
                if active_exchanges > 0:
                    all_news.append({
                        "title": f"{coin_name.title()} está listado em {active_exchanges} exchanges",
                        "description": f"{coin_name.title()} pode ser negociado em diversas exchanges com diferentes pares de negociação.",
                        "url": f"https://www.coingecko.com/en/coins/{coin_id}#markets",
                        "source": "CoinGecko Markets",
                        "date": datetime.now().isoformat()
                    })
            
            # Limitar ao número de notícias solicitado
            return all_news[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao obter notícias para {coin_id}: {str(e)}")
            return []

    async def get_token_info(self, token_id: str) -> Dict[str, Any]:
        """
        Obtém informações completas sobre um token, incluindo preço, histórico e dados de mercado.
        
        Args:
            token_id: ID do token no CoinGecko
            
        Returns:
            Dicionário com informações completas do token
        """
        logger.info(f"Obtendo informações completas para o token {token_id}")
        
        try:
            # Obter dados do token
            token_data = await self.get_coin_data(token_id)
            
            # Obter histórico de preços (30 dias)
            price_history = await self.get_coin_market_chart(token_id, 'usd', days='30')
            
            # Compilar informações
            return {
                "token_id": token_id,
                "name": token_data.get("name"),
                "symbol": token_data.get("symbol"),
                "price_data": {
                    "current_price_usd": token_data.get("market_data", {}).get("current_price", {}).get("usd"),
                    "market_cap_usd": token_data.get("market_data", {}).get("market_cap", {}).get("usd"),
                    "total_volume_usd": token_data.get("market_data", {}).get("total_volume", {}).get("usd"),
                    "price_change_24h": token_data.get("market_data", {}).get("price_change_percentage_24h"),
                    "price_change_7d": token_data.get("market_data", {}).get("price_change_percentage_7d"),
                    "price_change_30d": token_data.get("market_data", {}).get("price_change_percentage_30d"),
                    "all_time_high": token_data.get("market_data", {}).get("ath", {}).get("usd"),
                    "all_time_low": token_data.get("market_data", {}).get("atl", {}).get("usd")
                },
                "liquidity_data": {
                    "total_supply": token_data.get("market_data", {}).get("total_supply"),
                    "circulating_supply": token_data.get("market_data", {}).get("circulating_supply"),
                    "fdv_to_mcap_ratio": self._calculate_fdv_to_mcap_ratio(token_data.get("market_data", {}))
                },
                "market_data": token_data.get("market_data", {}),
                "community_data": token_data.get("community_data", {}),
                "developer_data": token_data.get("developer_data", {}),
                "price_history": price_history
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações do token {token_id}: {str(e)}")
            return {"error": f"Falha ao obter informações: {str(e)}"}
            
    def _calculate_fdv_to_mcap_ratio(self, market_data: Dict[str, Any]) -> Optional[float]:
        """
        Calcula o ratio entre Fully Diluted Valuation e Market Cap.
        
        Args:
            market_data: Dados de mercado do token
            
        Returns:
            Ratio FDV/MCAP ou None se dados insuficientes
        """
        try:
            mcap = market_data.get("market_cap", {}).get("usd")
            total_supply = market_data.get("total_supply")
            circulating_supply = market_data.get("circulating_supply")
            current_price = market_data.get("current_price", {}).get("usd")
            
            if all([mcap, total_supply, circulating_supply, current_price]) and circulating_supply > 0:
                fdv = total_supply * current_price
                return fdv / mcap
            return None
        except (TypeError, ZeroDivisionError):
            return None

    async def get_coin_by_contract(self, contract_address: str, chain: str = 'ethereum') -> Dict[str, Any]:
        """
        Busca um token pelo endereço do contrato na blockchain.
        
        Args:
            contract_address: Endereço do contrato na blockchain
            chain: Nome da blockchain (ethereum, binance-smart-chain, etc.)
            
        Returns:
            Informações do token ou erro
        """
        logger.info(f"Buscando token pelo endereço {contract_address} na chain {chain}")
        
        try:
            # Mapear chain para o formato usado pelo CoinGecko
            chain_map = {
                'eth': 'ethereum',
                'bsc': 'binance-smart-chain',
                'polygon': 'polygon-pos',
                'arbitrum': 'arbitrum-one',
                'optimism': 'optimistic-ethereum',
                'avalanche': 'avalanche'
            }
            
            chain_id = chain_map.get(chain.lower(), chain.lower())
            
            # Buscar lista de tokens
            coins = await self.get_coins_list()
            
            # Filtrar por tokens que tenham informações de plataforma
            for coin in coins:
                if 'platforms' in coin and chain_id in coin['platforms']:
                    # Converter endereços para lowercase para comparação
                    if coin['platforms'][chain_id].lower() == contract_address.lower():
                        logger.info(f"Token encontrado: {coin['id']} ({coin['symbol']})")
                        return coin
            
            logger.warning(f"Token não encontrado para o endereço {contract_address} na chain {chain_id}")
            return {"error": "Token não encontrado"}
            
        except Exception as e:
            logger.error(f"Erro ao buscar token por contrato: {str(e)}")
            return {"error": f"Falha ao buscar token: {str(e)}"}

    async def get_coin_by_id(self, coin_id: str) -> Dict[str, Any]:
        """
        Obtém informações de um token pelo seu ID no CoinGecko.
        
        Args:
            coin_id: ID do token no CoinGecko
            
        Returns:
            Dict com informações do token ou dict com erro
        """
        try:
            # Primeiro busca o token na lista de moedas
            coins = await self.get_coins_list()
            found = False
            
            for coin in coins:
                if coin.get("id") == coin_id or coin.get("symbol", "").lower() == coin_id:
                    found = True
                    coin_id = coin.get("id")
                    break
            
            if not found:
                # Tentar buscar por meio da pesquisa
                search_results = await self.search_coins(coin_id)
                if search_results and len(search_results) > 0:
                    coin_id = search_results[0].get("id")
                    found = True
            
            if not found:
                return {"error": f"Token não encontrado: {coin_id}"}
                
            # Buscar dados detalhados do token
            return await self.get_coin_data(coin_id)
            
        except Exception as e:
            logger.error(f"Erro ao buscar token por ID {coin_id}: {str(e)}")
            return {"error": str(e)}
    
    async def get_coin_market_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Obtém dados de mercado de um token pelo seu ID no CoinGecko.
        
        Args:
            coin_id: ID do token no CoinGecko
            
        Returns:
            Dict com dados de mercado do token
        """
        try:
            # Obter dados detalhados do token
            coin_data = await self.get_coin_data(coin_id)
            
            if "error" in coin_data:
                return {"error": coin_data["error"]}
                
            # Extrair apenas os dados de mercado
            if "market_data" in coin_data:
                return coin_data["market_data"]
            else:
                return {"error": f"Dados de mercado não disponíveis para o token {coin_id}"}
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados de mercado para {coin_id}: {str(e)}")
            return {"error": str(e)}

# Instância global do cliente
coingecko_client = CoinGeckoClient()
