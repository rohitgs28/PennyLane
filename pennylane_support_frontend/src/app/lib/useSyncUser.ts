'use client';

import { useEffect, useRef } from 'react';
import { useMutation } from '@apollo/client';
import { SYNC_USER } from '@/app/graphql/operations';
import { useAuthUser } from './useAuthUser';

export function useSyncUser() {
  const { user, isLoading } = useAuthUser();
  const [syncUser] = useMutation(SYNC_USER);
  const inFlight = useRef(false);

  const previousSub = useRef<string | null>(null);

  useEffect(() => {
    if (!user) {
      previousSub.current = null;
    }

    if (isLoading || !user || inFlight.current) return;

   
    const sub: string | undefined = (user as any)?.sub;
    const rawEmail: unknown =
      (user as any)?.email ??
      (user as any)?.['https://pennylane.app/email'] ??
      (user as any)?.name;
    const email: string | undefined = typeof rawEmail === 'string' ? rawEmail : undefined;

    const username: string =
      (user as any)?.name ||
      (email ? email.split('@')[0] : 'user');

    if (!sub || !email) return;


    if (previousSub.current === sub) return;

    previousSub.current = sub;
    inFlight.current = true;
    syncUser({ variables: { email, username, auth0Id: sub } })
      .catch(() => {})
      .finally(() => {
        inFlight.current = false;
      });
  }, [user, isLoading, syncUser]);
}
