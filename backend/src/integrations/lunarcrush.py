"""
Cliente para a API do LunarCRUSH - uma fonte de dados de sentimento social para criptomoedas.
"""
import os
import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class LunarCrushClient:
    """Cliente para interagir com a API do LunarCRUSH."""
    
    BASE_URL = "https://api.lunarcrush.com/v2"
    
    def __init__(self):
        """Inicializa o cliente do LunarCRUSH."""
        self.api_key = os.getenv("LUNARCRUSH_API_KEY")
        if not self.api_key:
            logger.warning("LUNARCRUSH_API_KEY não definida. As requisições falharão.")
        
        self.cache = {}
        self.cache_ttl = 300  # Cache de 5 minutos para dados de sentimento
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do LunarCRUSH.
        
        Args:
            endpoint: Caminho do endpoint da API.
            params: Parâmetros da query (opcional).
            
        Returns:
            Resposta da API em formato JSON.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Verificar se a API key está configurada
        if not self.api_key:
            raise ValueError("LUNARCRUSH_API_KEY não configurada")
        
        # Preparar parâmetros
        request_params = params.copy() if params else {}
        request_params["key"] = self.api_key
        
        # Verificar se temos dados em cache
        cache_key = f"{endpoint}:{json.dumps(request_params)}"
        if cache_key in self.cache:
            # Verificar se o cache ainda é válido
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=request_params
                )
                
                # Verificar se houve erro
                response.raise_for_status()
                
                # Armazenar resultado no cache
                result = response.json()
                self.cache[cache_key] = (result, datetime.now())
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao chamar a API do LunarCRUSH: {e.response.status_code} - {e.response.text}")
            raise
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do LunarCRUSH: {str(e)}")
            raise
    
    async def get_assets(self, limit: int = 10, page: int = 1) -> List[Dict[str, Any]]:
        """
        Obtém a lista dos ativos de criptomoeda mais populares.
        
        Args:
            limit: Número máximo de resultados por página.
            page: Número da página.
            
        Returns:
            Lista de ativos.
        """
        params = {
            "data": "market",
            "limit": limit,
            "page": page
        }
        
        try:
            data = await self._make_request("", params)
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter lista de ativos: {str(e)}")
            return []
    
    async def get_asset(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um ativo específico.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            
        Returns:
            Dicionário com informações do ativo.
        """
        params = {
            "data": "assets",
            "symbol": symbol
        }
        
        try:
            data = await self._make_request("", params)
            assets = data.get("data", [])
            
            if not assets:
                logger.warning(f"Ativo com símbolo {symbol} não encontrado")
                return {}
                
            return assets[0]
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do ativo {symbol}: {str(e)}")
            return {}
    
    async def get_feeds(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém feeds de notícias e mídias sociais para um ativo específico.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            limit: Número máximo de resultados.
            
        Returns:
            Lista de feeds sociais.
        """
        params = {
            "data": "feeds",
            "symbol": symbol,
            "limit": limit
        }
        
        try:
            data = await self._make_request("", params)
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter feeds para {symbol}: {str(e)}")
            return []
    
    async def get_coin_of_the_day(self) -> Dict[str, Any]:
        """
        Obtém o "Coin of the Day" do LunarCRUSH.
        
        Returns:
            Dicionário com informações da moeda do dia.
        """
        params = {
            "data": "market",
            "type": "fast",
            "sort": "galaxy_score",
            "desc": True,
            "limit": 1
        }
        
        try:
            data = await self._make_request("", params)
            coins = data.get("data", [])
            
            if not coins:
                return {}
                
            return coins[0]
            
        except Exception as e:
            logger.error(f"Erro ao obter coin of the day: {str(e)}")
            return {}
    
    async def get_galaxy_score(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém o "Galaxy Score" para um ativo específico.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            
        Returns:
            Dicionário com o Galaxy Score e outras métricas.
        """
        try:
            asset_data = await self.get_asset(symbol)
            
            if not asset_data:
                return {
                    "symbol": symbol,
                    "error": "Asset not found"
                }
                
            return {
                "symbol": symbol,
                "galaxy_score": asset_data.get("galaxy_score", 0),
                "alt_rank": asset_data.get("alt_rank", 0),
                "social_score": asset_data.get("social_score", 0),
                "social_volume": asset_data.get("social_volume", 0),
                "social_impact_score": asset_data.get("social_impact_score", 0),
                "average_sentiment": asset_data.get("average_sentiment", 0),
                "sentiment_absolute": asset_data.get("sentiment_absolute", 0),
                "twitter_volume": asset_data.get("twitter_volume", 0),
                "reddit_volume": asset_data.get("reddit_volume", 0),
                "news_volume": asset_data.get("news_volume", 0)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter Galaxy Score para {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "error": str(e)
            }
    
    async def get_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém análise de sentimento social para um ativo específico.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            
        Returns:
            Dicionário com sentimento social.
        """
        try:
            # Obter dados do ativo
            asset_data = await self.get_asset(symbol)
            
            if not asset_data:
                return {
                    "symbol": symbol,
                    "error": "Asset not found"
                }
            
            # Obter feeds recentes
            feeds = await self.get_feeds(symbol, limit=20)
            
            # Analisar sentimento dos feeds
            feed_sentiments = []
            for feed in feeds:
                feed_sentiments.append({
                    "source": feed.get("type", ""),
                    "title": feed.get("title", ""),
                    "sentiment": feed.get("sentiment", 0),
                    "url": feed.get("url", ""),
                    "time": feed.get("time", 0)
                })
            
            # Calcular métricas
            return {
                "symbol": symbol,
                "name": asset_data.get("name", ""),
                "timestamp": datetime.now().isoformat(),
                "average_sentiment": asset_data.get("average_sentiment", 0),
                "sentiment_absolute": asset_data.get("sentiment_absolute", 0),
                "bullish_sentiment": asset_data.get("sentiment_1d", {}).get("bullish", 0),
                "bearish_sentiment": asset_data.get("sentiment_1d", {}).get("bearish", 0),
                "neutral_sentiment": asset_data.get("sentiment_1d", {}).get("neutral", 0),
                "social_impact_score": asset_data.get("social_impact_score", 0),
                "social_score": asset_data.get("social_score", 0),
                "social_volume": asset_data.get("social_volume", 0),
                "social_volume_change_24h": asset_data.get("social_volume_global_rank_pct_change", 0),
                "social_contributors": asset_data.get("social_contributors", 0),
                "galaxy_score": asset_data.get("galaxy_score", 0),
                "alt_rank": asset_data.get("alt_rank", 0),
                "twitter_volume": asset_data.get("twitter_volume", 0),
                "reddit_volume": asset_data.get("reddit_volume", 0),
                "news_volume": asset_data.get("news_volume", 0),
                "recent_feeds": feed_sentiments[:10] if feed_sentiments else []
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter sentimento social para {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "error": str(e)
            }
    
    async def get_market_sentiment(self, top_coins: int = 10) -> Dict[str, Any]:
        """
        Obtém uma visão geral do sentimento do mercado.
        
        Args:
            top_coins: Número de principais moedas a analisar.
            
        Returns:
            Dicionário com sentimento geral do mercado.
        """
        try:
            # Obter top moedas
            top_assets = await self.get_assets(limit=top_coins)
            
            if not top_assets:
                return {
                    "error": "No assets found"
                }
            
            # Calcular médias de sentimento
            total_sentiment = 0
            total_galaxy_score = 0
            total_bullish = 0
            total_bearish = 0
            total_neutral = 0
            
            for asset in top_assets:
                total_sentiment += asset.get("average_sentiment", 0)
                total_galaxy_score += asset.get("galaxy_score", 0)
                total_bullish += asset.get("sentiment_1d", {}).get("bullish", 0)
                total_bearish += asset.get("sentiment_1d", {}).get("bearish", 0)
                total_neutral += asset.get("sentiment_1d", {}).get("neutral", 0)
            
            # Lista de moedas analisadas
            coins_analyzed = [{
                "symbol": asset.get("symbol", ""),
                "name": asset.get("name", ""),
                "average_sentiment": asset.get("average_sentiment", 0),
                "galaxy_score": asset.get("galaxy_score", 0),
                "social_volume": asset.get("social_volume", 0),
                "price_btc": asset.get("price_btc", 0),
                "percent_change_24h": asset.get("percent_change_24h", 0),
                "sentiment_relative_change_24h": asset.get("average_sentiment_relative_change", 0)
            } for asset in top_assets]
            
            # Determinar sentimento geral
            avg_sentiment = total_sentiment / len(top_assets) if top_assets else 0
            sentiment_classification = "neutral"
            
            if avg_sentiment > 60:
                sentiment_classification = "bullish"
            elif avg_sentiment < 40:
                sentiment_classification = "bearish"
            
            # Moeda do dia
            coin_of_day = await self.get_coin_of_the_day()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "average_sentiment": avg_sentiment,
                "sentiment_classification": sentiment_classification,
                "average_galaxy_score": total_galaxy_score / len(top_assets) if top_assets else 0,
                "bullish_percentage": (total_bullish / (total_bullish + total_bearish + total_neutral)) * 100 if (total_bullish + total_bearish + total_neutral) > 0 else 0,
                "bearish_percentage": (total_bearish / (total_bullish + total_bearish + total_neutral)) * 100 if (total_bullish + total_bearish + total_neutral) > 0 else 0,
                "neutral_percentage": (total_neutral / (total_bullish + total_bearish + total_neutral)) * 100 if (total_bullish + total_bearish + total_neutral) > 0 else 0,
                "coins_analyzed": coins_analyzed,
                "coin_of_day": {
                    "symbol": coin_of_day.get("symbol", ""),
                    "name": coin_of_day.get("name", ""),
                    "galaxy_score": coin_of_day.get("galaxy_score", 0),
                    "alt_rank": coin_of_day.get("alt_rank", 0),
                    "average_sentiment": coin_of_day.get("average_sentiment", 0),
                    "social_volume": coin_of_day.get("social_volume", 0),
                    "percent_change_24h": coin_of_day.get("percent_change_24h", 0)
                } if coin_of_day else {}
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter sentimento geral do mercado: {str(e)}")
            return {
                "error": str(e)
            }

# Instância global do cliente
lunarcrush_client = LunarCrushClient() 