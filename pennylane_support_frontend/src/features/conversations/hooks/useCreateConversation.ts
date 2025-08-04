import { useMutation } from '@apollo/client';
import { CREATE_CONVERSATION } from '@/app/graphql/operations';
import { useToast } from '@chakra-ui/react';


export function useCreateConversation(onCreated?: () => void) {
  const toast = useToast();
  const [mutate, { loading }] = useMutation(CREATE_CONVERSATION, {
    onCompleted: () => { toast({ title: 'Conversation created', status: 'success' }); onCreated?.(); },
    onError: (e) => toast({ title: 'Create failed', description: e.message, status: 'error' }),
  });
  return { createConversation: mutate, creating: loading };
}