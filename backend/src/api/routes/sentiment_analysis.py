from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import random
from loguru import logger

from ...core.agent_manager import agent_manager
from ...agents.sentiment_agent import SentimentAgent
from ...integrations.supabase import supabase
from ...db.database import Database

router = APIRouter()
db = Database()

class SentimentAnalysisRequest(BaseModel):
    symbol: str
    user_id: str

class SentimentAnalysisResponse(BaseModel):
    analysis_id: str
    symbol: str
    overall_sentiment: Dict[str, Any]
    sentiment_by_source: Dict[str, Dict[str, float]]
    engagement_metrics: Dict[str, Any]
    discussion_trends: List[str]
    timestamp: str

# Registrar o agente de sentimento
sentiment_agent = SentimentAgent()
agent_manager.register_agent(sentiment_agent)

@router.post("/", response_model=SentimentAnalysisResponse)
async def analyze_token_sentiment(request: SentimentAnalysisRequest):
    """
    Realiza análise de sentimento de um token.
    
    Args:
        request: Dados do token para análise
        
    Returns:
        SentimentAnalysisResponse: Resultado da análise de sentimento
    """
    try:
        # Executa análise de sentimento
        analysis_result = await agent_manager.run_analysis(
            token_data={"symbol": request.symbol},
            agent_names=["SentimentAgent"]
        )
        
        agent_result = analysis_result.get("SentimentAgent", {})
        
        if "error" in agent_result:
            logger.error(f"Erro na análise de sentimento: {agent_result['error']}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao realizar análise de sentimento: {agent_result['error']}"
            )
        
        # Prepara dados para salvar no banco
        analysis_data = {
            "user_id": request.user_id,
            "symbol": request.symbol,
            "analysis_type": "sentiment",
            "result": {
                "overall_sentiment": agent_result.get("overall_sentiment", {"sentiment": "neutral", "score": 50}),
                "sentiment_by_source": agent_result.get("sentiment_by_source", {}),
                "engagement_metrics": agent_result.get("engagement_metrics", {"total_mentions": 0}),
                "discussion_trends": agent_result.get("discussion_trends", []),
            },
            "created_at": datetime.now().isoformat(),
            "timestamp": agent_result.get("timestamp", datetime.now().isoformat())
        }
        
        # Tenta salvar análise no banco - permite continuar mesmo se falhar
        try:
            result = await db.save_analysis(analysis_data)
            if "error" in result:
                logger.error(f"Erro ao salvar análise no banco: {result['error']}")
                analysis_id = f"temp_{request.symbol}_{int(datetime.now().timestamp())}"
            else:
                analysis_id = result.get("id", f"temp_{request.symbol}_{int(datetime.now().timestamp())}")
        except Exception as e:
            logger.error(f"Erro ao acessar banco de dados: {str(e)}")
            analysis_id = f"temp_{request.symbol}_{int(datetime.now().timestamp())}"
        
        # Extrai os dados para a resposta
        overall_sentiment = analysis_data["result"]["overall_sentiment"]
        sentiment_by_source = analysis_data["result"]["sentiment_by_source"]
        engagement_metrics = analysis_data["result"]["engagement_metrics"]
        discussion_trends = analysis_data["result"]["discussion_trends"]
        
        # Retorna resposta formatada
        return SentimentAnalysisResponse(
            analysis_id=analysis_id,
            symbol=request.symbol,
            overall_sentiment=overall_sentiment,
            sentiment_by_source=sentiment_by_source,
            engagement_metrics=engagement_metrics,
            discussion_trends=discussion_trends,
            timestamp=analysis_data["timestamp"]
        )
        
    except HTTPException as he:
        # Propagar exceções HTTP
        raise he
    except Exception as e:
        logger.error(f"Erro ao realizar análise de sentimento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar análise de sentimento: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=SentimentAnalysisResponse)
async def get_sentiment_analysis(analysis_id: str):
    """
    Obtém uma análise de sentimento específica pelo ID.
    
    Args:
        analysis_id: ID da análise
        
    Returns:
        SentimentAnalysisResponse: Resultado da análise de sentimento
    """
    try:
        # Busca análise no banco
        analysis = await db.get_analysis(analysis_id)
        
        if "error" in analysis:
            raise HTTPException(
                status_code=404,
                detail="Análise não encontrada"
            )
        
        if analysis.get("analysis_type") != "sentiment":
            raise HTTPException(
                status_code=400,
                detail="A análise solicitada não é do tipo sentimento"
            )
        
        # Extrai os dados do resultado
        result = analysis.get("result", {})
        overall_sentiment = result.get("overall_sentiment", {})
        sentiment_by_source = result.get("sentiment_by_source", {})
        engagement_metrics = result.get("engagement_metrics", {})
        discussion_trends = result.get("discussion_trends", [])
        
        return SentimentAnalysisResponse(
            analysis_id=analysis.get("id"),
            symbol=analysis.get("symbol"),
            overall_sentiment=overall_sentiment,
            sentiment_by_source=sentiment_by_source,
            engagement_metrics=engagement_metrics,
            discussion_trends=discussion_trends,
            timestamp=analysis.get("timestamp", analysis.get("created_at"))
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análise: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[SentimentAnalysisResponse])
async def get_user_sentiment_analyses(user_id: str, limit: int = 10):
    """
    Obtém análises de sentimento de um usuário.
    
    Args:
        user_id: ID do usuário
        limit: Número máximo de análises a retornar
        
    Returns:
        List[SentimentAnalysisResponse]: Lista de análises de sentimento
    """
    try:
        # Busca análises do usuário no banco
        analyses = await db.get_user_analyses(user_id, analysis_type="sentiment", limit=limit)
        
        if isinstance(analyses, dict) and "error" in analyses:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar análises do usuário: {analyses['error']}"
            )
        
        # Se a lista estiver vazia, retorna uma lista vazia
        if not analyses:
            return []
        
        return [
            SentimentAnalysisResponse(
                analysis_id=analysis.get("id"),
                symbol=analysis.get("symbol"),
                overall_sentiment=analysis.get("result", {}).get("overall_sentiment", {}),
                sentiment_by_source=analysis.get("result", {}).get("sentiment_by_source", {}),
                engagement_metrics=analysis.get("result", {}).get("engagement_metrics", {}),
                discussion_trends=analysis.get("result", {}).get("discussion_trends", []),
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