import { useQuery } from '@apollo/client';
import { LIST_CHALLENGES_PAGED } from '@/app/graphql/operations';


export const CHALLENGE_PAGE_SIZE = 12 as const;


export function useChallenges(searchTerm: string, tagFilter: string | undefined, page: number) {
    const { data, loading, refetch } = useQuery(LIST_CHALLENGES_PAGED, {
        variables: { search: searchTerm, tag: tagFilter, page, pageSize: CHALLENGE_PAGE_SIZE },
        notifyOnNetworkStatusChange: true,
    });
    return { challenges: data?.challengesPaged?.items ?? [], total: data?.challengesPaged?.total ?? 0, loading, refetch };
}
