import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
import asyncio
from typing import Dict, Any, Optional, List
import json

# Configurar logging
logger = logging.getLogger(__name__)

# Garantir que as variáveis de ambiente estejam carregadas
load_dotenv()

class SupabaseClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance.client = cls._get_client()
        return cls._instance
    
    @staticmethod
    def _get_client() -> Client:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não definidas")
            
        return create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
    
    async def get_user(self, user_id: str):
        """Obtém informações do usuário pelo ID"""
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            # Executar de forma assíncrona usando um loop de eventos
            result = await asyncio.to_thread(
                lambda: self.client.table("users").select("*").eq("id", user_id).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao obter usuário: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def create_user(self, user_data: Dict[str, Any]):
        """Cria um novo usuário no banco de dados"""
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            result = await asyncio.to_thread(
                lambda: self.client.table("users").insert(user_data).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]):
        """Atualiza informações do usuário"""
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            result = await asyncio.to_thread(
                lambda: self.client.table("users").update(user_data).eq("id", user_id).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def save_analysis(self, analysis_data: Dict[str, Any]):
        """
        Salva uma análise de token no banco de dados.
        
        Args:
            analysis_data: Dados da análise a serem salvos
            
        Returns:
            Resposta da operação
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
            
            # Converter objetos complexos para JSON
            for key, value in analysis_data.items():
                if isinstance(value, (dict, list)):
                    analysis_data[key] = json.dumps(value)
                
            result = await asyncio.to_thread(
                lambda: self.client.table("token_analyses").insert(analysis_data).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao salvar análise: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def get_analysis(self, analysis_id: str):
        """
        Obtém uma análise específica pelo ID.
        
        Args:
            analysis_id: ID da análise
            
        Returns:
            Dados da análise
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            result = await asyncio.to_thread(
                lambda: self.client.table("token_analyses").select("*").eq("id", analysis_id).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao obter análise: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def get_user_analyses(self, user_id: str, analysis_type: Optional[str] = None, limit: int = 10):
        """
        Obtém análises de um usuário específico.
        
        Args:
            user_id: ID do usuário
            analysis_type: Tipo de análise (opcional)
            limit: Número máximo de análises a retornar
            
        Returns:
            Lista de análises do usuário
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            query = self.client.table("token_analyses").select("*").eq("user_id", user_id)
            
            if analysis_type:
                query = query.eq("analysis_type", analysis_type)
                
            query = query.order("created_at", desc=True).limit(limit)
            
            result = await asyncio.to_thread(lambda: query.execute())
            return result
        except Exception as e:
            logger.error(f"Erro ao obter análises do usuário: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def save_portfolio(self, portfolio_data: Dict[str, Any]):
        """
        Salva um portfólio no banco de dados.
        
        Args:
            portfolio_data: Dados do portfólio
            
        Returns:
            Resposta da operação
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            # Converter objetos complexos para JSON
            for key, value in portfolio_data.items():
                if isinstance(value, (dict, list)):
                    portfolio_data[key] = json.dumps(value)
                    
            result = await asyncio.to_thread(
                lambda: self.client.table("portfolios").insert(portfolio_data).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao salvar portfólio: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def update_portfolio(self, portfolio_id: str, portfolio_data: Dict[str, Any]):
        """
        Atualiza um portfólio existente.
        
        Args:
            portfolio_id: ID do portfólio
            portfolio_data: Novos dados do portfólio
            
        Returns:
            Resposta da operação
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            # Converter objetos complexos para JSON
            for key, value in portfolio_data.items():
                if isinstance(value, (dict, list)):
                    portfolio_data[key] = json.dumps(value)
                    
            result = await asyncio.to_thread(
                lambda: self.client.table("portfolios").update(portfolio_data).eq("id", portfolio_id).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao atualizar portfólio: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def get_user_portfolio(self, user_id: str):
        """
        Obtém o portfólio de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados do portfólio
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            result = await asyncio.to_thread(
                lambda: self.client.table("portfolios").select("*").eq("user_id", user_id).limit(1).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao obter portfólio do usuário: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def save_user_preferences(self, preferences_data: Dict[str, Any]):
        """
        Salva preferências do usuário.
        
        Args:
            preferences_data: Dados de preferências
            
        Returns:
            Resposta da operação
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            # Converter objetos complexos para JSON
            for key, value in preferences_data.items():
                if isinstance(value, (dict, list)):
                    preferences_data[key] = json.dumps(value)
                    
            result = await asyncio.to_thread(
                lambda: self.client.table("user_preferences").insert(preferences_data).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao salvar preferências: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def update_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]):
        """
        Atualiza preferências do usuário.
        
        Args:
            user_id: ID do usuário
            preferences_data: Novos dados de preferências
            
        Returns:
            Resposta da operação
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            # Converter objetos complexos para JSON
            for key, value in preferences_data.items():
                if isinstance(value, (dict, list)):
                    preferences_data[key] = json.dumps(value)
                    
            result = await asyncio.to_thread(
                lambda: self.client.table("user_preferences").update(preferences_data).eq("user_id", user_id).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao atualizar preferências: {str(e)}")
            return {"error": str(e), "data": None}
    
    async def get_user_preferences(self, user_id: str):
        """
        Obtém preferências do usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Dados de preferências
        """
        try:
            if not self.client:
                logger.error("Cliente Supabase não inicializado")
                return {"error": "Cliente Supabase não inicializado", "data": None}
                
            result = await asyncio.to_thread(
                lambda: self.client.table("user_preferences").select("*").eq("user_id", user_id).limit(1).execute()
            )
            return result
        except Exception as e:
            logger.error(f"Erro ao obter preferências do usuário: {str(e)}")
            return {"error": str(e), "data": None}

# Singleton para acessar o cliente Supabase
supabase = SupabaseClient()
