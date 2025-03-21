import asyncio
import json
import uuid
from datetime import datetime
import logging
from typing import Dict, Any, List, Optional
import os
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("full_analysis_test")

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar agentes e integrações
from src.agents.token_agent import TokenAgent
from src.agents.sentiment_agent import SentimentAgent
from src.agents.onchain_agent import OnchainAgent
from src.integrations.coingecko import CoinGeckoClient
from src.integrations.telegram import telegram_client
from src.integrations.blockchain_explorer import blockchain_explorer

class FullAnalysisTester:
    """
    Tester que executa uma análise completa utilizando todos os agentes e integrações.
    """
    
    def __init__(self):
        """
        Inicializa o tester com todos os agentes e clientes necessários.
        """
        logger.info("Inicializando tester de análise completa")
        self.token_agent = TokenAgent()
        self.sentiment_agent = SentimentAgent()
        self.onchain_agent = OnchainAgent()
        self.coingecko = CoinGeckoClient()
        
    async def run_full_analysis(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma análise completa de um token utilizando todos os agentes.
        
        Args:
            token_data: Dados do token para análise (URL, símbolo ou endereço)
            
        Returns:
            Resultado completo da análise
        """
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        logger.info(f"Iniciando análise completa para: {token_data}")
        results = {
            "analysis_id": analysis_id,
            "timestamp": timestamp,
            "token_data": token_data,
            "status": "pending",
            "validation": {},
            "token_analysis": {},
            "sentiment_analysis": {},
            "onchain_analysis": {},
            "integrations_status": {},
            "errors": []
        }
        
        # 1. Validar os dados de entrada
        logger.info("Validando dados de entrada")
        token_valid = await self.token_agent.validate_input(token_data)
        sentiment_valid = await self.sentiment_agent.validate_input(token_data)
        onchain_valid = await self.onchain_agent.validate_input(token_data)
        
        results["validation"] = {
            "token_agent": token_valid,
            "sentiment_agent": sentiment_valid,
            "onchain_agent": onchain_valid,
            "overall": token_valid and sentiment_valid and onchain_valid
        }
        
        if not token_valid:
            error_msg = "Dados de token inválidos para o TokenAgent"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        # 2. Executar análise básica do token
        logger.info("Executando análise básica do token")
        try:
            token_analysis = await self.token_agent.analyze(token_data)
            results["token_analysis"] = token_analysis
            
            if "error" in token_analysis:
                results["errors"].append(f"Erro na análise do token: {token_analysis['error']}")
                logger.error(f"Erro na análise do token: {token_analysis['error']}")
        except Exception as e:
            error_msg = f"Exceção na análise do token: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        # 3. Executar análise de sentimento
        if sentiment_valid:
            logger.info("Executando análise de sentimento")
            try:
                # Usar o símbolo e nome do token da análise base, se disponível
                if "error" not in results["token_analysis"]:
                    token_data["symbol"] = results["token_analysis"].get("symbol")
                    token_data["name"] = results["token_analysis"].get("name")
                
                sentiment_analysis = await self.sentiment_agent.analyze(token_data)
                results["sentiment_analysis"] = sentiment_analysis
                
                if "error" in sentiment_analysis:
                    results["errors"].append(f"Erro na análise de sentimento: {sentiment_analysis['error']}")
                    logger.error(f"Erro na análise de sentimento: {sentiment_analysis['error']}")
            except Exception as e:
                error_msg = f"Exceção na análise de sentimento: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # 4. Executar análise on-chain
        if onchain_valid:
            logger.info("Executando análise on-chain")
            try:
                # Tentar obter o endereço do contrato a partir da análise do token
                if "error" not in results["token_analysis"] and not token_data.get("address"):
                    blockchain_explorers = results["token_analysis"].get("additional_info", {}).get("blockchain_explorers", [])
                    if blockchain_explorers and len(blockchain_explorers) > 0:
                        for explorer in blockchain_explorers:
                            if explorer and "0x" in explorer:
                                address = explorer.split("/")[-1]
                                if address.startswith("0x"):
                                    token_data["address"] = address
                                    token_data["chain"] = "ethereum"  # Assumir ethereum por padrão
                                    break
                
                onchain_analysis = await self.onchain_agent.analyze(token_data)
                results["onchain_analysis"] = onchain_analysis
                
                if "error" in onchain_analysis:
                    results["errors"].append(f"Erro na análise on-chain: {onchain_analysis['error']}")
                    logger.error(f"Erro na análise on-chain: {onchain_analysis['error']}")
            except Exception as e:
                error_msg = f"Exceção na análise on-chain: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # 5. Verificar status das integrações
        logger.info("Verificando status das integrações")
        try:
            results["integrations_status"] = {
                "coingecko": await self.coingecko.ping(),
                "telegram": await telegram_client.check_connection(),
                "blockchain_explorer": await blockchain_explorer.check_connection()
            }
            
            # Registrar erros de integrações que falharam
            for integration, status in results["integrations_status"].items():
                if not status:
                    results["errors"].append(f"Integração {integration} não está disponível")
                    logger.error(f"Integração {integration} não está disponível")
        except Exception as e:
            error_msg = f"Erro ao verificar integrações: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        # 6. Finalizar e definir status
        if len(results["errors"]) == 0:
            results["status"] = "success"
        elif len(results["errors"]) < 3:  # Se tivermos poucos erros, considerar parcial
            results["status"] = "partial"
        else:
            results["status"] = "failed"
        
        logger.info(f"Análise completa finalizada com status: {results['status']}")
        return results

async def main():
    """
    Função principal para executar os testes.
    """
    print("🧪 Teste de Análise Completa do DeFi Insight")
    print("===========================================")
    
    # Opções de tokens para teste
    test_tokens = [
        {"name": "Bitcoin", "url": "https://www.coingecko.com/en/coins/bitcoin"},
        {"name": "Ethereum", "url": "https://www.coingecko.com/en/coins/ethereum"},
        {"name": "Solana", "url": "https://www.coingecko.com/en/coins/solana"},
        {"name": "Arbitrum", "url": "https://www.coingecko.com/en/coins/arbitrum"},
        {"name": "Cardano", "url": "https://www.coingecko.com/en/coins/cardano"}
    ]
    
    # Mostrar opções para o usuário
    print("\nEscolha um token para análise:")
    for i, token in enumerate(test_tokens):
        print(f"{i+1}. {token['name']}")
    print(f"{len(test_tokens)+1}. Outro (fornecer URL)")
    
    # Obter escolha do usuário
    while True:
        try:
            choice = input("\nDigite o número da opção (ou q para sair): ")
            if choice.lower() == 'q':
                print("Saindo...")
                return
                
            choice = int(choice)
            if 1 <= choice <= len(test_tokens):
                token_data = {"url": test_tokens[choice-1]["url"]}
                break
            elif choice == len(test_tokens)+1:
                url = input("Digite a URL do token (CoinGecko ou CoinMarketCap): ")
                token_data = {"url": url}
                break
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")
    
    # Iniciar análise
    tester = FullAnalysisTester()
    print(f"\n🔍 Iniciando análise completa para {token_data['url']}...")
    
    try:
        # Executar a análise
        results = await tester.run_full_analysis(token_data)
        
        # Salvar resultados em arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_results_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Análise concluída! Resultados salvos em {filename}")
        
        # Exibir resumo
        print("\n📊 Resumo da Análise:")
        print(f"Status: {results['status']}")
        
        if results["token_analysis"] and "error" not in results["token_analysis"]:
            token = results["token_analysis"]
            print(f"\nToken: {token.get('name')} ({token.get('symbol')})")
            print(f"Preço: ${token.get('price', {}).get('current'):,.2f}")
            print(f"Mudança 24h: {token.get('price', {}).get('change_24h'):,.2f}%")
            print(f"Rank: #{token.get('market_data', {}).get('rank')}")
        
        if results["sentiment_analysis"] and "error" not in results["sentiment_analysis"]:
            sentiment = results["sentiment_analysis"]
            sentiment_value = sentiment.get("sentiment_score", 0)
            print(f"\nSentimento: {sentiment.get('sentiment_label')} ({sentiment_value:,.2f})")
            print(f"Menções: {sentiment.get('mentions', 0)}")
        
        if results["onchain_analysis"] and "error" not in results["onchain_analysis"]:
            onchain = results["onchain_analysis"]
            print(f"\nDados On-chain:")
            print(f"Transações: {onchain.get('transactions_count', 'N/A')}")
            print(f"Holders: {onchain.get('holders_count', 'N/A')}")
        
        # Exibir status das integrações
        print("\nStatus das Integrações:")
        for integration, status in results["integrations_status"].items():
            status_text = "✅ Conectado" if status else "❌ Falha"
            print(f"{integration}: {status_text}")
        
        # Exibir erros, se houver
        if results["errors"]:
            print("\n⚠️ Erros encontrados:")
            for error in results["errors"]:
                print(f"- {error}")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar a análise: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 