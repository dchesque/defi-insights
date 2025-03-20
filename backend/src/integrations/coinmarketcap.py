"""
Cliente para a API do CoinMarketCap - uma fonte abrangente de dados de mercado de criptomoedas.
"""
import os
import httpx
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class CoinMarketCapClient:
    """Cliente para interagir com a API do CoinMarketCap."""
    
    BASE_URL = "https://pro-api.coinmarketcap.com/v1"
    
    def __init__(self):
        """Inicializa o cliente do CoinMarketCap."""
        self.api_key = os.getenv("COINMARKETCAP_API_KEY")
        if not self.api_key:
            logger.warning("COINMARKETCAP_API_KEY não definida. As requisições falharão.")
        
        self.cache = {}
        self.cache_ttl = 60  # Cache de 1 minuto para dados de preço
        self.long_cache_ttl = 900  # Cache de 15 minutos para dados menos voláteis
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, long_cache: bool = False) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do CoinMarketCap.
        
        Args:
            endpoint: Caminho do endpoint da API.
            params: Parâmetros da query (opcional).
            long_cache: Se True, usa o cache mais longo para dados menos voláteis.
            
        Returns:
            Resposta da API em formato JSON.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Verificar se a API key está configurada
        if not self.api_key:
            raise ValueError("COINMARKETCAP_API_KEY não configurada")
        
        # Preparar parâmetros
        request_params = params.copy() if params else {}
        
        # Verificar se temos dados em cache
        cache_key = f"{endpoint}:{json.dumps(request_params)}"
        if cache_key in self.cache:
            # Verificar se o cache ainda é válido
            cached_data, timestamp = self.cache[cache_key]
            
            ttl = self.long_cache_ttl if long_cache else self.cache_ttl
            if datetime.now() - timestamp < timedelta(seconds=ttl):
                return cached_data
        
        try:
            headers = {
                "X-CMC_PRO_API_KEY": self.api_key,
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=request_params,
                    headers=headers
                )
                
                # Verificar se houve erro
                response.raise_for_status()
                
                # Armazenar resultado no cache
                result = response.json()
                self.cache[cache_key] = (result, datetime.now())
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao chamar a API do CoinMarketCap: {e.response.status_code} - {e.response.text}")
            raise
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do CoinMarketCap: {str(e)}")
            raise
    
    async def get_latest_listings(self, limit: int = 100, convert: str = "USD") -> List[Dict[str, Any]]:
        """
        Obtém as últimas listagens de criptomoedas ordenadas por capitalização de mercado.
        
        Args:
            limit: Número máximo de resultados a retornar.
            convert: Moeda para converter os valores (ex: "USD", "BRL").
            
        Returns:
            Lista de criptomoedas com dados de mercado.
        """
        params = {
            "limit": min(limit, 5000),  # Limitar para não exceder limites da API
            "convert": convert
        }
        
        try:
            data = await self._make_request("cryptocurrency/listings/latest", params)
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter últimas listagens: {str(e)}")
            return []
    
    async def get_cryptocurrency_info(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre uma criptomoeda pelo símbolo.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            
        Returns:
            Dicionário com informações da criptomoeda.
        """
        params = {
            "symbol": symbol.upper()
        }
        
        try:
            data = await self._make_request("cryptocurrency/info", params, long_cache=True)
            coin_data = data.get("data", {}).get(symbol.upper(), {})
            
            if not coin_data:
                logger.warning(f"Criptomoeda com símbolo {symbol} não encontrada")
                return {}
            
            return coin_data
            
        except Exception as e:
            logger.error(f"Erro ao obter informações da criptomoeda {symbol}: {str(e)}")
            return {}
    
    async def get_price(self, symbols: Union[str, List[str]], convert: str = "USD") -> Dict[str, Dict[str, Any]]:
        """
        Obtém o preço atual para um ou mais símbolos de criptomoedas.
        
        Args:
            symbols: Símbolo(s) das criptomoedas (ex: "BTC" ou ["BTC", "ETH"]).
            convert: Moeda para converter os valores (ex: "USD", "BRL").
            
        Returns:
            Dicionário com dados de preço para cada símbolo.
        """
        # Converter para string se for lista
        if isinstance(symbols, list):
            symbols_str = ",".join(symbols)
        else:
            symbols_str = symbols
        
        params = {
            "symbol": symbols_str.upper(),
            "convert": convert
        }
        
        try:
            data = await self._make_request("cryptocurrency/quotes/latest", params)
            return data.get("data", {})
            
        except Exception as e:
            logger.error(f"Erro ao obter preços para {symbols_str}: {str(e)}")
            return {}
    
    async def get_global_metrics(self, convert: str = "USD") -> Dict[str, Any]:
        """
        Obtém métricas globais do mercado de criptomoedas.
        
        Args:
            convert: Moeda para converter os valores (ex: "USD", "BRL").
            
        Returns:
            Dicionário com métricas globais.
        """
        params = {
            "convert": convert
        }
        
        try:
            data = await self._make_request("global-metrics/quotes/latest", params)
            return data.get("data", {})
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas globais: {str(e)}")
            return {}
    
    async def get_trending_currencies(self, limit: int = 10, convert: str = "USD", time_period: str = "24h") -> List[Dict[str, Any]]:
        """
        Obtém as criptomoedas em tendência (com maior variação de preço).
        
        Args:
            limit: Número máximo de resultados.
            convert: Moeda para converter os valores (ex: "USD", "BRL").
            time_period: Período de tempo para calcular a variação ("24h", "7d", "30d").
            
        Returns:
            Lista de criptomoedas em tendência.
        """
        try:
            # Primeiro obtemos todas as criptomoedas
            all_currencies = await self.get_latest_listings(limit=200, convert=convert)
            
            # Agora ordenamos por variação de preço
            time_key_map = {
                "24h": "percent_change_24h",
                "7d": "percent_change_7d",
                "30d": "percent_change_30d"
            }
            
            time_key = time_key_map.get(time_period, "percent_change_24h")
            
            # Ordenar por variação (valorização) em valor absoluto
            sorted_currencies = sorted(
                all_currencies, 
                key=lambda x: abs(x.get("quote", {}).get(convert, {}).get(time_key, 0)), 
                reverse=True
            )
            
            return sorted_currencies[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao obter criptomoedas em tendência: {str(e)}")
            return []
    
    async def search_cryptocurrencies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca criptomoedas pelo nome ou símbolo.
        
        Args:
            query: Termo de busca.
            limit: Número máximo de resultados.
            
        Returns:
            Lista de criptomoedas correspondentes à busca.
        """
        try:
            # Obter todas as criptomoedas
            all_currencies = await self.get_latest_listings(limit=2000)
            
            # Filtrar pelo termo de busca
            query = query.lower()
            filtered_currencies = [
                currency for currency in all_currencies
                if query in currency.get("name", "").lower() or query in currency.get("symbol", "").lower()
            ]
            
            return filtered_currencies[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao buscar criptomoedas com termo '{query}': {str(e)}")
            return []
    
    async def get_market_pairs(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém pares de negociação para uma criptomoeda específica.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            limit: Número máximo de resultados.
            
        Returns:
            Lista de pares de negociação.
        """
        params = {
            "symbol": symbol.upper(),
            "limit": limit
        }
        
        try:
            data = await self._make_request("cryptocurrency/market-pairs/latest", params)
            return data.get("data", {}).get("market_pairs", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter pares de negociação para {symbol}: {str(e)}")
            return []
    
    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Simula um índice de medo e ganância com base nos dados disponíveis.
        
        Returns:
            Dicionário com o índice de medo e ganância.
        """
        try:
            # Obter métricas globais
            global_metrics = await self.get_global_metrics()
            
            # Obter criptomoedas principais
            top_currencies = await self.get_latest_listings(limit=10)
            
            # Calcular índice com base em vários fatores
            btc_dominance = global_metrics.get("btc_dominance", 0)
            market_cap_change = global_metrics.get("quote", {}).get("USD", {}).get("total_market_cap_yesterday_percentage_change", 0)
            
            # Média das variações de preço das principais criptomoedas
            avg_price_change = sum(
                currency.get("quote", {}).get("USD", {}).get("percent_change_24h", 0)
                for currency in top_currencies
            ) / max(len(top_currencies), 1)
            
            # Calcular o índice (formula simples)
            # Se BTC dominance é alto e mercado em queda = medo
            # Se BTC dominance é baixo e mercado em alta = ganância
            raw_index = (
                (60 - min(btc_dominance, 60)) / 2 +  # 0-30
                (market_cap_change + 20) / 2 +        # 0-30 (esperando um range de -20% a +20%)
                (avg_price_change + 20) / 2.5         # 0-40 (esperando um range de -20% a +20%)
            )
            
            # Limitar ao range 0-100
            index_value = max(0, min(100, raw_index))
            
            # Classificar o índice
            if index_value <= 20:
                classification = "Medo Extremo"
            elif index_value <= 40:
                classification = "Medo"
            elif index_value <= 60:
                classification = "Neutro"
            elif index_value <= 80:
                classification = "Ganância"
            else:
                classification = "Ganância Extrema"
            
            return {
                "value": round(index_value),
                "value_classification": classification,
                "timestamp": datetime.now().isoformat(),
                "data_source": "CoinMarketCap"
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular índice de medo e ganância: {str(e)}")
            return {
                "value": 50,
                "value_classification": "Neutro",
                "timestamp": datetime.now().isoformat(),
                "data_source": "CoinMarketCap",
                "error": str(e)
            }
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Obtém uma visão geral do mercado de criptomoedas.
        
        Returns:
            Dicionário com visão geral do mercado.
        """
        try:
            # Obter dados em paralelo
            global_metrics = await self.get_global_metrics()
            top_currencies = await self.get_latest_listings(limit=20)
            trending_gainers = await self.get_trending_currencies(limit=5, time_period="24h")
            fear_greed = await self.get_fear_greed_index()
            
            # Formatar dados para retorno
            result = {
                "total_market_cap": global_metrics.get("quote", {}).get("USD", {}).get("total_market_cap", 0),
                "total_volume_24h": global_metrics.get("quote", {}).get("USD", {}).get("total_volume_24h", 0),
                "btc_dominance": global_metrics.get("btc_dominance", 0),
                "eth_dominance": global_metrics.get("eth_dominance", 0),
                "active_cryptocurrencies": global_metrics.get("active_cryptocurrencies", 0),
                "market_cap_change_24h": global_metrics.get("quote", {}).get("USD", {}).get("total_market_cap_yesterday_percentage_change", 0),
                "fear_greed_index": fear_greed,
                "top_currencies": [
                    {
                        "id": currency.get("id", 0),
                        "name": currency.get("name", ""),
                        "symbol": currency.get("symbol", ""),
                        "price": currency.get("quote", {}).get("USD", {}).get("price", 0),
                        "market_cap": currency.get("quote", {}).get("USD", {}).get("market_cap", 0),
                        "volume_24h": currency.get("quote", {}).get("USD", {}).get("volume_24h", 0),
                        "percent_change_24h": currency.get("quote", {}).get("USD", {}).get("percent_change_24h", 0),
                        "percent_change_7d": currency.get("quote", {}).get("USD", {}).get("percent_change_7d", 0)
                    }
                    for currency in top_currencies
                ],
                "trending_gainers": [
                    {
                        "id": currency.get("id", 0),
                        "name": currency.get("name", ""),
                        "symbol": currency.get("symbol", ""),
                        "price": currency.get("quote", {}).get("USD", {}).get("price", 0),
                        "percent_change_24h": currency.get("quote", {}).get("USD", {}).get("percent_change_24h", 0)
                    }
                    for currency in trending_gainers
                ]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter visão geral do mercado: {str(e)}")
            return {
                "error": str(e)
            }

# Instância global do cliente
coinmarketcap_client = CoinMarketCapClient() 