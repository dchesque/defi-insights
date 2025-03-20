from typing import Dict, List, Any, Type
from .base_agent import BaseAgent

class AgentManager:
    """Gerenciador de agentes de análise"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Registra um novo agente no gerenciador.
        
        Args:
            agent: Instância do agente a ser registrado
        """
        self.agents[agent.name] = agent
    
    def get_agent(self, agent_name: str) -> BaseAgent:
        """
        Obtém um agente pelo nome.
        
        Args:
            agent_name: Nome do agente
            
        Returns:
            BaseAgent: Instância do agente solicitado
            
        Raises:
            KeyError: Se o agente não for encontrado
        """
        if agent_name not in self.agents:
            raise KeyError(f"Agente {agent_name} não encontrado")
        return self.agents[agent_name]
    
    def list_agents(self) -> List[Dict[str, str]]:
        """
        Lista todos os agentes registrados.
        
        Returns:
            List[Dict[str, str]]: Lista de informações dos agentes
        """
        return [agent.get_agent_info() for agent in self.agents.values()]
    
    async def run_analysis(self, token_data: Dict[str, Any], agent_names: List[str] = None) -> Dict[str, Any]:
        """
        Executa análise usando os agentes especificados.
        
        Args:
            token_data: Dados do token para análise
            agent_names: Lista de nomes dos agentes a serem usados. Se None, usa todos.
            
        Returns:
            Dict[str, Any]: Resultados combinados das análises
        """
        results = {}
        
        # Se nenhum agente específico for solicitado, usa todos
        agents_to_run = [self.get_agent(name) for name in (agent_names or self.agents.keys())]
        
        for agent in agents_to_run:
            try:
                # Valida dados de entrada
                if not await agent.validate_input(token_data):
                    results[agent.name] = {"error": "Dados de entrada inválidos"}
                    continue
                
                # Executa análise
                analysis_result = await agent.analyze(token_data)
                results[agent.name] = analysis_result
                
            except Exception as e:
                results[agent.name] = {"error": str(e)}
        
        return results
    
    def clear_agents(self) -> None:
        """Remove todos os agentes registrados"""
        self.agents.clear()

# Instância global do gerenciador de agentes
agent_manager = AgentManager()
