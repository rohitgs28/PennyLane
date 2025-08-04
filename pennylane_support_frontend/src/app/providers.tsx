'use client';

import { ReactNode, useMemo } from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import { ApolloProvider } from '@apollo/client';
import { apolloClient } from '@/lib/apolloClient';
import AuthProvider from '@/auth/Authprovider';
import AppNav from '@/app/components/nav/AppNav';
import TokenBridge from './TokenBridge';        

type Props = { children: ReactNode };

export default function Providers({ children }: Props) {
  const client = useMemo(() => apolloClient, []);

  return (
    <ChakraProvider>
      <ApolloProvider client={client}>
        <AuthProvider>
          <TokenBridge />                          
          <AppNav />
          {children}
        </AuthProvider>
      </ApolloProvider>
    </ChakraProvider>
  );
}
