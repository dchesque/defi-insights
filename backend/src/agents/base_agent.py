"""
Classe base para todos os agentes de análise
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import json
from datetime import datetime

class BaseAgent(ABC):
    """
    Classe base para todos os agentes de análise.
    """
    
    def __init__(self, cache_enabled: bool = True):
        """
        Inicializa o agente base.
        
        Args:
            cache_enabled: Se o cache deve ser utilizado
        """
        self.cache_enabled = cache_enabled
        self.results = {}
    
    @abstractmethod
    async def analyze(self, token: str, **kwargs) -> Dict[str, Any]:
        """
        Método abstrato para analisar um token.
        
        Args:
            token: Token a ser analisado
            
        Returns:
            Dict[str, Any]: Resultados da análise
        """
        pass
    
    async def get_cached_result(self, token: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Obtém resultados em cache se disponíveis e não expirados.
        
        Args:
            token: Token para buscar no cache
            max_age_hours: Idade máxima dos resultados em cache em horas
            
        Returns:
            Optional[Dict[str, Any]]: Resultados em cache ou None
        """
        if not self.cache_enabled:
            return None
            
        # Implementação simples de cache (em produção, usar Redis ou similar)
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{self.__class__.__name__}_{token}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    
                # Verificar se o cache expirou
                timestamp = datetime.fromisoformat(data.get("timestamp", "2000-01-01T00:00:00"))
                age_hours = (datetime.now() - timestamp).total_seconds() / 3600
                
                if age_hours <= max_age_hours:
                    return data
            except Exception as e:
                print(f"Erro ao carregar cache: {str(e)}")
                
        return None
    
    async def save_to_cache(self, token: str, data: Dict[str, Any]) -> None:
        """
        Salva resultados em cache.
        
        Args:
            token: Token usado como chave de cache
            data: Dados a serem salvos
        """
        if not self.cache_enabled:
            return
            
        # Garantir que há um timestamp nos dados
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()
            
        # Implementação simples de cache
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cache")
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, f"{self.__class__.__name__}_{token}.json")
        
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {str(e)}")
            
    def _format_token(self, token: str) -> str:
        """
        Formata um token para uso consistente.
        
        Args:
            token: Token a ser formatado
            
        Returns:
            str: Token formatado
        """
        return token.strip().upper() 