

import React from 'react';
import { HStack, Input, Select, Button } from '@chakra-ui/react';
import { useConversationCategories } from '../hooks/useConversationCategories';

interface Props {
  searchTerm: string;
  statusFilter?: string;
  categoryFilter?: string;
  assigneeId?: number;
  onChange: (changes: Partial<Props>) => void;
  isAgent: boolean;
  users: import('@/types/domain').SupportUser[];
}

/**
 * Render a form of dropdowns and inputs to filter the conversation list.
 *
 * Exposes a single `onChange` handler that merges partial filter changes and lets
 * the parent component control state.  If the user is an agent, an additional
 * "Assigned to" dropdown is shown.
 */

export const ConversationFilters: React.FC<Props> = ({
  searchTerm,
  statusFilter,
  categoryFilter,
  assigneeId,
  onChange,
  isAgent,
  users,
}) => {
  const categories = useConversationCategories();
  return (
    <HStack spacing={3} mb={6} wrap="wrap">
      <Input
        placeholder="Search topic..."
        value={searchTerm}
        onChange={(e) => onChange({ searchTerm: e.target.value })}
        maxW="200px"
      />
      <Select
        placeholder="Status"
        value={statusFilter ?? ''}
        onChange={(e) =>
          onChange({ statusFilter: e.target.value || undefined })
        }
        maxW="160px"
      >
        <option value="OPEN">OPEN</option>
        <option value="ASSIGNED">ASSIGNED</option>
        <option value="RESOLVED">RESOLVED</option>
        <option value="CLOSED">CLOSED</option>
      </Select>
      <Select
        placeholder="Category"
        value={categoryFilter ?? ''}
        onChange={(e) =>
          onChange({ categoryFilter: e.target.value || undefined })
        }
        maxW="180px"
      >
        {/* Cast the map callback parameter to string to satisfy TypeScript */}
        {categories.map((c: string) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </Select>
      {isAgent && (
        <Select
          placeholder="Assigned to"
          value={assigneeId ?? ''}
          onChange={(e) =>
            onChange({
              assigneeId: e.target.value ? Number(e.target.value) : undefined,
            })
          }
          maxW="200px"
        >
          {users.map((u) => (
            <option key={u.id} value={u.id}>
              {u.name ?? u.email}
            </option>
          ))}
        </Select>
      )}
      <Button
        onClick={() =>
          onChange({
            searchTerm: '',
            statusFilter: undefined,
            categoryFilter: undefined,
            assigneeId: undefined,
          })
        }
      >
        Reset
      </Button>
    </HStack>
  );
};