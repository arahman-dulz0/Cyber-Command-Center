import type { MetadataRoute } from "next";
import { docSlugs } from "@/lib/content";
import { postSlugs } from "@/lib/blog";

const BASE = "https://cybercommandcenter.dev";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: BASE, lastModified: now, changeFrequency: "monthly", priority: 1 },
    { url: `${BASE}/docs`, lastModified: now, changeFrequency: "monthly", priority: 0.8 },
    { url: `${BASE}/api-reference`, lastModified: now, changeFrequency: "monthly", priority: 0.7 },
    { url: `${BASE}/demo`, lastModified: now, changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE}/blog`, lastModified: now, changeFrequency: "weekly", priority: 0.7 },
  ];
  const docRoutes: MetadataRoute.Sitemap = docSlugs().map((slug) => ({
    url: `${BASE}/docs/${slug}`,
    lastModified: now,
    changeFrequency: "monthly",
    priority: 0.6,
  }));
  const blogRoutes: MetadataRoute.Sitemap = postSlugs().map((slug) => ({
    url: `${BASE}/blog/${slug}`,
    lastModified: now,
    changeFrequency: "monthly",
    priority: 0.6,
  }));
  return [...staticRoutes, ...docRoutes, ...blogRoutes];
}
