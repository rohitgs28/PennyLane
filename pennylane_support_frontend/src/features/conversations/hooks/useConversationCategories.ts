import { useQuery } from '@apollo/client';
import { GET_CONVERSATION_CATEGORIES } from '@/app/graphql/operations';

export function useConversationCategories() {
  const { data } = useQuery(GET_CONVERSATION_CATEGORIES);
  return data?.conversationCategories ?? [];
}
