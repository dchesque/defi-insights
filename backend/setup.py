#!/usr/bin/env python
"""
Script de instalação para o backend DeFi Insight
"""
import os
import sys
import subprocess
import platform
import secrets
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é >= 3.8"""
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8 ou superior é necessário")
        sys.exit(1)
    print("✅ Versão do Python OK")

def install_dependencies():
    """Instala as dependências do projeto"""
    print("\n📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar as dependências")
        sys.exit(1)

def setup_env_file():
    """Configura o arquivo .env se não existir"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("\n📝 Arquivo .env já existe")
    else:
        if env_example_path.exists():
            # Copia .env.example para .env
            with open(env_example_path, "r") as example_file:
                env_content = example_file.read()
            
            # Gera um JWT secret key
            jwt_secret = secrets.token_hex(32)
            env_content = env_content.replace("JWT_SECRET_KEY=", f"JWT_SECRET_KEY={jwt_secret}")
            
            with open(env_path, "w") as env_file:
                env_file.write(env_content)
                
            print("\n📝 Arquivo .env criado a partir do .env.example")
            print("   JWT_SECRET_KEY foi gerado automaticamente")
        else:
            print("\n⚠️ .env.example não encontrado. Crie o arquivo .env manualmente")
    
    print("⚠️ IMPORTANTE: Configure as credenciais das APIs no arquivo .env")
    print("   Mais informações no arquivo README_ENV.md")

def create_database_schema():
    """Cria o schema inicial do banco de dados no Supabase se necessário"""
    # Em uma implementação real, isso poderia executar migrations ou scripts SQL
    # Para este exemplo, vamos apenas informar que o usuário precisa configurar o Supabase
    print("\n🗄️ Configuração do banco de dados:")
    print("   1. Acesse o console do Supabase")
    print("   2. Crie as seguintes tabelas:")
    print("      - users")
    print("      - token_analyses")
    print("      - portfolios")
    print("      - user_preferences")
    print("\n   Consulte a documentação para o schema detalhado")

def update_permissions():
    """Atualiza permissões do script start.py"""
    if platform.system() != "Windows":
        try:
            os.chmod("start.py", 0o755)
            print("\n🔒 Permissões de execução adicionadas ao start.py")
        except:
            print("\n⚠️ Não foi possível atualizar permissões do start.py")
            print("   Você pode precisar executá-lo com: python start.py")

def main():
    """Função principal de setup"""
    print("\n🚀 Configurando o backend DeFi Insight\n")
    
    check_python_version()
    install_dependencies()
    setup_env_file()
    create_database_schema()
    update_permissions()
    
    print("\n✨ Setup concluído! O backend está pronto para ser executado.")
    print("   Para iniciar o servidor, execute:")
    if platform.system() == "Windows":
        print("   > python start.py")
    else:
        print("   $ ./start.py")
    print("\n   A API estará disponível em:")
    print("   http://localhost:8000")
    print("   E a documentação em:")
    print("   http://localhost:8000/docs")

if __name__ == "__main__":
    main() 