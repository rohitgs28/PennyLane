'use client';

import { useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { setAccessToken } from '@/lib/apolloClient';

/**
 * Bridges Auth0 React SDK → Apollo header.
 * Mounts once inside <AuthProvider>.
 */
export default function TokenBridge() {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    if (!isAuthenticated) {
      setAccessToken(null);
      return;
    }
    (async () => {
      try {
        const token = await getAccessTokenSilently({
          authorizationParams: {
            audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE!,
          },
        });
        
        setAccessToken(token);
      } catch {
        setAccessToken(null);
      }
    })();
  }, [isAuthenticated, getAccessTokenSilently]);

  return null;
}
