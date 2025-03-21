from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import re
from urllib.parse import urlparse

from ..core.base_agent import BaseAgent
from ..integrations.coingecko import CoinGeckoClient

logger = logging.getLogger(__name__)

class TokenAgent(BaseAgent):
    """
    Agente responsável por obter e analisar informações de tokens.
    """
    
    def __init__(self):
        """
        Inicializa o agente de token.
        """
        super().__init__()
        self.coingecko = CoinGeckoClient()
        self.name = "TokenAgent"  # Nome para registro no AgentManager
        self.description = "Agente responsável por obter e analisar informações de tokens"
        logger.info("TokenAgent inicializado")
        
    async def analyze(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza análise de um token.
        
        Args:
            token_data: Dados do token para análise
            
        Returns:
            Resultado da análise
        """
        try:
            symbol = token_data.get("symbol", "").upper()
            contract_address = token_data.get("address")
            chain = token_data.get("chain", "ethereum")
            url = token_data.get("url", "")
            
            # Se foi fornecido um URL, extrair o ID do token
            token_id = None
            if url:
                extracted_data = self.extract_token_from_url(url)
                if extracted_data:
                    if "id" in extracted_data:
                        token_id = extracted_data["id"]
                    if "symbol" in extracted_data and not symbol:
                        symbol = extracted_data["symbol"].upper()
                    if "contract" in extracted_data and not contract_address:
                        contract_address = extracted_data["contract"]
                        chain = extracted_data.get("chain", chain)
            
            if not token_id and not symbol and not contract_address:
                return {
                    "error": "Symbol, URL ou address deve ser fornecido para análise de token"
                }
                
            logger.info(f"Iniciando análise do token: {symbol or token_id or contract_address}")
            
            # Buscar dados do token
            token_info = {}
            
            # Primeiro, tentar pelo ID exato (mais preciso)
            if token_id:
                token_info = await self.coingecko.get_coin_data(token_id)
            
            # Se não encontrou pelo ID ou não tinha ID, tentar pelo contrato
            if (not token_info or "error" in token_info) and contract_address:
                token_info = await self.coingecko.get_coin_by_contract(contract_address, chain)
                if "error" in token_info and symbol:
                    # Tentar pelo símbolo se falhar pelo endereço
                    token_info = await self.coingecko.get_coin_by_id(symbol.lower())
            
            # Se ainda não encontrou, tentar pelo símbolo
            if (not token_info or "error" in token_info) and symbol and not token_id:
                token_info = await self.coingecko.get_coin_by_id(symbol.lower())
            
            if not token_info or "error" in token_info:
                return {
                    "error": f"Erro ao buscar informações do token: {token_info.get('error', 'Token não encontrado')}"
                }
                
            # Obter dados de mercado
            token_id = token_info.get("id")
            market_data = await self.coingecko.get_coin_market_data(token_id)
            
            # Construir resposta
            result = {
                "name": token_info.get("name"),
                "symbol": token_info.get("symbol", "").upper(),
                "price": {
                    "current": market_data.get("current_price", {}).get("usd"),
                    "change_24h": market_data.get("price_change_percentage_24h"),
                    "change_7d": market_data.get("price_change_percentage_7d"),
                    "change_30d": market_data.get("price_change_percentage_30d")
                },
                "market_data": {
                    "market_cap": market_data.get("market_cap", {}).get("usd"),
                    "volume_24h": market_data.get("total_volume", {}).get("usd"),
                    "circulating_supply": market_data.get("circulating_supply"),
                    "total_supply": market_data.get("total_supply"),
                    "max_supply": market_data.get("max_supply"),
                    "rank": market_data.get("market_cap_rank")
                },
                "additional_info": {
                    "description": token_info.get("description", {}).get("en", ""),
                    "homepage": token_info.get("links", {}).get("homepage", [])[0] if token_info.get("links", {}).get("homepage") else None,
                    "github": token_info.get("links", {}).get("repos_url", {}).get("github", []),
                    "twitter": token_info.get("links", {}).get("twitter_screen_name"),
                    "telegram": token_info.get("links", {}).get("telegram_channel_identifier"),
                    "blockchain_explorers": token_info.get("links", {}).get("blockchain_site", []),
                    "categories": token_info.get("categories", [])
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Análise do token {symbol or token_id} concluída com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise do token: {str(e)}")
            return {
                "error": f"Falha na análise do token: {str(e)}"
            }
            
    def extract_token_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extrai informações do token a partir de uma URL do CoinGecko ou CoinMarketCap.
        
        Args:
            url: URL do token (ex: https://www.coingecko.com/en/coins/bitcoin)
            
        Returns:
            Dict com ID do token, símbolo e outras informações extraídas
        """
        try:
            if not url:
                return {}
                
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path.lower()
            
            result = {}
            
            # CoinGecko URLs
            if "coingecko.com" in domain:
                # Formato: https://www.coingecko.com/en/coins/bitcoin
                coin_match = re.search(r'/coins/([a-zA-Z0-9-_]+)', path)
                if coin_match:
                    result["id"] = coin_match.group(1)
                    result["source"] = "coingecko"
                    return result
                    
                # Formato de contrato: https://www.coingecko.com/en/coins/ethereum/contract/0x...
                contract_match = re.search(r'/coins/([a-zA-Z0-9-_]+)/contract/(0x[a-fA-F0-9]+)', path)
                if contract_match:
                    result["chain"] = contract_match.group(1)
                    result["contract"] = contract_match.group(2)
                    result["source"] = "coingecko"
                    return result
            
            # CoinMarketCap URLs
            elif "coinmarketcap.com" in domain:
                # Formato: https://coinmarketcap.com/currencies/bitcoin/
                currency_match = re.search(r'/currencies/([a-zA-Z0-9-_]+)', path)
                if currency_match:
                    # Extrair o nome do token para buscar no CoinGecko
                    cmc_id = currency_match.group(1)
                    
                    # Mapeamento conhecido de IDs do CMC para o CoinGecko
                    cmc_to_coingecko = {
                        'bitcoin': 'bitcoin',
                        'ethereum': 'ethereum',
                        'tether': 'tether',
                        'binancecoin': 'binancecoin',
                        'ripple': 'xrp',
                        'usd-coin': 'usd-coin',
                        'solana': 'solana',
                        'cardano': 'cardano',
                        'dogecoin': 'dogecoin',
                        'polkadot-new': 'polkadot'
                        # Adicionar mais mapeamentos se necessário
                    }
                    
                    # Se temos o mapeamento direto, usar ele
                    if cmc_id in cmc_to_coingecko:
                        result["id"] = cmc_to_coingecko[cmc_id]
                        result["source"] = "coinmarketcap_mapped"
                        return result
                    
                    # Extrair símbolo de uma URL do CMC (se possível)
                    # Para os principais tokens, é comum o símbolo estar no título do site
                    # Mas isso requer um scraping do HTML, o que não estamos fazendo aqui
                    
                    # Converter hífen para espaço e capitalizar para fazer busca
                    search_term = ' '.join(word.capitalize() for word in cmc_id.split('-'))
                    result["search_term"] = search_term
                    result["source"] = "coinmarketcap"
                    return result
                    
                # Formato de token no CMC: https://coinmarketcap.com/currencies/tether/tokens/
                # Para obter o address seria necessário fazer web scraping
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da URL {url}: {str(e)}")
            return {}
            
    async def validate_input(self, token_data: Dict[str, Any]) -> bool:
        """
        Valida os dados de entrada do token.
        
        Args:
            token_data: Dados do token para validação
            
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        if not token_data:
            logger.error("Dados de entrada estão vazios")
            return False
            
        # Verificar se pelo menos um dos identificadores do token está presente
        symbol = token_data.get("symbol", "")
        address = token_data.get("address", "")
        url = token_data.get("url", "")
        
        if not symbol and not address and not url:
            logger.error("Nem o símbolo, endereço ou URL do token foram fornecidos")
            return False
            
        # Se o URL foi fornecido, verificar se é uma URL válida
        if url:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.warning(f"URL fornecida é inválida: {url}")
                # Não retornamos False aqui pois ainda podemos tentar pelo símbolo ou address
        
        # Se o endereço foi fornecido, validar o formato
        if address and not (address.startswith("0x") and len(address) == 42):
            logger.warning(f"Formato de endereço potencialmente inválido: {address}")
            # Não retornamos False aqui pois ainda podemos tentar pelo símbolo
            
        return True 