"""
Cliente para interação com a API Anthropic Claude para análise de sentimento e processamento de linguagem natural.
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
import anthropic

class AnthropicClient:
    """
    Cliente para interação com a API Anthropic Claude.
    """
    
    def __init__(self):
        """
        Inicializa o cliente Anthropic Claude com a API key do .env.
        """
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        
        if not self.api_key:
            logger.warning("API key da Anthropic não encontrada no .env - algumas funcionalidades estarão limitadas")
        
        self.client = None
        self.async_client = None
        
    def _get_client(self):
        """
        Obtém o cliente Anthropic.
        
        Returns:
            anthropic.Anthropic: Cliente da API
        """
        if not self.client and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        return self.client
    
    def _get_async_client(self):
        """
        Obtém o cliente assíncrono da Anthropic.
        
        Returns:
            anthropic.AsyncAnthropic: Cliente assíncrono da API
        """
        if not self.async_client and self.api_key:
            self.async_client = anthropic.AsyncAnthropic(api_key=self.api_key)
        return self.async_client
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analisa o sentimento de um texto usando o Claude.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Dict[str, Any]: Resultado da análise de sentimento com score (0-100) e sentimento predominante
        """
        if not self.api_key:
            # Retornar análise simulada em caso de API key não disponível
            return {
                "score": 50,  # Neutro por padrão
                "sentiment": "neutral",
                "confidence": 0.7,
                "is_simulated": True
            }
        
        client = self._get_async_client()
        
        system_prompt = """
        Você é um analisador de sentimento especializado em criptomoedas e DeFi. 
        Avalie o texto fornecido e determine o sentimento geral em relação ao ativo ou protocolo mencionado.
        Responda em formato JSON com as seguintes chaves:
        - score: Valor de 0 a 100, onde 0 é extremamente negativo, 50 é neutro e 100 é extremamente positivo
        - sentiment: Uma das seguintes categorias: "very_negative", "negative", "slightly_negative", "neutral", "slightly_positive", "positive", "very_positive"
        - confidence: Sua confiança na análise, de 0 a 1
        - keywords: Lista das 3-5 palavras-chave mais importantes do texto
        """
        
        try:
            # Limitar o tamanho do texto para evitar custos excessivos
            if len(text) > 8000:
                text = text[:8000] + "..."
                
            message = await client.messages.create(
                model=self.model,
                system=system_prompt,
                max_tokens=300,
                messages=[
                    {"role": "user", "content": text}
                ]
            )
            
            response_content = message.content[0].text
            
            # Extrair apenas o JSON da resposta
            json_match = response_content.strip()
            
            # Verificar se a resposta contém JSON
            try:
                if "{" in json_match and "}" in json_match:
                    # Extrair apenas a parte JSON da resposta
                    json_start = json_match.find("{")
                    json_end = json_match.rfind("}") + 1
                    json_str = json_match[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    # Se não encontrar JSON, criar um resultado padrão
                    result = {
                        "score": 50,
                        "sentiment": "neutral",
                        "confidence": 0.5,
                        "keywords": ["unclear"]
                    }
                
                return result
                
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar JSON da resposta: {response_content}")
                return {
                    "score": 50,
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "error": "Falha ao extrair análise",
                    "keywords": ["error", "parsing"]
                }
                
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento: {str(e)}")
            return {
                "score": 50,
                "sentiment": "neutral",
                "confidence": 0,
                "error": str(e),
                "keywords": ["error"]
            }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def summarize_discussions(self, texts: List[str], query: str = None) -> Dict[str, Any]:
        """
        Sumariza múltiplos textos de discussões sobre um token.
        
        Args:
            texts: Lista de textos para sumarizar
            query: Consulta ou token específico para focar
            
        Returns:
            Dict[str, Any]: Resumo das discussões
        """
        if not self.api_key or not texts:
            # Retornar resumo simulado em caso de API key não disponível ou sem textos
            return {
                "summary": "Não foi possível gerar um resumo com os dados fornecidos.",
                "key_points": [],
                "is_simulated": True
            }
        
        client = self._get_async_client()
        
        # Preparar o contexto com os textos
        combined_text = "\n---\n".join(texts[:10])  # Limitar a 10 textos para economizar tokens
        
        if len(combined_text) > 12000:
            combined_text = combined_text[:12000] + "..."
        
        focus_point = f" sobre {query}" if query else ""
        
        system_prompt = f"""
        Você é um analista especializado em criptomoedas e DeFi. 
        Analise as discussões fornecidas{focus_point} e crie um resumo conciso dos pontos principais.
        
        Responda em formato JSON com as seguintes chaves:
        - summary: Um resumo de 2-3 parágrafos destacando os temas principais das discussões
        - sentiment: O sentimento geral predominante ("very_negative", "negative", "slightly_negative", "neutral", "slightly_positive", "positive", "very_positive")
        - key_points: Lista de 3-7 pontos-chave extraídos das discussões
        - controversies: Quaisquer controvérsias ou pontos de discordância importantes
        - insights: Até 3 insights ou conclusões importantes
        """
        
        try:
            message = await client.messages.create(
                model=self.model,
                system=system_prompt,
                max_tokens=800,
                messages=[
                    {"role": "user", "content": f"Por favor, analise estas discussões{focus_point}:\n\n{combined_text}"}
                ]
            )
            
            response_content = message.content[0].text
            
            # Extrair apenas o JSON da resposta
            try:
                if "{" in response_content and "}" in response_content:
                    # Extrair apenas a parte JSON da resposta
                    json_start = response_content.find("{")
                    json_end = response_content.rfind("}") + 1
                    json_str = response_content[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    # Se não encontrar JSON, criar um resultado padrão
                    result = {
                        "summary": "Não foi possível extrair um resumo estruturado das discussões.",
                        "sentiment": "neutral",
                        "key_points": ["Dados insuficientes para análise"],
                        "controversies": [],
                        "insights": []
                    }
                
                return result
                
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar JSON da resposta: {response_content}")
                # Tentar extrair ao menos o resumo
                return {
                    "summary": response_content[:500] + "...",
                    "sentiment": "neutral",
                    "key_points": ["Erro na análise estruturada"],
                    "controversies": [],
                    "insights": []
                }
                
        except Exception as e:
            logger.error(f"Erro ao sumarizar discussões: {str(e)}")
            return {
                "summary": "Ocorreu um erro ao processar as discussões.",
                "sentiment": "neutral",
                "key_points": [f"Erro: {str(e)}"],
                "controversies": [],
                "insights": []
            }

# Instância global para uso em toda a aplicação
anthropic_client = AnthropicClient() 