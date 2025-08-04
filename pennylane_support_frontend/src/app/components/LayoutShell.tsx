'use client';
import { ReactNode } from 'react';
import { Box, Container } from '@chakra-ui/react';

type Props = { children: ReactNode; maxW?: string | number; pt?: number | string; pb?: number | string; };

export default function LayoutShell({ children, maxW = '6xl', pt = 10, pb = 14 }: Props) {
  return (
    <Box as="main">
      <Container maxW={maxW} pt={pt} pb={pb}>
        {children}
      </Container>
    </Box>
  );
}
