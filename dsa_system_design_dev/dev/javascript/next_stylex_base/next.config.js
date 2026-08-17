/** @type {import('next').NextConfig} */
const nextConfig = {
    transpilePackages: ['@stylexjs/stylex'],
    webpack: (config) => {
        config.infrastructureLogging = { level: 'error' };
        return config;
    },
};

module.exports = nextConfig;
