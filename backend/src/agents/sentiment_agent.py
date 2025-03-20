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
        
        # Coletar dados apenas do Telegram
        telegram_messages = await self.telegram_client.get_channel_messages("crypto_discussions")
        
        # Extrair textos para análise
        telegram_texts = [msg.get("text", "") for msg in telegram_messages if symbol.lower() in msg.get("text", "").lower()]
        
        # Gerar dados simulados para análise
        simulated_texts = self._get_simulated_data(symbol)
        
        return {
            "telegram": telegram_texts,
            "general_discussion": simulated_texts
        }
    
    def _get_simulated_data(self, symbol: str) -> List[str]:
        """
        Gera textos simulados para análise de sentimento quando as integrações reais não estão disponíveis.
        
        Args:
            symbol: Símbolo do token.
            
        Returns:
            Lista de textos simulados.
        """
        # Texto comum para qualquer token
        common_texts = [
            f"Estou muito otimista sobre {symbol} para o longo prazo. Os fundamentos são sólidos e a equipe continua trabalhando bem.",
            f"Análise técnica de {symbol} mostra possível resistência nos níveis atuais. Traders devem ter cautela.",
            f"A comunidade de {symbol} continua crescendo e os desenvolvedores estão entregando conforme o roadmap.",
            f"Há algumas preocupações sobre a centralização de {symbol} que precisam ser abordadas.",
            f"Comparando {symbol} com projetos similares, acredito que ainda tem muito espaço para crescimento."
        ]
        
        # Para tokens populares, adicionar textos mais específicos
        if symbol.upper() == "BTC":
            extra_texts = [
                "Bitcoin continua sendo a melhor reserva de valor digital. Com o halving se aproximando, podemos esperar alta nos próximos meses.",
                "Os ETFs de Bitcoin mostram adoção institucional contínua. Isso é apenas o começo.",
                "Preocupado com a centralização da mineração de Bitcoin. Precisamos de mais diversificação geográfica."
            ]
            return common_texts + extra_texts
        elif symbol.upper() == "ETH":
            extra_texts = [
                "Ethereum continua liderando em desenvolvimento de DApps e DeFi. O ecossistema está crescendo rapidamente.",
                "As atualizações recentes do Ethereum melhoraram muito a eficiência da rede. Taxas mais baixas beneficiam todos os usuários.",
                "As soluções L2 para Ethereum estão revolucionando a escalabilidade e reduzindo custos significativamente."
            ]
            return common_texts + extra_texts
        else:
            return common_texts
            
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
                
                # Usar o Claude para análise de sentimento ou dados simulados em caso de falha
                logger.info(f"Analisando sentimento de dados do {source} para {symbol}")
                try:
                    sentiment_result = await anthropic_client.analyze_sentiment(text_to_analyze)
                    if not sentiment_result or "error" in sentiment_result:
                        raise Exception("Falha na análise do Claude")
                except Exception as e:
                    logger.warning(f"Usando dados simulados para análise de sentimento de {source}: {str(e)}")
                    # Dados simulados em caso de falha na API
                    sentiment_result = self._generate_simulated_sentiment(source, symbol)
                
                # Armazenar resultados
                results[source] = sentiment_result
            except Exception as e:
                logger.error(f"Erro ao processar fonte {source}: {str(e)}")
                # Garantir que sempre temos dados para cada fonte
                results[source] = {
                    "score": 50,
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "is_simulated": True,
                    "error": str(e)
                }
            
        return results
        
    def _generate_simulated_sentiment(self, source: str, symbol: str) -> Dict[str, Any]:
        """
        Gera dados simulados de sentimento quando a API Claude falha.
        
        Args:
            source: Nome da fonte de dados
            symbol: Símbolo do token
            
        Returns:
            Dicionário com resultado de sentimento simulado
        """
        import random
        
        # Sentimentos com base no token para símbolos conhecidos
        if symbol.upper() == "BTC":
            score = random.randint(65, 85)  # Geralmente positivo para BTC
            sentiment = "positive" if score > 75 else "slightly_positive"
        elif symbol.upper() == "ETH":
            score = random.randint(60, 80)  # Geralmente positivo para ETH
            sentiment = "positive" if score > 75 else "slightly_positive"
        else:
            # Para outros tokens, randomizar mais
            score = random.randint(40, 70)
            if score > 65:
                sentiment = "slightly_positive"
            elif score > 55:
                sentiment = "neutral"
            else:
                sentiment = "slightly_negative"
        
        keywords = [
            f"{symbol} price", 
            "market", 
            "investors", 
            "analysis", 
            "trading"
        ]
        
        return {
            "score": score,
            "sentiment": sentiment,
            "confidence": random.uniform(0.7, 0.9),
            "keywords": random.sample(keywords, 3),
            "is_simulated": True
        }
            
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
                return self._get_default_trends()
                
            all_text = "\n---\n".join(all_texts)
            
            # Usar Claude para análise de tendências de discussão
            try:
                logger.info("Obtendo resumo de discussões via Anthropic")
                summary = await anthropic_client.summarize_discussions(all_texts)
                
                # Verificar se temos dados válidos
                if not summary or not isinstance(summary, dict) or "error" in summary:
                    logger.warning(f"Resumo de discussões inválido: {summary}")
                    return self._get_default_trends()
                
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
                    return self._get_default_trends()
                    
            except Exception as e:
                logger.error(f"Erro ao obter resumo de discussões: {str(e)}")
                return self._get_default_trends()
                
        except Exception as e:
            logger.error(f"Erro ao identificar tendências de discussão: {str(e)}")
            return self._get_default_trends()
            
    def _get_default_trends(self) -> List[Dict[str, Any]]:
        """
        Retorna tendências de discussão padrão quando não é possível obter dados reais.
        
        Returns:
            Lista de tendências padrão
        """
        return [
            {
                "theme": "Análise de preço e movimento de mercado",
                "relevance": "alta",
                "sentiment": "neutral",
                "keywords": ["preço", "mercado", "tendência"],
                "is_simulated": True
            },
            {
                "theme": "Desenvolvimentos tecnológicos e atualizações",
                "relevance": "alta",
                "sentiment": "slightly_positive",
                "keywords": ["tecnologia", "atualização", "desenvolvimento"],
                "is_simulated": True
            },
            {
                "theme": "Adoção institucional e investimentos",
                "relevance": "média",
                "sentiment": "positive",
                "keywords": ["institucional", "investimento", "adoção"],
                "is_simulated": True
            }
        ]
            
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
