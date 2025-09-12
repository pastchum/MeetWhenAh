/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add HTTPS for local development
  ...(process.env.NODE_ENV === 'development' && {
    server: {
      https: {
        key: './localhost+2-key.pem',
        cert: './localhost+2.pem',
      },
    },
  }),
};

export default nextConfig;