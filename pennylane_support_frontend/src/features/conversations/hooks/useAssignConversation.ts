

import { useMutation } from '@apollo/client';
import { ASSIGN_CONVERSATION } from '@/app/graphql/operations';
import { useToast } from '@chakra-ui/react';

export function useAssignConversation(onAssigned?: () => void) {
  const toast = useToast();
  const [mutate, { loading }] = useMutation(ASSIGN_CONVERSATION, {
    onCompleted: () => {
      toast({ title: 'Conversation assigned!', status: 'success', duration: 2000 });
      onAssigned?.();
    },
    onError: (e) => {
      toast({
        title: e.message.includes('forbidden') ? 'Only support agents can assign.' : 'Failed to assign conversation',
        status: 'error',
        duration: 2500,
      });
    },
  });

  return { assignConversation: (id: number) => mutate({ variables: { conversationId: id } }), assigning: loading };
}
