from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from ...core.agent_manager import agent_manager
from ...agents.onchain_agent import OnchainAgent
from ...integrations.supabase import supabase

router = APIRouter()

class OnchainAnalysisRequest(BaseModel):
    address: str
    chain: str = "eth"  # default Ethereum
    user_id: str

class OnchainAnalysisResponse(BaseModel):
    analysis_id: str
    address: str
    chain: str
    holder_distribution: Dict[str, Any]
    transaction_metrics: Dict[str, Any]
    liquidity_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timestamp: str

# Registrar o agente on-chain
onchain_agent = OnchainAgent()
agent_manager.register_agent(onchain_agent)

@router.post("/", response_model=OnchainAnalysisResponse)
async def analyze_token_onchain(request: OnchainAnalysisRequest):
    """
    Realiza análise on-chain de um token.
    
    Args:
        request: Dados do token para análise
        
    Returns:
        OnchainAnalysisResponse: Resultado da análise on-chain
    """
    try:
        # Executa análise on-chain
        analysis_result = await agent_manager.run_analysis(
            token_data={
                "address": request.address,
                "chain": request.chain
            },
            agent_names=["OnchainAgent"]
        )
        
        if "error" in analysis_result.get("OnchainAgent", {}):
            raise HTTPException(
                status_code=400,
                detail=analysis_result["OnchainAgent"]["error"]
            )
        
        # Prepara dados para salvar no banco
        analysis_data = {
            "user_id": request.user_id,
            "address": request.address,
            "chain": request.chain,
            "analysis_type": "onchain",
            "holder_distribution": analysis_result["OnchainAgent"]["holder_distribution"],
            "transaction_metrics": analysis_result["OnchainAgent"]["transaction_metrics"],
            "liquidity_analysis": analysis_result["OnchainAgent"]["liquidity_analysis"],
            "risk_assessment": analysis_result["OnchainAgent"]["risk_assessment"],
            "timestamp": analysis_result["OnchainAgent"]["timestamp"]
        }
        
        # Salva análise no banco
        result = supabase.save_analysis(analysis_data)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar análise no banco de dados"
            )
        
        # Retorna resposta formatada
        return OnchainAnalysisResponse(
            analysis_id=result.data[0]["id"],
            address=request.address,
            chain=request.chain,
            holder_distribution=analysis_result["OnchainAgent"]["holder_distribution"],
            transaction_metrics=analysis_result["OnchainAgent"]["transaction_metrics"],
            liquidity_analysis=analysis_result["OnchainAgent"]["liquidity_analysis"],
            risk_assessment=analysis_result["OnchainAgent"]["risk_assessment"],
            timestamp=analysis_result["OnchainAgent"]["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar análise on-chain: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=OnchainAnalysisResponse)
async def get_onchain_analysis(analysis_id: str):
    """
    Obtém uma análise on-chain específica pelo ID.
    
    Args:
        analysis_id: ID da análise
        
    Returns:
        OnchainAnalysisResponse: Resultado da análise on-chain
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
        
        if analysis["analysis_type"] != "onchain":
            raise HTTPException(
                status_code=400,
                detail="A análise solicitada não é do tipo on-chain"
            )
        
        return OnchainAnalysisResponse(
            analysis_id=analysis["id"],
            address=analysis["address"],
            chain=analysis["chain"],
            holder_distribution=analysis["holder_distribution"],
            transaction_metrics=analysis["transaction_metrics"],
            liquidity_analysis=analysis["liquidity_analysis"],
            risk_assessment=analysis["risk_assessment"],
            timestamp=analysis["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análise: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[OnchainAnalysisResponse])
async def get_user_onchain_analyses(user_id: str):
    """
    Obtém todas as análises on-chain de um usuário.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        List[OnchainAnalysisResponse]: Lista de análises on-chain
    """
    try:
        # Busca análises do usuário no banco
        result = supabase.get_user_analyses(user_id)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar análises do usuário"
            )
        
        # Filtra apenas análises on-chain
        onchain_analyses = [
            analysis for analysis in result.data
            if analysis["analysis_type"] == "onchain"
        ]
        
        return [
            OnchainAnalysisResponse(
                analysis_id=analysis["id"],
                address=analysis["address"],
                chain=analysis["chain"],
                holder_distribution=analysis["holder_distribution"],
                transaction_metrics=analysis["transaction_metrics"],
                liquidity_analysis=analysis["liquidity_analysis"],
                risk_assessment=analysis["risk_assessment"],
                timestamp=analysis["timestamp"]
            )
            for analysis in onchain_analyses
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análises do usuário: {str(e)}"
        ) 