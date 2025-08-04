'use client';

import NextLink from 'next/link';
import {
  Avatar,
  Box,
  Button,
  Flex,
  HStack,
  Heading,
  Link as ChakraLink,
  Spacer,
  Spinner,
  Text,
} from '@chakra-ui/react';
import { usePathname } from 'next/navigation';
import { useAuth0 } from '@auth0/auth0-react';

const audience =
  process.env.NEXT_PUBLIC_AUTH0_AUDIENCE || 'https://pennylane-support-api';
const redirectUri = '/auth/callback';                   // single canonical URL

function NavItem({
  href,
  children,
}: {
  href: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const active = pathname.startsWith(href);

  return (
    <ChakraLink
      as={NextLink}
      href={href}
      fontWeight={active ? 'semibold' : 'medium'}
      color={active ? 'blue.600' : 'gray.700'}
      _hover={{ textDecoration: 'none', color: 'blue.600' }}
    >
      {children}
    </ChakraLink>
  );
}

export default function AppNav() {
  const pathname = usePathname();                       // current page
  const { user, isLoading, isAuthenticated, loginWithRedirect, logout } =
    useAuth0();


  /** Always trigger Auth0 with the single whitelisted callback URL */
  const signIn = () =>
    loginWithRedirect({
      authorizationParams: {
        audience,
        redirect_uri: `${window.location.origin}${redirectUri}`,
        scope: 'openid profile email offline_access',
      },
      appState: { returnTo: pathname },
    });

  return (
    <Box as="nav" borderBottomWidth="1px" py={3}>
      <Flex align="center" px={{ base: 4, md: 0 }}>
        <Heading size="md">
          <ChakraLink as={NextLink} href="/">
            PennyLane
          </ChakraLink>
        </Heading>

        <HStack spacing={6} ml={8}>
          <NavItem href="/challenges">Challenges</NavItem>
          <NavItem href="/conversations">Conversations</NavItem>
        </HStack>

        <Spacer />

        {isLoading ? (
          <Spinner size="sm" />
        ) : isAuthenticated ? (
          <HStack spacing={3}>
            <Avatar
              size="sm"
              src={user?.picture ?? undefined}
              name={user?.name ?? undefined}
            />
            <Text display={{ base: 'none', md: 'block' }}>
              {user?.name || user?.nickname || user?.email}
            </Text>
            <Button
              size="sm"
              onClick={() =>
                logout({ logoutParams: { returnTo: window.location.origin } })
              }
            >
              Logout
            </Button>
          </HStack>
        ) : (
          <Button size="sm" onClick={signIn}>
            Login
          </Button>
        )}
      </Flex>
    </Box>
  );
}
