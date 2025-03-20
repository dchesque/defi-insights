import os
from supabase import create_client, Client
from dotenv import load_dotenv

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
            raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY devem estar definidas")
        
        return create_client(supabase_url, supabase_key)
    
    def get_user(self, user_id: str):
        """Obtém informações do usuário pelo ID"""
        return self.client.table("users").select("*").eq("id", user_id).execute()
    
    def create_user(self, user_data: dict):
        """Cria um novo usuário no banco de dados"""
        return self.client.table("users").insert(user_data).execute()
    
    def update_user(self, user_id: str, user_data: dict):
        """Atualiza informações do usuário"""
        return self.client.table("users").update(user_data).eq("id", user_id).execute()
    
    def save_analysis(self, analysis_data: dict):
        """Salva uma análise de token no banco de dados"""
        return self.client.table("token_analyses").insert(analysis_data).execute()
    
    def get_user_analyses(self, user_id: str):
        """Obtém todas as análises de um usuário específico"""
        return self.client.table("token_analyses").select("*").eq("user_id", user_id).execute()
    
    def save_portfolio(self, portfolio_data: dict):
        """Salva um portfólio no banco de dados"""
        return self.client.table("portfolios").insert(portfolio_data).execute()
    
    def update_portfolio(self, portfolio_id: str, portfolio_data: dict):
        """Atualiza um portfólio existente"""
        return self.client.table("portfolios").update(portfolio_data).eq("id", portfolio_id).execute()
    
    def get_user_portfolios(self, user_id: str):
        """Obtém todos os portfólios de um usuário"""
        return self.client.table("portfolios").select("*").eq("user_id", user_id).execute()
    
    def save_user_preferences(self, preferences_data: dict):
        """Salva preferências do usuário"""
        return self.client.table("user_preferences").insert(preferences_data).execute()
    
    def update_user_preferences(self, user_id: str, preferences_data: dict):
        """Atualiza preferências do usuário"""
        return self.client.table("user_preferences").update(preferences_data).eq("user_id", user_id).execute()
    
    def get_user_preferences(self, user_id: str):
        """Obtém preferências do usuário"""
        return self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()

# Singleton para acessar o cliente Supabase
supabase = SupabaseClient()
