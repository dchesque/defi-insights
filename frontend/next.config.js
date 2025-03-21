// frontend/next.config.js - Criado em 21/03/2025 15:25
/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    // Configurações de redirecionamento para autenticação
    async redirects() {
      return [
        {
          source: '/login',
          destination: '/dashboard',
          has: [
            {
              type: 'cookie',
              key: 'auth_token',
            },
          ],
          permanent: false,
        },
        {
          source: '/register',
          destination: '/dashboard',
          has: [
            {
              type: 'cookie',
              key: 'auth_token',
            },
          ],
          permanent: false,
        },
      ];
    },
    // Configurações de rotas que exigem autenticação
    async middleware() {
      const authRoutes = ['/dashboard', '/portfolio', '/analysis', '/settings'];
      return {
        matcher: authRoutes,
      };
    },
    // Variáveis de ambiente públicas
    env: {
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    },
    // Configurações de imagens
    images: {
      domains: ['www.coingecko.com', 'assets.coingecko.com'],
    },
    // Configurações de compilação
    swcMinify: true,
  };
  
  module.exports = nextConfig;