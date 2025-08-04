'use client';

import { Button } from '@chakra-ui/react';
import { useAuthUser } from '@/app/lib/useAuthUser';
import { useAssignConversation } from '@/features/conversations/hooks/useAssignConversation';

/**
 * Shows an “Assign to me” button to support agents.
 *
 * Hidden when the conversation is already assigned or the
 * current user lacks the `support_admin` role.
 */
type Props = {
  conversationId: number;
  assigned?: boolean;
  /** optional callback so parent list pages can refetch after a mutation */
  onAssigned?: () => void;
};

export default function AssignButton({ conversationId, assigned, onAssigned }: Props) {
  const { isAuthenticated, roles, signIn } = useAuthUser();
  const isAgent = isAuthenticated && roles?.includes('support_admin');

  // nothing to do if user isn’t an agent or the conversation is taken
  if (!isAgent || assigned) return null;

  const { assignConversation, assigning } = useAssignConversation(onAssigned);

  const handleClick = () => {
    if (!isAuthenticated) {
      // delegate to your Auth0/Supertokens sign-in flow
      signIn();
      return;
    }
    assignConversation(conversationId);
  };

  return (
    <Button size="sm" onClick={handleClick} isLoading={assigning}>
      Assign&nbsp;to&nbsp;me
    </Button>
  );
}
