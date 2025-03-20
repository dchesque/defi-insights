#!/usr/bin/env python
"""
Script para testar a API DeFi Insight
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime
import httpx

def parse_args():
    parser = argparse.ArgumentParser(description="Testa a API DeFi Insight")
    parser.add_argument("--host", default="http://localhost:8000", help="Host da API")
    parser.add_argument("--test", default="all", choices=["all", "health", "auth", "technical", "sentiment", "onchain", "portfolio"], 
                        help="Teste específico para executar")
    return parser.parse_args()

async def test_health(client, base_url):
    """Testa a rota de health check"""
    print("\n🔍 Testando health check...")
    
    try:
        response = await client.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health check OK")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao acessar a API: {str(e)}")
        return False

async def test_auth(client, base_url):
    """Testa a rota de autenticação"""
    print("\n🔍 Testando autenticação...")
    
    try:
        # Tenta registrar um usuário temporário para teste
        email = f"test_{int(time.time())}@example.com"
        password = "Test123456"
        
        register_data = {
            "email": email,
            "password": password,
            "name": "Usuário de Teste"
        }
        
        register_response = await client.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"📝 Registro: {register_response.status_code}")
        
        # Tenta fazer login
        login_data = {
            "username": email,
            "password": password
        }
        
        token_response = await client.post(f"{base_url}/api/auth/token", data=login_data)
        print(f"🔑 Login: {token_response.status_code}")
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            token = token_data.get("access_token")
            
            # Testa obter dados do usuário
            headers = {"Authorization": f"Bearer {token}"}
            me_response = await client.get(f"{base_url}/api/auth/me", headers=headers)
            print(f"👤 Dados do usuário: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_id = me_response.json().get("id")
                print(f"✅ Autenticação OK (user_id: {user_id})")
                return True, token, user_id
        
        print("❌ Falha na autenticação")
        return False, None, None
    except Exception as e:
        print(f"❌ Erro ao testar autenticação: {str(e)}")
        return False, None, None

async def test_technical_analysis(client, base_url, token, user_id):
    """Testa análise técnica"""
    print("\n🔍 Testando análise técnica...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Solicita análise técnica de BTC
        analysis_data = {
            "symbol": "BTC",
            "timeframe": "1d",
            "user_id": user_id
        }
        
        analysis_response = await client.post(
            f"{base_url}/api/analysis/technical", 
            json=analysis_data,
            headers=headers
        )
        
        print(f"📊 Análise técnica: {analysis_response.status_code}")
        
        if analysis_response.status_code == 200:
            analysis_id = analysis_response.json().get("analysis_id")
            
            # Obtém a análise pelo ID
            get_analysis_response = await client.get(
                f"{base_url}/api/analysis/technical/{analysis_id}",
                headers=headers
            )
            
            print(f"🔍 Obter análise: {get_analysis_response.status_code}")
            
            # Obtém análises do usuário
            user_analyses_response = await client.get(
                f"{base_url}/api/analysis/technical/user/{user_id}",
                headers=headers
            )
            
            print(f"📋 Análises do usuário: {user_analyses_response.status_code}")
            
            if (analysis_response.status_code == 200 and 
                get_analysis_response.status_code == 200 and
                user_analyses_response.status_code == 200):
                print("✅ Análise técnica OK")
                return True
        
        print("❌ Falha na análise técnica")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar análise técnica: {str(e)}")
        return False

async def test_sentiment_analysis(client, base_url, token, user_id):
    """Testa análise de sentimento"""
    print("\n🔍 Testando análise de sentimento...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Solicita análise de sentimento de ETH
        analysis_data = {
            "symbol": "ETH",
            "user_id": user_id
        }
        
        analysis_response = await client.post(
            f"{base_url}/api/sentiment", 
            json=analysis_data,
            headers=headers
        )
        
        print(f"🔮 Análise de sentimento: {analysis_response.status_code}")
        
        if analysis_response.status_code == 200:
            analysis_id = analysis_response.json().get("analysis_id")
            
            # Obtém a análise pelo ID
            get_analysis_response = await client.get(
                f"{base_url}/api/sentiment/{analysis_id}",
                headers=headers
            )
            
            print(f"🔍 Obter análise: {get_analysis_response.status_code}")
            
            # Obtém análises do usuário
            user_analyses_response = await client.get(
                f"{base_url}/api/sentiment/user/{user_id}",
                headers=headers
            )
            
            print(f"📋 Análises do usuário: {user_analyses_response.status_code}")
            
            if (analysis_response.status_code == 200 and 
                get_analysis_response.status_code == 200 and
                user_analyses_response.status_code == 200):
                print("✅ Análise de sentimento OK")
                return True
        
        print("❌ Falha na análise de sentimento")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar análise de sentimento: {str(e)}")
        return False

async def test_onchain_analysis(client, base_url, token, user_id):
    """Testa análise on-chain"""
    print("\n🔍 Testando análise on-chain...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Solicita análise on-chain de um endereço
        analysis_data = {
            "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",  # Endereço do contrato UNI
            "chain": "eth",
            "user_id": user_id
        }
        
        analysis_response = await client.post(
            f"{base_url}/api/onchain", 
            json=analysis_data,
            headers=headers
        )
        
        print(f"⛓️ Análise on-chain: {analysis_response.status_code}")
        
        if analysis_response.status_code == 200:
            analysis_id = analysis_response.json().get("analysis_id")
            
            # Obtém a análise pelo ID
            get_analysis_response = await client.get(
                f"{base_url}/api/onchain/{analysis_id}",
                headers=headers
            )
            
            print(f"🔍 Obter análise: {get_analysis_response.status_code}")
            
            # Obtém análises do usuário
            user_analyses_response = await client.get(
                f"{base_url}/api/onchain/user/{user_id}",
                headers=headers
            )
            
            print(f"📋 Análises do usuário: {user_analyses_response.status_code}")
            
            if (analysis_response.status_code == 200 and 
                get_analysis_response.status_code == 200 and
                user_analyses_response.status_code == 200):
                print("✅ Análise on-chain OK")
                return True
        
        print("❌ Falha na análise on-chain")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar análise on-chain: {str(e)}")
        return False

async def test_portfolio(client, base_url, token, user_id):
    """Testa gerenciamento de portfólio"""
    print("\n🔍 Testando gerenciamento de portfólio...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Cria um portfólio
        portfolio_data = {
            "name": f"Portfólio de Teste {int(time.time())}",
            "description": "Portfólio criado automaticamente para teste",
            "user_id": user_id,
            "tokens": [
                {
                    "symbol": "BTC",
                    "amount": 0.5,
                    "purchase_price": 30000,
                    "purchase_date": datetime.now().isoformat()
                },
                {
                    "symbol": "ETH",
                    "amount": 5,
                    "purchase_price": 2000,
                    "purchase_date": datetime.now().isoformat()
                }
            ]
        }
        
        create_response = await client.post(
            f"{base_url}/api/portfolio", 
            json=portfolio_data,
            headers=headers
        )
        
        print(f"📁 Criar portfólio: {create_response.status_code}")
        
        if create_response.status_code == 200:
            portfolio_id = create_response.json().get("id")
            
            # Obtém o portfólio pelo ID
            get_response = await client.get(
                f"{base_url}/api/portfolio/{portfolio_id}",
                headers=headers
            )
            
            print(f"🔍 Obter portfólio: {get_response.status_code}")
            
            # Atualiza o portfólio
            update_data = {
                "name": f"Portfólio Atualizado {int(time.time())}"
            }
            
            update_response = await client.put(
                f"{base_url}/api/portfolio/{portfolio_id}",
                json=update_data,
                headers=headers
            )
            
            print(f"✏️ Atualizar portfólio: {update_response.status_code}")
            
            # Obtém todos os portfólios do usuário
            list_response = await client.get(
                f"{base_url}/api/portfolio/user/{user_id}",
                headers=headers
            )
            
            print(f"📋 Listar portfólios: {list_response.status_code}")
            
            # Exclui o portfólio
            delete_response = await client.delete(
                f"{base_url}/api/portfolio/{portfolio_id}",
                headers=headers
            )
            
            print(f"🗑️ Excluir portfólio: {delete_response.status_code}")
            
            if (create_response.status_code == 200 and
                get_response.status_code == 200 and
                update_response.status_code == 200 and
                list_response.status_code == 200 and
                delete_response.status_code == 200):
                print("✅ Gerenciamento de portfólio OK")
                return True
        
        print("❌ Falha no gerenciamento de portfólio")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar gerenciamento de portfólio: {str(e)}")
        return False

async def run_tests(args):
    """Executa os testes conforme configuração"""
    base_url = args.host
    test_type = args.test
    
    print(f"\n🚀 Iniciando testes da API em {base_url}")
    print(f"📝 Tipo de teste: {test_type}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Testa health check
        if test_type in ["all", "health"]:
            health_ok = await test_health(client, base_url)
            if not health_ok and test_type == "all":
                print("⛔ Health check falhou, abortando testes subsequentes")
                return
        
        # Testa autenticação
        if test_type in ["all", "auth", "technical", "sentiment", "onchain", "portfolio"]:
            auth_ok, token, user_id = await test_auth(client, base_url)
            if not auth_ok and test_type in ["all", "technical", "sentiment", "onchain", "portfolio"]:
                print("⛔ Autenticação falhou, abortando testes subsequentes")
                return
        
        # Testa análise técnica
        if test_type in ["all", "technical"]:
            await test_technical_analysis(client, base_url, token, user_id)
        
        # Testa análise de sentimento
        if test_type in ["all", "sentiment"]:
            await test_sentiment_analysis(client, base_url, token, user_id)
        
        # Testa análise on-chain
        if test_type in ["all", "onchain"]:
            await test_onchain_analysis(client, base_url, token, user_id)
        
        # Testa gerenciamento de portfólio
        if test_type in ["all", "portfolio"]:
            await test_portfolio(client, base_url, token, user_id)
    
    print("\n🏁 Testes concluídos!")

if __name__ == "__main__":
    args = parse_args()
    
    if sys.version_info >= (3, 7):
        import asyncio
        asyncio.run(run_tests(args))
    else:
        print("❌ Python 3.7 ou superior é necessário para executar este script")
        sys.exit(1) 