import asyncio
from src.agents.token_agent import TokenAgent
import json
from datetime import datetime

async def analyze_bitcoin():
    """Testa a análise do Bitcoin de forma direta"""
    try:
        # Criar instância do TokenAgent
        token_agent = TokenAgent()
        
        # Configurar dados para análise usando a URL oficial do Bitcoin no CoinGecko
        token_data = {
            "url": "https://www.coingecko.com/en/coins/bitcoin",
            "symbol": "BTC"  # Como fallback caso o URL não funcione
        }
        
        # Extrair informações do token a partir da URL
        extracted_data = token_agent.extract_token_from_url(token_data["url"])
        print(f"Dados extraídos da URL: {json.dumps(extracted_data, indent=2)}")
        
        # Validar entrada
        is_valid = await token_agent.validate_input(token_data)
        print(f"Dados válidos: {is_valid}")
        
        if not is_valid:
            print("Dados de entrada inválidos para análise de BTC")
            return
        
        # Executar análise diretamente
        print("Iniciando análise...")
        token_result = await token_agent.analyze(token_data)
        
        # Formatar para exibição
        print("\n== RESULTADO DA ANÁLISE ==")
        print(json.dumps(token_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Erro ao analisar Bitcoin: {str(e)}")

if __name__ == "__main__":
    # Executar a função assíncrona
    print("Iniciando teste de análise do Bitcoin...")
    asyncio.run(analyze_bitcoin())
    print("Teste concluído!") 