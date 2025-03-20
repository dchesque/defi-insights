# DeFi Insight Backend

Backend da plataforma DeFi Insight, um sistema avançado de análise de tokens cripto utilizando inteligência artificial.

## 🚀 Funcionalidades

O backend do DeFi Insight oferece três tipos principais de análise:

1. **Análise Técnica** - Indicadores como RSI, MACD, Bollinger Bands e médias móveis
2. **Análise de Sentimento** - Análise de redes sociais como Twitter, Reddit e Telegram
3. **Análise On-Chain** - Distribuição de holders, liquidez, transações e avaliação de riscos

Além disso, o backend oferece:

- Sistema completo de autenticação e autorização
- Gerenciamento de portfólios
- API RESTful documentada

## 🛠️ Tecnologias

- **FastAPI** - Framework web de alta performance
- **Supabase** - Banco de dados e autenticação
- **Python 3.8+** - Linguagem de programação
- **Pandas, NumPy, TA** - Bibliotecas para análise de dados
- **CCXT, Binance** - Integração com exchanges
- **Swagger/OpenAPI** - Documentação automática da API

## ⚙️ Estrutura do Projeto

```
backend/
│
├── src/                  # Código fonte principal
│   ├── api/              # Rotas da API
│   │   ├── routes/       # Endpoints
│   │   └── dependencies/ # Middlewares e dependências
│   │
│   ├── agents/           # Agentes de análise
│   │   ├── technical_agent.py
│   │   ├── sentiment_agent.py
│   │   └── onchain_agent.py
│   │
│   ├── core/             # Componentes principais
│   │   ├── base_agent.py
│   │   └── agent_manager.py
│   │
│   ├── integrations/     # Integrações externas
│   │   └── supabase.py
│   │
│   └── main.py           # Ponto de entrada da aplicação
│
├── scripts/              # Scripts utilitários
│   ├── database_schema.sql  # Schema do banco de dados
│   └── test_api.py       # Testes de API 
│
├── tests/                # Testes unitários e de integração
│
├── .env                  # Variáveis de ambiente (não versionado)
├── .env.example          # Exemplo de variáveis de ambiente
├── requirements.txt      # Dependências do projeto
├── setup.py              # Script de configuração inicial
└── start.py              # Script para iniciar o servidor
```

## 🔧 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip ou poetry
- Conta no Supabase
- (Opcional) Chaves API para os serviços externos

### Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/defi-insight.git
cd defi-insight/backend
```

2. Execute o script de setup:
```bash
python setup.py
```

3. Configure as variáveis de ambiente:
```bash
# Suas credenciais já estão no arquivo .env
# Edite para adicionar chaves de serviços externos se necessário
```

4. Configure o banco de dados no Supabase:
   - Acesse o console do Supabase
   - No SQL Editor, execute o script em `scripts/database_schema.sql`

## 🏃‍♂️ Executando o Servidor

Para iniciar o servidor de desenvolvimento:

```bash
# Usando o script de inicialização
python start.py

# Ou diretamente com uvicorn
uvicorn src.main:app --reload
```

A API estará disponível em:
- URL: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs

## 🔌 Uso da API

### Endpoints Principais

#### Autenticação
- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/token` - Obter token de acesso
- `GET /api/auth/me` - Obter dados do usuário atual

#### Análise Técnica
- `POST /api/analysis/technical` - Solicitar análise técnica
- `GET /api/analysis/technical/{id}` - Obter análise específica
- `GET /api/analysis/technical/user/{user_id}` - Listar análises do usuário

#### Análise de Sentimento
- `POST /api/sentiment` - Solicitar análise de sentimento
- `GET /api/sentiment/{id}` - Obter análise específica
- `GET /api/sentiment/user/{user_id}` - Listar análises do usuário

#### Análise On-Chain
- `POST /api/onchain` - Solicitar análise on-chain
- `GET /api/onchain/{id}` - Obter análise específica
- `GET /api/onchain/user/{user_id}` - Listar análises do usuário

#### Portfólio
- `POST /api/portfolio` - Criar portfólio
- `GET /api/portfolio/{id}` - Obter portfólio
- `PUT /api/portfolio/{id}` - Atualizar portfólio
- `DELETE /api/portfolio/{id}` - Excluir portfólio
- `GET /api/portfolio/user/{user_id}` - Listar portfólios do usuário

### Exemplo de Uso

Para solicitar uma análise técnica:

```bash
curl -X POST http://localhost:8000/api/analysis/technical \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC", "timeframe": "1d", "user_id": "seu-user-id"}'
```

## 🧪 Testes

Para executar testes automatizados:

```bash
# Testa todos os endpoints
python scripts/test_api.py

# Testa apenas um componente específico
python scripts/test_api.py --test technical
```

## 📝 Configuração Avançada

### Variáveis de Ambiente

As variáveis de ambiente são documentadas no arquivo [README_ENV.md](README_ENV.md).

### Escalabilidade

Para ambientes de produção, considere:

1. Configurar um servidor proxy como Nginx
2. Usar Gunicorn como servidor WSGI
3. Configurar cache para reduzir chamadas de API externas
4. Implementar rate limiting para evitar abuso da API

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia as diretrizes de contribuição antes de enviar uma PR.

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/awesome-feature`)
3. Commit suas mudanças (`git commit -m 'Add awesome feature'`)
4. Push para a branch (`git push origin feature/awesome-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes.

