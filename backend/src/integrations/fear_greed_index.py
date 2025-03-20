"""
Cliente para a API do Fear & Greed Index.
"""
import os
import httpx
import json
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime, timedelta

class FearGreedIndexClient:
    """Cliente para obter o índice de medo e ganância do mercado de criptomoedas."""
    
    BASE_URL = "https://api.alternative.me/fng/"
    
    def __init__(self):
        """Inicializa o cliente do Fear & Greed Index."""
        self.cache = {}
        self.cache_ttl = 3600  # Cache de 1 hora para não sobrecarregar a API
    
    async def _make_request(self, endpoint: str = "", params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Faz uma requisição para a API do Fear & Greed Index.
        
        Args:
            endpoint: Caminho do endpoint da API.
            params: Parâmetros da query (opcional).
            
        Returns:
            Resposta da API em formato JSON.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Verificar se temos dados em cache
        cache_key = f"{endpoint}:{json.dumps(params or {})}"
        cache_entry = self.cache.get(cache_key)
        
        if cache_entry and (datetime.now() - cache_entry["timestamp"]).total_seconds() < self.cache_ttl:
            return cache_entry["data"]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    url,
                    params=params
                )
                
                # Verificar se houve erro
                response.raise_for_status()
                
                # Armazenar resultado no cache
                result = response.json()
                self.cache[cache_key] = {
                    "data": result,
                    "timestamp": datetime.now()
                }
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP ao chamar a API do Fear & Greed Index: {e.response.status_code} - {e.response.text}")
            raise
            
        except Exception as e:
            logger.error(f"Erro ao chamar a API do Fear & Greed Index: {str(e)}")
            raise
    
    async def get_current_index(self) -> Dict[str, Any]:
        """
        Obtém o valor atual do índice de medo e ganância.
        
        Returns:
            Dados atuais do índice de medo e ganância.
        """
        try:
            data = await self._make_request(params={"limit": "1"})
            
            if "data" in data and len(data["data"]) > 0:
                return {
                    "value": int(data["data"][0]["value"]),
                    "value_classification": data["data"][0]["value_classification"],
                    "timestamp": data["data"][0]["timestamp"],
                    "time_until_update": data["data"][0]["time_until_update"]
                }
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao obter índice atual de medo e ganância: {str(e)}")
            return {}
    
    async def get_historical_index(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Obtém o histórico do índice de medo e ganância.
        
        Args:
            days: Número de dias para retornar (limitado a 100).
            
        Returns:
            Lista com o histórico do índice de medo e ganância.
        """
        days = min(days, 100)  # Limitar a 100 dias para evitar sobrecarga
        
        try:
            data = await self._make_request(params={"limit": str(days)})
            
            if "data" in data:
                return [{
                    "value": int(item["value"]),
                    "value_classification": item["value_classification"],
                    "timestamp": item["timestamp"],
                    "date": datetime.fromtimestamp(int(item["timestamp"])).strftime("%Y-%m-%d")
                } for item in data["data"]]
            return []
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico do índice de medo e ganância: {str(e)}")
            return []
    
    async def get_average_index(self, days: int = 7) -> Dict[str, Any]:
        """
        Calcula a média do índice de medo e ganância para um período.
        
        Args:
            days: Número de dias para calcular a média.
            
        Returns:
            Valor médio e classificação do índice.
        """
        try:
            historical_data = await self.get_historical_index(days)
            
            if not historical_data:
                return {}
                
            values = [item["value"] for item in historical_data]
            avg_value = sum(values) / len(values)
            
            # Classificar o valor médio
            classification = self._classify_value(avg_value)
            
            return {
                "average_value": round(avg_value, 1),
                "classification": classification,
                "days": days,
                "start_date": historical_data[-1]["date"],
                "end_date": historical_data[0]["date"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular média do índice de medo e ganância: {str(e)}")
            return {}
    
    async def get_index_trend(self, days: int = 30) -> Dict[str, Any]:
        """
        Analisa a tendência do índice de medo e ganância.
        
        Args:
            days: Número de dias para analisar.
            
        Returns:
            Análise de tendência do índice.
        """
        try:
            historical_data = await self.get_historical_index(days)
            
            if len(historical_data) < 7:
                return {"error": "Dados insuficientes para análise de tendência"}
                
            # Dividir em períodos recentes e anteriores
            recent_period = historical_data[:7]  # Últimos 7 dias
            earlier_period = historical_data[7:min(14, len(historical_data))]  # 7 dias anteriores
            
            if not earlier_period:
                return {"error": "Dados insuficientes para comparação"}
                
            recent_avg = sum(item["value"] for item in recent_period) / len(recent_period)
            earlier_avg = sum(item["value"] for item in earlier_period) / len(earlier_period)
            
            # Calcular mudança em percentual
            change = ((recent_avg - earlier_avg) / earlier_avg) * 100
            
            # Determinar tendência
            if change > 10:
                trend = "forte alta"
            elif change > 3:
                trend = "alta"
            elif change < -10:
                trend = "forte queda"
            elif change < -3:
                trend = "queda"
            else:
                trend = "estável"
                
            return {
                "recent_average": round(recent_avg, 1),
                "earlier_average": round(earlier_avg, 1),
                "change_percentage": round(change, 1),
                "trend": trend,
                "recent_classification": self._classify_value(recent_avg),
                "earlier_classification": self._classify_value(earlier_avg)
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar tendência do índice de medo e ganância: {str(e)}")
            return {"error": str(e)}
    
    def _classify_value(self, value: float) -> str:
        """
        Classifica um valor do índice de medo e ganância.
        
        Args:
            value: Valor numérico do índice.
            
        Returns:
            Classificação textual do índice.
        """
        if value <= 20:
            return "Medo Extremo"
        elif value <= 40:
            return "Medo"
        elif value <= 60:
            return "Neutro"
        elif value <= 80:
            return "Ganância"
        else:
            return "Ganância Extrema"

# Instância global do cliente
fear_greed_client = FearGreedIndexClient() 