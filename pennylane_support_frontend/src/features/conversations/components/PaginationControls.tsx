import { Button, HStack, Text } from '@chakra-ui/react';
import React from 'react';

interface Props {
  page: number;
  total: number;
  perPage: number;
  onChange: (page: number) => void;
}

export const PaginationControls: React.FC<Props> = ({ page, total, perPage, onChange }) => {
  const totalPages = Math.max(1, Math.ceil(total / perPage));
  const hasPrev = page > 1;
  const hasNext = page < totalPages;
  return (
    <HStack>
      <Button onClick={() => hasPrev && onChange(page - 1)} isDisabled={!hasPrev}>Prev</Button>
      <Text>Page {page} / {totalPages}</Text>
      <Button onClick={() => hasNext && onChange(page + 1)} isDisabled={!hasNext}>Next</Button>
    </HStack>
  );
};
