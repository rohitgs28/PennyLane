import './globals.css';
import Providers from './providers';   // ← default import now

export const metadata = { title: 'PennyLane' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
