// frontend/middleware.ts - Criado em 21/03/2025 15:30
/**
 * Middleware do Next.js para proteção de rotas autenticadas.
 */
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Verificar se há token de autenticação
  const authToken = request.cookies.get('auth_token')?.value;
  
  // Se não houver token e a rota requer autenticação, redirecionar para login
  if (!authToken) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    
    // Adicionar URL de redirecionamento para retornar após o login
    url.searchParams.set('redirect', request.nextUrl.pathname);
    
    return NextResponse.redirect(url);
  }
  
  return NextResponse.next();
}

// Definir em quais rotas o middleware deve ser executado
export const config = {
  matcher: [
    '/dashboard/:path*',
    '/portfolio/:path*',
    '/analysis/:path*',
    '/settings/:path*'
  ],
};