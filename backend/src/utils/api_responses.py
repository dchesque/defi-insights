# backend/src/utils/api_responses.py - Criado em 21/03/2025 14:00
"""
Utilitários para padronizar as respostas da API.
Facilita a integração com o frontend ao garantir consistência.
"""
from typing import Any, Dict, List, Optional, Union
from fastapi.responses import JSONResponse
from fastapi import status
from datetime import datetime
import uuid

class ApiResponse:
    """
    Classe base para padronizar respostas da API.
    """
    @staticmethod
    def success(
        data: Any, 
        message: str = "Operação concluída com sucesso",
        status_code: int = status.HTTP_200_OK,
        metadata: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Cria uma resposta de sucesso padronizada.
        
        Args:
            data: Dados da resposta
            message: Mensagem de sucesso
            status_code: Código HTTP de status
            metadata: Metadados adicionais (opcional)
            
        Returns:
            JSONResponse com os dados formatados
        """
        response_body = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
        
        if metadata:
            response_body["metadata"] = metadata
            
        return JSONResponse(
            content=response_body,
            status_code=status_code
        )
    
    @staticmethod
    def error(
        message: str = "Ocorreu um erro",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    ) -> JSONResponse:
        """
        Cria uma resposta de erro padronizada.
        
        Args:
            message: Mensagem de erro
            status_code: Código HTTP de status
            error_code: Código de erro interno (opcional)
            details: Detalhes adicionais do erro (opcional)
            
        Returns:
            JSONResponse com o erro formatado
        """
        response_body = {
            "success": False,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
        
        if error_code:
            response_body["error_code"] = error_code
            
        if details:
            response_body["details"] = details
            
        return JSONResponse(
            content=response_body,
            status_code=status_code
        )
    
    @staticmethod
    def paginated_list(
        items: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 10,
        message: str = "Dados recuperados com sucesso"
    ) -> JSONResponse:
        """
        Cria uma resposta paginada para listas.
        
        Args:
            items: Itens da página atual
            total: Total de itens disponíveis
            page: Número da página atual
            page_size: Tamanho da página
            message: Mensagem de sucesso
            
        Returns:
            JSONResponse com os dados paginados
        """
        total_pages = (total + page_size - 1) // page_size
        
        response_body = {
            "success": True,
            "message": message,
            "data": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }
        
        return JSONResponse(
            content=response_body,
            status_code=status.HTTP_200_OK,
            headers={
                "X-Total-Count": str(total),
                "Content-Range": f"items {(page-1)*page_size}-{min(page*page_size, total)}/{total}"
            }
        )