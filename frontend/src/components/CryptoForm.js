// frontend/src/components/CryptoForm.js - Atualizado em 21/03/2025 16:05
import React, { useState } from 'react';
import { FaSearch } from 'react-icons/fa';

/**
 * Componente de formulário para inserção de URLs de criptomoedas para análise
 * @param {function} onAnalyze - Função chamada quando o usuário submete o formulário
 */
const CryptoForm = ({ onAnalyze }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validação básica
    if (!url.trim()) {
      setError('Por favor, insira uma URL de criptomoeda');
      return;
    }
    
    // Verificar se é uma URL válida do CoinGecko ou CoinMarketCap
    const isValidUrl = 
      url.includes('coingecko.com') || 
      url.includes('coinmarketcap.com');
      
    if (!isValidUrl) {
      setError('Por favor, insira uma URL válida do CoinGecko ou CoinMarketCap');
      return;
    }
    
    setError('');
    onAnalyze(url);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Cole o link da criptomoeda (ex: https://www.coingecko.com/en/coins/bitcoin)"
          className="w-full p-4 pl-4 pr-24 rounded-md bg-[#1A1C31] border border-gray-700 text-white placeholder-gray-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
        <button
          type="submit"
          className="absolute inset-y-0 right-0 flex items-center justify-center bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-r-md px-6 hover:opacity-90 transition-opacity"
        >
          Analisar
        </button>
      </form>
      
      {error && (
        <p className="mt-2 text-red-400 text-sm">{error}</p>
      )}
      
      <div className="mt-3 text-xs text-gray-500 flex items-center justify-center">
        <FaSearch className="mr-1" /> 
        Exemplos: 
        <a href="#" aria-label="Analisar Bitcoin" onClick={(e) => {
          e.preventDefault();
          setUrl('https://www.coingecko.com/en/coins/bitcoin');
        }} className="ml-1 text-indigo-400 hover:text-indigo-300">
          Bitcoin
        </a>
        <span className="mx-1">•</span>
        <a href="#" onClick={(e) => {
          e.preventDefault();
          setUrl('https://www.coingecko.com/en/coins/ethereum');
        }} className="text-indigo-400 hover:text-indigo-300">
          Ethereum
        </a>
        <span className="mx-1">•</span>
        <a href="#" onClick={(e) => {
          e.preventDefault();
          setUrl('https://www.coingecko.com/en/coins/solana');
        }} className="text-indigo-400 hover:text-indigo-300">
          Solana
        </a>
      </div>
    </div>
  );
};

export default CryptoForm;