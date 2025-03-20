#!/usr/bin/env python
"""
Script para iniciar o servidor DeFi Insight.
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

def check_env():
    """Verifica se as variáveis de ambiente essenciais estão configuradas."""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "JWT_SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ As seguintes variáveis de ambiente estão faltando:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPor favor, configure o arquivo .env com essas variáveis.")
        return False
    
    return True

def start_server():
    """Inicia o servidor FastAPI com Uvicorn."""
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Verifica configuração
    if not check_env():
        sys.exit(1)
    
    # Obtém configurações do .env
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    print(f"\n🚀 Iniciando servidor DeFi Insight...")
    print(f"   Endereço: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    print(f"   Documentação: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    print(f"   Modo debug: {'✅' if debug else '❌'}")
    
    # Iniciar Uvicorn
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=debug
    )

if __name__ == "__main__":
    start_server() 