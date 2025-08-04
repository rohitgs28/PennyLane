"use client";

import React from 'react';
import { Box, Heading, Text, Tag, Link as ChakraLink } from '@chakra-ui/react';
import { ChallengeSummary } from '@/types/domain';
import { useAuthUser } from '@/app/lib/useAuthUser';
import NextLink from 'next/link';
import LayoutShell from '@/app/components/LayoutShell';


interface Props {
  challenge: ChallengeSummary;
}

export const ChallengeCard: React.FC<Props> = ({ challenge }) => {
 
  const { isAuthenticated, roles, user } = useAuthUser();
  const isAgent = isAuthenticated && roles?.includes('support_admin');

  return (
   <LayoutShell>
    <ChakraLink
      as={NextLink}
      href={`/challenges/${challenge.publicId}`}
      _hover={{ textDecoration: 'none' }}
    >
      <Box
        borderWidth="1px"
        borderRadius="md"
        p={4}
        _hover={{ boxShadow: 'md' }}
      >
        <Heading size="sm">{challenge.title}</Heading>
        <Text color="gray.600" mt={1}>
          {challenge.category} • {challenge.difficulty} • {challenge.points} pts
        </Text>
        <Text mt={3}>{challenge.description}</Text>

        {challenge.assignedSupport && (
          <Tag size="sm" mt={2} colorScheme="green">
            Assigned to{' '}
            {challenge.assignedSupport.username ??
              challenge.assignedSupport.email}
          </Tag>
        )}
      </Box>
    </ChakraLink>
    
    </LayoutShell>
  );
};