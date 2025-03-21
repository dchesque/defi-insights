"""
Classes e funções para gerenciar o acesso ao banco de dados.
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..integrations.supabase import supabase
from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class Database:
    """
    Classe para gerenciar o acesso ao banco de dados.
    Utiliza Supabase como backend de armazenamento.
    """
    
    def __init__(self):
        """
        Inicializa a conexão com o banco de dados.
        """
        self.supabase = supabase
        logger.info("Conexão com o banco de dados inicializada")
        
    async def save_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva uma análise no banco de dados.
        
        Args:
            analysis_data: Dados da análise a ser salva
            
        Returns:
            Dados da análise salva, incluindo ID
        """
        try:
            # Preparar os dados para salvar
            if "result" in analysis_data and isinstance(analysis_data["result"], dict):
                # Converter dicionários para JSON
                analysis_data["result_json"] = json.dumps(analysis_data["result"])
                del analysis_data["result"]
                
            # Salvar na tabela de análises
            result = await self.supabase.save_analysis(analysis_data)
            
            if result.error:
                logger.error(f"Erro ao salvar análise: {result.error}")
                return {"error": str(result.error)}
                
            logger.info(f"Análise salva com sucesso. ID: {result.data[0].get('id')}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Erro ao salvar análise: {str(e)}")
            return {"error": str(e)}
            
    async def get_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """
        Obtém uma análise pelo ID.
        
        Args:
            analysis_id: ID da análise
            
        Returns:
            Dados da análise
        """
        try:
            result = await self.supabase.get_analysis(analysis_id)
            
            if result.error:
                logger.error(f"Erro ao obter análise: {result.error}")
                return {"error": str(result.error)}
                
            if not result.data:
                logger.warning(f"Análise não encontrada: {analysis_id}")
                return {"error": "Análise não encontrada"}
                
            # Converter JSON de volta para dicionário
            analysis = result.data[0]
            if "result_json" in analysis and analysis["result_json"]:
                try:
                    analysis["result"] = json.loads(analysis["result_json"])
                    del analysis["result_json"]
                except json.JSONDecodeError:
                    logger.error(f"Erro ao decodificar JSON da análise: {analysis_id}")
                    
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao obter análise: {str(e)}")
            return {"error": str(e)}
            
    async def get_user_analyses(self, user_id: str, 
                               analysis_type: Optional[str] = None, 
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém análises de um usuário.
        
        Args:
            user_id: ID do usuário
            analysis_type: Tipo de análise (opcional)
            limit: Número máximo de análises a retornar
            
        Returns:
            Lista de análises do usuário
        """
        try:
            result = await self.supabase.get_user_analyses(user_id, analysis_type, limit)
            
            if result.error:
                logger.error(f"Erro ao obter análises do usuário: {result.error}")
                return [{"error": str(result.error)}]
                
            # Converter JSON de volta para dicionário em cada análise
            analyses = result.data
            for analysis in analyses:
                if "result_json" in analysis and analysis["result_json"]:
                    try:
                        analysis["result"] = json.loads(analysis["result_json"])
                        del analysis["result_json"]
                    except json.JSONDecodeError:
                        logger.error(f"Erro ao decodificar JSON da análise: {analysis.get('id')}")
                        
            return analyses
            
        except Exception as e:
            logger.error(f"Erro ao obter análises do usuário: {str(e)}")
            return [{"error": str(e)}]
            
    async def save_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Salva um portfólio no banco de dados.
        
        Args:
            portfolio_data: Dados do portfólio a ser salvo
            
        Returns:
            Dados do portfólio salvo, incluindo ID
        """
        try:
            # Preparar os dados para salvar
            if "assets" in portfolio_data and isinstance(portfolio_data["assets"], list):
                # Converter lista para JSON
                portfolio_data["assets_json"] = json.dumps(portfolio_data["assets"])
                del portfolio_data["assets"]
                
            # Salvar na tabela de portfólios
            result = await self.supabase.save_portfolio(portfolio_data)
            
            if result.error:
                logger.error(f"Erro ao salvar portfólio: {result.error}")
                return {"error": str(result.error)}
                
            logger.info(f"Portfólio salvo com sucesso. ID: {result.data[0].get('id')}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Erro ao salvar portfólio: {str(e)}")
            return {"error": str(e)}
            
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """
        Obtém o portfólio de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados do portfólio
        """
        try:
            result = await self.supabase.get_user_portfolio(user_id)
            
            if result.error:
                logger.error(f"Erro ao obter portfólio do usuário: {result.error}")
                return {"error": str(result.error)}
                
            if not result.data:
                logger.warning(f"Portfólio não encontrado para o usuário: {user_id}")
                return {"error": "Portfólio não encontrado"}
                
            # Converter JSON de volta para lista
            portfolio = result.data[0]
            if "assets_json" in portfolio and portfolio["assets_json"]:
                try:
                    portfolio["assets"] = json.loads(portfolio["assets_json"])
                    del portfolio["assets_json"]
                except json.JSONDecodeError:
                    logger.error(f"Erro ao decodificar JSON do portfólio: {portfolio.get('id')}")
                    
            return portfolio
            
        except Exception as e:
            logger.error(f"Erro ao obter portfólio do usuário: {str(e)}")
            return {"error": str(e)} 