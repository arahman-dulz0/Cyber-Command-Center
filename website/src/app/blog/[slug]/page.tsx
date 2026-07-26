import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { PageShell } from "@/components/page-shell";
import { getPost, postSlugs, renderPost } from "@/lib/blog";

export function generateStaticParams() {
  return postSlugs().map((slug) => ({ slug }));
}

export const dynamicParams = false;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = getPost(slug);
  return {
    title: post ? `${post.title} — Cyber Command Center` : "Blog",
    description: post?.excerpt,
  };
}

function fmtDate(iso: string): string {
  return new Date(iso + "T00:00:00Z").toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  });
}

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = getPost(slug);
  if (!post) notFound();
  const html = renderPost(post.body);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.excerpt,
    datePublished: post.date,
    author: { "@type": "Organization", name: "Cyber Command Center OSS" },
    publisher: { "@type": "Organization", name: "Cyber Command Center OSS" },
  };

  return (
    <PageShell>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <Link
        href="/blog"
        className="mb-6 inline-block text-xs uppercase tracking-widest text-faint transition-colors hover:text-cyan"
      >
        Blog
      </Link>
      <div className="eyebrow mb-3">{fmtDate(post.date)}</div>
      <h1 className="font-display text-3xl font-semibold tracking-tight text-ink md:text-4xl">
        {post.title}
      </h1>
      <article
        className="prose mt-8"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </PageShell>
  );
}
