import * as stylex from '@stylexjs/stylex';
import './globals.css';

const styles = stylex.create({
    html: {
        colorScheme: 'light dark',
    },
    body: {
        fontFamily: 'system-ui, sans-serif',
        margin: 0,
        padding: 0,
        backgroundColor: {
            default: '#ffffff',
            '@media (prefers-color-scheme: dark)': '#1a1a1a',
        },
        color: {
            default: '#000000',
            '@media (prefers-color-scheme: dark)': '#ffffff',
        },
    },
});

export const metadata = {
    title: 'Hello World Counter',
    description: 'A Next.js counter built with StyleX',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" {...stylex.props(styles.html)} suppressHydrationWarning>
            <body {...stylex.props(styles.body)}>{children}</body>
        </html>
    );
}
