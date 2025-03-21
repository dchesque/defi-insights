# backend/src/api/middlewares/error_handler.py - Criado em 21/03/2025 14:10
"""
Middleware para tratamento global de exceções.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import traceback
from datetime import datetime
import uuid
from loguru import logger

async def error_handler_middleware(request: Request, call_next):
    """
    Middleware para capturar exceções e formatar respostas de erro.
    
    Args:
        request: Requisição atual
        call_next: Próxima função na cadeia de middleware
        
    Returns:
        Resposta formatada, seja de sucesso ou erro
    """
    try:
        return await call_next(request)
    except Exception as exc:
        # Log detalhado do erro
        logger.error(f"Erro não tratado: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # Se já for uma HTTPException, preservar status code e detail
        if isinstance(exc, HTTPException):
            status_code = exc.status_code
            detail = exc.detail
        # Se for erro de validação, tratar específicamente
        elif isinstance(exc, RequestValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            detail = "Erro de validação dos dados"
            error_details = exc.errors()
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Erro interno do servidor"
        
        # Montar resposta padronizada
        error_response = {
            "success": False,
            "message": detail,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4()),
            "path": request.url.path
        }
        
        # Adicionar detalhes para erros de validação
        if isinstance(exc, RequestValidationError):
            error_response["details"] = error_details
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )