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

class BlockchainExplorerClient:
    """
    Cliente para obter dados básicos on-chain de exploradores de blockchain.
    Usa web scraping para obter dados sem necessidade de API key.
    """
    
    def __init__(self):
        """Inicializa o cliente de explorador de blockchain."""
        self.base_url = os.getenv("BLOCKCHAIN_EXPLORER_BASE_URL", "https://etherscan.io/address/")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
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
            
        # Na implementação real, faríamos scraping das informações
        # Aqui, vamos retornar dados simulados para demonstração
        return self._get_mock_address_info(address, chain)
        
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
            
        # Na implementação real, faríamos scraping das informações
        # Aqui, vamos retornar dados simulados para demonstração
        return self._get_mock_token_holders(token_address, chain)
        
    async def get_token_transactions(self, token_address: str, limit: int = 10, chain: str = "eth") -> List[Dict[str, Any]]:
        """
        Obtém as transações recentes de um token.
        
        Args:
            token_address: Endereço do contrato do token
            limit: Número máximo de transações a retornar
            chain: Cadeia de blocos (eth, bsc, polygon, etc.)
            
        Returns:
            Lista de transações recentes.
        """
        if not self._is_valid_address(token_address):
            logger.error(f"Endereço de token inválido: {token_address}")
            return [{"error": "Endereço de token inválido"}]
            
        # Na implementação real, faríamos scraping das informações
        # Aqui, vamos retornar dados simulados para demonstração
        return self._get_mock_token_transactions(token_address, limit, chain)
        
    async def get_token_contract_info(self, token_address: str, chain: str = "eth") -> Dict[str, Any]:
        """
        Obtém informações sobre o contrato de um token.
        
        Args:
            token_address: Endereço do contrato do token
            chain: Cadeia de blocos (eth, bsc, polygon, etc.)
            
        Returns:
            Dados do contrato.
        """
        if not self._is_valid_address(token_address):
            logger.error(f"Endereço de token inválido: {token_address}")
            return {"error": "Endereço de token inválido"}
            
        # Na implementação real, faríamos scraping das informações
        # Aqui, vamos retornar dados simulados para demonstração
        return self._get_mock_contract_info(token_address, chain)
        
    def _is_valid_address(self, address: str) -> bool:
        """
        Verifica se um endereço de blockchain é válido.
        
        Args:
            address: Endereço a ser verificado
            
        Returns:
            True se o endereço for válido, False caso contrário.
        """
        # Formato básico de um endereço Ethereum: 0x seguido por 40 caracteres hexadecimais
        pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(pattern, address))
        
    def _get_mock_address_info(self, address: str, chain: str) -> Dict[str, Any]:
        """
        Gera dados simulados de informações de endereço.
        
        Args:
            address: Endereço da carteira ou contrato
            chain: Cadeia de blocos
            
        Returns:
            Dados simulados do endereço.
        """
        # Algumas informações serão determinísticas com base no endereço para consistência
        address_hash = sum(ord(c) for c in address)
        
        # Determinando se é um contrato ou uma carteira com base no último caractere
        is_contract = int(address[-1], 16) % 2 == 0
        
        if is_contract:
            contract_type = ["ERC20 Token", "ERC721 NFT", "DEX", "Lending", "Staking"][address_hash % 5]
            verified = address_hash % 10 >= 7  # 30% chance de não ser verificado
            
            return {
                "address": address,
                "chain": chain,
                "type": "Contract",
                "contract_type": contract_type,
                "verified": verified,
                "balance": round(address_hash % 1000 * 0.01, 2),
                "token_name": f"Token_{address[2:8]}",
                "token_symbol": address[2:5].upper(),
                "transactions": address_hash % 10000 + 100,
                "created_at": "2022-10-15T14:30:00Z",
                "creator": f"0x{address_hash % 16**40:040x}"[:42],
                "last_activity": "2023-06-01T09:15:00Z"
            }
        else:
            # Carteira comum
            return {
                "address": address,
                "chain": chain,
                "type": "EOA",  # Externally Owned Account
                "balance": round(address_hash % 1000 * 0.01, 2),
                "transactions": address_hash % 1000 + 10,
                "first_activity": "2021-05-10T08:45:00Z",
                "last_activity": "2023-06-05T16:20:00Z",
                "token_count": address_hash % 50 + 2,
                "nft_count": address_hash % 20
            }
    
    def _get_mock_token_holders(self, token_address: str, chain: str) -> List[Dict[str, Any]]:
        """
        Gera dados simulados de detentores de tokens.
        
        Args:
            token_address: Endereço do contrato do token
            chain: Cadeia de blocos
            
        Returns:
            Lista simulada de detentores do token.
        """
        address_hash = sum(ord(c) for c in token_address)
        total_supply = address_hash % 1000000000 + 10000000
        
        holders = []
        
        # Gerar detentores principais (whales)
        for i in range(10):
            percent = 50 / (i + 1) ** 1.5  # Distribuição decrescente
            if i == 0 and percent > 30:
                percent = 30  # Limitar o maior detentor a 30%
                
            holder_address = f"0x{(address_hash + i) % 16**40:040x}"[:42]
            
            # Marcar alguns endereços como exchanges ou contratos
            holder_type = "Unknown"
            if i == 0:
                holder_type = "Contract (DEX LP)"
            elif i == 1:
                holder_type = "Exchange"
            elif i % 3 == 0:
                holder_type = "Whale"
                
            holders.append({
                "rank": i + 1,
                "address": holder_address,
                "quantity": int(total_supply * percent / 100),
                "percentage": round(percent, 2),
                "type": holder_type,
                "first_acquisition": f"2022-{(i + 1):02d}-15T10:30:00Z"
            })
            
        return holders
        
    def _get_mock_token_transactions(self, token_address: str, limit: int, chain: str) -> List[Dict[str, Any]]:
        """
        Gera dados simulados de transações de tokens.
        
        Args:
            token_address: Endereço do contrato do token
            limit: Número máximo de transações a retornar
            chain: Cadeia de blocos
            
        Returns:
            Lista simulada de transações do token.
        """
        address_hash = sum(ord(c) for c in token_address)
        transactions = []
        
        for i in range(limit):
            # Determinar se é compra ou venda
            is_buy = (address_hash + i) % 3 != 0  # 2/3 de chance de ser compra
            
            # Determinar o valor
            value = address_hash % 10000 / (i + 1) + 100
            
            # Gerar endereços
            from_address = f"0x{(address_hash + i*3) % 16**40:040x}"[:42]
            to_address = f"0x{(address_hash + i*7) % 16**40:040x}"[:42]
            
            # Tornar algumas transações de exchange
            is_exchange = (i % 5 == 0)
            if is_exchange:
                if is_buy:
                    from_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
                    from_label = "USDT Treasury"
                else:
                    to_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Uniswap
                    to_label = "Uniswap V2"
            else:
                from_label = ""
                to_label = ""
                
            # Calcular a hora (transações mais recentes primeiro)
            hours_ago = i * 6  # A cada 6 horas
            
            transactions.append({
                "hash": f"0x{(address_hash + i) % 16**64:064x}",
                "block": 17500000 - i,
                "timestamp": f"2023-06-{15-i//4:02d}T{23-(i%24):02d}:00:00Z",
                "from": from_address,
                "from_label": from_label,
                "to": to_address,
                "to_label": to_label,
                "value": round(value, 4),
                "transaction_type": "Buy" if is_buy else "Sell",
                "gas_price": 20 + (i % 10),
                "status": "Success"
            })
            
        return transactions
        
    def _get_mock_contract_info(self, token_address: str, chain: str) -> Dict[str, Any]:
        """
        Gera dados simulados de informações de contrato.
        
        Args:
            token_address: Endereço do contrato do token
            chain: Cadeia de blocos
            
        Returns:
            Dados simulados do contrato.
        """
        address_hash = sum(ord(c) for c in token_address)
        
        # Determinar o tipo de token
        token_types = ["ERC20", "ERC721", "ERC1155"]
        token_type = token_types[address_hash % len(token_types)]
        
        # Determinar se o contrato é verificado
        is_verified = address_hash % 10 >= 3  # 70% chance de ser verificado
        
        # Calcular o total supply
        total_supply = address_hash % 1000000000 + 10000000
        
        # Gerar dados do contrato
        contract_info = {
            "address": token_address,
            "chain": chain,
            "token_type": token_type,
            "name": f"Token_{token_address[2:8]}",
            "symbol": token_address[2:5].upper(),
            "decimals": 18,
            "total_supply": total_supply,
            "verified": is_verified,
            "owner": f"0x{(address_hash * 2) % 16**40:040x}"[:42],
            "implementation": None,  # Para proxies
            "creation_date": "2022-10-15T14:30:00Z",
            "creation_tx": f"0x{(address_hash * 3) % 16**64:064x}"
        }
        
        # Adicionar informações específicas para contratos verificados
        if is_verified:
            contract_info.update({
                "compiler": f"Solidity 0.8.{address_hash % 10}",
                "license": "MIT",
                "has_proxy": address_hash % 5 == 0,
                "audited": address_hash % 3 == 0
            })
            
            if contract_info["has_proxy"]:
                contract_info["implementation"] = f"0x{(address_hash * 5) % 16**40:040x}"[:42]
                
        return contract_info

# Instância global do cliente
blockchain_explorer_client = BlockchainExplorerClient() 