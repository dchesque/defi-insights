// frontend/src/index.js - Atualizado em 21/03/2025 16:50
import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/globals.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

/**
 * Ponto de entrada da aplicação BaseMind.ai
 * Inicializa o React e renderiza o componente raiz App
 */

// Verificar se as variáveis de ambiente estão configuradas
if (!process.env.REACT_APP_API_URL && !process.env.NEXT_PUBLIC_API_URL) {
  console.warn(
    'Aviso: URL da API não configurada. ' +
    'Certifique-se de criar um arquivo .env.local com REACT_APP_API_URL ou NEXT_PUBLIC_API_URL.'
  );
}

// Obter o elemento raiz do DOM
const root = ReactDOM.createRoot(document.getElementById('root'));

// Renderizar a aplicação
root.render(
  <React.StrictMode>
    {/* ToastContainer para exibir notificações na aplicação */}
    <ToastContainer
      position="top-right"
      autoClose={5000}
      hideProgressBar={false}
      newestOnTop={true}
      closeOnClick
      rtl={false}
      pauseOnFocusLoss
      draggable
      pauseOnHover
      theme="dark"
    />
    
    {/* Componente principal da aplicação */}
    <App />
  </React.StrictMode>
);

// Reportar métricas de web vitals para análise de desempenho
// Para mais informações: https://bit.ly/CRA-vitals
reportWebVitals();