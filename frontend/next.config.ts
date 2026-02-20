import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export for deployment (no SSR support)
  output: 'export',
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
