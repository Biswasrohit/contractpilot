import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  webpack: (config) => {
    // react-pdf requires canvas to be disabled in SSR
    config.resolve.alias.canvas = false;
    return config;
  },
};

export default nextConfig;
