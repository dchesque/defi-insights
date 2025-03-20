-- Esquema de banco de dados para DeFi Insight
-- Execute este script no SQL Editor do Supabase

-- Configurações de segurança
ALTER DATABASE postgres SET timezone TO 'UTC-3';

-- Tabela de usuários (complementar à tabela auth.users do Supabase)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Tabela de análises de tokens
CREATE TABLE IF NOT EXISTS token_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol TEXT,
    address TEXT,
    chain TEXT,
    timeframe TEXT,
    analysis_type TEXT NOT NULL CHECK (analysis_type IN ('technical', 'sentiment', 'onchain')),
    indicators JSONB,
    signals JSONB,
    trend_analysis JSONB,
    support_resistance JSONB,
    overall_sentiment JSONB,
    sentiment_by_source JSONB,
    engagement_metrics JSONB,
    discussion_trends JSONB,
    holder_distribution JSONB,
    transaction_metrics JSONB,
    liquidity_analysis JSONB,
    risk_assessment JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índices para melhorar a performance das consultas
CREATE INDEX IF NOT EXISTS idx_token_analyses_user_id ON token_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_token_analyses_symbol ON token_analyses(symbol);
CREATE INDEX IF NOT EXISTS idx_token_analyses_type ON token_analyses(analysis_type);

-- Tabela de portfólios
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    tokens JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Índice para melhorar a performance das consultas
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id);

-- Tabela de preferências do usuário
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    theme TEXT DEFAULT 'light',
    notification_settings JSONB DEFAULT '{}'::jsonb,
    display_currency TEXT DEFAULT 'USD',
    default_analysis_type TEXT DEFAULT 'technical',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Função para atualizar o campo updated_at automaticamente
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar o campo updated_at automaticamente
CREATE TRIGGER update_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_token_analyses_timestamp
BEFORE UPDATE ON token_analyses
FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_portfolios_timestamp
BEFORE UPDATE ON portfolios
FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

CREATE TRIGGER update_user_preferences_timestamp
BEFORE UPDATE ON user_preferences
FOR EACH ROW EXECUTE PROCEDURE update_timestamp();

-- Permissões RLS (Row Level Security)
-- Habilita RLS em todas as tabelas
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE token_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Políticas de acesso para users
CREATE POLICY users_select_own ON users
    FOR SELECT USING (auth.uid() = id);
    
CREATE POLICY users_update_own ON users
    FOR UPDATE USING (auth.uid() = id);

-- Políticas de acesso para token_analyses
CREATE POLICY token_analyses_select_own ON token_analyses
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY token_analyses_insert_own ON token_analyses
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY token_analyses_update_own ON token_analyses
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY token_analyses_delete_own ON token_analyses
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas de acesso para portfolios
CREATE POLICY portfolios_select_own ON portfolios
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY portfolios_insert_own ON portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY portfolios_update_own ON portfolios
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY portfolios_delete_own ON portfolios
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas de acesso para user_preferences
CREATE POLICY user_preferences_select_own ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY user_preferences_insert_own ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY user_preferences_update_own ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- Trigger para criar preferências de usuário ao criar um novo usuário
CREATE OR REPLACE FUNCTION create_user_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_preferences (user_id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON users
FOR EACH ROW EXECUTE PROCEDURE create_user_preferences(); 