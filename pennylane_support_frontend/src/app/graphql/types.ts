
export interface AssignConversationMutation {
    assignConversation?: {
      ok: boolean;
      conversation?: {
        id: number;
        status: string;
        assignedSupport?: {
          id: number;
          username?: string | null;
          email?: string | null;
        } | null;
      } | null;
    } | null;
  }
  
  export interface AssignConversationMutationVariables {
    conversationId: number;
  }
  