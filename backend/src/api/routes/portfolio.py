from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from ...integrations.supabase import supabase

router = APIRouter()

class PortfolioToken(BaseModel):
    symbol: str
    address: str = None
    chain: str = "eth"
    amount: float
    purchase_price: float
    purchase_date: str

class PortfolioCreate(BaseModel):
    name: str
    description: str = None
    user_id: str
    tokens: List[PortfolioToken] = []

class PortfolioTokenUpdate(BaseModel):
    symbol: str
    address: str = None
    chain: str = "eth"
    amount: float = None
    purchase_price: float = None
    purchase_date: str = None

class PortfolioUpdate(BaseModel):
    name: str = None
    description: str = None
    tokens: List[PortfolioTokenUpdate] = None

class PortfolioResponse(BaseModel):
    id: str
    name: str
    description: str = None
    user_id: str
    tokens: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str

@router.post("/", response_model=PortfolioResponse)
async def create_portfolio(portfolio: PortfolioCreate):
    """
    Cria um novo portfólio para o usuário.
    
    Args:
        portfolio: Dados do portfólio
        
    Returns:
        PortfolioResponse: Portfólio criado
    """
    try:
        # Prepara dados para salvar no banco
        portfolio_data = {
            "name": portfolio.name,
            "description": portfolio.description,
            "user_id": portfolio.user_id,
            "tokens": [token.dict() for token in portfolio.tokens],
            "created_at": supabase.client.table("portfolios").select("now()").execute().data[0][0],
            "updated_at": supabase.client.table("portfolios").select("now()").execute().data[0][0]
        }
        
        # Salva portfólio no banco
        result = supabase.save_portfolio(portfolio_data)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar portfólio no banco de dados"
            )
        
        # Retorna portfólio criado
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar portfólio: {str(e)}"
        )

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: str):
    """
    Obtém um portfólio específico pelo ID.
    
    Args:
        portfolio_id: ID do portfólio
        
    Returns:
        PortfolioResponse: Portfólio encontrado
    """
    try:
        # Busca portfólio no banco
        result = supabase.client.table("portfolios").select("*").eq("id", portfolio_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Portfólio não encontrado"
            )
        
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter portfólio: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[PortfolioResponse])
async def get_user_portfolios(user_id: str):
    """
    Obtém todos os portfólios de um usuário.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        List[PortfolioResponse]: Lista de portfólios
    """
    try:
        # Busca portfólios do usuário no banco
        result = supabase.get_user_portfolios(user_id)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar portfólios do usuário"
            )
        
        return result.data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter portfólios do usuário: {str(e)}"
        )

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(portfolio_id: str, portfolio_update: PortfolioUpdate):
    """
    Atualiza um portfólio existente.
    
    Args:
        portfolio_id: ID do portfólio
        portfolio_update: Dados para atualização
        
    Returns:
        PortfolioResponse: Portfólio atualizado
    """
    try:
        # Busca portfólio atual
        current_portfolio = supabase.client.table("portfolios").select("*").eq("id", portfolio_id).execute()
        
        if not current_portfolio.data:
            raise HTTPException(
                status_code=404,
                detail="Portfólio não encontrado"
            )
            
        current_data = current_portfolio.data[0]
        
        # Prepara dados para atualização
        update_data = {}
        
        if portfolio_update.name is not None:
            update_data["name"] = portfolio_update.name
            
        if portfolio_update.description is not None:
            update_data["description"] = portfolio_update.description
            
        if portfolio_update.tokens is not None:
            # Para simplificar, substituímos completamente os tokens
            # Em uma implementação real, você provavelmente iria mesclar os tokens existentes com os novos
            update_data["tokens"] = [token.dict() for token in portfolio_update.tokens]
            
        update_data["updated_at"] = supabase.client.table("portfolios").select("now()").execute().data[0][0]
        
        # Atualiza portfólio
        result = supabase.update_portfolio(portfolio_id, update_data)
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao atualizar portfólio"
            )
            
        return result.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar portfólio: {str(e)}"
        )

@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: str):
    """
    Remove um portfólio.
    
    Args:
        portfolio_id: ID do portfólio
    """
    try:
        # Verifica se o portfólio existe
        current_portfolio = supabase.client.table("portfolios").select("*").eq("id", portfolio_id).execute()
        
        if not current_portfolio.data:
            raise HTTPException(
                status_code=404,
                detail="Portfólio não encontrado"
            )
            
        # Remove portfólio
        result = supabase.client.table("portfolios").delete().eq("id", portfolio_id).execute()
        
        if result.error:
            raise HTTPException(
                status_code=500,
                detail="Erro ao remover portfólio"
            )
            
        return {"message": "Portfólio removido com sucesso"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover portfólio: {str(e)}"
        )
