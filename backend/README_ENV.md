# Configuração das Variáveis de Ambiente

Este documento contém instruções para configurar corretamente o arquivo `.env` para a API DeFi Insight.

## Requisitos

Antes de começar, você precisará criar contas e obter chaves API para os seguintes serviços:

1. [Supabase](https://supabase.com/) - Banco de dados e autenticação
2. [CoinGecko](https://www.coingecko.com/en/api) - Dados de mercado de criptomoedas
3. [Binance](https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072) - Dados de trading
4. [Twitter](https://developer.twitter.com/en/docs/twitter-api) - Análise de sentimento
5. [Reddit](https://www.reddit.com/dev/api/) - Análise de sentimento
6. [Telegram](https://core.telegram.org/api/obtaining_api_id) - Análise de sentimento
7. [Etherscan](https://etherscan.io/apis) - Dados on-chain para Ethereum
8. [BSCScan](https://bscscan.com/apis) - Dados on-chain para Binance Smart Chain
9. [Covalent](https://www.covalenthq.com/docs/api/) - Dados on-chain multichain
10. [Moralis](https://moralis.io/) - Dados on-chain e NFTs
11. [OpenAI](https://platform.openai.com/) - NLP e análise avançada
12. [HuggingFace](https://huggingface.co/inference-api) - Modelos de ML alternativos

## Instruções de Configuração

### Supabase

1. Crie uma conta no [Supabase](https://supabase.com/)
2. Crie um novo projeto
3. Vá para "Project Settings" > "API"
4. Copie a "URL" e a "anon public" key para as variáveis:
   ```
   SUPABASE_URL=sua_url_do_supabase
   SUPABASE_KEY=sua_chave_do_supabase
   ```

### Configurações de Segurança

1. Gere uma chave secreta forte para JWT:
   ```
   JWT_SECRET_KEY=chave_secreta_aleatoria_e_segura
   ```
   Você pode usar Python para gerar uma chave:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

### APIs de Dados de Mercado

#### CoinGecko
1. Registre-se para [CoinGecko API](https://www.coingecko.com/en/api/pricing)
2. Obtenha e adicione sua chave:
   ```
   COINGECKO_API_KEY=sua_chave_coingecko
   ```

#### Binance
1. Crie uma conta na [Binance](https://www.binance.com/)
2. Vá para "API Management" e crie uma nova API key
3. Adicione ao arquivo:
   ```
   BINANCE_API_KEY=sua_chave_binance
   BINANCE_API_SECRET=seu_secret_binance
   ```

### APIs de Dados Sociais

#### Twitter
1. Crie uma conta no [Twitter Developer Portal](https://developer.twitter.com/)
2. Crie um projeto e um aplicativo
3. Obtenha as credenciais:
   ```
   TWITTER_API_KEY=sua_chave_twitter
   TWITTER_API_SECRET=seu_secret_twitter
   ```

#### Reddit
1. Acesse [Reddit Preferences > Apps](https://www.reddit.com/prefs/apps)
2. Crie um novo aplicativo e obtenha as credenciais:
   ```
   REDDIT_CLIENT_ID=seu_client_id_reddit
   REDDIT_CLIENT_SECRET=seu_client_secret_reddit
   ```

#### Telegram
1. Acesse [my.telegram.org/apps](https://my.telegram.org/apps)
2. Crie um novo aplicativo
3. Adicione ao arquivo:
   ```
   TELEGRAM_API_ID=seu_api_id_telegram
   TELEGRAM_API_HASH=seu_api_hash_telegram
   ```

### APIs de Dados On-Chain

#### Etherscan
1. Crie uma conta no [Etherscan](https://etherscan.io/)
2. Vá para "API Keys" e crie uma nova chave
3. Adicione ao arquivo:
   ```
   ETHERSCAN_API_KEY=sua_chave_etherscan
   ```

#### BSCScan
1. Crie uma conta no [BSCScan](https://bscscan.com/)
2. Vá para "API Keys" e crie uma nova chave
3. Adicione ao arquivo:
   ```
   BSCSCAN_API_KEY=sua_chave_bscscan
   ```

#### Covalent
1. Registre-se na [Covalent](https://www.covalenthq.com/)
2. Obtenha sua chave API:
   ```
   COVALENT_API_KEY=sua_chave_covalent
   ```

#### Moralis
1. Crie uma conta no [Moralis](https://moralis.io/)
2. Crie um novo servidor e obtenha sua chave API:
   ```
   MORALIS_API_KEY=sua_chave_moralis
   ```

### Configurações de NLP e IA

#### OpenAI
1. Crie uma conta no [OpenAI](https://platform.openai.com/)
2. Vá para "API keys" e crie uma nova chave:
   ```
   OPENAI_API_KEY=sua_chave_openai
   ```

#### HuggingFace
1. Crie uma conta no [HuggingFace](https://huggingface.co/)
2. Vá para "Settings" > "Access Tokens" e crie um novo token:
   ```
   HUGGINGFACE_API_KEY=seu_token_huggingface
   ```

## Observações Importantes

- Nunca compartilhe seu arquivo `.env` ou exponha suas chaves de API publicamente
- Para desenvolvimento local, você pode não precisar de todas as APIs acima
- No ambiente de produção, use variáveis de ambiente do servidor em vez de um arquivo `.env`
- Mantenha suas chaves com as permissões mínimas necessárias para garantir a segurança

## Exemplo de uso no código

Para usar uma variável de ambiente no código:

```python
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Acessa a variável
api_key = os.getenv("OPENAI_API_KEY") 