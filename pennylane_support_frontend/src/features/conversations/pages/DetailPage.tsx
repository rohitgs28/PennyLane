'use client'; 
import React from 'react';
import { useParams } from 'next/navigation';
import { Box, Button, Heading, Spinner, Tag, Text, Textarea, VStack } from '@chakra-ui/react';
import { useQuery, useMutation } from '@apollo/client';
import { GET_CONVERSATION, ADD_POST } from '@/app/graphql/operations';
import { useAuthUser } from '@/app/lib/useAuthUser';

export default function ConversationDetailPage() {
  const params = useParams<{ id: string }>();
  const conversationId = Number(params?.id);
  const { user, isAuthenticated } = useAuthUser();
  const displayName = user?.name || user?.nickname || user?.email || 'User';

  const { data, loading, refetch } = useQuery(GET_CONVERSATION, {
    variables: { id: conversationId },
    skip: isNaN(conversationId),
  });

  const [message, setMessage] = React.useState('');
  const [addPost, { loading: posting }] = useMutation(ADD_POST, {
    onCompleted: () => { setMessage(''); refetch(); },
  });

  if (loading) return <Spinner />;
  const conv = data?.conversation;
  if (!conv) return <Text>Conversation not found.</Text>;

  const sendReply = () => {
    if (!message.trim()) return;
    addPost({ variables: { conversationId: conv.id, content: message.trim(), authorDisplayName: displayName } });
  };

  return (
    <Box maxW="4xl" mx="auto" p={4}>
      <Heading>{conv.topic}</Heading>
      <Text color="gray.600" mt={1}>{conv.category} • {conv.status} • {new Date(conv.createdAt).toLocaleString()}</Text>
      {conv.assignedSupport && (
        <Tag size="sm" mt={2} colorScheme="green">Assigned to {conv.assignedSupport.username ?? conv.assignedSupport.email}</Tag>
      )}
      <Text mt={4} fontSize="sm" color="gray.500">{conv.challenge?.title ? `Challenge: ${conv.challenge.title}` : 'No challenge linked'}</Text>
      <VStack align="stretch" spacing={3} mt={6}>{conv.posts.map((p: any) => (
        <Box key={p.id} p={3} bg="gray.50" borderRadius="md"><Text fontSize="sm">{p.content}</Text><Text fontSize="xs" color="gray.500" mt={1}>{p.authorDisplayName} • {new Date(p.createdAt).toLocaleString()}</Text></Box>))}</VStack>
      {isAuthenticated && (
        <Box mt={6}><Textarea placeholder="Reply…" value={message} onChange={(e) => setMessage(e.target.value)} mb={2}/><Button onClick={sendReply} isLoading={posting}>Send</Button></Box>
      )}
    </Box>
  );
}