#!/usr/bin/env python
"""
Script para iniciar o servidor DeFi Insight.
"""
import os
import sys
import subprocess
from dotenv import load_dotenv
from colorama import init, Fore, Style
import signal

# Inicializar colorama
init()

def check_env():
    """Verifica se o arquivo .env existe e contém as variáveis essenciais."""
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    
    if not os.path.exists(dotenv_path):
        print(f"{Fore.RED}❌ Arquivo .env não encontrado!{Style.RESET_ALL}")
        print(f"Por favor, execute {Fore.YELLOW}python setup.py{Style.RESET_ALL} para configurar o ambiente.")
        return False
    
    # Carregar variáveis do .env com encoding específico para evitar erros
    try:
        load_dotenv(dotenv_path, encoding="utf-8")
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao carregar arquivo .env: {str(e)}{Style.RESET_ALL}")
        print(f"Verifique se o arquivo está em formato UTF-8 válido.")
        return False
    
    essential_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in essential_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"{Fore.RED}❌ Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}{Style.RESET_ALL}")
        print(f"Por favor, edite o arquivo {Fore.YELLOW}.env{Style.RESET_ALL} e adicione as variáveis necessárias.")
        return False
    
    return True

def setup_env():
    """Configura o ambiente para execução."""
    # Verificar e criar diretórios necessários
    dirs = ["logs", "cache"]
    for dir_name in dirs:
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"{Fore.GREEN}✓ Diretório criado: {dir_name}{Style.RESET_ALL}")
    
    # Configurar variáveis específicas para evitar multiprocessamento
    os.environ["PYTHONOPTIMIZE"] = "1"    # Desativar assert e debug
    os.environ["PYTHONUNBUFFERED"] = "1"  # Desativar buffer
    os.environ["UVICORN_NO_FORK"] = "1"   # Evitar forking de processos

def start_server():
    """Inicia o servidor FastAPI usando Uvicorn."""
    # Adicionar o diretório atual ao PYTHONPATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    print(f"\n{Fore.CYAN}🚀 Iniciando servidor DeFi Insight...{Style.RESET_ALL}")
    print(f"   URL: {Fore.GREEN}http://0.0.0.0:{port}{Style.RESET_ALL}")
    print(f"   Documentação: {Fore.GREEN}http://0.0.0.0:{port}/docs{Style.RESET_ALL}")
    print(f"   Modo depuração: {Fore.GREEN}{'Ativado' if debug else 'Desativado'}{Style.RESET_ALL}")
    print(f"   {Fore.YELLOW}Atenção: Multiprocessamento desativado para compatibilidade com Windows{Style.RESET_ALL}")
    
    # Comando simples que evita o multiprocessamento
    try:
        # Usar python -m para executar uvicorn diretamente sem subprocess
        cmd = [
            sys.executable, 
            "-m", 
            "uvicorn", 
            "src.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(port),
            "--workers", "1",  # Usar apenas um worker
        ]
        
        # Configurar manipulador de sinal para encerrar adequadamente
        def signal_handler(sig, frame):
            print(f"\n{Fore.YELLOW}⚠️ Encerrando servidor...{Style.RESET_ALL}")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Iniciar o processo diretamente com execvp
        os.execvp(cmd[0], cmd)
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erro ao iniciar o servidor: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar ambiente
    if not check_env():
        sys.exit(1)
    
    # Configurar ambiente
    setup_env()
    
    # Iniciar servidor
    start_server() 