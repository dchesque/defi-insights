"""
Utilitário para gerenciamento de cache
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class Cache:
    """
    Classe para gerenciamento de cache simples baseado em arquivos.
    """
    
    def __init__(self, cache_dir: str = None):
        """
        Inicializa o cache.
        
        Args:
            cache_dir: Diretório para armazenar arquivos de cache. Se None, usa o diretório padrão.
        """
        if cache_dir is None:
            # Usar diretório padrão na pasta backend/cache
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.cache_dir = os.path.join(base_dir, "cache")
        else:
            self.cache_dir = cache_dir
            
        # Garantir que o diretório existe
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def get(self, key: str, max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Obtém um item do cache se não estiver expirado.
        
        Args:
            key: Chave do item
            max_age_hours: Idade máxima em horas para considerar o cache válido
            
        Returns:
            Optional[Dict[str, Any]]: Dados do cache ou None se expirado/inexistente
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return None
            
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Verificar se o cache expirou
            timestamp = datetime.fromisoformat(data.get("timestamp", "2000-01-01T00:00:00"))
            age_hours = (datetime.now() - timestamp).total_seconds() / 3600
            
            if age_hours <= max_age_hours:
                return data
                
        except Exception as e:
            print(f"Erro ao ler cache: {str(e)}")
            
        return None
    
    async def set(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Salva um item no cache.
        
        Args:
            key: Chave do item
            data: Dados a serem salvos
            
        Returns:
            bool: True se o cache foi salvo com sucesso
        """
        # Adicionar timestamp se não existir
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()
            
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar cache: {str(e)}")
            return False
    
    async def invalidate(self, key: str) -> bool:
        """
        Invalida um item do cache.
        
        Args:
            key: Chave do item a ser invalidado
            
        Returns:
            bool: True se o item foi invalidado com sucesso
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                return True
            except Exception as e:
                print(f"Erro ao invalidar cache: {str(e)}")
                
        return False
    
    async def clear_all(self) -> int:
        """
        Limpa todos os itens do cache.
        
        Returns:
            int: Número de itens removidos
        """
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
                except Exception as e:
                    print(f"Erro ao remover {filename}: {str(e)}")
                    
        return count

# Instância global para uso em toda a aplicação
cache = Cache() 