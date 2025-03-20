"""
Cliente para a API do CryptoPanic - uma fonte de notícias e análise de sentimento para criptomoedas.
"""
import os
import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class CryptoPanicClient:
    """Cliente para interagir com a API do CryptoPanic."""
    
    BASE_URL = "https://cryptopanic.com/api/v1"
    
    def __init__(self):
        """Inicializa o cliente do CryptoPanic."""
        self.api_key = os.getenv("CRYPTOPANIC_API_KEY")
        if not self.api_key:
            logger.warning("CRYPTOPANIC_API_KEY não definida. As requisições falharão.")
        
        self.cache = {}
        self.cache_ttl = 300  # Cache de 5 minutos para notícias
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do CryptoPanic.
        
        Args:
            endpoint: Caminho do endpoint da API.
            params: Parâmetros da query (opcional).
            
        Returns:
            Resposta da API em formato JSON.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Verificar se a API key está configurada
        if not self.api_key:
            raise ValueError("CRYPTOPANIC_API_KEY não configurada")
        
        # Preparar parâmetros
        request_params = params.copy() if params else {}
        request_params["auth_token"] = self.api_key
        
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
            logger.error(f"Erro HTTP ao chamar a API do CryptoPanic: {e.response.status_code} - {e.response.text}")
            raise
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do CryptoPanic: {str(e)}")
            raise
    
    async def get_news(self, currencies: Optional[str] = None, regions: Optional[str] = None, 
                     kind: Optional[str] = None, filter: Optional[str] = None, 
                     page: int = 1, public: bool = True) -> Dict[str, Any]:
        """
        Obtém notícias de criptomoedas com várias opções de filtragem.
        
        Args:
            currencies: Lista de símbolos de criptomoedas separados por vírgula (ex: "BTC,ETH").
            regions: Lista de regiões separadas por vírgula (ex: "en,br").
            kind: Tipo de notícia ("news", "media").
            filter: Filtro de notícias ("rising", "hot", "bullish", "bearish", "important", "saved").
            page: Número da página.
            public: Se True, retorna apenas notícias públicas.
            
        Returns:
            Dicionário com resultados de notícias.
        """
        params = {"page": page}
        
        if currencies:
            params["currencies"] = currencies
            
        if regions:
            params["regions"] = regions
            
        if kind:
            params["kind"] = kind
            
        if filter:
            params["filter"] = filter
            
        if public:
            params["public"] = "true"
        
        try:
            data = await self._make_request("posts", params)
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter notícias: {str(e)}")
            return {"results": []}
    
    async def get_token_sentiment(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Analisa o sentimento de mercado para um token específico com base nas notícias.
        
        Args:
            symbol: Símbolo da criptomoeda (ex: "BTC").
            days: Número de dias para analisar.
            
        Returns:
            Dicionário com análise de sentimento.
        """
        try:
            # Obter notícias relacionadas ao token
            bullish_news = await self.get_news(currencies=symbol, filter="bullish")
            bearish_news = await self.get_news(currencies=symbol, filter="bearish")
            
            # Contabilizar notícias por sentimento
            bullish_count = len(bullish_news.get("results", []))
            bearish_count = len(bearish_news.get("results", []))
            
            # Obter notícias gerais (sem filtro de sentimento)
            all_news = await self.get_news(currencies=symbol)
            all_news_count = len(all_news.get("results", []))
            
            # Calcular médias
            neutral_count = all_news_count - (bullish_count + bearish_count)
            bullish_percentage = (bullish_count / all_news_count) * 100 if all_news_count > 0 else 0
            bearish_percentage = (bearish_count / all_news_count) * 100 if all_news_count > 0 else 0
            neutral_percentage = (neutral_count / all_news_count) * 100 if all_news_count > 0 else 0
            
            # Determinar sentimento predominante
            if bullish_percentage > bearish_percentage and bullish_percentage > neutral_percentage:
                sentiment = "bullish"
            elif bearish_percentage > bullish_percentage and bearish_percentage > neutral_percentage:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            # Extrair algumas notícias recentes para exemplo
            recent_news = []
            for news in all_news.get("results", [])[:5]:
                votes = news.get("votes", {})
                news_sentiment = "neutral"
                if votes.get("positive", 0) > votes.get("negative", 0):
                    news_sentiment = "bullish"
                elif votes.get("negative", 0) > votes.get("positive", 0):
                    news_sentiment = "bearish"
                
                recent_news.append({
                    "title": news.get("title", ""),
                    "url": news.get("url", ""),
                    "published_at": news.get("published_at", ""),
                    "sentiment": news_sentiment,
                    "votes": votes
                })
            
            # Montar resultado final
            return {
                "symbol": symbol,
                "sentiment": sentiment,
                "bullish_percentage": bullish_percentage,
                "bearish_percentage": bearish_percentage,
                "neutral_percentage": neutral_percentage,
                "total_news_count": all_news_count,
                "bullish_news_count": bullish_count,
                "bearish_news_count": bearish_count,
                "neutral_news_count": neutral_count,
                "recent_news": recent_news,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento para {symbol}: {str(e)}")
            return {
                "symbol": symbol,
                "sentiment": "unknown",
                "error": str(e)
            }
    
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """
        Obtém uma visão geral do sentimento do mercado.
        
        Returns:
            Dicionário com análise de sentimento do mercado.
        """
        try:
            # Obter notícias de diferentes sentimentos
            bullish_news = await self.get_news(filter="bullish")
            bearish_news = await self.get_news(filter="bearish")
            important_news = await self.get_news(filter="important")
            all_news = await self.get_news()
            
            # Contabilizar notícias por sentimento
            bullish_count = len(bullish_news.get("results", []))
            bearish_count = len(bearish_news.get("results", []))
            all_news_count = len(all_news.get("results", []))
            
            # Calcular médias
            neutral_count = all_news_count - (bullish_count + bearish_count)
            bullish_percentage = (bullish_count / all_news_count) * 100 if all_news_count > 0 else 0
            bearish_percentage = (bearish_count / all_news_count) * 100 if all_news_count > 0 else 0
            neutral_percentage = (neutral_count / all_news_count) * 100 if all_news_count > 0 else 0
            
            # Determinar sentimento predominante do mercado
            if bullish_percentage > bearish_percentage and bullish_percentage > neutral_percentage:
                market_sentiment = "bullish"
            elif bearish_percentage > bullish_percentage and bearish_percentage > neutral_percentage:
                market_sentiment = "bearish"
            else:
                market_sentiment = "neutral"
            
            # Calcular índice de medo e ganância baseado no sentimento
            # (Escala 0-100: 0-25 medo extremo, 25-45 medo, 45-55 neutro, 55-75 ganância, 75-100 ganância extrema)
            fear_greed_index = 50 + ((bullish_percentage - bearish_percentage) / 2)
            fear_greed_index = max(0, min(100, fear_greed_index))
            
            # Definir classificação do índice
            if fear_greed_index <= 25:
                fear_greed_classification = "Medo Extremo"
            elif fear_greed_index <= 45:
                fear_greed_classification = "Medo"
            elif fear_greed_index <= 55:
                fear_greed_classification = "Neutro"
            elif fear_greed_index <= 75:
                fear_greed_classification = "Ganância"
            else:
                fear_greed_classification = "Ganância Extrema"
            
            # Extrair notícias importantes recentes
            trending_news = []
            for news in important_news.get("results", [])[:5]:
                votes = news.get("votes", {})
                news_sentiment = "neutral"
                if votes.get("positive", 0) > votes.get("negative", 0):
                    news_sentiment = "bullish"
                elif votes.get("negative", 0) > votes.get("positive", 0):
                    news_sentiment = "bearish"
                
                trending_news.append({
                    "title": news.get("title", ""),
                    "url": news.get("url", ""),
                    "published_at": news.get("published_at", ""),
                    "sentiment": news_sentiment,
                    "votes": votes,
                    "currencies": [c.get("code", "") for c in news.get("currencies", [])]
                })
            
            # Montar resultado final
            return {
                "market_sentiment": market_sentiment,
                "bullish_percentage": bullish_percentage,
                "bearish_percentage": bearish_percentage,
                "neutral_percentage": neutral_percentage,
                "total_news_count": all_news_count,
                "fear_greed_index": {
                    "value": round(fear_greed_index),
                    "classification": fear_greed_classification
                },
                "trending_news": trending_news,
                "timestamp": datetime.now().isoformat(),
                "source": "CryptoPanic"
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter sentimento geral do mercado: {str(e)}")
            return {
                "market_sentiment": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instância global do cliente
cryptopanic_client = CryptoPanicClient() 