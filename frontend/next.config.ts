import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  experimental: {
    optimizeServerReact: true,
    optimizeCss: true,
    optimisticClientCache: true,
    appDocumentPreloading: true,
  },

}

export default nextConfig
