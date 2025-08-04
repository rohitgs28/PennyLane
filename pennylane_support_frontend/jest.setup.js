// Add jest-dom matchers
import '@testing-library/jest-dom';

// Mock Next.js Link using plain JS (no JSX/TS)
jest.mock('next/link', () => ({
  __esModule: true,

  default: ({ href = '#', children }) => {
    const child = Array.isArray(children) ? children[0] : children;
    return child?.type === 'a'
      ? child
      : <a href={typeof href === 'string' ? href : '#'}>{children}</a>;
  },
}));



jest.mock('next/link', () => ({
  __esModule: true,
  //   ⬇⬇ render children unchanged — no extra <a>
  default: ({ children }) => children,
}));