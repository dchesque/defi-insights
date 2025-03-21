# backend/src/utils/config.py - Atualizado em 21/03/2025 14:20
"""
Gerenciador de configurações da aplicação.
"""
import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configurações da aplicação.
    Carrega variáveis de ambiente e fornece valores padrão.
    """
    # API Server Settings
    API_HOST: str = Field("0.0.0.0", env="API_HOST")
    API_PORT: int = Field(8000, env="API_PORT")
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    
    # Frontend Settings
    FRONTEND_URL: str = Field("http://localhost:3000", env="FRONTEND_URL")
    CORS_ORIGINS: str = Field("http://localhost:3000,http://localhost:8080", env="CORS_ORIGINS")
    
    # Authentication Settings
    SECRET_KEY: str = Field("your-super-secret-key-for-jwt", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Supabase Settings
    SUPABASE_URL: str = Field("", env="SUPABASE_URL")
    SUPABASE_KEY: str = Field("", env="SUPABASE_KEY")
    
    # Anthropic Settings
    ANTHROPIC_API_KEY: str = Field("", env="ANTHROPIC_API_KEY")
    
    # Directories
    LOGS_DIR: str = Field("logs", env="LOGS_DIR")
    CACHE_DIR: str = Field("cache", env="CACHE_DIR")
    
    # Cache Settings
    CACHE_ENABLED: bool = Field(True, env="CACHE_ENABLED")
    CACHE_TTL_SECONDS: int = Field(3600, env="CACHE_TTL_SECONDS")
    
    # Rate Limits
    RATE_LIMIT_TOKENS: int = Field(100, env="RATE_LIMIT_TOKENS")
    RATE_LIMIT_REFILL_SECONDS: int = Field(60, env="RATE_LIMIT_REFILL_SECONDS")
    
    # Web Scraping Settings
    USER_AGENT: str = Field(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        env="USER_AGENT"
    )
    
    # CoinGecko API Settings
    COINGECKO_API_URL: str = Field("https://api.coingecko.com/api/v3", env="COINGECKO_API_URL")
    COINGECKO_REQUEST_DELAY: float = Field(1.5, env="COINGECKO_REQUEST_DELAY")
    
    # Etherscan API Settings
    ETHERSCAN_API_KEY: str = Field("", env="ETHERSCAN_API_KEY")
    ETHERSCAN_API_URL: str = Field("https://api.etherscan.io/api", env="ETHERSCAN_API_URL")
    
    # Compatibilidade com variáveis antigas do .env
    PORT: int | None = Field(None, env="PORT")
    HOST: str | None = Field(None, env="HOST")
    JWT_SECRET: str | None = Field(None, env="JWT_SECRET")
    JWT_ALGORITHM: str | None = Field(None, env="JWT_ALGORITHM")
    RATE_LIMIT_CALLS: int | None = Field(None, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int | None = Field(None, env="RATE_LIMIT_PERIOD")
    CACHE_TTL: int | None = Field(None, env="CACHE_TTL")
    LOG_FORMAT: str | None = Field(None, env="LOG_FORMAT")
    
    @property
    def get_cors_origins(self) -> list:
        """Converte a string de origens CORS em uma lista"""
        if not self.CORS_ORIGINS:
            return [self.FRONTEND_URL]
        return self.CORS_ORIGINS.split(",")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"  # Ignorar campos extras que não estão definidos na classe
    }

@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação.
    Cacheado para evitar recarregar configurações desnecessariamente.
    
    Returns:
        Settings: Configurações da aplicação
    """
    return Settings()