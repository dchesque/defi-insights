#!/usr/bin/env python
"""
Script de configuração inicial para DeFi Insight.
"""
import os
import sys
import subprocess
import platform

def check_python_version():
    """Verifica a versão do Python."""
    print("🔍 Verificando versão do Python...")
    required_version = (3, 7)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"❌ Python {required_version[0]}.{required_version[1]} ou superior é necessário")
        print(f"   Versão atual: {current_version[0]}.{current_version[1]}")
        sys.exit(1)
    
    print(f"✅ Usando Python {current_version[0]}.{current_version[1]}.{current_version[2]}")

def install_dependencies():
    """Instala as dependências do projeto."""
    print("\n🔧 Instalando dependências...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        sys.exit(1)

def setup_env_file():
    """Configura o arquivo .env se ele não existir."""
    print("\n🔧 Configurando variáveis de ambiente...")
    
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("📝 Criando arquivo .env a partir do exemplo...")
            
            # Em Windows, precisamos usar 'copy' em vez de 'cp'
            if platform.system() == "Windows":
                os.system("copy .env.example .env")
            else:
                os.system("cp .env.example .env")
                
            print("✅ Arquivo .env criado! Por favor, edite-o com suas credenciais.")
        else:
            print("📝 Criando arquivo .env básico...")
            
            with open(".env", "w") as f:
                f.write("""# DeFi Insight - Variáveis de ambiente
# Preencha com suas credenciais

# ===== Configurações Supabase =====
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase

# ===== Configurações de Segurança =====
JWT_SECRET_KEY=chave_secreta_para_jwt
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ===== Configurações da API =====
PORT=8000
HOST=0.0.0.0
DEBUG=True
""")
            
            print("✅ Arquivo .env básico criado! Por favor, edite-o com suas credenciais.")
    else:
        print("✅ Arquivo .env já existe!")

def setup_directories():
    """Cria estrutura de diretórios se necessário."""
    print("\n🔧 Verificando estrutura de diretórios...")
    
    # Lista de diretórios para garantir que existem
    directories = [
        "src/api/routes",
        "src/core",
        "src/agents",
        "src/integrations",
        "src/utils",
        "scripts",
        "tests"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"📁 Criando diretório: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    print("✅ Estrutura de diretórios verificada!")

def show_next_steps():
    """Exibe próximos passos para o usuário."""
    print("\n🚀 Configuração inicial concluída!")
    print("\n📝 Próximos passos:")
    print("  1. Edite o arquivo .env com suas credenciais do Supabase")
    print("  2. Configure o banco de dados no Supabase executando:")
    print("     python scripts/init_supabase.py --create-tables")
    print("  3. Inicie o servidor com:")
    print("     python start.py")
    print("  4. Acesse a documentação da API em:")
    print("     http://localhost:8000/docs")

if __name__ == "__main__":
    print("🚀 Iniciando configuração do DeFi Insight...")
    
    check_python_version()
    install_dependencies()
    setup_directories()
    setup_env_file()
    show_next_steps() 