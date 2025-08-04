import { useMutation } from '@apollo/client';
import { ASSIGN_CONVERSATION } from '@/app/graphql/operations';
import type {
  AssignConversationMutation,
  AssignConversationMutationVariables,
} from '@/app/graphql/types';
import { useToast } from '@chakra-ui/react';

export function useAssignConversation(onAssigned?: () => void) {
  const toast = useToast();
  const [mutate, { loading }] = useMutation<
    AssignConversationMutation,
    AssignConversationMutationVariables
  >(ASSIGN_CONVERSATION, {
    update: (cache, { data }) => {
      const assignedConv = data?.assignConversation?.conversation;
      if (!assignedConv) return;
      // Update the conversation list in the cache
      cache.modify({
        fields: {
          conversationsPaged(existing) {
            // conversationsPaged has shape { total, items }
            const updatedItems = existing.items.map((item: any) =>
              item.id === assignedConv.id ? { ...item, ...assignedConv } : item
            );
            return { ...existing, items: updatedItems };
          },
        },
      });
    },
    onCompleted: () => {
      toast({
        title: 'Conversation assigned!',
        status: 'success',
        duration: 2000,
      });
      onAssigned?.();
    },
    onError: (e) => {
      toast({
        title: e.message.includes('forbidden')
          ? 'Only support agents can assign.'
          : 'Failed to assign conversation',
        status: 'error',
        duration: 2500,
      });
    },
  });

  return {
    assignConversation: (id: number) =>
      mutate({ variables: { conversationId: id } }),
    assigning: loading,
  };
}
