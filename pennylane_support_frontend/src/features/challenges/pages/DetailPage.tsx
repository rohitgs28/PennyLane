"use client";

import React from 'react';
import {
  Box,
  Button,
  Divider,
  Heading,
  HStack,
  Input,
  Tag,
  Text,
  Textarea,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { useParams } from 'next/navigation';
import { useChallenge } from '../hooks/useChallenge';
import { useCreateConversation } from '@/features/conversations/hooks/useCreateConversation';
import AssignButton from '@/app/components/AssignButton';
import { useMutation } from '@apollo/client';
import { ADD_POST } from '@/app/graphql/operations';
import { useAuthUser } from '@/app/lib/useAuthUser';
import LayoutShell from '@/app/components/LayoutShell';

export default function ChallengeDetailPage() {
  const { publicId } = useParams<{ publicId: string }>();
  const { data, loading, refetch } = useChallenge(publicId);
  const toast = useToast();
  const challenge = data?.challenge;


  const { user, isAuthenticated } = useAuthUser();
  const displayName = user?.name || user?.nickname || user?.email || 'User';
  const isLoggedIn = !!isAuthenticated;
  const [topic, setTopic] = React.useState('');
  const [category, setCategory] = React.useState('PennyLane Help');
  const [firstPost, setFirstPost] = React.useState('');
  const { createConversation, creating } = useCreateConversation(() => {
    setTopic('');
    setFirstPost('');
    refetch();
  });
  const startConversation = () => {
    if (!topic.trim() || !category.trim() || !firstPost.trim()) {
      toast({
        title: 'Please fill in topic, category and description.',
        status: 'warning',
      });
      return;
    }
    createConversation({
      variables: {
        challengePublicId: publicId,
        topic: topic.trim(),
        category: category.trim(),
        firstPost: firstPost.trim(),
        authorDisplayName: displayName,
      },
    });
  };

  const [replyById, setReplyById] = React.useState<Record<number, string>>({});
  const [addPost, { loading: replying }] = useMutation(ADD_POST, {
    onCompleted: () => {
      toast({ title: 'Reply posted', status: 'success' });
      setReplyById({});
      refetch();
    },
    onError: (e) =>
      toast({ title: 'Reply failed', description: e.message, status: 'error' }),
  });
  const reply = (convId: number) => {
    const content = (replyById[convId] || '').trim();
    if (!content) {
      toast({ title: 'Enter a reply first.', status: 'warning' });
      return;
    }
    addPost({
      variables: {
        conversationId: convId,
        content,
        authorDisplayName: displayName,
      },
    });
  };

  if (loading) return <Text>Loading…</Text>;
  if (!challenge) return <Text>Challenge not found.</Text>;

  return (
  <LayoutShell maxW="4xl">
    <Box>
      <Heading mb={2}>{challenge.title}</Heading>
      <Text color="gray.600">
        {challenge.category} • {challenge.difficulty} • {challenge.points} pts
      </Text>
      <HStack mt={2} spacing={2}>
        {(challenge.tags ?? []).map((t: any) => (
          <Tag key={t.name}>{t.name}</Tag>
        ))}
      </HStack>
      <Text mt={4}>{challenge.description}</Text>
      <Divider my={6} />
      <Heading size="md" mb={3}>
        Start a conversation
      </Heading>
      <VStack align="stretch" spacing={3}>
        <Input
          placeholder="Topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          isDisabled={!isLoggedIn}
        />
        <Input
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          isDisabled={!isLoggedIn}
        />
        <Textarea
          placeholder="Describe your issue…"
          value={firstPost}
          onChange={(e) => setFirstPost(e.target.value)}
          isDisabled={!isLoggedIn}
        />
        <Button
          onClick={startConversation}
          isLoading={creating}
          colorScheme="blue"
          isDisabled={!isLoggedIn}
        >
          Create
        </Button>
      </VStack>
      <Divider my={6} />
      <Heading size="md" mb={3}>
        Conversations
      </Heading>
      {challenge.conversations?.length ? (
        <VStack align="stretch" spacing={4}>
          {challenge.conversations.map((c: any) => (
            <Box key={c.id} borderWidth="1px" borderRadius="md" p={4}>
              <Heading size="sm">{c.topic}</Heading>
              <Text color="gray.600" mt={1}>
                {c.category} • {c.status} •{' '}
                {new Date(c.createdAt).toLocaleString()}
              </Text>
              <HStack mt={2} spacing={3}>
                <AssignButton
                  conversationId={c.id}
                  onAssigned={() => refetch()}
                />
              </HStack>
              {c.posts?.map((p: any) => (
                <Box
                  key={p.id}
                  bg="gray.50"
                  borderRadius="md"
                  p={3}
                  mt={3}
                >
                  <Text>{p.content}</Text>
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {p.authorDisplayName || 'User'} •{' '}
                    {new Date(p.createdAt).toLocaleString()}
                  </Text>
                </Box>
              ))}
              <HStack mt={3} spacing={3} align="flex-start">
                <Textarea
                  placeholder="Reply…"
                  value={replyById[c.id] || ''}
                  onChange={(e) =>
                    setReplyById((s) => ({ ...s, [c.id]: e.target.value }))
                  }
                  isDisabled={!isLoggedIn}
                />
                <Button
                  onClick={() => reply(c.id)}
                  isLoading={replying}
                  isDisabled={!isLoggedIn}
                >
                  Reply
                </Button>
              </HStack>
            </Box>
          ))}
        </VStack>
      ) : (
        <Text>No conversations yet.</Text>
      )}
    </Box>
    </LayoutShell>
  );
}