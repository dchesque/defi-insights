from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
import random
from loguru import logger

from ...core.agent_manager import agent_manager
from ...agents.sentiment_agent import SentimentAgent
from ...integrations.supabase import supabase

router = APIRouter()

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
            # Gerar resultado mock em caso de erro
            agent_result = _generate_mock_sentiment_result(request.symbol)
        
        # Prepara dados para salvar no banco
        analysis_data = {
            "user_id": request.user_id,
            "symbol": request.symbol,
            "analysis_type": "sentiment",
            "overall_sentiment": agent_result.get("overall_sentiment", {"sentiment": "neutral", "score": 50}),
            "sentiment_by_source": agent_result.get("sentiment_by_source", {}),
            "engagement_metrics": agent_result.get("engagement_metrics", {"total_mentions": 0}),
            "discussion_trends": agent_result.get("discussion_trends", []),
            "timestamp": agent_result.get("timestamp", datetime.now().isoformat())
        }
        
        # Tenta salvar análise no banco - permite continuar mesmo se falhar
        try:
            result = supabase.save_analysis(analysis_data)
            if result.error:
                logger.error(f"Erro ao salvar análise no Supabase: {result.error}")
                analysis_id = f"temp_{request.symbol}_{int(datetime.now().timestamp())}"
            else:
                analysis_id = result.data[0]["id"]
        except Exception as e:
            logger.error(f"Erro ao acessar Supabase: {str(e)}")
            analysis_id = f"temp_{request.symbol}_{int(datetime.now().timestamp())}"
        
        # Retorna resposta formatada
        return SentimentAnalysisResponse(
            analysis_id=analysis_id,
            symbol=request.symbol,
            overall_sentiment=analysis_data["overall_sentiment"],
            sentiment_by_source=analysis_data["sentiment_by_source"],
            engagement_metrics=analysis_data["engagement_metrics"],
            discussion_trends=analysis_data["discussion_trends"],
            timestamp=analysis_data["timestamp"]
        )
        
    except Exception as e:
        logger.error(f"Erro ao realizar análise de sentimento: {str(e)}")
        # Gerar mock em caso de erro geral
        mock_result = _generate_mock_sentiment_result(request.symbol)
        
        return SentimentAnalysisResponse(
            analysis_id=f"error_{request.symbol}_{int(datetime.now().timestamp())}",
            symbol=request.symbol,
            overall_sentiment=mock_result["overall_sentiment"],
            sentiment_by_source=mock_result["sentiment_by_source"],
            engagement_metrics=mock_result["engagement_metrics"],
            discussion_trends=mock_result["discussion_trends"],
            timestamp=datetime.now().isoformat()
        )

def _generate_mock_sentiment_result(symbol: str) -> Dict[str, Any]:
    """
    Gera um resultado de análise de sentimento simulado em caso de falha.
    
    Args:
        symbol: Símbolo do token.
        
    Returns:
        Dicionário com resultado simulado.
    """
    # Define o sentimento com base no símbolo
    if symbol.upper() in ["BTC", "ETH"]:
        sentiment = "positive"
        score = random.randint(70, 85)
    else:
        sentiments = ["slightly_negative", "neutral", "slightly_positive"]
        sentiment = random.choice(sentiments)
        score = 40 if sentiment == "slightly_negative" else 50 if sentiment == "neutral" else 60
    
    mock_sources = {
        "telegram": {
            "score": score,
            "sentiment": sentiment,
            "confidence": 0.8,
            "is_simulated": True
        },
        "general_discussion": {
            "score": score - random.randint(-5, 5),
            "sentiment": sentiment,
            "confidence": 0.75,
            "is_simulated": True
        }
    }
    
    mock_trends = [
        {
            "theme": f"Análise técnica do {symbol} mostra padrões interessantes",
            "relevance": "alta",
            "sentiment": sentiment,
            "is_simulated": True
        },
        {
            "theme": f"Discussão sobre o futuro de {symbol} no mercado",
            "relevance": "média",
            "sentiment": sentiment,
            "is_simulated": True
        }
    ]
    
    return {
        "overall_sentiment": {
            "score": score,
            "sentiment": sentiment,
            "confidence": 0.8,
            "sources_count": 2,
            "is_simulated": True
        },
        "sentiment_by_source": mock_sources,
        "engagement_metrics": {
            "total_mentions": random.randint(5, 20),
            "mentions_by_source": {
                "telegram": random.randint(2, 10),
                "general_discussion": random.randint(3, 10)
            },
            "activity_level": "médio",
            "trend": "estável",
            "is_simulated": True
        },
        "discussion_trends": mock_trends,
        "timestamp": datetime.now().isoformat()
    }

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
        result = supabase.client.table("token_analyses").select("*").eq("id", analysis_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Análise não encontrada"
            )
        
        analysis = result.data[0]
        
        if analysis["analysis_type"] != "sentiment":
            raise HTTPException(
                status_code=400,
                detail="A análise solicitada não é do tipo sentimento"
            )
        
        return SentimentAnalysisResponse(
            analysis_id=analysis["id"],
            symbol=analysis["symbol"],
            overall_sentiment=analysis["overall_sentiment"],
            sentiment_by_source=analysis["sentiment_by_source"],
            engagement_metrics=analysis["engagement_metrics"],
            discussion_trends=analysis["discussion_trends"],
            timestamp=analysis["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análise: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[SentimentAnalysisResponse])
async def get_user_sentiment_analyses(user_id: str):
    """
    Obtém todas as análises de sentimento de um usuário.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        List[SentimentAnalysisResponse]: Lista de análises de sentimento
    """
    try:
        # Busca análises do usuário no banco
        result = supabase.get_user_analyses(user_id)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar análises do usuário"
            )
        
        # Filtra apenas análises de sentimento
        sentiment_analyses = [
            analysis for analysis in result.data
            if analysis["analysis_type"] == "sentiment"
        ]
        
        return [
            SentimentAnalysisResponse(
                analysis_id=analysis["id"],
                symbol=analysis["symbol"],
                overall_sentiment=analysis["overall_sentiment"],
                sentiment_by_source=analysis["sentiment_by_source"],
                engagement_metrics=analysis["engagement_metrics"],
                discussion_trends=analysis["discussion_trends"],
                timestamp=analysis["timestamp"]
            )
            for analysis in sentiment_analyses
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análises do usuário: {str(e)}"
        ) 