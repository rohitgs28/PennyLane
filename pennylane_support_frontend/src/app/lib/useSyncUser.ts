'use client';

import { useEffect, useRef } from 'react';
import { useMutation } from '@apollo/client';
import { SYNC_USER } from '@/app/graphql/operations';
import { useAuthUser } from './useAuthUser';

export function useSyncUser() {
  const { user, isLoading } = useAuthUser();
  const [syncUser] = useMutation(SYNC_USER);
  const inFlight = useRef(false);

  useEffect(() => {
    if (isLoading || !user || inFlight.current) return;

    const sub = (user as any)?.sub;
    const email = (user as any)?.email;
    const username =
      (user as any)?.nickname ||
      (user as any)?.name ||
      (email ? email.split('@')[0] : 'user');

    if (!sub || !email) return;

    const key = `synced:${sub}`;
    if (typeof window !== 'undefined' && localStorage.getItem(key)) return;

    inFlight.current = true;
    syncUser({ variables: { email, username, auth0Id: sub } })
      .catch(() => {})
      .finally(() => {
        inFlight.current = false;
        try { localStorage.setItem(key, '1'); } catch {}
      });
  }, [user, isLoading, syncUser]);
}
