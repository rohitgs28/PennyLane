import { useQuery } from '@apollo/client';
import { GET_CONVERSATION_CATEGORIES } from '@/app/graphql/operations';


/**
 * Retrieve the list of available conversation categories from the GraphQL API.
 *
 * @returns An array of category strings, or an empty array if the query has not yet returned.
 */

export function useConversationCategories() {
  const { data } = useQuery(GET_CONVERSATION_CATEGORIES);
  return data?.conversationCategories ?? [];
}
