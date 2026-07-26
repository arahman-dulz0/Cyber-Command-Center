import type { Metadata, Viewport } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const space = Space_Grotesk({
  variable: "--font-space",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
});
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});
const jbmono = JetBrains_Mono({
  variable: "--font-jbmono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

// Resolve the canonical origin: explicit env → Vercel deploy URL → production domain.
const SITE =
  process.env.NEXT_PUBLIC_SITE_URL ??
  (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "https://cybercommandcenter.dev");
const TITLE = "Cyber Command Center OSS — AI Cybersecurity Operations Platform";
const DESC =
  "Open-source, self-hosted AI security operations platform. Correlates CVEs with EPSS, CISA KEV, ExploitDB and GitHub PoCs, runs autonomous intelligence collection, RAG over your own notes, a multi-agent report crew, and closed-loop remediation — all on local infrastructure with Ollama.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE),
  title: TITLE,
  description: DESC,
  applicationName: "Cyber Command Center OSS",
  keywords: [
    "cybersecurity",
    "threat intelligence",
    "SOC",
    "self-hosted",
    "open source",
    "CVE",
    "EPSS",
    "CISA KEV",
    "Ollama",
    "RAG",
    "security automation",
  ],
  authors: [{ name: "Cyber Command Center OSS" }],
  openGraph: {
    type: "website",
    url: SITE,
    title: TITLE,
    description: DESC,
    siteName: "Cyber Command Center OSS",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESC,
  },
  robots: { index: true, follow: true },
  alternates: { canonical: SITE },
};

export const viewport: Viewport = {
  themeColor: "#05070d",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${space.variable} ${inter.variable} ${jbmono.variable}`}
    >
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
