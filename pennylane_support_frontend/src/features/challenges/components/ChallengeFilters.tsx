import React from 'react';
import { HStack, Input, Select, Button } from '@chakra-ui/react';


interface Props {
  searchTerm: string;
  tagFilter?: string;
  onChange: (

    partial: {
      searchTerm?: string;
      tagFilter?: string;
    }

  ) => void;
}

export const ChallengeFilters: React.FC<Props> = ({ searchTerm, tagFilter, onChange }) => (

  <HStack spacing={4} mb={6} wrap="wrap">
    <Input placeholder="Search title or description…" value={searchTerm} onChange={(e) => onChange({ searchTerm: e.target.value })} width="320px" />
    <Select placeholder="Filter by tag" value={tagFilter ?? ''} onChange={(e) => onChange({ tagFilter: e.target.value || undefined })} width="220px">
      <option value="basics">basics</option>
      <option value="optimization">optimization</option>
      <option value="observables">observables</option>
    </Select>
    <Button variant="outline" onClick={() => onChange({ searchTerm: '', tagFilter: undefined })}>Reset</Button>
  </HStack>

);