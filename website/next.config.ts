import type { NextConfig } from "next";

// Fully static export — the site is 100% SSG, so we emit a plain `out/` folder
// that any static host serves with no runtime and no framework plugin. This
// sidesteps @netlify/plugin-nextjs (which can't process this Next build).
// Security headers move to public/_headers (next.config headers() don't apply
// to a static export).
const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
  poweredByHeader: false,
  reactStrictMode: true,
};

export default nextConfig;
