import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone only for Docker (Render/Fly). Vercel uses its own Next runtime.
  ...(process.env.DOCKER_BUILD === "1" ? { output: "standalone" as const } : {}),
};

export default nextConfig;
