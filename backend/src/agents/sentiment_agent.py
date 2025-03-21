"""
Agente de análise de sentimento para tokens.
"""
import asyncio
import os
import logging
import json
import time
from datetime import datetime
import re
from typing import Dict, List, Any, Optional
from loguru import logger

from ..core.base_agent import BaseAgent
from ..integrations.telegram import TelegramClient
from ..integrations.anthropic import anthropic_client
from ..utils.cache import Cache

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAgent(BaseAgent):
    """
    Agente especializado em análise de sentimento de tokens baseado em dados sociais.
    """
    
    def __init__(self):
        """Inicializa o agente de análise de sentimento."""
        super().__init__()
        self.telegram_client = TelegramClient()
        self.cache = Cache()
        self.name = "SentimentAgent"
        
    async def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Valida os dados de entrada para análise de sentimento.
        
        Args:
            data: Dados de entrada contendo ao menos o símbolo do token.
            
        Returns:
            True se os dados forem válidos, False caso contrário.
        """
        if not data:
            logger.error("Dados de entrada vazios")
            return False
            
        if "symbol" not in data:
            logger.error("Símbolo do token não fornecido")
            return False
            
        return True
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza a análise de sentimento para um token.
        
        Args:
            data: Dados de entrada contendo o símbolo do token.
            
        Returns:
            Dicionário com os resultados da análise de sentimento.
        """
        if not await self.validate_input(data):
            return {"error": "Dados de entrada inválidos"}
            
        try:
            symbol = data["symbol"]
            logger.info(f"Iniciando análise de sentimento para o token: {symbol}")
            
            # Verificar cache
            cache_key = f"sentiment_{symbol}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Retornando resultado em cache para {symbol}")
                return cached_result
            
            # Obter dados sociais de diferentes fontes
            social_data = await self._fetch_social_data(symbol)
            
            # Analisar sentimento dos dados coletados
            sentiment_results = await self._analyze_sentiment(symbol, social_data)
            
            # Calcular métricas de engajamento
            engagement_metrics = self._calculate_engagement_metrics(social_data)
            
            # Identificar tendências de discussão
            discussion_trends = await self._identify_discussion_trends(social_data)
            
            # Compilar resultados
            results = {
                "symbol": symbol,
                "overall_sentiment": self._calculate_overall_sentiment(sentiment_results),
                "sentiment_by_source": sentiment_results,
                "engagement_metrics": engagement_metrics,
                "discussion_trends": discussion_trends,
                "timestamp": datetime.now().isoformat()
            }
            
            # Salvar no cache
            await self.cache.set(cache_key, results)
            
            logger.info(f"Análise de sentimento concluída para o token: {symbol}")
            return results
            
        except Exception as e:
            logger.error(f"Erro ao realizar análise de sentimento: {str(e)}")
            return {"error": f"Falha na análise: {str(e)}"}
            
    async def _fetch_social_data(self, symbol: str) -> Dict[str, List[str]]:
        """
        Coleta dados sociais relacionados ao token.
        
        Args:
            symbol: Símbolo do token.
            
        Returns:
            Dicionário com dados sociais por fonte.
        """
        logger.info(f"Coletando dados sociais para {symbol}")
        
        # Coletar dados do Telegram
        telegram_messages = await self.telegram_client.get_channel_messages("crypto_discussions")
        telegram_discussions = await self.telegram_client.get_recent_discussions(symbol)
        
        # Extrair textos para análise
        telegram_channel_texts = [msg.get("text", "") for msg in telegram_messages if symbol.lower() in msg.get("text", "").lower()]
        telegram_discussion_texts = [msg.get("text", "") for msg in telegram_discussions]
        
        # Combinar textos do Telegram
        telegram_texts = telegram_channel_texts + telegram_discussion_texts
        
        # Buscar dados de notícias de criptomoedas via CoinGecko
        try:
            from ..integrations.coingecko import coingecko_client
            news_data = await coingecko_client.get_coin_news(symbol.lower())
            news_texts = [f"{item.get('title', '')}: {item.get('description', '')}" for item in news_data if item.get('title')]
        except Exception as e:
            logger.warning(f"Erro ao obter notícias do CoinGecko: {str(e)}")
            news_texts = []
        
        return {
            "telegram": telegram_texts,
            "news": news_texts
        }
    
    async def _analyze_sentiment(self, symbol: str, social_data: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Analisa o sentimento dos dados sociais coletados.
        
        Args:
            symbol: Símbolo do token.
            social_data: Dados sociais coletados de diferentes fontes.
            
        Returns:
            Dicionário com análises de sentimento por fonte.
        """
        results = {}
        
        # Processar cada fonte de dados
        for source, posts in social_data.items():
            try:
                if not posts:
                    logger.info(f"Sem dados de {source} para {symbol}")
                    results[source] = {
                        "score": 50,
                        "sentiment": "neutral",
                        "confidence": 0,
                        "no_data": True
                    }
                    continue
                    
                # Concatenar todos os posts para análise
                text_to_analyze = "\n".join(posts[:10])  # Limitar a 10 posts para economia
                
                # Usar o Claude para análise de sentimento
                logger.info(f"Analisando sentimento de dados do {source} para {symbol}")
                sentiment_result = await anthropic_client.analyze_sentiment(text_to_analyze)
                
                # Armazenar resultados
                results[source] = sentiment_result
            except Exception as e:
                logger.error(f"Erro ao processar fonte {source}: {str(e)}")
                # Garantir que sempre temos dados para cada fonte
                results[source] = {
                    "score": 50,
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "error": str(e)
                }
            
        return results
        
    def _calculate_engagement_metrics(self, social_data: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Calcula métricas de engajamento com base nos dados sociais.
        
        Args:
            social_data: Dados sociais coletados de diferentes fontes.
            
        Returns:
            Dicionário com métricas de engajamento.
        """
        total_mentions = sum(len(posts) for posts in social_data.values())
        
        return {
            "total_mentions": total_mentions,
            "mentions_by_source": {source: len(posts) for source, posts in social_data.items()},
            "activity_level": "alto" if total_mentions > 10 else "médio" if total_mentions > 5 else "baixo",
            "trend": "crescente"  # Em um caso real, compararíamos com dados históricos
        }
            
    async def _identify_discussion_trends(self, social_data: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Identifica tendências de discussão nos dados sociais.
        
        Args:
            social_data: Dados sociais coletados de diferentes fontes.
            
        Returns:
            Lista de tendências identificadas.
        """
        try:
            # Concatenar todos os textos para análise
            all_texts = []
            for source, texts in social_data.items():
                all_texts.extend(texts[:5])  # Limitar a 5 posts por fonte
                
            if not all_texts:
                logger.warning("Sem textos para identificar tendências de discussão")
                return []
                
            all_text = "\n---\n".join(all_texts)
            
            # Usar Claude para análise de tendências de discussão
            try:
                logger.info("Obtendo resumo de discussões via Anthropic")
                summary = await anthropic_client.summarize_discussions(all_texts)
                
                # Verificar se temos dados válidos
                if not summary or not isinstance(summary, dict) or "error" in summary:
                    logger.warning(f"Resumo de discussões inválido: {summary}")
                    return []
                
                # Extrair tendências do resumo
                trends = []
                if "key_points" in summary and summary["key_points"]:
                    for i, point in enumerate(summary.get("key_points", [])[:5]):
                        trends.append({
                            "theme": point,
                            "relevance": "alta" if i < 2 else "média" if i < 4 else "baixa",
                            "sentiment": summary.get("sentiment", "neutral"),
                            "keywords": []  # Em uma implementação completa, extrairíamos palavras-chave
                        })
                    return trends
                else:
                    logger.warning("Resumo não contém pontos-chave")
                    return []
                    
            except Exception as e:
                logger.error(f"Erro ao obter resumo de discussões: {str(e)}")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao identificar tendências de discussão: {str(e)}")
            return []
            
    def _calculate_overall_sentiment(self, sentiment_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula o sentimento geral com base nos resultados de diferentes fontes.
        
        Args:
            sentiment_results: Resultados de sentimento por fonte.
            
        Returns:
            Dicionário com o sentimento geral.
        """
        try:
            # Extrair pontuações de sentimento de cada fonte
            scores = []
            confidence_values = []
            
            for source, result in sentiment_results.items():
                if "no_data" in result and result["no_data"]:
                    continue
                    
                score = result.get("score")
                confidence = result.get("confidence", 0.5)
                
                if score is not None:
                    scores.append(score * confidence)
                    confidence_values.append(confidence)
            
            # Calcular média ponderada
            if not scores:
                return {
                    "score": 50,
                    "sentiment": "neutral",
                    "confidence": 0,
                    "sources_count": 0
                }
                
            weighted_avg = sum(scores) / sum(confidence_values) if sum(confidence_values) > 0 else 50
            
            # Determinar o sentimento com base na pontuação
            sentiment = "very_negative"
            if weighted_avg >= 85:
                sentiment = "very_positive"
            elif weighted_avg >= 65:
                sentiment = "positive"
            elif weighted_avg >= 55:
                sentiment = "slightly_positive"
            elif weighted_avg >= 45:
                sentiment = "neutral"
            elif weighted_avg >= 35:
                sentiment = "slightly_negative"
            elif weighted_avg >= 15:
                sentiment = "negative"
                
            # Calcular confiança geral
            avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
            
            return {
                "score": round(weighted_avg, 1),
                "sentiment": sentiment,
                "confidence": round(avg_confidence, 2),
                "sources_count": len(scores)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular sentimento geral: {str(e)}")
            return {
                "score": 50,
                "sentiment": "neutral",
                "confidence": 0,
                "error": str(e)
            }
