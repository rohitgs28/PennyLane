import { useQuery } from '@apollo/client';
import { LIST_CONVERSATIONS_PAGED } from '@/app/graphql/operations';

export const CONV_PAGE_SIZE = 20 as const;

export interface ConversationsQueryVars {
  searchTerm?: string;
  statusFilter?: string;
  categoryFilter?: string;
  assigneeId?: number;
  page: number;
}

export function useConversations(vars: ConversationsQueryVars) {
  const { data, loading, networkStatus, refetch } = useQuery(LIST_CONVERSATIONS_PAGED, {
    variables: {
      search: vars.searchTerm,
      status: vars.statusFilter,
      category: vars.categoryFilter,
      assignedToUserId: vars.assigneeId,
      page: vars.page,
      pageSize: CONV_PAGE_SIZE,
    },
    notifyOnNetworkStatusChange: true,
  });

  return {
    conversations: data?.conversationsPaged.items ?? [],
    total: data?.conversationsPaged.total ?? 0,
    loading: loading && networkStatus === 1,
    refetch,
  };
}