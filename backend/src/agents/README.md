# Agentes de Análise DeFi Insight

Este diretório contém os agentes especializados responsáveis pelas diferentes análises de tokens na plataforma DeFi Insight.

## Arquitetura dos Agentes

Todos os agentes herdam da classe base `BaseAgent` definida em `src/core/base_agent.py`. A arquitetura segue o padrão de design Strategy, permitindo que novos tipos de análise sejam facilmente adicionados ao sistema.

### Características Comuns

Cada agente implementa pelo menos os seguintes métodos:

- `validate_input()`: Verifica se os dados de entrada são válidos
- `analyze()`: Método principal que realiza a análise e retorna os resultados
- `_fetch_data()`: Obtém dados necessários para a análise
- Métodos auxiliares específicos de cada agente

## Agentes Disponíveis

### TechnicalAgent

Localização: `technical_agent.py`

Realiza análise técnica de tokens com base em dados históricos de preço, calculando vários indicadores técnicos.

**Indicadores calculados:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bandas de Bollinger
- Médias Móveis (SMA, EMA)
- Volume médio
- Suportes e resistências
- Tendências de preço

### SentimentAgent

Localização: `sentiment_agent.py`

Analisa o sentimento do mercado em relação a um token específico, baseado em dados de redes sociais e comunidades.

**Fontes analisadas:**
- Twitter/X
- Reddit
- Telegram
- Discord
- Fóruns especializados

**Métricas:**
- Sentimento geral (positivo, neutro, negativo)
- Nível de engajamento
- Tendências de discussão
- Sentimento por fonte
- Mudança de sentimento ao longo do tempo

### OnchainAgent

Localização: `onchain_agent.py`

Analisa dados on-chain de tokens, fornecendo insights sobre transações, distribuição de tokens e atividade.

**Elementos analisados:**
- Distribuição de holders
- Concentração de tokens (top 10, 50, 100 endereços)
- Análise de liquidez em DEXs
- Volume de transações
- Classificação por tipo de holder (indivíduos, exchanges, contratos)
- Identificação de riscos on-chain

## Como implementar um novo agente

Para adicionar um novo agente de análise:

1. Crie um novo arquivo Python neste diretório (ex: `new_agent.py`)
2. Importe e herde da classe `BaseAgent`
3. Implemente o método `analyze()` e outros métodos específicos necessários
4. Registre o agente no `AgentManager` em `src/main.py`

Exemplo de estrutura para um novo agente:

```python
from core.base_agent import BaseAgent

class NewAgent(BaseAgent):
    """Agente para um novo tipo de análise"""
    
    async def validate_input(self, token_data: dict) -> bool:
        """Validar entrada de dados"""
        # Implementação da validação
        return True
        
    async def analyze(self, token_data: dict) -> dict:
        """Realizar a análise"""
        # Implementação da análise
        results = await self._process_data(token_data)
        return results
        
    async def _fetch_specialized_data(self, token_data: dict) -> dict:
        """Buscar dados específicos para este tipo de análise"""
        # Implementação da busca de dados
        return data
```

## Integração com o sistema

Depois de criar um novo agente, você precisará:

1. Registrá-lo no `AgentManager` em `src/main.py`
2. Criar endpoints API correspondentes em `src/api/routes/`
3. Definir modelos de entrada/saída para os endpoints
4. Atualizar a documentação

Veja os outros agentes existentes como exemplos de implementação completa. 