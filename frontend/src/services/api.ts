// frontend/src/services/api.ts - Atualizado em 21/03/2025 14:35
/**
 * Serviço para comunicação com a API do backend.
 * Centraliza todas as chamadas HTTP e gerencia autenticação e erros.
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ApiErrorResponse, ApiResponse, PaginatedResponse } from '../types/models';

export class ApiService {
  private api: AxiosInstance;
  private isRefreshing: boolean = false;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    // Criar instância do axios com configurações padrão
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 segundos de timeout
    });

    // Interceptor de requisição para adicionar token JWT
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Interceptor de resposta para tratar erros
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
        
        // Tratar erro de autenticação (token expirado)
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            try {
              // Aguardar token de refreshing em andamento
              const newToken = await this.refreshPromise;
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
              }
              return this.api(originalRequest);
            } catch (refreshError) {
              // Se refresh falhar, direcionar para login
              this.handleAuthError();
              return Promise.reject(refreshError);
            }
          }

          originalRequest._retry = true;
          this.isRefreshing = true;
          
          try {
            // Tentar renovar o token
            this.refreshPromise = this.refreshToken();
            const newToken = await this.refreshPromise;
            
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            
            return this.api(originalRequest);
          } catch (refreshError) {
            this.handleAuthError();
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
            this.refreshPromise = null;
          }
        }
        
        // Formatar erros
        const errorResponse: ApiErrorResponse = {
          success: false,
          message: error.response?.data 
            ? (error.response.data as any).message || 'Erro desconhecido'
            : error.message || 'Erro desconhecido',
          timestamp: new Date().toISOString(),
          request_id: (error.response?.data as any)?.request_id || 'client-error',
          path: error.config?.url,
          error_code: (error.response?.data as any)?.error_code,
          details: (error.response?.data as any)?.details
        };
        
        return Promise.reject(errorResponse);
      }
    );
  }

  // Métodos privados
  private async refreshToken(): Promise<string> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('Refresh token não encontrado');
      }
      
      const response = await this.api.post<ApiResponse<{ access_token: string }>>('/api/auth/refresh', {
        refresh_token: refreshToken
      });
      
      const newToken = response.data.data.access_token;
      localStorage.setItem('auth_token', newToken);
      return newToken;
    } catch (error) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      throw error;
    }
  }

  private handleAuthError(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    
    // Redirecionar para página de login
    if (typeof window !== 'undefined') {
      window.location.href = '/login?session_expired=true';
    }
  }

  // Métodos públicos para chamadas à API
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.api.get<ApiResponse<T>>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.api.post<ApiResponse<T>>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.api.put<ApiResponse<T>>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.api.delete<ApiResponse<T>>(url, config);
    return response.data;
  }

  async getPaginated<T>(url: string, page: number = 1, pageSize: number = 10, filters?: any): Promise<PaginatedResponse<T>> {
    const params = {
      page,
      page_size: pageSize,
      ...filters
    };
    
    const response = await this.api.get<PaginatedResponse<T>>(url, { params });
    return response.data;
  }
}

// Exportar instância única do serviço (Singleton)
export const apiService = new ApiService();