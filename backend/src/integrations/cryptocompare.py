"""
Cliente para a API do CryptoCompare - uma fonte de dados de mercado de criptomoedas.
"""
import os
import httpx
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class CryptoCompareClient:
    """Cliente para interagir com a API do CryptoCompare."""
    
    BASE_URL = "https://min-api.cryptocompare.com/data"
    
    def __init__(self):
        """Inicializa o cliente do CryptoCompare."""
        self.api_key = os.getenv("CRYPTOCOMPARE_API_KEY")
        if not self.api_key:
            logger.warning("CRYPTOCOMPARE_API_KEY não definida. Algumas funcionalidades podem ser limitadas.")
        
        self.cache = {}
        self.cache_ttl = 60  # Cache de 1 minuto para dados de preço
        self.long_cache_ttl = 3600  # Cache de 1 hora para dados históricos
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, long_cache: bool = False) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do CryptoCompare.
        
        Args:
            endpoint: Caminho do endpoint da API.
            params: Parâmetros da query (opcional).
            long_cache: Se True, usa o cache mais longo para dados históricos.
            
        Returns:
            Resposta da API em formato JSON.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Adicionar a API Key aos parâmetros
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
            headers = {}
            if self.api_key:
                headers["authorization"] = f"Apikey {self.api_key}"
            
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
                
                # Verificar se a resposta tem erro
                if result.get("Response") == "Error":
                    logger.error(f"Erro da API do CryptoCompare: {result.get('Message')}")
                    raise Exception(result.get("Message"))
                
                self.cache[cache_key] = (result, datetime.now())
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao chamar a API do CryptoCompare: {e.response.status_code} - {e.response.text}")
            raise
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do CryptoCompare: {str(e)}")
            raise
    
    async def get_price(
        self, 
        fsyms: Union[str, List[str]], 
        tsyms: Union[str, List[str]] = "USD"
    ) -> Dict[str, Any]:
        """
        Obtém o preço atual para um ou mais símbolos de criptomoedas.
        
        Args:
            fsyms: Símbolo(s) das criptomoedas (ex: "BTC" ou ["BTC", "ETH"]).
            tsyms: Moeda(s) para conversão (ex: "USD" ou ["USD", "EUR"]).
            
        Returns:
            Dicionário com preços.
        """
        # Converter para lista se for string
        if isinstance(fsyms, str):
            fsyms = [fsyms]
        
        if isinstance(tsyms, str):
            tsyms = [tsyms]
        
        params = {
            "fsyms": ",".join(fsyms),
            "tsyms": ",".join(tsyms)
        }
        
        try:
            data = await self._make_request("pricemulti", params)
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter preços: {str(e)}")
            return {}
    
    async def get_historical_data(
        self, 
        fsym: str, 
        tsym: str = "USD", 
        limit: int = 30, 
        aggregate: int = 1,
        interval: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos para um símbolo de criptomoeda.
        
        Args:
            fsym: Símbolo da criptomoeda (ex: "BTC").
            tsym: Moeda para conversão (ex: "USD").
            limit: Número de pontos de dados (max 2000).
            aggregate: Número de unidades a agregar.
            interval: Intervalo de tempo ("minute", "hour", "day").
            
        Returns:
            Lista de pontos de dados históricos.
        """
        # Mapear intervalo para endpoint
        endpoint_map = {
            "minute": "histominute",
            "hour": "histohour",
            "day": "histoday"
        }
        
        if interval not in endpoint_map:
            raise ValueError(f"Intervalo inválido: {interval}. Deve ser um de: {', '.join(endpoint_map.keys())}")
        
        endpoint = endpoint_map[interval]
        
        params = {
            "fsym": fsym,
            "tsym": tsym,
            "limit": min(limit, 2000),
            "aggregate": aggregate
        }
        
        try:
            data = await self._make_request(endpoint, params, long_cache=True)
            return data.get("Data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter dados históricos para {fsym}: {str(e)}")
            return []
    
    async def get_top_exchanges(self, fsym: str, tsym: str = "USD", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém as principais exchanges para um par de negociação.
        
        Args:
            fsym: Símbolo da criptomoeda (ex: "BTC").
            tsym: Moeda para conversão (ex: "USD").
            limit: Número máximo de exchanges a retornar.
            
        Returns:
            Lista de exchanges.
        """
        params = {
            "fsym": fsym,
            "tsym": tsym,
            "limit": limit
        }
        
        try:
            data = await self._make_request("top/exchanges", params)
            return data.get("Data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter top exchanges para {fsym}/{tsym}: {str(e)}")
            return []
    
    async def get_top_pairs(self, fsym: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém os principais pares de negociação para uma criptomoeda.
        
        Args:
            fsym: Símbolo da criptomoeda (ex: "BTC").
            limit: Número máximo de pares a retornar.
            
        Returns:
            Lista de pares de negociação.
        """
        params = {
            "fsym": fsym,
            "limit": limit
        }
        
        try:
            data = await self._make_request("top/pairs", params)
            return data.get("Data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter top pares para {fsym}: {str(e)}")
            return []
    
    async def get_token_details(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um token.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            
        Returns:
            Dicionário com detalhes do token.
        """
        try:
            # Obter informações sobre o token
            coin_list_data = await self._make_request("all/coinlist", long_cache=True)
            coin_data = coin_list_data.get("Data", {}).get(symbol.upper(), {})
            
            if not coin_data:
                return {
                    "symbol": symbol,
                    "found": False,
                    "error": "Token não encontrado"
                }
            
            # Buscar dados adicionais
            price_data = await self.get_price(symbol)
            
            # Processamento
            return {
                "symbol": symbol,
                "found": True,
                "name": coin_data.get("CoinName", ""),
                "full_name": coin_data.get("FullName", ""),
                "algorithm": coin_data.get("Algorithm", ""),
                "proof_type": coin_data.get("ProofType", ""),
                "fully_premined": coin_data.get("FullyPremined", "0") == "1",
                "total_coin_supply": coin_data.get("TotalCoinSupply", ""),
                "built_on": coin_data.get("BuiltOn", ""),
                "smart_contract_address": coin_data.get("SmartContractAddress", ""),
                "description": coin_data.get("Description", ""),
                "twitter_handle": coin_data.get("Twitter", ""),
                "website_url": coin_data.get("WebsiteUrl", ""),
                "forum_url": coin_data.get("ForumUrl", ""),
                "github_url": coin_data.get("GithubUrl", ""),
                "image_url": f"https://www.cryptocompare.com{coin_data.get('ImageUrl', '')}",
                "current_price": price_data.get(symbol.upper(), {}).get("USD", 0) if price_data else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do token {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "found": False,
                "error": str(e)
            }
    
    async def get_market_data(self, limit: int = 10) -> Dict[str, Any]:
        """
        Obtém dados gerais de mercado, incluindo top criptomoedas.
        
        Args:
            limit: Número máximo de criptomoedas a retornar no top.
            
        Returns:
            Dicionário com dados de mercado.
        """
        try:
            # Obter lista das principais criptomoedas
            top_list = await self._make_request("top/mktcapfull", {"limit": limit, "tsym": "USD"})
            
            # Extrair apenas os dados relevantes
            top_tokens = []
            for item in top_list.get("Data", []):
                info = item.get("CoinInfo", {})
                raw = item.get("RAW", {}).get("USD", {})
                display = item.get("DISPLAY", {}).get("USD", {})
                
                top_tokens.append({
                    "symbol": info.get("Name", ""),
                    "name": info.get("FullName", ""),
                    "price": raw.get("PRICE", 0),
                    "price_formatted": display.get("PRICE", "$0"),
                    "market_cap": raw.get("MKTCAP", 0),
                    "market_cap_formatted": display.get("MKTCAP", "$0"),
                    "volume_24h": raw.get("TOTALVOLUME24H", 0),
                    "volume_24h_formatted": display.get("TOTALVOLUME24H", "$0"),
                    "change_24h_pct": raw.get("CHANGEPCT24HOUR", 0),
                    "change_24h_formatted": display.get("CHANGEPCT24HOUR", "0") + "%",
                    "image_url": f"https://www.cryptocompare.com{info.get('ImageUrl', '')}"
                })
            
            # Obter dados globais de mercado
            global_data = await self._make_request("global", {"tsym": "USD"})
            
            result = {
                "top_tokens": top_tokens,
                "total_market_cap": global_data.get("Data", {}).get("total_market_cap", 0),
                "total_volume_24h": global_data.get("Data", {}).get("total_volume_24h", 0),
                "btc_dominance": global_data.get("Data", {}).get("btc_dominance", 0)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de mercado: {str(e)}")
            return {
                "top_tokens": [],
                "total_market_cap": 0,
                "total_volume_24h": 0,
                "btc_dominance": 0,
                "error": str(e)
            }
    
    async def get_social_stats(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém estatísticas sociais para uma criptomoeda.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            
        Returns:
            Dicionário com estatísticas sociais.
        """
        try:
            params = {"coinid": symbol.upper()}
            data = await self._make_request("social/coin/latest", params)
            
            social_data = data.get("Data", {})
            
            if not social_data:
                return {
                    "symbol": symbol,
                    "found": False,
                    "error": "Dados sociais não encontrados"
                }
            
            # Extrair dados relevantes
            result = {
                "symbol": symbol,
                "found": True,
                "twitter": {
                    "followers": social_data.get("Twitter", {}).get("followers", 0),
                    "following": social_data.get("Twitter", {}).get("following", 0),
                    "statuses": social_data.get("Twitter", {}).get("statuses", 0),
                    "points": social_data.get("Twitter", {}).get("Points", 0)
                },
                "reddit": {
                    "subscribers": social_data.get("Reddit", {}).get("subscribers", 0),
                    "active_users": social_data.get("Reddit", {}).get("active_users", 0),
                    "posts_per_day": social_data.get("Reddit", {}).get("posts_per_day", 0),
                    "comments_per_day": social_data.get("Reddit", {}).get("comments_per_day", 0),
                    "points": social_data.get("Reddit", {}).get("Points", 0)
                },
                "github": {
                    "stars": social_data.get("CodeRepository", {}).get("stars", 0),
                    "forks": social_data.get("CodeRepository", {}).get("forks", 0),
                    "closed_issues": social_data.get("CodeRepository", {}).get("closed_issues", 0),
                    "open_issues": social_data.get("CodeRepository", {}).get("open_issues", 0),
                    "contributors": social_data.get("CodeRepository", {}).get("contributors", 0),
                    "points": social_data.get("CodeRepository", {}).get("Points", 0)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas sociais para {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "found": False,
                "error": str(e)
            }

# Instância global do cliente
cryptocompare_client = CryptoCompareClient() 