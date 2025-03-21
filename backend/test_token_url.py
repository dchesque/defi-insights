import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Importar o TokenAgent
from src.agents.token_agent import TokenAgent

async def test_token_url_analysis():
    """
    Testa a análise de tokens usando URLs de diferentes fontes.
    """
    print("\n🔍 Testando análise de múltiplas URLs...")
    print("=====================================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Lista de URLs para teste
    test_urls = [
        # CoinGecko URLs
        {"name": "Bitcoin (CoinGecko)", "url": "https://www.coingecko.com/en/coins/bitcoin"},
        {"name": "Ethereum (CoinGecko)", "url": "https://www.coingecko.com/en/coins/ethereum"},
        
        # CoinMarketCap URLs
        {"name": "Bitcoin (CMC)", "url": "https://coinmarketcap.com/currencies/bitcoin/"},
        {"name": "Ethereum (CMC)", "url": "https://coinmarketcap.com/currencies/ethereum/"},
        
        # Adicional CoinGecko URLs
        {"name": "Solana (CoinGecko)", "url": "https://www.coingecko.com/en/coins/solana"},
        {"name": "Cardano (CoinGecko)", "url": "https://www.coingecko.com/en/coins/cardano"}
    ]
    
    # Criar instância do TokenAgent
    token_agent = TokenAgent()
    
    # Resultados
    results = []
    
    # Testar cada URL
    for test in test_urls:
        print(f"\nAnalisando: {test['name']} - {test['url']}")
        
        try:
            # Preparar dados
            token_data = {"url": test['url']}
            
            # Executar análise
            result = await token_agent.analyze(token_data)
            
            # Verificar se obtivemos dados válidos
            valid = "error" not in result
            
            # Exibir resumo
            if valid:
                print(f"✅ Análise concluída com sucesso!")
                print(f"   ID: {result.get('id', 'N/A')}")
                print(f"   Source: {result.get('source', 'N/A')}")
                print(f"   Nome: {result.get('name')}")
                print(f"   Símbolo: {result.get('symbol')}")
                print(f"   Preço: ${result.get('price', {}).get('current'):,.2f}")
                print(f"   Rank: #{result.get('market_data', {}).get('rank')}")
            else:
                print(f"❌ Erro: {result.get('error')}")
            
            # Adicionar ao resumo
            results.append({
                "name": test['name'],
                "url": test['url'],
                "valid": valid,
                "data": result if valid else {"error": result.get("error")}
            })
            
        except Exception as e:
            print(f"❌ Exceção: {str(e)}")
            results.append({
                "name": test['name'],
                "url": test['url'],
                "valid": False,
                "data": {"error": str(e)}
            })
    
    # Salvar resultados em arquivo JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"token_url_analysis_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resultados completos salvos em {filename}")
    
    # Resumo final
    print("\n📊 Resumo Final:")
    print("================")
    
    success_count = sum(1 for r in results if r["valid"])
    print(f"Total de tokens testados: {len(results)}")
    print(f"Sucessos: {success_count}")
    print(f"Falhas: {len(results) - success_count}")
    
    if success_count == len(results):
        print("\n✅ Todos os testes foram bem-sucedidos!")
    else:
        print("\n⚠️ Alguns testes falharam.")

if __name__ == "__main__":
    # Executar função assíncrona
    asyncio.run(test_token_url_analysis()) 