import { useQuery } from '@apollo/client';
import { GET_CHALLENGE } from '@/app/graphql/operations';


export function useChallenge(publicId: string) {
    return useQuery(GET_CHALLENGE, { variables: { publicId }, fetchPolicy: 'cache-and-network' });
}