import asyncio
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("integration_tester")

# Importar integrações
from src.integrations.coingecko import CoinGeckoClient
from src.integrations.telegram import telegram_client
from src.integrations.blockchain_explorer import blockchain_explorer

async def test_integrations():
    """
    Testa a conexão com todas as integrações e exibe resultados.
    """
    print("\n🔌 Testando conexão com todas as integrações...")
    print("=============================================")
    
    results = {}
    
    # Testar CoinGecko
    print("\n1. Testando CoinGecko API...")
    try:
        coingecko = CoinGeckoClient()
        coingecko_status = await coingecko.ping()
        results["coingecko"] = coingecko_status
        status_text = "✅ Online" if coingecko_status else "❌ Offline"
        print(f"   Status: {status_text}")
        
        if coingecko_status:
            # Testar busca básica
            btc_price = await coingecko.get_coin_price(["bitcoin"], ["usd"])
            if btc_price and "bitcoin" in btc_price:
                print(f"   Bitcoin price: ${btc_price['bitcoin']['usd']:,.2f}")
            
            # Testar busca de dados de moeda
            global_data = await coingecko.get_global_data()
            active_coins = global_data.get("active_cryptocurrencies", 0)
            print(f"   Total de criptomoedas ativas: {active_coins:,}")
    except Exception as e:
        results["coingecko"] = False
        print(f"   Erro: {str(e)}")
    
    # Testar Telegram
    print("\n2. Testando Telegram Web Scraping...")
    try:
        telegram_status = await telegram_client.check_connection()
        results["telegram"] = telegram_status
        status_text = "✅ Online" if telegram_status else "❌ Offline"
        print(f"   Status: {status_text}")
        
        if telegram_status:
            # Testar busca em canais
            messages = await telegram_client.get_channel_messages("binance_announcements", limit=3)
            print(f"   Mensagens recentes encontradas: {len(messages)}")
            if messages:
                print(f"   Exemplo: {messages[0].get('text', '')[:100]}...")
    except Exception as e:
        results["telegram"] = False
        print(f"   Erro: {str(e)}")
    
    # Testar Blockchain Explorer
    print("\n3. Testando Blockchain Explorer...")
    try:
        blockchain_status = await blockchain_explorer.check_connection()
        results["blockchain_explorer"] = blockchain_status
        status_text = "✅ Online" if blockchain_status else "❌ Offline"
        print(f"   Status: {status_text}")
        
        if blockchain_status:
            # Testar busca de endereço
            # Endereço da carteira da Binance
            address_info = await blockchain_explorer.get_address_info("0x28C6c06298d514Db089934071355E5743bf21d60", "eth")
            print(f"   Binance wallet balance: {address_info.get('balance', 'N/A')}")
    except Exception as e:
        results["blockchain_explorer"] = False
        print(f"   Erro: {str(e)}")
    
    # Resumo
    print("\n📋 Resumo do status das integrações:")
    print("=================================")
    all_ok = True
    
    for integration, status in results.items():
        status_text = "✅ Online" if status else "❌ Offline"
        print(f"{integration}: {status_text}")
        if not status:
            all_ok = False
    
    if all_ok:
        print("\n✅ Todas as integrações estão funcionando corretamente!")
    else:
        print("\n⚠️ Algumas integrações apresentaram problemas!")
    
    return results

if __name__ == "__main__":
    print("🧪 Teste de Integrações DeFi Insight")
    print("===================================")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        results = asyncio.run(test_integrations())
        print("\nTeste concluído!")
    except Exception as e:
        print(f"\n❌ Erro ao executar testes: {str(e)}") 