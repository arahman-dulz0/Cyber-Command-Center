import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { PageShell } from "@/components/page-shell";
import { docSlugs, docTitle, renderDoc } from "@/lib/content";

export function generateStaticParams() {
  return docSlugs().map((slug) => ({ slug }));
}

export const dynamicParams = false;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return { title: `${docTitle(slug)} — Cyber Command Center docs` };
}

export default async function DocPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const html = renderDoc(slug);
  if (!html) notFound();

  return (
    <PageShell>
      <Link
        href="/docs"
        className="mb-6 inline-block text-xs uppercase tracking-widest text-faint transition-colors hover:text-cyan"
      >
        Documentation
      </Link>
      <article className="prose" dangerouslySetInnerHTML={{ __html: html }} />
    </PageShell>
  );
}
