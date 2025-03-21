from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
from loguru import logger

from ...models.onchain import OnchainRequest, OnchainResponse
from ...core.agent_manager import agent_manager
from ...agents.onchain_agent import OnchainAgent
from ...db.database import Database

router = APIRouter()
db = Database()

# Registrar o agente de análise onchain
onchain_agent = OnchainAgent()
agent_manager.register_agent(onchain_agent)

@router.post("/", response_model=OnchainResponse)
async def analyze_token_onchain(request: OnchainRequest):
    """
    Realiza análise onchain de um token.
    
    Args:
        request: Dados do token para análise
        
    Returns:
        OnchainResponse: Resultado da análise onchain
    """
    try:
        # Executa análise onchain
        analysis_result = await agent_manager.run_analysis(
            token_data={
                "address": request.token_address,
                "chain": request.chain
            },
            agent_names=["OnchainAgent"]
        )
        
        agent_result = analysis_result.get("OnchainAgent", {})
        
        if "error" in agent_result:
            logger.error(f"Erro na análise onchain: {agent_result['error']}")
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao realizar análise onchain: {agent_result['error']}"
            )
        
        # Prepara dados para salvar no banco
        analysis_id = str(uuid.uuid4())
        analysis_data = {
            "id": analysis_id,
            "user_id": request.user_id,
            "token_address": request.token_address,
            "chain": request.chain,
            "analysis_type": "onchain",
            "result": agent_result,
            "created_at": datetime.now().isoformat()
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
        
        # Formatar resposta
        onchain_response = OnchainResponse(
            analysis_id=analysis_id,
            token_address=request.token_address,
            **agent_result
        )
        
        return onchain_response
        
    except HTTPException as he:
        # Propagar exceções HTTP
        raise he
    except Exception as e:
        logger.error(f"Erro ao realizar análise onchain: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao realizar análise onchain: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=OnchainResponse)
async def get_onchain_analysis(analysis_id: str):
    """
    Obtém uma análise onchain específica pelo ID.
    
    Args:
        analysis_id: ID da análise
        
    Returns:
        OnchainResponse: Resultado da análise onchain
    """
    try:
        # Busca análise no banco
        analysis = await db.get_analysis(analysis_id)
        
        if "error" in analysis:
            raise HTTPException(
                status_code=404,
                detail="Análise não encontrada"
            )
        
        if analysis.get("analysis_type") != "onchain":
            raise HTTPException(
                status_code=400,
                detail="A análise solicitada não é do tipo onchain"
            )
        
        # Extrair os dados da resposta
        result = analysis.get("result", {})
        
        # Formatar resposta
        onchain_response = OnchainResponse(
            analysis_id=analysis.get("id"),
            token_address=analysis.get("token_address"),
            **result
        )
        
        return onchain_response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter análise: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[OnchainResponse])
async def get_user_onchain_analyses(user_id: str, limit: int = 10):
    """
    Obtém análises onchain de um usuário.
    
    Args:
        user_id: ID do usuário
        limit: Número máximo de análises a retornar
        
    Returns:
        List[OnchainResponse]: Lista de análises onchain
    """
    try:
        # Busca análises do usuário no banco
        analyses = await db.get_user_analyses(user_id, analysis_type="onchain", limit=limit)
        
        if isinstance(analyses, dict) and "error" in analyses:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar análises do usuário: {analyses['error']}"
            )
        
        # Se a lista estiver vazia, retorna uma lista vazia
        if not analyses:
            return []
        
        # Formatar resposta
        return [
            OnchainResponse(
                analysis_id=analysis.get("id"),
                token_address=analysis.get("token_address"),
                **analysis.get("result", {})
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