// frontend/src/pages/RegisterPage.js - Criado em 21/03/2025 16:30
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../App';
import { FaLock, FaEnvelope, FaUser, FaExclamationTriangle } from 'react-icons/fa';

/**
 * Página de registro de novos usuários
 * Permite que visitantes criem uma nova conta
 */
const RegisterPage = () => {
  // Estados para o formulário
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Hooks do React Router
  const navigate = useNavigate();
  
  // Obter contexto de autenticação
  const { register, error: authError, isAuthenticated } = useAuthContext();
  
  // Efeito para redirecionar se já estiver autenticado
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);
  
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
    if (!name.trim()) {
      setFormError('Por favor, informe seu nome');
      return;
    }
    
    if (!email.trim()) {
      setFormError('Por favor, informe seu email');
      return;
    }
    
    if (!password) {
      setFormError('Por favor, crie uma senha');
      return;
    }
    
    if (password !== confirmPassword) {
      setFormError('As senhas não coincidem');
      return;
    }
    
    if (password.length < 8) {
      setFormError('A senha deve ter pelo menos 8 caracteres');
      return;
    }
    
    try {
      setIsSubmitting(true);
      setFormError('');
      
      // Tentar fazer o registro
      const success = await register({
        name,
        email,
        password
      });
      
      if (success) {
        // Se registro for bem-sucedido, o efeito acima redirecionará
        // Não precisamos fazer nada aqui
      } else {
        // Se registro falhar mas não lançar erro
        setFormError('Falha ao criar conta. Tente novamente.');
        setIsSubmitting(false);
      }
    } catch (err) {
      setFormError(err.message || 'Ocorreu um erro durante o registro');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-[#0F1123]">
      <div className="max-w-md w-full bg-[#1A1C31] rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Crie sua conta</h1>
          <p className="text-gray-400 mt-2">
            Registre-se para acessar análises avançadas de criptomoedas
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
            <label htmlFor="name" className="block text-gray-300 mb-2 font-medium">
              Nome
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaUser className="text-gray-500" />
              </div>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="pl-10 w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                placeholder="Seu nome"
                disabled={isSubmitting}
              />
            </div>
          </div>
          
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
          
          <div className="mb-5">
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
                placeholder="Mínimo 8 caracteres"
                disabled={isSubmitting}
              />
            </div>
          </div>
          
          <div className="mb-6">
            <label htmlFor="confirmPassword" className="block text-gray-300 mb-2 font-medium">
              Confirmar Senha
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaLock className="text-gray-500" />
              </div>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="pl-10 w-full rounded-md bg-[#12141F] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                placeholder="Confirme sua senha"
                disabled={isSubmitting}
              />
            </div>
          </div>
          
          <button
            type="submit"
            className="w-full py-3 px-4 font-medium text-center text-white bg-gradient-to-r from-indigo-600 to-purple-600 rounded-md hover:opacity-90 transition-opacity disabled:opacity-70"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Criando conta...' : 'Criar conta'}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-gray-400">
            Já tem uma conta?{' '}
            <Link to="/login" className="text-indigo-400 hover:text-indigo-300">
              Entre aqui
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;