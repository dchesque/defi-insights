"""
Testes básicos para verificar se a aplicação FastAPI está funcionando.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa a aplicação
try:
    from src.main import app
    client = TestClient(app)
except ImportError:
    pytestmark = pytest.mark.skip(reason="Módulos necessários não encontrados")

def test_read_root():
    """Testa o endpoint raiz da aplicação."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Bem-vindo" in response.json()["message"] 