"""
Cliente para a API do DefiLlama - uma fonte de dados para métricas DeFi.
"""
import httpx
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class DefiLlamaClient:
    """Cliente para interagir com a API do DefiLlama."""
    
    BASE_URL = "https://api.llama.fi"
    
    def __init__(self):
        """Inicializa o cliente do DefiLlama."""
        self.cache = {}
        self.cache_ttl = 300  # Cache de 5 minutos para dados principais
        self.long_cache_ttl = 3600  # Cache de 1 hora para dados históricos
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(httpx.HTTPStatusError)
    )
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, long_cache: bool = False) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do DefiLlama.
        
        Args:
            endpoint: Caminho do endpoint da API.
            params: Parâmetros da query (opcional).
            long_cache: Se True, usa o cache mais longo para dados históricos.
            
        Returns:
            Resposta da API em formato JSON.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Preparar parâmetros
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
            logger.error(f"Erro HTTP ao chamar a API do DefiLlama: {e.response.status_code} - {e.response.text}")
            raise
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do DefiLlama: {str(e)}")
            raise
    
    async def get_protocols(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de todos os protocolos DeFi.
        
        Returns:
            Lista com informações sobre os protocolos.
        """
        try:
            data = await self._make_request("protocols")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter lista de protocolos: {str(e)}")
            return []
    
    async def get_protocol(self, protocol_slug: str) -> Dict[str, Any]:
        """
        Obtém detalhes sobre um protocolo específico.
        
        Args:
            protocol_slug: Slug do protocolo (ex: "aave").
            
        Returns:
            Dicionário com informações do protocolo.
        """
        try:
            data = await self._make_request(f"protocol/{protocol_slug}")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do protocolo {protocol_slug}: {str(e)}")
            return {}
    
    async def get_global_tvl(self) -> Dict[str, Any]:
        """
        Obtém o TVL global de todos os protocolos DeFi.
        
        Returns:
            Dicionário com dados históricos de TVL.
        """
        try:
            data = await self._make_request("charts", long_cache=True)
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter TVL global: {str(e)}")
            return {}
    
    async def get_tvl_by_chain(self) -> Dict[str, Any]:
        """
        Obtém o TVL separado por blockchain.
        
        Returns:
            Dicionário com TVL por blockchain.
        """
        try:
            data = await self._make_request("chains", long_cache=True)
            return data
            
        except Exception as e:
            logger.error(f"Erro ao obter TVL por blockchain: {str(e)}")
            return {}
    
    async def get_yields(self, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém dados sobre as oportunidades de yield farming no ecossistema DeFi.
        
        Args:
            offset: Índice inicial dos resultados.
            limit: Número máximo de resultados.
            
        Returns:
            Lista com oportunidades de yield farming.
        """
        try:
            params = {
                "offset": offset,
                "limit": limit
            }
            
            data = await self._make_request("pools", params=params)
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de yield farming: {str(e)}")
            return []
    
    async def get_yield_by_project(self, project_name: str) -> List[Dict[str, Any]]:
        """
        Obtém dados de yield farming para um projeto específico.
        
        Args:
            project_name: Nome do projeto (ex: "aave").
            
        Returns:
            Lista com oportunidades de yield farming do projeto.
        """
        try:
            params = {
                "project": project_name
            }
            
            data = await self._make_request("pools", params=params)
            return data.get("data", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de yield farming para {project_name}: {str(e)}")
            return []
    
    async def get_protocol_tvl_by_chain(self, protocol_slug: str) -> Dict[str, Any]:
        """
        Obtém o TVL de um protocolo separado por blockchain.
        
        Args:
            protocol_slug: Slug do protocolo (ex: "aave").
            
        Returns:
            Dicionário com TVL do protocolo por blockchain.
        """
        try:
            protocol_data = await self.get_protocol(protocol_slug)
            
            if not protocol_data or "chainTvls" not in protocol_data:
                return {}
            
            return protocol_data.get("chainTvls", {})
            
        except Exception as e:
            logger.error(f"Erro ao obter TVL por blockchain para {protocol_slug}: {str(e)}")
            return {}
    
    async def get_top_protocols(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém a lista dos principais protocolos DeFi por TVL.
        
        Args:
            limit: Número máximo de protocolos a retornar.
            
        Returns:
            Lista com os principais protocolos.
        """
        try:
            all_protocols = await self.get_protocols()
            
            # Ordenar por TVL e limitar
            sorted_protocols = sorted(all_protocols, key=lambda x: x.get("tvl", 0), reverse=True)
            top_protocols = sorted_protocols[:limit]
            
            return top_protocols
            
        except Exception as e:
            logger.error(f"Erro ao obter top protocolos: {str(e)}")
            return []
    
    async def get_protocol_historical_tvl(self, protocol_slug: str) -> List[Dict[str, Any]]:
        """
        Obtém o histórico de TVL para um protocolo específico.
        
        Args:
            protocol_slug: Slug do protocolo (ex: "aave").
            
        Returns:
            Lista com dados históricos de TVL do protocolo.
        """
        try:
            protocol_data = await self.get_protocol(protocol_slug)
            
            if not protocol_data or "tvl" not in protocol_data:
                return []
            
            return protocol_data.get("tvl", [])
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico de TVL para {protocol_slug}: {str(e)}")
            return []
    
    async def get_protocol_by_name(self, name: str) -> Dict[str, Any]:
        """
        Busca um protocolo pelo nome (não diferencia maiúsculas/minúsculas).
        
        Args:
            name: Nome do protocolo a ser buscado.
            
        Returns:
            Dicionário com informações do protocolo.
        """
        try:
            all_protocols = await self.get_protocols()
            
            # Buscar por correspondência de nome (case insensitive)
            name_lower = name.lower()
            for protocol in all_protocols:
                if protocol.get("name", "").lower() == name_lower:
                    return await self.get_protocol(protocol.get("slug", ""))
            
            # Se não encontrou pelo nome exato, tenta correspondência parcial
            for protocol in all_protocols:
                if name_lower in protocol.get("name", "").lower():
                    return await self.get_protocol(protocol.get("slug", ""))
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao buscar protocolo por nome '{name}': {str(e)}")
            return {}
    
    async def get_defi_market_overview(self) -> Dict[str, Any]:
        """
        Obtém uma visão geral do mercado DeFi, incluindo TVL global, TVL por cadeia e top protocolos.
        
        Returns:
            Dicionário com visão geral do mercado DeFi.
        """
        try:
            # Buscar dados em paralelo para otimizar tempo
            global_tvl_data = await self.get_global_tvl()
            tvl_by_chain_data = await self.get_tvl_by_chain()
            top_protocols_data = await self.get_top_protocols(limit=10)
            
            # Calcular métricas adicionais
            current_tvl = global_tvl_data[-1]["totalLiquidityUSD"] if global_tvl_data else 0
            
            # Calcular variação diária
            if len(global_tvl_data) > 1:
                prev_tvl = global_tvl_data[-2]["totalLiquidityUSD"]
                daily_change = (current_tvl - prev_tvl) / prev_tvl * 100 if prev_tvl else 0
            else:
                daily_change = 0
            
            # Formatar top protocolos para incluir apenas dados importantes
            formatted_top_protocols = []
            for protocol in top_protocols_data:
                formatted_top_protocols.append({
                    "name": protocol.get("name", ""),
                    "slug": protocol.get("slug", ""),
                    "tvl": protocol.get("tvl", 0),
                    "change_1d": protocol.get("change_1d", 0),
                    "change_7d": protocol.get("change_7d", 0),
                    "chain": protocol.get("chain", ""),
                    "category": protocol.get("category", ""),
                    "symbol": protocol.get("symbol", ""),
                    "logo": protocol.get("logo", "")
                })
            
            # Formatar TVL por cadeia
            formatted_chains = []
            for chain in tvl_by_chain_data:
                formatted_chains.append({
                    "name": chain.get("name", ""),
                    "tvl": chain.get("tvl", 0),
                    "tokenSymbol": chain.get("tokenSymbol", ""),
                    "change_1d": chain.get("change_1d", 0),
                    "change_7d": chain.get("change_7d", 0)
                })
            
            result = {
                "current_tvl": current_tvl,
                "daily_change_percentage": daily_change,
                "protocols_count": len(await self.get_protocols()),
                "top_chains": sorted(formatted_chains, key=lambda x: x["tvl"], reverse=True)[:5],
                "top_protocols": formatted_top_protocols
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter visão geral do mercado DeFi: {str(e)}")
            return {}

# Instância global do cliente
defillama_client = DefiLlamaClient() 