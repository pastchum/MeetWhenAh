/** @type {import('next').NextConfig} */
const nextConfig = {
  swcMinify: true,
  experimental: {
    forceSwcTransforms: true,
  },
  rewrites: async () => {
    return [
      {
        source: '/api/:path*',
        destination: process.env.BACKEND_URL ? `${process.env.BACKEND_URL}/api/:path*` : 'http://localhost:8000/api/:path*',
      },
    ]
  },
  // Optimize for production
  output: 'standalone',
  poweredByHeader: false,
};

export default nextConfig;