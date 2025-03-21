// frontend/src/components/Header.js - Atualizado em 21/03/2025 16:45
import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaChevronDown, FaUser, FaSignOutAlt, FaCog, FaWallet } from 'react-icons/fa';
import { useAuthContext } from '../App';

/**
 * Componente Header da aplicação
 * Exibe a barra de navegação principal com opções dinâmicas baseadas na autenticação
 */
const Header = () => {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuthContext();
  const userMenuRef = useRef(null);
  const location = useLocation();

  // Fechar menu ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Fechar menus ao navegar
  useEffect(() => {
    setUserMenuOpen(false);
    setMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <header className="py-4 px-6 md:px-12 flex justify-between items-center border-b border-gray-800">
      <Link to="/" className="flex items-center">
        <div className="bg-indigo-600 rounded-full w-8 h-8 flex items-center justify-center mr-2">
          <span className="text-white font-bold">B</span>
        </div>
        <span className="font-bold">BaseMind<span className="text-indigo-400">.ai</span></span>
      </Link>
      
      {/* Menu para desktop */}
      <nav className="hidden md:flex items-center space-x-6">
        <Link to="/" className={`text-gray-300 hover:text-white ${location.pathname === '/' ? 'text-white' : ''}`}>
          Home
        </Link>
        
        {isAuthenticated && (
          <>
            <Link to="/dashboard" className={`text-gray-300 hover:text-white ${location.pathname === '/dashboard' ? 'text-white' : ''}`}>
              Dashboard
            </Link>
            <Link to="/portfolio" className={`text-gray-300 hover:text-white ${location.pathname === '/portfolio' ? 'text-white' : ''}`}>
              Portfólio
            </Link>
          </>
        )}
        
        <Link to="/features" className={`text-gray-300 hover:text-white ${location.pathname === '/features' ? 'text-white' : ''}`}>
          Recursos
        </Link>
        <Link to="/about" className={`text-gray-300 hover:text-white ${location.pathname === '/about' ? 'text-white' : ''}`}>
          Sobre
        </Link>
      </nav>
      
      {/* Área de autenticação */}
      <div className="flex items-center">
        {isAuthenticated ? (
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-gray-800"
            >
              <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
                <FaUser className="text-white" />
              </div>
              <span className="hidden md:inline-block text-sm">{user?.name || 'Usuário'}</span>
              <FaChevronDown className={`transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
            </button>
            
            {/* Menu de usuário dropdown */}
            {userMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 py-2 bg-[#1A1C31] rounded-md shadow-xl border border-gray-800 z-50">
                <Link 
                  to="/dashboard" 
                  className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 flex items-center"
                >
                  <FaUser className="mr-2" />
                  Dashboard
                </Link>
                <Link 
                  to="/portfolio" 
                  className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 flex items-center"
                >
                  <FaWallet className="mr-2" />
                  Portfólio
                </Link>
                <Link 
                  to="/settings" 
                  className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 flex items-center"
                >
                  <FaCog className="mr-2" />
                  Configurações
                </Link>
                <button 
                  onClick={logout}
                  className="w-full text-left block px-4 py-2 text-sm text-gray-300 hover:bg-gray-800 flex items-center border-t border-gray-800 mt-1 pt-1"
                >
                  <FaSignOutAlt className="mr-2" />
                  Sair
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center">
            <Link 
              to="/login" 
              className="text-gray-300 hover:text-white mr-4"
            >
              Entrar
            </Link>
            <Link 
              to="/register" 
              className="px-4 py-2 border border-indigo-600 rounded text-indigo-400 hover:bg-indigo-600 hover:text-white transition-colors"
            >
              Registrar
            </Link>
          </div>
        )}
      </div>
      
      {/* Menu para mobile (botão hamburguer) */}
      <button 
        className="md:hidden text-gray-300 focus:outline-none"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
        </svg>
      </button>
      
      {/* Menu mobile dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute top-16 inset-x-0 bg-[#1A1C31] border-b border-gray-800 z-50">
          <div className="px-4 py-2">
            <Link to="/" className="block py-2 text-gray-300 hover:text-white">
              Home
            </Link>
            
            {isAuthenticated && (
              <>
                <Link to="/dashboard" className="block py-2 text-gray-300 hover:text-white">
                  Dashboard
                </Link>
                <Link to="/portfolio" className="block py-2 text-gray-300 hover:text-white">
                  Portfólio
                </Link>
              </>
            )}
            
            <Link to="/features" className="block py-2 text-gray-300 hover:text-white">
              Recursos
            </Link>
            <Link to="/about" className="block py-2 text-gray-300 hover:text-white">
              Sobre
            </Link>
            
            {!isAuthenticated && (
              <>
                <Link to="/login" className="block py-2 text-gray-300 hover:text-white">
                  Entrar
                </Link>
                <Link to="/register" className="block py-2 text-gray-300 hover:text-white">
                  Registrar
                </Link>
              </>
            )}
            
            {isAuthenticated && (
              <button 
                onClick={logout}
                className="block w-full text-left py-2 text-gray-300 hover:text-white"
              >
                Sair
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;