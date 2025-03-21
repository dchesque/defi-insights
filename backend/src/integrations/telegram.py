"""
Cliente para interação com o Telegram via web scraping.
"""
import os
import httpx
import re
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class TelegramClient:
    """
    Cliente para obter dados do Telegram via web scraping de canais públicos.
    Documentação: https://core.telegram.org/api/obtaining_api_id
    """
    
    def __init__(self):
        """Inicializa o cliente do Telegram."""
        logger.info("Inicializando cliente real do Telegram para canais públicos")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.cache = {}
        self.cache_ttl = 900  # 15 minutos
        
        # Canais públicos de criptmoedas para monitorar
        self.crypto_channels = {
            "cryptosignalalert": "https://t.me/s/cryptosignalalert",
            "crypto_discussions": "https://t.me/s/cryptoforbeginners",
            "altcoinsignal": "https://t.me/s/altcoinsignal",
            "binance_announcements": "https://t.me/s/binance_announcements",
            "whaleanalert": "https://t.me/s/whale_alert_io",
            "cryptonews": "https://t.me/s/cryptonews"
        }
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(lambda e: isinstance(e, (httpx.HTTPError, asyncio.TimeoutError)))
    )
    async def _fetch_channel_content(self, channel_url: str) -> str:
        """
        Faz o download do conteúdo de um canal do Telegram.
        
        Args:
            channel_url: URL do canal público
            
        Returns:
            HTML do canal
        """
        logger.info(f"Consultando canal do Telegram: {channel_url}")
        
        # Verificar se temos dados em cache
        if channel_url in self.cache:
            data, timestamp = self.cache[channel_url]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.info(f"Usando dados em cache para {channel_url}")
                return data
        
        # Fazer requisição HTTP para o canal público
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(channel_url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                
                # Salvar no cache
                self.cache[channel_url] = (response.text, datetime.now())
                
                return response.text
        except Exception as e:
            logger.error(f"Erro ao acessar canal do Telegram: {str(e)}")
            raise
            
    async def _parse_channel_messages(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extrai mensagens do HTML de um canal do Telegram.
        
        Args:
            html_content: HTML do canal
            
        Returns:
            Lista de mensagens extraídas
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            messages = []
            
            # Encontrar todas as mensagens
            message_containers = soup.select('div.tgme_widget_message_bubble')
            
            for container in message_containers:
                try:
                    # Extrair texto da mensagem
                    text_element = container.select_one('div.tgme_widget_message_text')
                    text = text_element.get_text(strip=True) if text_element else ""
                    
                    # Extrair timestamp
                    time_element = container.select_one('a.tgme_widget_message_date time')
                    timestamp = time_element.get('datetime') if time_element else ""
                    
                    # Extrair views
                    views_element = container.select_one('span.tgme_widget_message_views')
                    views = views_element.get_text(strip=True) if views_element else "0"
                    
                    # Extrair autor (nome do canal)
                    author_element = container.select_one('div.tgme_widget_message_author')
                    author = author_element.get_text(strip=True) if author_element else ""
                    
                    # Extrair ID da mensagem
                    link_element = container.select_one('a.tgme_widget_message_date')
                    message_url = link_element.get('href') if link_element else ""
                    message_id = message_url.split('/')[-1] if message_url else ""
                    
                    messages.append({
                        "id": message_id,
                        "text": text,
                        "timestamp": timestamp,
                        "views": views,
                        "author": author
                    })
                except Exception as e:
                    logger.warning(f"Erro ao processar mensagem: {str(e)}")
                    continue
                    
            return messages
        except Exception as e:
            logger.error(f"Erro ao analisar HTML do Telegram: {str(e)}")
            return []
        
    async def get_recent_discussions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém discussões recentes relacionadas a uma consulta (símbolo de token) em canais públicos.
        
        Args:
            query: Termo de busca (ex: símbolo do token)
            limit: Número máximo de resultados
            
        Returns:
            Lista de mensagens relacionadas à consulta.
        """
        logger.info(f"Buscando discussões sobre {query} no Telegram")
        all_messages = []
        
        # Buscar em todos os canais
        for channel_name, channel_url in self.crypto_channels.items():
            try:
                html_content = await self._fetch_channel_content(channel_url)
                messages = await self._parse_channel_messages(html_content)
                
                # Filtrar mensagens relacionadas à consulta
                related_messages = [
                    msg for msg in messages 
                    if query.lower() in msg["text"].lower()
                ]
                
                all_messages.extend(related_messages)
            except Exception as e:
                logger.error(f"Erro ao buscar mensagens no canal {channel_name}: {str(e)}")
        
        # Ordenar por timestamp (mais recentes primeiro) e limitar ao número solicitado
        all_messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return all_messages[:limit]
        
    async def get_channel_messages(self, channel_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Obtém mensagens de um canal específico do Telegram.
        
        Args:
            channel_name: Nome do canal
            limit: Número máximo de mensagens para retornar
            
        Returns:
            Lista de mensagens do canal.
        """
        logger.info(f"Obtendo mensagens do canal {channel_name}")
        
        # Verificar se o canal está na lista
        channel_url = self.crypto_channels.get(channel_name)
        if not channel_url:
            logger.warning(f"Canal {channel_name} não encontrado, usando canal padrão")
            # Usar o primeiro canal como padrão
            channel_name, channel_url = next(iter(self.crypto_channels.items()))
        
        try:
            html_content = await self._fetch_channel_content(channel_url)
            messages = await self._parse_channel_messages(html_content)
            return messages[:limit]
        except Exception as e:
            logger.error(f"Erro ao obter mensagens do canal {channel_name}: {str(e)}")
            return []
            
    async def check_connection(self) -> bool:
        """
        Verifica se a conexão com o Telegram está funcionando corretamente.
        
        Returns:
            True se a conexão estiver funcionando, False caso contrário.
        """
        try:
            # Tenta acessar o primeiro canal da lista
            _, channel_url = next(iter(self.crypto_channels.items()))
            await self._fetch_channel_content(channel_url)
            logger.info("Conexão com o Telegram está funcionando")
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com o Telegram: {str(e)}")
            return False

# Instância global do cliente
telegram_client = TelegramClient()