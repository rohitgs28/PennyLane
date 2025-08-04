import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  fonts: {
    heading:
      'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
    body:
      'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
  },
  colors: {
    brand: {
      50:  '#e6f2ff',
      100: '#cfe7ff',
      200: '#a6d2ff',
      300: '#73b6ff',
      400: '#3f99f0',
      500: '#0074E0', // ← requested blue
      600: '#0068c8',
      700: '#0056a3',
      800: '#00437d',
      900: '#002b4f',
    },
    gray: {
      50:  '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
  },
  components: {
    Button: {
      baseStyle: { borderRadius: 'lg' },
      defaultProps: { colorScheme: 'brand' }, 
    },
    Badge: {
      baseStyle: { borderRadius: 'md', px: 2, py: 0.5 },
    },
    Container: {
      baseStyle: { px: 6 },
    },
  },
  styles: {
    global: {
      'html, body': { bg: 'white', color: 'gray.900' },
      '::selection': { background: 'brand.200' },
    },
  },
});

export default theme;
