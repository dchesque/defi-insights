// frontend/src/pages/LoginPage.js - Criado em 21/03/2025 16:25
import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../App';
import { FaLock, FaEnvelope, FaExclamationTriangle } from 'react-icons/fa';

/**
 * Página de login da aplicação
 * Permite aos usuários autenticarem-se na plataforma
 */
const LoginPage = () => {
  // Estados para o formulário
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Hooks do React Router
  const navigate = useNavigate();
  const location = useLocation();
  
  // Obter contexto de autenticação
  const { login, error: authError, isAuthenticated } = useAuthContext();
  
  // Obter URL de redirecionamento dos query params, se houver
  const redirectTo = new URLSearchParams(location.search).get('redirect') || '/dashboard';
  
  // Efeito para redirecionar se já estiver autenticado
  useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectTo, { replace: true });
    }
  }, [isAuthenticated, navigate, redirectTo]);
  
  // Efeito para mostrar erro de autenticação, se houver
  useEffect(() => {
    if (authError) {
      setFormError(authError);
      setIsSubmitting(false);
    }
  }, [authError]);
  
  // Manipulador do envio do formulário
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validação básica
    if (!email.trim()) {
      setFormError('Por favor, informe seu email');
      return;
    }
    
    if (!password) {
      setFormError('Por favor, informe sua senha');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setFormError('');
      
      // Tentar fazer login
      const success = await login({ email, password });
      
      if (success) {
        // Se login for bem-sucedido, o efeito acima redirecionará
        // Não precisamos fazer nada aqui
      } else {
        // Se login falhar mas não lançar erro
        setFormError('Falha ao fazer login. Verifique suas credenciais.');
        setIsSubmitting(false);
      }
    } catch (err) {
      setFormError(err.message || 'Ocorreu um erro durante o login');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-[#0F1123]">
      <div className="max-w-md w-full bg-[#1A1C31] rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Entrar no BaseMind.ai</h1>
          <p className="text-gray-400 mt-2">
            Faça login para acessar sua conta e análises
          </p>
        </div>
        
        {formError && (
          <div className="mb-6 p-3 bg-red-900/30 border border-red-800 rounded-md flex items-start">
            <FaExclamationTriangle className="text-red-500 mt-1 mr-2 flex-shrink-0" />
            <p className="text-red-400 text-sm">{formError}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-5">
            <label htmlFor="email" className="block text-gray-300 mb-2 font-medium">
              Email
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaEnvelope className="text-gray-500" />
              </div>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10 w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                placeholder="seu@email.com"
                disabled={isSubmitting}
              />
            </div>
          </div>
          
          <div className="mb-6">
            <label htmlFor="password" className="block text-gray-300 mb-2 font-medium">
              Senha
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaLock className="text-gray-500" />
              </div>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10 w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                placeholder="••••••••"
                disabled={isSubmitting}
              />
            </div>
          </div>
          
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <input
                id="remember"
                type="checkbox"
                className="h-4 w-4 rounded border-gray-700 bg-[#12141F] focus:ring-indigo-500 text-indigo-500"
              />
              <label htmlFor="remember" className="ml-2 block text-sm text-gray-400">
                Lembrar-me
              </label>
            </div>
            
            <a href="#" className="text-sm text-indigo-400 hover:text-indigo-300">
              Esqueceu sua senha?
            </a>
          </div>
          
          <button
            type="submit"
            className="w-full py-3 px-4 font-medium text-center text-white bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md hover:opacity-90 transition-opacity disabled:opacity-70"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-gray-400">
            Não tem uma conta?{' '}
            <Link to="/register" className="text-indigo-400 hover:text-indigo-300">
              Registre-se
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;