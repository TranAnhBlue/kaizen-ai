import type { ReactNode } from 'react';
import './globals.css';
export const metadata = { title: 'Kaizen AI', description: 'Nền tảng cải tiến liên tục' };
export default function RootLayout({ children }: { children: ReactNode }) { return <html lang="vi"><body>{children}</body></html>; }
