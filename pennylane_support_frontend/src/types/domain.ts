
export interface SupportUser {
  id: number;
  username?: string;
  email?: string;
}

export interface ChallengeSummary {
  id: number;
  publicId: string;
  title: string;
  category: string;
  difficulty: string;
  points: number;
  description: string;
  assignedSupport?: SupportUser | null;
}

export interface ConversationSummary {
  id: number;
  topic: string;
  category: string;
  status: 'OPEN' | 'ASSIGNED' | 'RESOLVED' | 'CLOSED';
  createdAt: string;
  challenge?: Pick<ChallengeSummary, 'title'> | null;
  assignedSupport?: SupportUser | null;
}
