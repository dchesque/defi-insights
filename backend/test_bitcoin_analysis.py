import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Importar o TokenAgent
from src.agents.token_agent import TokenAgent

async def test_bitcoin_analysis():
    """
    Testa a análise do Bitcoin usando o TokenAgent diretamente.
    """
    print("\n🔍 Testando análise do Bitcoin...")
    print("===============================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Criar instância do TokenAgent
    token_agent = TokenAgent()
    
    # Dados do Bitcoin a partir da URL do CoinGecko
    token_data = {
        "url": "https://www.coingecko.com/en/coins/bitcoin"
    }
    
    print(f"\nRealizando análise para: {token_data['url']}")
    
    try:
        # Executar análise
        result = await token_agent.analyze(token_data)
        
        # Salvar resultado em arquivo JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bitcoin_analysis_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Análise concluída! Resultados salvos em {filename}")
        
        # Exibir resumo
        print("\n📊 Resumo da Análise:")
        print(f"Nome: {result.get('name')}")
        print(f"Símbolo: {result.get('symbol')}")
        print(f"Preço: ${result.get('price', {}).get('current'):,.2f}")
        print(f"Variação 24h: {result.get('price', {}).get('change_24h'):,.5f}%")
        print(f"Variação 7d: {result.get('price', {}).get('change_7d'):,.5f}%")
        print(f"Variação 30d: {result.get('price', {}).get('change_30d'):,.5f}%")
        print(f"Market Cap: ${result.get('market_data', {}).get('market_cap'):,.0f}")
        print(f"Volume 24h: ${result.get('market_data', {}).get('volume_24h'):,.0f}")
        print(f"Fornecimento Circulante: {result.get('market_data', {}).get('circulating_supply'):,.1f}")
        print(f"Fornecimento Total: {result.get('market_data', {}).get('total_supply'):,.1f}")
        print(f"Fornecimento Máximo: {result.get('market_data', {}).get('max_supply'):,.1f}")
        print(f"Rank: #{result.get('market_data', {}).get('rank')}")
        
        # Informações adicionais
        print("\nInformações Adicionais:")
        print(f"Categorias: {', '.join(result.get('additional_info', {}).get('categories', []))}")
        
    except Exception as e:
        print(f"\n❌ Erro ao realizar análise: {str(e)}")

if __name__ == "__main__":
    # Executar função assíncrona
    asyncio.run(test_bitcoin_analysis()) 