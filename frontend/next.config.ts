import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  ...(process.env.DOCKER_BUILD === "1" ? { output: "standalone" as const } : {}),
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
