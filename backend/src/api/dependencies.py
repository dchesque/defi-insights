from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv
from src.integrations.supabase import supabase

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Configurações do JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "seu_secret_key_aqui")  # Usar a variável de ambiente
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Obtém o usuário atual a partir do token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        dict: Dados do usuário
        
    Raises:
        HTTPException: Se o token for inválido
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodifica o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        # Busca usuário no Supabase
        result = supabase.get_user(user_id)
        
        if result.error or not result.data:
            raise credentials_exception
            
        return result.data[0]
        
    except JWTError:
        raise credentials_exception

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token de acesso JWT.
    
    Args:
        data: Dados para incluir no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        str: Token JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
