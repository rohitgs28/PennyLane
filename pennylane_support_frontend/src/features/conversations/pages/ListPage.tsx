'use client'; 
import React from 'react';
import { Box, Heading, Spinner, Text } from '@chakra-ui/react';
import { useAuthUser } from '@/app/lib/useAuthUser';
import { useQuery } from '@apollo/client';
import { GET_ASSIGNED_USERS } from '@/app/graphql/operations';
import { useConversations } from '../hooks/useConversations';
import { ConversationFilters } from '../components/ConversationFilters';
import { ConversationCard } from '../components/ConversationCard';
import { PaginationControls } from '../components/PaginationControls';
import { ConversationSummary  } from '@/types/domain';

export default function ConversationsListPage() {
  const { isAuthenticated, roles } = useAuthUser();
  const isAgent = isAuthenticated && roles?.includes('support_admin');

  // fetch list of assignable users once for filter dropdown
  const { data: usersData } = useQuery(GET_ASSIGNED_USERS);
  const users = usersData?.assignedUsers ?? [];

  // local filters / paging state
  const [filters, setFilters] = React.useState({
    searchTerm: '',
    statusFilter: undefined as string | undefined,
    categoryFilter: undefined as string | undefined,
    assigneeId: undefined as number | undefined,
  });
  const [page, setPage] = React.useState(1);

  // conversations query
  const { conversations, total, loading, refetch } = useConversations({ ...filters, page, });

  // when filters change reset to first page & refetch
 const updateFilters = (partial: Partial<typeof filters>) => {
    setFilters((cur) => ({ ...cur, ...partial }));
    setPage(1);
    refetch();
  };

  return (
    <Box maxW="6xl" mx="auto" p={4}>
      <Heading mb={6}>Conversations</Heading>
      <ConversationFilters
        {...filters}
        onChange={updateFilters}
        isAgent={isAgent}
        users={users}
      />
      {loading ? (
        <Spinner />
      ) : (
        <>
          <Box display="grid" gap={6}>
            {conversations.map((c: ConversationSummary ) => (
              <ConversationCard key={c.id} conversation={c} onAssigned={() => refetch()} />
            ))}
            {conversations.length === 0 && <Text>No conversations match your filters.</Text>}
          </Box>
          {total > 0 && (
            <PaginationControls page={page} total={total} perPage={20} onChange={(p) => { setPage(p); refetch(); }} />
          )}
        </>
      )}
    </Box>
  );
}
