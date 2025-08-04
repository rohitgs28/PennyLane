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

/**
 * Variables controlling the conversations query.
 *
 * @property searchTerm    Optional search keyword to filter conversation topics.
 * @property statusFilter  Optional status (e.g. "ASSIGNED", "OPEN") to filter by.
 * @property categoryFilter Optional category slug to filter conversations by type.
 * @property assigneeId     Optional user ID to filter conversations assigned to a specific agent.
 * @property page           The current page number (1-indexed) for pagination.
 */

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