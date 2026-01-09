import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Smart Livestock AI - Health Monitoring & Identification',
    description: 'AI-powered livestock health monitoring and animal identification system for farmers and veterinarians. Optimized for rural environments.',
    keywords: ['livestock', 'AI', 'health monitoring', 'animal detection', 'farming', 'veterinary'],
    authors: [{ name: 'Smart Livestock AI Team' }],
    viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
    themeColor: '#22c55e',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <head>
                <link rel="icon" href="/icon.svg" type="image/svg+xml" />
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
            </head>
            <body className="antialiased">
                {children}
            </body>
        </html>
    );
}
