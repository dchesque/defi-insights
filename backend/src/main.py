from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Adicionar o diretório raiz ao sys.path para resolver problemas de importação
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Carregar variáveis de ambiente com encoding específico
try:
    dotenv_path = os.path.join(backend_dir, ".env")
    load_dotenv(dotenv_path, encoding="utf-8")
    logger.info("Variáveis de ambiente carregadas com sucesso")
except Exception as e:
    logger.error(f"Erro ao carregar variáveis de ambiente: {str(e)}")

# Criar aplicação FastAPI
app = FastAPI(
    title="DeFi Insight API",
    description="API de análise avançada de tokens cripto utilizando inteligência artificial",
    version="0.1.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, limitar para os domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importando e registrando as rotas
from src.api.routes import auth, token_analysis, portfolio, sentiment_analysis, onchain_analysis
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(token_analysis.router, prefix="/api/analysis", tags=["Análise Técnica"])
app.include_router(sentiment_analysis.router, prefix="/api/sentiment", tags=["Análise de Sentimento"])
app.include_router(onchain_analysis.router, prefix="/api/onchain", tags=["Análise On-Chain"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfólio"])

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API DeFi Insight. Acesse /docs para a documentação."}

@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "version": app.version,
        "supabase_connection": True if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY") else False
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # Desativar completamente o multiprocessamento e o reload para evitar problemas no Windows
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False,  # Desativar o reload para evitar multiprocessamento
        workers=1,     # Usar apenas um worker
        use_colors=True
    ) 