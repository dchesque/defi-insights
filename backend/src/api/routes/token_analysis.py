from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from ...core.agent_manager import agent_manager
from ...agents.technical_agent import TechnicalAgent
from ...integrations.supabase import supabase

router = APIRouter()

# Modelos Pydantic
class TokenAnalysisRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"  # default 1 hora
    user_id: str

class TokenAnalysisResponse(BaseModel):
    analysis_id: str
    symbol: str
    timeframe: str
    indicators: Dict[str, Any]
    signals: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    support_resistance: Dict[str, List[float]]
    timestamp: str

# Registrar o agente técnico
technical_agent = TechnicalAgent()
agent_manager.register_agent(technical_agent)

@router.post("/technical", response_model=TokenAnalysisResponse)
async def analyze_token_technical(request: TokenAnalysisRequest):
    """
    Realiza análise técnica de um token.
    
    Args:
        request: Dados do token para análise
        
    Returns:
        TokenAnalysisResponse: Resultado da análise técnica
    """
    try:
        # Executa análise técnica
        analysis_result = await agent_manager.run_analysis(
            token_data={
                "symbol": request.symbol,
                "timeframe": request.timeframe
            },
            agent_names=["TechnicalAgent"]
        )
        
        if "error" in analysis_result.get("TechnicalAgent", {}):
            raise HTTPException(
                status_code=400,
                detail=analysis_result["TechnicalAgent"]["error"]
            )
        
        # Prepara dados para salvar no banco
        analysis_data = {
            "user_id": request.user_id,
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "analysis_type": "technical",
            "indicators": analysis_result["TechnicalAgent"]["indicators"],
            "signals": analysis_result["TechnicalAgent"]["signals"],
            "trend_analysis": analysis_result["TechnicalAgent"]["trend_analysis"],
            "support_resistance": analysis_result["TechnicalAgent"]["support_resistance"],
            "timestamp": analysis_result["TechnicalAgent"]["timestamp"]
        }
        
        # Salva análise no banco
        result = supabase.save_analysis(analysis_data)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar análise no banco de dados"
            )
        
        # Retorna resposta formatada
        return TokenAnalysisResponse(
            analysis_id=result.data[0]["id"],
            symbol=request.symbol,
            timeframe=request.timeframe,
            indicators=analysis_result["TechnicalAgent"]["indicators"],
            signals=analysis_result["TechnicalAgent"]["signals"],
            trend_analysis=analysis_result["TechnicalAgent"]["trend_analysis"],
            support_resistance=analysis_result["TechnicalAgent"]["support_resistance"],
            timestamp=analysis_result["TechnicalAgent"]["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar análise técnica: {str(e)}"
        )

@router.get("/technical/{analysis_id}", response_model=TokenAnalysisResponse)
async def get_technical_analysis(analysis_id: str):
    """
    Obtém uma análise técnica específica pelo ID.
    
    Args:
        analysis_id: ID da análise
        
    Returns:
        TokenAnalysisResponse: Resultado da análise técnica
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
        
        return TokenAnalysisResponse(
            analysis_id=analysis["id"],
            symbol=analysis["symbol"],
            timeframe=analysis["timeframe"],
            indicators=analysis["indicators"],
            signals=analysis["signals"],
            trend_analysis=analysis["trend_analysis"],
            support_resistance=analysis["support_resistance"],
            timestamp=analysis["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análise: {str(e)}"
        )

@router.get("/technical/user/{user_id}", response_model=List[TokenAnalysisResponse])
async def get_user_technical_analyses(user_id: str):
    """
    Obtém todas as análises técnicas de um usuário.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        List[TokenAnalysisResponse]: Lista de análises técnicas
    """
    try:
        # Busca análises do usuário no banco
        result = supabase.get_user_analyses(user_id)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar análises do usuário"
            )
        
        # Filtra apenas análises técnicas
        technical_analyses = [
            analysis for analysis in result.data
            if analysis["analysis_type"] == "technical"
        ]
        
        return [
            TokenAnalysisResponse(
                analysis_id=analysis["id"],
                symbol=analysis["symbol"],
                timeframe=analysis["timeframe"],
                indicators=analysis["indicators"],
                signals=analysis["signals"],
                trend_analysis=analysis["trend_analysis"],
                support_resistance=analysis["support_resistance"],
                timestamp=analysis["timestamp"]
            )
            for analysis in technical_analyses
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análises do usuário: {str(e)}"
        )
