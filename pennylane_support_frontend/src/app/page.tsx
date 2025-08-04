"use client";

import React from 'react';
import NextLink from 'next/link';
import {
  Box,
  Button,
  Heading,
  HStack,
  Text,
  VStack,
  Link as ChakraLink,
} from '@chakra-ui/react';
import { useAuthUser } from '@/app/lib/useAuthUser';


export default function HomePage() {
  const { isAuthenticated, user, signIn } = useAuthUser();

  return (
    <Box px={6} py={8} maxW="6xl" mx="auto">
      <Heading mb={4}>Welcome to PennyLane Support</Heading>
      <Text fontSize="lg" mb={6} color="gray.600">
        Your hub for tackling quantum computing challenges and sharing knowledge with the community.
      </Text>
      {!isAuthenticated ? (
        <VStack align="start" spacing={4}>
          <Text fontSize="md">
            Please log in to browse conversations and tackle challenges.
          </Text>
          <Button size="md" colorScheme="blue" onClick={signIn}>
            Log in
          </Button>
        </VStack>
      ) : (
        <VStack align="start" spacing={4}>
          <Text fontSize="lg">
            Hello {user?.name || user?.nickname || user?.email}!
          </Text>
          <Text>
            Use the links below to start exploring challenges and join the conversation.
          </Text>
          <HStack spacing={4}>
            <ChakraLink as={NextLink} href="/challenges">
              <Button colorScheme="teal">View Challenges</Button>
            </ChakraLink>
            <ChakraLink as={NextLink} href="/conversations">
              <Button colorScheme="purple">View Conversations</Button>
            </ChakraLink>
          </HStack>
        </VStack>
      )}
    </Box>
  );
}