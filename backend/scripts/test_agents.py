#!/usr/bin/env python
"""
Script para testar agentes de análise individualmente.
Útil para desenvolvimento e depuração.
"""
import os
import sys
import json
import argparse
import asyncio
from datetime import datetime

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.agent_manager import AgentManager
from src.agents.technical_agent import TechnicalAgent
from src.agents.sentiment_agent import SentimentAgent
from src.agents.onchain_agent import OnchainAgent
from src.utils.token_utils import to_json

def parse_args():
    """Analisa os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description="Testa agentes de análise individualmente")
    parser.add_argument("agent", choices=["technical", "sentiment", "onchain", "all"],
                        help="Agente a ser testado")
    parser.add_argument("--symbol", default="BTC", help="Símbolo do token para análise")
    parser.add_argument("--timeframe", default="1d", help="Timeframe para análise técnica")
    parser.add_argument("--address", default="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", 
                        help="Endereço do contrato para análise on-chain")
    parser.add_argument("--chain", default="eth", help="Chain para análise on-chain")
    parser.add_argument("--output", default="results.json", help="Arquivo para salvar resultados")
    return parser.parse_args()

async def test_technical_agent(args):
    """Testa o agente de análise técnica"""
    print(f"\n🔍 Testando TechnicalAgent com {args.symbol} ({args.timeframe})")
    
    # Inicializa o agente
    agent = TechnicalAgent()
    
    # Prepara os dados de entrada
    token_data = {
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "user_id": "test_user"
    }
    
    # Executa a análise
    try:
        start_time = datetime.now()
        results = await agent.analyze(token_data)
        end_time = datetime.now()
        
        # Calcula duração
        duration = (end_time - start_time).total_seconds()
        
        # Exibe resultados resumidos
        print(f"✅ Análise concluída em {duration:.2f} segundos")
        print(f"📊 Resumo da análise técnica para {args.symbol}:")
        print(f"  - Tendência geral: {results.get('trend', 'N/A')}")
        print(f"  - RSI: {results.get('indicators', {}).get('rsi', {}).get('value', 'N/A')}")
        print(f"  - Recomendação: {results.get('recommendation', 'N/A')}")
        
        # Salva os resultados completos
        with open(args.output, "w") as f:
            f.write(to_json(results))
        print(f"💾 Resultados completos salvos em {args.output}")
        
        return results
    except Exception as e:
        print(f"❌ Erro ao executar análise técnica: {str(e)}")
        return None

async def test_sentiment_agent(args):
    """Testa o agente de análise de sentimento"""
    print(f"\n🔍 Testando SentimentAgent com {args.symbol}")
    
    # Inicializa o agente
    agent = SentimentAgent()
    
    # Prepara os dados de entrada
    token_data = {
        "symbol": args.symbol,
        "user_id": "test_user"
    }
    
    # Executa a análise
    try:
        start_time = datetime.now()
        results = await agent.analyze(token_data)
        end_time = datetime.now()
        
        # Calcula duração
        duration = (end_time - start_time).total_seconds()
        
        # Exibe resultados resumidos
        print(f"✅ Análise concluída em {duration:.2f} segundos")
        print(f"🔮 Resumo da análise de sentimento para {args.symbol}:")
        print(f"  - Sentimento geral: {results.get('overall_sentiment', 'N/A')}")
        print("  - Sentimento por fonte:")
        for source, data in results.get('sentiment_by_source', {}).items():
            print(f"    - {source}: {data.get('score', 'N/A')}")
        print(f"  - Engajamento total: {results.get('engagement_metrics', {}).get('total_mentions', 'N/A')} menções")
        
        # Salva os resultados completos
        with open(args.output, "w") as f:
            f.write(to_json(results))
        print(f"💾 Resultados completos salvos em {args.output}")
        
        return results
    except Exception as e:
        print(f"❌ Erro ao executar análise de sentimento: {str(e)}")
        return None

async def test_onchain_agent(args):
    """Testa o agente de análise on-chain"""
    print(f"\n🔍 Testando OnchainAgent com {args.address} ({args.chain})")
    
    # Inicializa o agente
    agent = OnchainAgent()
    
    # Prepara os dados de entrada
    token_data = {
        "address": args.address,
        "chain": args.chain,
        "user_id": "test_user"
    }
    
    # Executa a análise
    try:
        start_time = datetime.now()
        results = await agent.analyze(token_data)
        end_time = datetime.now()
        
        # Calcula duração
        duration = (end_time - start_time).total_seconds()
        
        # Exibe resultados resumidos
        print(f"✅ Análise concluída em {duration:.2f} segundos")
        print(f"⛓️ Resumo da análise on-chain para {args.address}:")
        print(f"  - Holders totais: {results.get('holder_distribution', {}).get('total_holders', 'N/A')}")
        print(f"  - Concentração (top 10): {results.get('holder_distribution', {}).get('concentration', {}).get('top_10_percent', 'N/A')}%")
        print(f"  - Volume 24h: {results.get('transaction_metrics', {}).get('volume_24h', 'N/A')}")
        print(f"  - Nível de risco: {results.get('risk_assessment', {}).get('risk_level', 'N/A')}")
        
        # Salva os resultados completos
        with open(args.output, "w") as f:
            f.write(to_json(results))
        print(f"💾 Resultados completos salvos em {args.output}")
        
        return results
    except Exception as e:
        print(f"❌ Erro ao executar análise on-chain: {str(e)}")
        return None

async def run_tests(args):
    """Executa os testes conforme configuração"""
    print(f"🚀 Iniciando testes de agentes DeFi Insight")
    
    results = {}
    
    # Testa agente técnico
    if args.agent in ["technical", "all"]:
        results["technical"] = await test_technical_agent(args)
    
    # Testa agente de sentimento
    if args.agent in ["sentiment", "all"]:
        results["sentiment"] = await test_sentiment_agent(args)
    
    # Testa agente on-chain
    if args.agent in ["onchain", "all"]:
        results["onchain"] = await test_onchain_agent(args)
    
    print("\n🏁 Testes concluídos!")
    
    # Se testou todos os agentes, salva resultado combinado
    if args.agent == "all":
        with open(f"all_{args.output}", "w") as f:
            f.write(to_json(results))
        print(f"💾 Resultados combinados salvos em all_{args.output}")

if __name__ == "__main__":
    args = parse_args()
    
    # Executa os testes assincronamente
    if sys.version_info >= (3, 7):
        asyncio.run(run_tests(args))
    else:
        print("❌ Python 3.7 ou superior é necessário para executar este script")
        sys.exit(1) 