"use client";

import { Auth0Provider } from '@auth0/auth0-react';
import { useRouter } from 'next/navigation';
import { ReactNode } from 'react';


export default function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();

  const onRedirectCallback = (appState?: { returnTo?: string }) => {
    router.push(appState?.returnTo || '/');
  };

  const audience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE!;
  const redirectUri =
    typeof window !== 'undefined'
      ? `${window.location.origin}/auth/callback`
      : 'http://localhost:3000/auth/callback';

  return (
    <Auth0Provider
      domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN!}
      clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!}
      authorizationParams={{
        redirect_uri: redirectUri,
        audience,
        // include offline_access so that refresh tokens can be used
        scope: 'openid profile email offline_access',
      }}
      // Persist tokens in localStorage so they survive refreshes.
      cacheLocation="localstorage"
      // Use refresh tokens so that expired access tokens can be renewed silently.
      useRefreshTokens
      onRedirectCallback={onRedirectCallback}
    >
      {children}
    </Auth0Provider>
  );
}