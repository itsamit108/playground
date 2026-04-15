'use client';

import { useState } from 'react';
import * as stylex from '@stylexjs/stylex';

const fadeIn = stylex.keyframes({
    from: { opacity: 0, transform: 'translateY(-8px)' },
    to: { opacity: 1, transform: 'translateY(0)' },
});

const styles = stylex.create({
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '24px',
        backgroundColor: {
            default: '#ffffff',
            '@media (prefers-color-scheme: dark)': '#0a0a0a',
        },
        fontFamily: 'system-ui, -apple-system, sans-serif',
    },
    wrapper: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '100%',
        maxWidth: '480px',
        animationName: fadeIn,
        animationDuration: '0.6s',
        animationTimingFunction: 'ease-out',
    },
    title: {
        fontSize: {
            default: '24px',
            '@media (min-width: 680px)': '32px',
        },
        fontWeight: '500',
        letterSpacing: '-0.02em',
        marginBottom: '64px',
        color: {
            default: '#171717',
            '@media (prefers-color-scheme: dark)': '#ededed',
        },
    },
    counterDisplay: {
        fontSize: {
            default: '96px',
            '@media (min-width: 680px)': '128px',
        },
        fontWeight: '300',
        lineHeight: 1,
        letterSpacing: '-0.05em',
        marginBottom: '80px',
        fontVariantNumeric: 'tabular-nums',
        color: {
            default: '#000000',
            '@media (prefers-color-scheme: dark)': '#ffffff',
        },
    },
    buttonGroup: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '16px',
        width: '100%',
    },
    button: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '56px',
        fontSize: '16px',
        fontWeight: '500',
        borderRadius: '28px',
        borderWidth: '1px',
        borderStyle: 'solid',
        cursor: 'pointer',
        transitionProperty: 'all',
        transitionDuration: '0.2s',
        transitionTimingFunction: 'ease',
        outline: 'none',
        flexGrow: 1,
    },
    actionButton: {
        backgroundColor: {
            default: '#ffffff',
            ':hover': '#f5f5f5',
            '@media (prefers-color-scheme: dark)': {
                default: '#000000',
                ':hover': '#1a1a1a',
            }
        },
        borderColor: {
            default: '#e5e5e5',
            '@media (prefers-color-scheme: dark)': '#333333',
        },
        color: {
            default: '#171717',
            '@media (prefers-color-scheme: dark)': '#ededed',
        },
    },
    resetButton: {
        flexGrow: 0,
        flexShrink: 0,
        flexBasis: 'auto',
        paddingTop: 0,
        paddingBottom: 0,
        paddingLeft: '24px',
        paddingRight: '24px',
        backgroundColor: 'transparent',
        borderColor: 'transparent',
        color: {
            default: '#a3a3a3',
            ':hover': '#171717',
            '@media (prefers-color-scheme: dark)': {
                default: '#525252',
                ':hover': '#ededed',
            },
        },
    },
});

export default function Home() {
    const [count, setCount] = useState(0);

    return (
        <main {...stylex.props(styles.container)}>
            <div {...stylex.props(styles.wrapper)}>
                <h1 {...stylex.props(styles.title)}>Hello World!</h1>
                <div {...stylex.props(styles.counterDisplay)}>{count}</div>
                <div {...stylex.props(styles.buttonGroup)}>
                    <button
                        {...stylex.props(styles.button, styles.actionButton)}
                        onClick={() => setCount((c) => c - 1)}
                        aria-label="Decrease"
                    >
                        -
                    </button>
                    <button
                        {...stylex.props(styles.button, styles.resetButton)}
                        onClick={() => setCount(0)}
                        aria-label="Reset"
                    >
                        Reset
                    </button>
                    <button
                        {...stylex.props(styles.button, styles.actionButton)}
                        onClick={() => setCount((c) => c + 1)}
                        aria-label="Increase"
                    >
                        +
                    </button>
                </div>
            </div>
        </main>
    );
}
