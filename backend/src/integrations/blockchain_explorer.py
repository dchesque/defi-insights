"""
Cliente para obter dados on-chain de exploradores de blockchain através de web scraping.
"""
import os
import httpx
import re
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio

class BlockchainExplorerClient:
    """
    Cliente para obter dados on-chain de exploradores de blockchain.
    Usa web scraping para obter dados sem necessidade de API key.
    """
    
    def __init__(self):
        """Inicializa o cliente de explorador de blockchain."""
        self.explorers = {
            "eth": "https://etherscan.io",
            "bsc": "https://bscscan.com",
            "polygon": "https://polygonscan.com",
            "arbitrum": "https://arbiscan.io",
            "optimism": "https://optimistic.etherscan.io",
            "avalanche": "https://snowtrace.io"
        }
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
    def _is_valid_address(self, address: str) -> bool:
        """
        Verifica se um endereço de blockchain é válido.
        
        Args:
            address: Endereço para verificar
            
        Returns:
            True se o endereço for válido.
        """
        # Verificação básica para endereços ETH/EVM (42 caracteres começando com 0x)
        return bool(address and len(address) == 42 and address.startswith("0x"))
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, asyncio.TimeoutError))
    )
    async def _fetch_page(self, url: str) -> str:
        """
        Faz o download de uma página web.
        
        Args:
            url: URL para download
            
        Returns:
            Conteúdo HTML da página
        """
        logger.debug(f"Fazendo download de {url}")
        
        # Verificar cache
        if url in self.cache:
            data, timestamp = self.cache[url]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.debug(f"Usando dados em cache para {url}")
                return data
                
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                
                # Salvar no cache
                self.cache[url] = (response.text, datetime.now())
                
                return response.text
        except Exception as e:
            logger.error(f"Erro ao fazer download de {url}: {str(e)}")
            raise
        
    async def get_address_info(self, address: str, chain: str = "eth") -> Dict[str, Any]:
        """
        Obtém informações básicas sobre um endereço de carteira ou contrato.
        
        Args:
            address: Endereço da carteira ou contrato
            chain: Cadeia de blocos (eth, bsc, polygon, etc.)
            
        Returns:
            Dados do endereço.
        """
        if not self._is_valid_address(address):
            logger.error(f"Endereço inválido: {address}")
            return {"error": "Endereço inválido"}
            
        # Obter base URL do explorer para a chain
        explorer_url = self.explorers.get(chain.lower())
        if not explorer_url:
            logger.error(f"Chain não suportada: {chain}")
            return {"error": f"Chain não suportada: {chain}"}
            
        # Construir URL para o endereço
        address_url = f"{explorer_url}/address/{address}"
        
        try:
            # Fazer download da página
            html_content = await self._fetch_page(address_url)
            
            # Extrair informações
            return await self._parse_address_info(html_content, address, chain)
        except Exception as e:
            logger.error(f"Erro ao obter informações do endereço {address}: {str(e)}")
            return {"error": f"Falha ao obter dados: {str(e)}"}
        
    async def _parse_address_info(self, html_content: str, address: str, chain: str) -> Dict[str, Any]:
        """
        Extrai informações do endereço a partir do HTML.
        
        Args:
            html_content: HTML da página do endereço
            address: Endereço consultado
            chain: Cadeia de blocos
            
        Returns:
            Informações extraídas do endereço
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            result = {
                "address": address,
                "chain": chain,
                "timestamp": datetime.now().isoformat()
            }
            
            # Extrair saldo em ETH/moeda nativa
            balance_element = soup.select_one("div.card-body span.u-label")
            if balance_element:
                balance_text = balance_element.get_text(strip=True)
                # Extrair valor numérico usando regex
                balance_match = re.search(r'(\d+\.?\d*)', balance_text)
                result["balance"] = float(balance_match.group(1)) if balance_match else 0
                result["currency"] = "ETH" if chain == "eth" else chain.upper()
            
            # Verificar se é um contrato
            is_contract = "Contract" in html_content or "Contract Address" in html_content
            result["is_contract"] = is_contract
            
            if is_contract:
                # Tentar encontrar nome do contrato/token
                token_name_element = soup.select_one("span.h4")
                if token_name_element:
                    result["token_name"] = token_name_element.get_text(strip=True)
                
                # Extrair dados do token se for um contrato ERC-20
                result["token_data"] = await self._extract_token_data(soup)
            
            # Extrair última atividade
            txs_element = soup.select_one("a[href*='txs']")
            if txs_element:
                txs_text = txs_element.get_text(strip=True)
                txs_match = re.search(r'(\d+)', txs_text)
                result["transaction_count"] = int(txs_match.group(1)) if txs_match else 0
            
            return result
        except Exception as e:
            logger.error(f"Erro ao analisar informações do endereço: {str(e)}")
            return {
                "address": address,
                "chain": chain,
                "error": f"Erro ao analisar página: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _extract_token_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extrai dados de um token a partir da sopa HTML.
        
        Args:
            soup: BeautifulSoup da página do token
            
        Returns:
            Dados do token extraídos
        """
        token_data = {}
        
        # Extrair informações básicas do token
        try:
            # Encontrar símbolos
            symbol_element = soup.select_one("span.text-secondary")
            if symbol_element:
                token_data["symbol"] = symbol_element.get_text(strip=True)
            
            # Encontrar decimais
            decimals_element = soup.find(string=re.compile("Decimals"))
            if decimals_element and decimals_element.parent:
                decimals_text = decimals_element.parent.get_text(strip=True)
                decimals_match = re.search(r'Decimals:\s*(\d+)', decimals_text)
                token_data["decimals"] = int(decimals_match.group(1)) if decimals_match else 18
            
            # Encontrar supply
            total_supply_element = soup.find(string=re.compile("Total Supply"))
            if total_supply_element and total_supply_element.parent:
                supply_text = total_supply_element.parent.get_text(strip=True)
                supply_match = re.search(r'([\d,\.]+)', supply_text)
                if supply_match:
                    # Remover vírgulas e converter para float
                    supply = supply_match.group(1).replace(',', '')
                    token_data["total_supply"] = float(supply)
        except Exception as e:
            logger.warning(f"Erro ao extrair dados do token: {str(e)}")
            
        return token_data
        
    async def get_token_holders(self, token_address: str, chain: str = "eth") -> List[Dict[str, Any]]:
        """
        Obtém informações sobre os principais detentores de um token.
        
        Args:
            token_address: Endereço do contrato do token
            chain: Cadeia de blocos (eth, bsc, polygon, etc.)
            
        Returns:
            Lista com os principais detentores.
        """
        if not self._is_valid_address(token_address):
            logger.error(f"Endereço de token inválido: {token_address}")
            return [{"error": "Endereço de token inválido"}]
            
        # Obter base URL do explorer para a chain
        explorer_url = self.explorers.get(chain.lower())
        if not explorer_url:
            logger.error(f"Chain não suportada: {chain}")
            return [{"error": f"Chain não suportada: {chain}"}]
            
        # Construir URL para os detentores do token
        holders_url = f"{explorer_url}/token/{token_address}#balances"
        
        try:
            # Fazer download da página
            html_content = await self._fetch_page(holders_url)
            
            # Extrair informações dos detentores
            return await self._parse_token_holders(html_content, token_address, chain)
        except Exception as e:
            logger.error(f"Erro ao obter detentores do token {token_address}: {str(e)}")
            return [{"error": f"Falha ao obter dados: {str(e)}"}]
    
    async def _parse_token_holders(self, html_content: str, token_address: str, chain: str) -> List[Dict[str, Any]]:
        """
        Extrai informações sobre os detentores de tokens a partir do HTML.
        
        Args:
            html_content: HTML da página de detentores
            token_address: Endereço do token
            chain: Cadeia de blocos
            
        Returns:
            Lista de detentores de tokens
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            holders = []
            
            # Encontrar tabela de detentores
            table = soup.select_one("table.table")
            if not table:
                return []
                
            rows = table.select("tbody tr")
            for row in rows:
                try:
                    columns = row.select("td")
                    if len(columns) >= 3:
                        rank_text = columns[0].get_text(strip=True)
                        address_element = columns[1].select_one("a")
                        address = address_element.get("href").split("/")[-1] if address_element else "Unknown"
                        address_text = address_element.get_text(strip=True) if address_element else "Unknown"
                        quantity_text = columns[2].get_text(strip=True)
                        percentage_text = columns[3].get_text(strip=True) if len(columns) > 3 else "0%"
                        
                        # Extrair valores numéricos
                        rank = int(rank_text) if rank_text.isdigit() else 0
                        quantity_match = re.search(r'([\d,\.]+)', quantity_text)
                        quantity = float(quantity_match.group(1).replace(',', '')) if quantity_match else 0
                        percentage_match = re.search(r'([\d\.]+)', percentage_text)
                        percentage = float(percentage_match.group(1)) if percentage_match else 0
                        
                        holder = {
                            "rank": rank,
                            "address": address,
                            "address_label": address_text if address_text != address else None,
                            "quantity": quantity,
                            "percentage": percentage
                        }
                        holders.append(holder)
                except Exception as e:
                    logger.warning(f"Erro ao processar detentor de token: {str(e)}")
                    continue
                    
            return holders
        except Exception as e:
            logger.error(f"Erro ao analisar detentores do token: {str(e)}")
            return []
            
    async def get_token_transactions(self, token_address: str, limit: int = 10, chain: str = "eth") -> List[Dict[str, Any]]:
        """
        Obtém transações recentes de um token.
        
        Args:
            token_address: Endereço do contrato do token
            limit: Número máximo de transações a retornar
            chain: Cadeia de blocos (eth, bsc, polygon, etc.)
            
        Returns:
            Lista de transações recentes
        """
        if not self._is_valid_address(token_address):
            logger.error(f"Endereço de token inválido: {token_address}")
            return [{"error": "Endereço de token inválido"}]
            
        # Obter base URL do explorer para a chain
        explorer_url = self.explorers.get(chain.lower())
        if not explorer_url:
            logger.error(f"Chain não suportada: {chain}")
            return [{"error": f"Chain não suportada: {chain}"}]
            
        # Construir URL para as transações do token
        transactions_url = f"{explorer_url}/token/{token_address}#transactions"
        
        try:
            # Fazer download da página
            html_content = await self._fetch_page(transactions_url)
            
            # Extrair informações das transações
            transactions = await self._parse_token_transactions(html_content, token_address, chain)
            return transactions[:limit]
        except Exception as e:
            logger.error(f"Erro ao obter transações do token {token_address}: {str(e)}")
            return [{"error": f"Falha ao obter dados: {str(e)}"}]
            
    async def _parse_token_transactions(self, html_content: str, token_address: str, chain: str) -> List[Dict[str, Any]]:
        """
        Extrai informações sobre transações de tokens a partir do HTML.
        
        Args:
            html_content: HTML da página de transações
            token_address: Endereço do token
            chain: Cadeia de blocos
            
        Returns:
            Lista de transações de tokens
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            transactions = []
            
            # Encontrar tabela de transações
            table = soup.select_one("table.table")
            if not table:
                return []
                
            rows = table.select("tbody tr")
            for row in rows:
                try:
                    columns = row.select("td")
                    if len(columns) >= 6:
                        tx_hash_element = columns[0].select_one("a")
                        tx_hash = tx_hash_element.get("href").split("/")[-1] if tx_hash_element else "Unknown"
                        
                        method_element = columns[1].select_one("span")
                        method = method_element.get_text(strip=True) if method_element else "Transfer"
                        
                        timestamp_element = columns[2].select_one("span[title]")
                        timestamp = timestamp_element.get("title", "") if timestamp_element else ""
                        
                        from_element = columns[3].select_one("a")
                        from_address = from_element.get("href").split("/")[-1] if from_element else "Unknown"
                        
                        to_element = columns[5].select_one("a")
                        to_address = to_element.get("href").split("/")[-1] if to_element else "Unknown"
                        
                        quantity_element = columns[6] if len(columns) > 6 else None
                        quantity_text = quantity_element.get_text(strip=True) if quantity_element else "0"
                        quantity_match = re.search(r'([\d,\.]+)', quantity_text)
                        quantity = float(quantity_match.group(1).replace(',', '')) if quantity_match else 0
                        
                        transaction = {
                            "tx_hash": tx_hash,
                            "method": method,
                            "timestamp": timestamp,
                            "from": from_address,
                            "to": to_address,
                            "quantity": quantity,
                            "token_address": token_address
                        }
                        transactions.append(transaction)
                except Exception as e:
                    logger.warning(f"Erro ao processar transação de token: {str(e)}")
                    continue
                    
            return transactions
        except Exception as e:
            logger.error(f"Erro ao analisar transações do token: {str(e)}")
            return []
            
    async def get_token_contract_info(self, token_address: str, chain: str = "eth") -> Dict[str, Any]:
        """
        Obtém informações do contrato de um token.
        
        Args:
            token_address: Endereço do contrato do token
            chain: Cadeia de blocos (eth, bsc, polygon, etc.)
            
        Returns:
            Informações do contrato
        """
        # Apenas uma wrapper para o método get_address_info, já que contém as mesmas informações
        return await self.get_address_info(token_address, chain)
        
    async def check_connection(self) -> bool:
        """
        Verifica se a conexão com o explorador de blockchain está funcionando.
        
        Returns:
            True se a conexão estiver funcionando, False caso contrário.
        """
        try:
            # Tenta acessar a página inicial do Etherscan
            explorer_url = self.explorers.get("eth", "https://etherscan.io")
            await self._fetch_page(explorer_url)
            logger.info("Conexão com o explorador de blockchain está funcionando")
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com o explorador de blockchain: {str(e)}")
            return False
            
    def _get_current_timestamp(self) -> str:
        """
        Retorna o timestamp atual formatado como string ISO.
        
        Returns:
            Timestamp ISO formatado
        """
        return datetime.now().isoformat()

# Instância global do cliente
blockchain_explorer = BlockchainExplorerClient() 