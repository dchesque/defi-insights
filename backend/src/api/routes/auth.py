from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any
from pydantic import BaseModel
from src.integrations.supabase import supabase
from ..dependencies import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    Registra um novo usuário.
    
    Args:
        user: Dados do usuário a ser registrado
        
    Returns:
        UserResponse: Dados do usuário registrado
        
    Raises:
        HTTPException: Se o registro falhar
    """
    try:
        # Verificar se o usuário já existe
        existing_users = supabase.client.table("users").select("*").eq("email", user.email).execute()
        
        if existing_users.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já registrado"
            )
        
        # Registrar usuário no Supabase
        new_user = {
            "email": user.email,
            "password": user.password,  # O Supabase fará o hash da senha
            "name": user.name
        }
        
        response = supabase.create_user(new_user)
        
        if response.error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao registrar usuário: {response.error.message}"
            )
        
        return response.data[0]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no servidor: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autentica um usuário e retorna um token JWT.
    
    Args:
        form_data: Dados de login (username=email, password)
        
    Returns:
        Token: Token de acesso
        
    Raises:
        HTTPException: Se a autenticação falhar
    """
    # Autenticar usuário
    try:
        # No Supabase, autenticação é tratada separadamente
        user_query = supabase.client.table("users").select("*").eq("email", form_data.username).execute()
        
        if not user_query.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_query.data[0]
        
        # Verificar senha (em produção, isso seria verificado pelo Supabase)
        if user["password"] != form_data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["id"]},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no servidor: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado.
    
    Args:
        current_user: Usuário atual (injetado via token)
        
    Returns:
        UserResponse: Dados do usuário
    """
    return current_user
