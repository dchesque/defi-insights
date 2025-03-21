// frontend/src/hooks/useAuth.ts - Criado em 21/03/2025 15:05
/**
 * Hook para gerenciamento de autenticação.
 * Encapsula a lógica de login, registro e logout.
 */
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom'; // Importação correta
import { apiService } from '../services/api';
import { User, AuthToken } from '../types/models';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData extends LoginCredentials {
  name: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const navigate = useNavigate(); // Usar useNavigate do React Router

  // Verificar se o usuário está autenticado ao carregar a página
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Verificar se há token no localStorage
        const token = localStorage.getItem('auth_token');
        if (!token) {
          setUser(null);
          setIsAuthenticated(false);
          setLoading(false);
          return;
        }

        // Verificar se o token é válido
        const response = await apiService.get<User>('/api/auth/me');
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (err) {
        // Token inválido ou expirado
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setLoading(true);
    setError(null);
    
    try {
      // Formatar os dados para o formato esperado pelo backend
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      
      // Fazer requisição de login
      const response = await apiService.post<AuthToken>('/api/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      // Salvar tokens
      localStorage.setItem('auth_token', response.data.access_token);
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token);
      }
      
      // Buscar informações do usuário
      const userResponse = await apiService.get<User>('/api/auth/me');
      setUser(userResponse.data);
      setIsAuthenticated(true);
      
      return true;
    } catch (err: any) {
      setError(err.message || 'Falha no login. Verifique suas credenciais.');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    setLoading(true);
    setError(null);
    
    try {
      await apiService.post('/api/auth/register', data);
      
      // Fazer login automaticamente após o registro
      return await login({
        email: data.email,
        password: data.password
      });
    } catch (err: any) {
      setError(err.message || 'Erro ao criar conta. Tente novamente.');
      return false;
    } finally {
      setLoading(false);
    }
  }, [login]);

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/login'); // Substituir router.push
  }, [navigate]);

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout
  };
}