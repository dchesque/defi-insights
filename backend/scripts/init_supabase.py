#!/usr/bin/env python
"""
Script para verificar e inicializar a configuração do Supabase.
Verifica a conexão, tabelas e permissões.
"""
import os
import sys
import asyncio
import argparse
from dotenv import load_dotenv

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.integrations.supabase import SupabaseClient
except ImportError:
    print("❌ Erro ao importar módulos do backend. Verifique se o caminho está correto.")
    sys.exit(1)

def parse_args():
    """Analisa os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description="Inicializa e verifica configuração do Supabase")
    parser.add_argument("--check-only", action="store_true", 
                        help="Apenas verificar a configuração sem tentar criar tabelas")
    parser.add_argument("--create-tables", action="store_true",
                        help="Criar tabelas conforme definido no schema")
    parser.add_argument("--verbose", action="store_true",
                        help="Exibir informações detalhadas")
    return parser.parse_args()

async def check_supabase_connection(client):
    """Verifica a conexão com o Supabase"""
    print("\n🔍 Verificando conexão com Supabase...")
    
    try:
        # Tenta buscar a hora atual do servidor
        result = await client.execute_query("SELECT NOW();")
        
        if result and len(result) > 0:
            print(f"✅ Conexão com Supabase estabelecida com sucesso!")
            print(f"   Hora do servidor: {result[0]['now']}")
            return True
        else:
            print("❌ Falha ao conectar ao Supabase: resposta vazia")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {str(e)}")
        return False

async def check_tables(client, verbose=False):
    """Verifica se as tabelas necessárias existem"""
    print("\n🔍 Verificando tabelas no Supabase...")
    
    required_tables = [
        "users",
        "token_analyses",
        "sentiment_analyses",
        "onchain_analyses",
        "portfolios",
        "portfolio_tokens",
        "user_preferences"
    ]
    
    try:
        # Busca todas as tabelas públicas
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
        """
        
        result = await client.execute_query(query)
        
        if not result:
            print("❌ Não foi possível obter a lista de tabelas")
            return False
        
        # Extrai nomes das tabelas
        existing_tables = [row["table_name"] for row in result]
        
        if verbose:
            print(f"📋 Tabelas encontradas: {', '.join(existing_tables)}")
        
        # Verifica quais tabelas obrigatórias estão ausentes
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"⚠️ Tabelas ausentes: {', '.join(missing_tables)}")
            return False
        else:
            print("✅ Todas as tabelas necessárias estão presentes!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {str(e)}")
        return False

async def check_row_level_security(client, verbose=False):
    """Verifica se RLS (Row Level Security) está habilitado para tabelas importantes"""
    print("\n🔍 Verificando Row Level Security (RLS)...")
    
    security_tables = [
        "users",
        "token_analyses",
        "sentiment_analyses",
        "onchain_analyses",
        "portfolios"
    ]
    
    try:
        query = """
        SELECT tablename, rowsecurity
        FROM pg_tables
        WHERE schemaname = 'public' AND tablename = ANY($1);
        """
        
        result = await client.execute_query(query, params=[security_tables])
        
        if not result:
            print("❌ Não foi possível verificar as políticas de segurança")
            return False
        
        # Verifica cada tabela
        tables_without_rls = []
        for row in result:
            if not row["rowsecurity"]:
                tables_without_rls.append(row["tablename"])
        
        if tables_without_rls:
            print(f"⚠️ Tabelas sem RLS ativado: {', '.join(tables_without_rls)}")
            return False
        else:
            print("✅ Row Level Security está ativado para todas as tabelas importantes!")
            return True
                    
    except Exception as e:
        print(f"❌ Erro ao verificar Row Level Security: {str(e)}")
        return False

async def check_policies(client, verbose=False):
    """Verifica políticas RLS existentes"""
    print("\n🔍 Verificando políticas de segurança...")
    
    try:
        query = """
        SELECT tablename, policyname, permissive, cmd, qual
        FROM pg_policies
        WHERE schemaname = 'public';
        """
        
        result = await client.execute_query(query)
        
        if not result:
            print("⚠️ Nenhuma política de segurança encontrada")
            return False
        
        # Conta políticas por tabela
        policy_count = {}
        for row in result:
            table = row["tablename"]
            if table not in policy_count:
                policy_count[table] = 0
            policy_count[table] += 1
        
        if verbose:
            print("\n📋 Políticas de segurança encontradas:")
            for row in result:
                cmd_map = {"r": "SELECT", "a": "INSERT", "w": "UPDATE", "d": "DELETE"}
                cmd = cmd_map.get(row["cmd"], row["cmd"])
                print(f"  - {row['tablename']}: {row['policyname']} ({cmd})")
        
        print(f"✅ Total de {len(result)} políticas distribuídas em {len(policy_count)} tabelas")
        return True
                    
    except Exception as e:
        print(f"❌ Erro ao verificar políticas: {str(e)}")
        return False

async def create_tables(client):
    """Cria tabelas conforme o schema definido"""
    print("\n🔧 Criando tabelas no Supabase...")
    
    # Caminho para o arquivo SQL
    sql_file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts",
        "database_schema.sql"
    )
    
    if not os.path.exists(sql_file_path):
        print(f"❌ Arquivo SQL não encontrado: {sql_file_path}")
        return False
    
    try:
        # Lê o conteúdo do arquivo SQL
        with open(sql_file_path, "r") as f:
            sql_content = f.read()
        
        # Divide em instruções individuais (divisão simplificada)
        # Para um parser mais robusto, considere usar uma biblioteca SQL
        sql_statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        # Executa cada instrução
        success_count = 0
        total_statements = len(sql_statements)
        
        for i, statement in enumerate(sql_statements):
            try:
                await client.execute_query(statement)
                success_count += 1
                print(f"✅ Executado com sucesso ({i+1}/{total_statements})")
            except Exception as e:
                print(f"⚠️ Erro na instrução {i+1}: {str(e)}")
        
        print(f"\n🔧 Execução concluída: {success_count}/{total_statements} instruções com sucesso")
        return success_count > 0
                    
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {str(e)}")
        return False

async def run_checks(args):
    """Executa as verificações conforme configuração"""
    print("🚀 Iniciando verificação do Supabase para DeFi Insight")
    
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Verifica variáveis de ambiente
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY devem ser definidas")
        return
    
    # Inicializa cliente Supabase
    try:
        client = SupabaseClient(supabase_url, supabase_key)
    except Exception as e:
        print(f"❌ Erro ao inicializar cliente Supabase: {str(e)}")
        return
    
    # Verifica conexão
    connection_ok = await check_supabase_connection(client)
    if not connection_ok:
        print("\n❌ Falha na conexão com Supabase. Verifique suas credenciais.")
        return
    
    # Verifica tabelas
    tables_ok = await check_tables(client, args.verbose)
    
    # Se deve criar tabelas
    if not tables_ok and args.create_tables:
        print("\n🔧 Tentando criar tabelas faltantes...")
        await create_tables(client)
        # Verifica novamente
        tables_ok = await check_tables(client, args.verbose)
    
    # Se tem tabelas, verifica segurança
    if tables_ok:
        await check_row_level_security(client, args.verbose)
        await check_policies(client, args.verbose)
    
    print("\n🏁 Verificação concluída!")

if __name__ == "__main__":
    args = parse_args()
    
    if sys.version_info >= (3, 7):
        asyncio.run(run_checks(args))
    else:
        print("❌ Python 3.7 ou superior é necessário para executar este script")
        sys.exit(1) 