"use client";

import React from 'react';
import { Box, Divider, Heading, SimpleGrid, Spinner, Text } from '@chakra-ui/react';
import LayoutShell from '@/app/components/LayoutShell';
import { useChallenges } from '../hooks/useChallenges';
import { ChallengeCard } from '../components/ChallengeCard';
import { ChallengeFilters } from '../components/ChallengeFilters';
import { PaginationControls } from '../../conversations/components/PaginationControls';
import type { ChallengeSummary } from '@/types/domain';


export default function ChallengesListPage() {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [tagFilter, setTagFilter] = React.useState<string | undefined>();
  const [page, setPage] = React.useState(1);
  const { challenges, total, loading, refetch } = useChallenges(
    searchTerm,
    tagFilter,
    page
  );

  const update = (partial: Partial<{
    searchTerm: string;
    tagFilter: string | undefined;
  }>) => {
    setPage(1);
    if (partial.searchTerm !== undefined) setSearchTerm(partial.searchTerm);
    if (partial.tagFilter !== undefined) setTagFilter(partial.tagFilter);
    refetch();
  };

  return (
    <LayoutShell>
      <Box>
        <Heading mb={6}>Coding Challenges</Heading>
        <ChallengeFilters
          searchTerm={searchTerm}
          tagFilter={tagFilter}
          onChange={update}
        />
        {loading ? (
          <Spinner />
        ) : (
          <>
            <SimpleGrid
              columns={{ base: 1, md: 2, lg: 3 }}
              spacing={4}
            >
              {challenges.map((ch: ChallengeSummary) => (
                <ChallengeCard key={ch.id} challenge={ch} />
              ))}
              {challenges.length === 0 && <Text>No challenges found.</Text>}
            </SimpleGrid>
            <Divider my={6} />
            <PaginationControls
              page={page}
              total={total}
              perPage={12}
              onChange={(p) => {
                setPage(p);
                refetch();
              }}
            />
          </>
        )}
      </Box>
    </LayoutShell>
  );
}