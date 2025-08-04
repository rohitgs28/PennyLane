'use client';

import { useAuth0 } from '@auth0/auth0-react';

const ROLES_CLAIM = 'https://pennylane.app/roles';  

export function useAuthUser() {
  const {
    user,
    isLoading,
    isAuthenticated,
    error,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
  } = useAuth0();


  const signIn = () =>
    loginWithRedirect({
      authorizationParams: {
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE!,
        redirect_uri: `${window.location.origin}/auth/callback`,
        scope: 'openid profile email offline_access',
      },
      /* return to the page we came from */
      appState: { returnTo: window.location.pathname + window.location.search },
    });

 
  const roles: string[] =
    (user && ((user as any)[ROLES_CLAIM] as string[] | undefined)) || [];

  
  return {
    user,
    roles,
    isLoading,
    isAuthenticated,
    error,
    signIn,
    logout,
    getAccessTokenSilently,
  } as const;
}
