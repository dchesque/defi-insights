from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """Classe base para todos os agentes de análise"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Agente base para análise de tokens"
    
    @abstractmethod
    async def analyze(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método abstrato para análise de tokens.
        
        Args:
            token_data: Dicionário contendo dados do token para análise
            
        Returns:
            Dict[str, Any]: Resultado da análise
        """
        pass
    
    @abstractmethod
    async def validate_input(self, token_data: Dict[str, Any]) -> bool:
        """
        Valida os dados de entrada do token.
        
        Args:
            token_data: Dados do token para validação
            
        Returns:
            bool: True se os dados são válidos, False caso contrário
        """
        pass
    
    def get_agent_info(self) -> Dict[str, str]:
        """
        Retorna informações sobre o agente.
        
        Returns:
            Dict[str, str]: Informações do agente
        """
        return {
            "name": self.name,
            "description": self.description
        }
