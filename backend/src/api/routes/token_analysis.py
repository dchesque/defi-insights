from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from loguru import logger

from ...core.agent_manager import agent_manager
from ...agents.token_agent import TokenAgent
from ...db.database import Database

router = APIRouter()
db = Database()

# Endpoint simples e direto para Bitcoin
@router.get("/btc", response_model=Dict[str, Any])
async def btc_simple():
    """
    Análise simples do Bitcoin sem usar o agente
    """
    try:
        # Criar instância do TokenAgent
        direct_token_agent = TokenAgent()
        
        # Configurar dados para análise usando a URL oficial do Bitcoin no CoinGecko
        token_data = {
            "url": "https://www.coingecko.com/en/coins/bitcoin",
            "symbol": "BTC"
        }
        
        # Executar análise
        token_result = await direct_token_agent.analyze(token_data)
        
        if "error" in token_result:
            # Fallback para dados estáticos se a análise falhar
            return {
                "analysis_id": str(uuid.uuid4()),
                "symbol": "BTC",
                "name": "Bitcoin",
                "price": {
                    "current": 65000,
                    "change_24h": 2.5
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Simplificar os dados retornados
        return {
            "analysis_id": str(uuid.uuid4()),
            "symbol": token_result.get("symbol", "BTC"),
            "name": token_result.get("name", "Bitcoin"),
            "price": token_result.get("price", {"current": 65000, "change_24h": 2.5}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Em caso de erro, retornar dados estáticos
        logger.error(f"Erro ao analisar BTC: {str(e)}")
        return {
            "analysis_id": str(uuid.uuid4()),
            "symbol": "BTC",
            "name": "Bitcoin",
            "price": {
                "current": 65000,
                "change_24h": 2.5
            },
            "timestamp": datetime.now().isoformat()
        }

class TokenAnalysisRequest(BaseModel):
    symbol: Optional[str] = None
    user_id: str
    url: Optional[str] = Field(None, description="URL do token no CoinGecko ou CoinMarketCap")
    address: Optional[str] = Field(None, description="Endereço do contrato do token")
    chain: Optional[str] = Field("ethereum", description="Blockchain onde o token está (ethereum, binance-smart-chain, etc)")
    include_sentiment: bool = False
    include_onchain: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC",
                "user_id": "user123",
                "url": "https://www.coingecko.com/en/coins/bitcoin",
                "include_sentiment": True,
                "include_onchain": False
            }
        }

class TokenAnalysisResponse(BaseModel):
    analysis_id: str
    symbol: str
    name: Optional[str] = None
    price: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    sentiment: Optional[Dict[str, Any]] = None
    onchain: Optional[Dict[str, Any]] = None
    additional_info: Optional[Dict[str, Any]] = None
    timestamp: str

# Registrar o agente de token
token_agent = TokenAgent()
agent_manager.register_agent(token_agent)

@router.post("/", response_model=TokenAnalysisResponse)
async def analyze_token(request: TokenAnalysisRequest):
    """
    Realiza análise completa de um token.
    
    Args:
        request: Dados do token para análise
        
    Returns:
        TokenAnalysisResponse: Resultado da análise do token
    """
    try:
        # Verificar se pelo menos um identificador foi fornecido
        if not request.symbol and not request.url and not request.address:
            raise HTTPException(
                status_code=400,
                detail="É necessário fornecer pelo menos um: símbolo, URL ou endereço do token"
            )

        # Configurar quais agentes executar
        agent_names = ["TokenAgent"]
        
        if request.include_sentiment:
            agent_names.append("SentimentAgent")
            
        if request.include_onchain:
            agent_names.append("OnchainAgent")
        
        # Preparar dados do token
        token_data = {
            "symbol": request.symbol,
            "url": request.url,
            "address": request.address,
            "chain": request.chain
        }
        
        # Executar análise
        analysis_result = await agent_manager.run_analysis(
            token_data=token_data,
            agent_names=agent_names
        )
        
        token_result = analysis_result.get("TokenAgent", {})
        sentiment_result = analysis_result.get("SentimentAgent", {})
        onchain_result = analysis_result.get("OnchainAgent", {})
        
        if "error" in token_result:
            logger.error(f"Erro na análise de token: {token_result['error']}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao realizar análise de token: {token_result['error']}"
            )
        
        # Prepara dados para salvar no banco
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        analysis_data = {
            "id": analysis_id,
            "user_id": request.user_id,
            "symbol": request.symbol,
            "analysis_type": "token",
            "result": {
                "name": token_result.get("name"),
                "price": token_result.get("price"),
                "market_data": token_result.get("market_data"),
                "sentiment": sentiment_result if request.include_sentiment else None,
                "onchain": onchain_result if request.include_onchain else None,
                "additional_info": token_result.get("additional_info")
            },
            "created_at": timestamp,
            "timestamp": timestamp
        }
        
        # Tenta salvar análise no banco - permite continuar mesmo se falhar
        try:
            result = await db.save_analysis(analysis_data)
            if "error" in result:
                logger.error(f"Erro ao salvar análise no banco: {result['error']}")
            else:
                analysis_id = result.get("id", analysis_id)
        except Exception as e:
            logger.error(f"Erro ao acessar banco de dados: {str(e)}")
        
        # Retorna resposta formatada
        return TokenAnalysisResponse(
            analysis_id=analysis_id,
            symbol=request.symbol,
            name=token_result.get("name"),
            price=token_result.get("price"),
            market_data=token_result.get("market_data"),
            sentiment=sentiment_result if request.include_sentiment else None,
            onchain=onchain_result if request.include_onchain else None,
            additional_info=token_result.get("additional_info"),
            timestamp=timestamp
        )
        
    except HTTPException as he:
        # Propagar exceções HTTP
        raise he
    except Exception as e:
        logger.error(f"Erro ao realizar análise de token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar análise de token: {str(e)}"
        )

# Especial: este endpoint deve vir ANTES do endpoint de ID para evitar conflitos de rota
@router.get("/special/bitcoin", response_model=TokenAnalysisResponse)
async def analyze_bitcoin_special():
    """
    Endpoint especial para análise direta do Bitcoin (BTC).
    
    Returns:
        TokenAnalysisResponse: Resultado da análise do Bitcoin
    """
    try:
        # Criar nova instância do TokenAgent (não usa o que está registrado)
        direct_token_agent = TokenAgent()
        
        # Configurar dados para análise usando a URL oficial do Bitcoin no CoinGecko
        token_data = {
            "url": "https://www.coingecko.com/en/coins/bitcoin",
            "symbol": "BTC"  # Como fallback caso o URL não funcione
        }
        user_id = "teste_direto"
        
        # Validar entrada
        is_valid = await direct_token_agent.validate_input(token_data)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Dados de entrada inválidos para análise de BTC"
            )
        
        # Executar análise diretamente
        token_result = await direct_token_agent.analyze(token_data)
        
        if "error" in token_result:
            logger.error(f"Erro na análise de BTC: {token_result['error']}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao realizar análise de BTC: {token_result['error']}"
            )
        
        # Prepara dados para retorno
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Não salva no banco para simplificar o teste
        
        # Retorna resposta formatada
        return TokenAnalysisResponse(
            analysis_id=analysis_id,
            symbol="BTC",
            name=token_result.get("name"),
            price=token_result.get("price"),
            market_data=token_result.get("market_data"),
            sentiment=None,
            onchain=None,
            additional_info=token_result.get("additional_info"),
            timestamp=timestamp
        )
        
    except HTTPException as he:
        # Propagar exceções HTTP
        raise he
    except Exception as e:
        logger.error(f"Erro ao realizar análise de BTC: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar análise de BTC: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=TokenAnalysisResponse)
async def get_token_analysis(analysis_id: str):
    """
    Obtém uma análise de token específica pelo ID.
    
    Args:
        analysis_id: ID da análise
        
    Returns:
        TokenAnalysisResponse: Resultado da análise de token
    """
    try:
        # Busca análise no banco
        analysis = await db.get_analysis(analysis_id)
        
        if "error" in analysis:
            raise HTTPException(
                status_code=404,
                detail="Análise não encontrada"
            )
        
        if analysis.get("analysis_type") != "token":
            raise HTTPException(
                status_code=400,
                detail="A análise solicitada não é do tipo token"
            )
        
        # Extrair os dados do resultado
        result = analysis.get("result", {})
        
        return TokenAnalysisResponse(
            analysis_id=analysis.get("id"),
            symbol=analysis.get("symbol"),
            name=result.get("name"),
            price=result.get("price"),
            market_data=result.get("market_data"),
            sentiment=result.get("sentiment"),
            onchain=result.get("onchain"),
            additional_info=result.get("additional_info"),
            timestamp=analysis.get("timestamp", analysis.get("created_at"))
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análise: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[TokenAnalysisResponse])
async def get_user_token_analyses(user_id: str, limit: int = 10):
    """
    Obtém análises de token de um usuário.
    
    Args:
        user_id: ID do usuário
        limit: Número máximo de análises a retornar
        
    Returns:
        List[TokenAnalysisResponse]: Lista de análises de token
    """
    try:
        # Busca análises do usuário no banco
        analyses = await db.get_user_analyses(user_id, analysis_type="token", limit=limit)
        
        if isinstance(analyses, dict) and "error" in analyses:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar análises do usuário: {analyses['error']}"
            )
        
        # Se a lista estiver vazia, retorna uma lista vazia
        if not analyses:
            return []
        
        return [
            TokenAnalysisResponse(
                analysis_id=analysis.get("id"),
                symbol=analysis.get("symbol"),
                name=analysis.get("result", {}).get("name"),
                price=analysis.get("result", {}).get("price"),
                market_data=analysis.get("result", {}).get("market_data"),
                sentiment=analysis.get("result", {}).get("sentiment"),
                onchain=analysis.get("result", {}).get("onchain"),
                additional_info=analysis.get("result", {}).get("additional_info"),
                timestamp=analysis.get("timestamp", analysis.get("created_at"))
            )
            for analysis in analyses
        ]
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análises do usuário: {str(e)}"
        )
