import React from 'react';
import NextLink from 'next/link';
import {
  Box,
  Button,
  Heading,
  Tag,
  Text,
  Link as ChakraLink,
} from '@chakra-ui/react';
import { useAssignConversation } from '../hooks/useAssignConversation';
import { useAuthUser } from '@/app/lib/useAuthUser';
import type { ConversationSummary } from '@/types/domain'; 

interface Props {
  conversation: ConversationSummary;
  onAssigned: () => void;
}

export const ConversationCard: React.FC<Props> = ({
  conversation,
  onAssigned,
}) => {
  const { isAuthenticated, roles } = useAuthUser();
  const isAgent = isAuthenticated && roles?.includes('support_admin');
  const { assignConversation, assigning } = useAssignConversation(onAssigned);


  return (
    <ChakraLink
      as={NextLink}
      href={`/conversations/${conversation.id}`}
      _hover={{ textDecoration: 'none' }}   // keep box hover only
    >
      <Box p={4} borderWidth="1px" borderRadius="md" _hover={{ bg: 'gray.50' }}>
        <Heading size="sm">{conversation.topic}</Heading>

        <Text color="gray.600" mt={1}>
          {conversation.category} • {conversation.status} •{' '}
          {new Date(conversation.createdAt).toLocaleString()}
        </Text>

        <Text mt={1} fontSize="sm" color="gray.500">
          {conversation.challenge?.title
            ? `Challenge: ${conversation.challenge.title}`
            : 'No challenge linked'}
        </Text>

        {conversation.assignedSupport ? (
          <Tag size="sm" mt={2} colorScheme="green">
            {`Assigned to ${conversation.assignedSupport.username ??
              conversation.assignedSupport.email
              }`}
          </Tag>
        ) : isAgent ? (
          <Button
            size="xs"
            mt={2}
            onClick={(e) => {
              e.preventDefault();           // stay on list page
              assignConversation(conversation.id);
            }}
            isLoading={assigning}
          >
            Assign to me
          </Button>
        ) : (
          <Tag size="sm" mt={2}>
            UNASSIGNED
          </Tag>
        )}
      </Box>
    </ChakraLink>
  );
};

