// frontend/src/App.js - Atualizado em 21/03/2025 16:20
import React, { createContext, useContext, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ReportPage from './pages/ReportPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import PortfolioPage from './pages/PortfolioPage';
import Header from './components/Header';
import Footer from './components/Footer';
import { useAuth } from './hooks/useAuth';

/**
 * Contexto para compartilhar o estado de autenticação entre componentes
 */
export const AuthContext = createContext(null);

/**
 * Hook personalizado para acessar o contexto de autenticação
 */
export const useAuthContext = () => useContext(AuthContext);

/**
 * Componente para rotas protegidas que requerem autenticação
 */
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuthContext();
  
  // Se ainda está carregando, mostrar um loader
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
      </div>
    );
  }
  
  // Se não está autenticado, redirecionar para login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  // Se está autenticado, renderizar o conteúdo protegido
  return children;
};

/**
 * Componente raiz da aplicação
 */
function App() {
  // Usar o hook de autenticação
  const auth = useAuth();
  
  return (
    <AuthContext.Provider value={auth}>
      <Router>
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-grow">
            <Routes>
              {/* Rotas públicas */}
              <Route path="/" element={<HomePage />} />
              <Route path="/report/:id" element={<ReportPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Rotas protegidas */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/portfolio" 
                element={
                  <ProtectedRoute>
                    <PortfolioPage />
                  </ProtectedRoute>
                } 
              />
              
              {/* Rota de fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;