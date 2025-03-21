# Guia de Integração do Frontend com o Backend DeFi Insight

## 1. Requisitos Iniciais

- Node.js (versão 16 ou superior)
- npm ou yarn
- Backend DeFi Insight em execução (porta 8000)

## 2. Configuração do Ambiente Frontend

### 2.1 Configuração de Variáveis de Ambiente

Crie um arquivo `.env.local` na raiz do diretório `frontend` com as seguintes variáveis:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para ambientes de produção, altere para a URL do servidor backend.

### 2.2 Instalação de Dependências

```bash
cd frontend
npm install
# ou
yarn install
```

## 3. Estrutura da Comunicação com a API

### 3.1 Serviço de API

O projeto utiliza o arquivo `frontend/src/services/api.ts` para todas as comunicações com o backend. Este serviço:

- Gerencia autenticação via token JWT
- Lida com renovação automática de tokens expirados
- Formata erros de forma consistente
- Implementa interceptores para adicionar headers de autenticação

### 3.2 Formato de Resposta da API

Todas as respostas do backend seguem o padrão:

```typescript
{
  success: boolean;
  message: string;
  data: T; // Dados específicos do endpoint
  timestamp: string;
  request_id: string;
  metadata?: any; // Opcional
}
```

### 3.3 Hooks React Especializados

Utilize os hooks personalizados para interagir com a API:

- `useAuth`: Gerencia autenticação (login, registro, logout)
- `useTokenAnalysis`: Análise de tokens
- `usePortfolio`: Gerenciamento de portfólio

## 4. Autenticação e Autorização

### 4.1 Fluxo de Autenticação

1. Usuário faz login via `useAuth().login()`
2. Token JWT é armazenado no localStorage
3. Token é automaticamente incluído nas requisições subsequentes
4. Tokens expirados são renovados automaticamente

### 4.2 Proteção de Rotas

O arquivo `frontend/middleware.ts` protege rotas autenticadas. Rotas protegidas incluem:
- `/dashboard/*`
- `/portfolio/*`
- `/analysis/*`
- `/settings/*`

## 5. Integrando com Endpoints Específicos

### 5.1 Análise de Tokens

```typescript
// Exemplo de uso do hook de análise de tokens
import { useTokenAnalysis } from '../hooks/useTokenAnalysis';

function TokenAnalysisComponent() {
  const { analyzeToken, loading, error, analysis } = useTokenAnalysis();
  
  const handleAnalyze = async () => {
    // Análise por símbolo
    await analyzeToken('BTC');
    
    // Ou análise por URL
    await analyzeToken('https://www.coingecko.com/en/coins/bitcoin');
    
    // Com opções adicionais
    await analyzeToken('ETH', { 
      includeOnchain: true,
      includeSentiment: true
    });
  };
  
  // Renderização do componente...
}
```

### 5.2 Gerenciamento de Portfólio

```typescript
// Exemplo de uso do hook de portfólio
import { usePortfolio } from '../hooks/usePortfolio';

function PortfolioComponent() {
  const { 
    getUserPortfolios, 
    createPortfolio, 
    addToken,
    portfolios
  } = usePortfolio();
  
  // Buscar portfólios do usuário
  useEffect(() => {
    getUserPortfolios();
  }, [getUserPortfolios]);
  
  // Adicionar token a um portfólio
  const handleAddToken = async (portfolioId) => {
    await addToken(portfolioId, {
      symbol: 'BTC',
      amount: 0.5,
      purchase_price: 50000,
      purchase_date: new Date().toISOString()
    });
  };
  
  // Renderização do componente...
}
```

## 6. Tratamento de Erros

O serviço `api.ts` padroniza os erros da API. Use o padrão:

```typescript
try {
  await analyzeToken('BTC');
} catch (error) {
  // error contém: 
  // - message: mensagem de erro amigável
  // - error_code: código de erro (opcional)
  // - details: detalhes adicionais (opcional)
  console.error('Erro:', error.message);
}
```

## 7. Tipagem

Use os tipos definidos em `frontend/src/types/models.ts` para garantir consistência de dados:

```typescript
import { TokenAnalysis, Portfolio } from '../types/models';

// Exemplo de uso da tipagem
const renderAnalysis = (analysis: TokenAnalysis) => {
  return (
    <div>
      <h2>{analysis.name} ({analysis.symbol})</h2>
      <p>Preço: ${analysis.price?.current}</p>
    </div>
  );
};
```

## 8. Testes de Integração

Antes de implementar novas funcionalidades, verifique:

1. Se você consegue fazer login/registro
2. Se tokens de autenticação são corretamente gerenciados
3. Se chamadas à API funcionam para endpoints principais
4. Se o CORS está configurado corretamente

## 9. Solução de Problemas Comuns

### 9.1 Erro de CORS

**Problema**: Erros de CORS no console do navegador

**Solução**: Verifique se a origem do frontend está na lista `CORS_ORIGINS` no backend (.env)

### 9.2 Problemas de Autenticação

**Problema**: Redirecionamentos inesperados para página de login

**Solução**: 
- Verifique se o token está sendo armazenado corretamente
- Confirme que o token não expirou
- Verifique se o middleware está configurado corretamente

### 9.3 Erros de Tipagem

**Problema**: Erros de tipo no TypeScript

**Solução**: Verifique se o modelo de dados do frontend está consistente com as respostas da API

## 10. Endpoints Disponíveis

| Endpoint | Descrição | Hook Relacionado |
|----------|-----------|------------------|
| `/api/auth/token` | Login/obtenção de token | `useAuth` |
| `/api/auth/register` | Registro de usuário | `useAuth` |
| `/api/auth/me` | Informações do usuário atual | `useAuth` |
| `/api/analysis` | Análise técnica de tokens | `useTokenAnalysis` |
| `/api/sentiment` | Análise de sentimento | `useTokenAnalysis` |
| `/api/onchain` | Análise on-chain | `useTokenAnalysis` |
| `/api/portfolio` | Gerenciamento de portfólio | `usePortfolio` |

Este guia cobre os aspectos essenciais para integrar o frontend Next.js com o backend FastAPI do DeFi Insight. Para questões específicas não cobertas, consulte a documentação do projeto ou entre em contato com a equipe de desenvolvimento.