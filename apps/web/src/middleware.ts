import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Route protection middleware.
 *
 * Establishes the structure for session-based route protection.
 * When authentication is implemented, this will validate session
 * tokens and enforce role-based route access.
 */

const PUBLIC_ROUTES = ['/', '/login', '/register', '/terms', '/privacy'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow static assets and API routes through
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  const isPublicRoute = PUBLIC_ROUTES.some((route) => 
    route === '/' ? pathname === '/' : pathname.startsWith(route)
  );
  const sessionToken = request.cookies.get('session_token')?.value;

  // Redirect unauthenticated users to login
  if (!isPublicRoute && !sessionToken) {
    const loginUrl = new URL('/login', request.url);
    if (pathname !== '/') {
      loginUrl.searchParams.set('redirect', pathname);
    }
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users away from public routes to dashboard
  if (isPublicRoute && sessionToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
