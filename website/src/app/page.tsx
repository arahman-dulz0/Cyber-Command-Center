import { Nav } from "@/components/nav";
import { Hero } from "@/components/hero";
import { Stats } from "@/components/stats";
import { Why } from "@/components/why";
import { Modules } from "@/components/modules";
import { Architecture } from "@/components/architecture";
import { Roadmap } from "@/components/roadmap";
import { Install } from "@/components/install";
import { Demo } from "@/components/demo";
import { TechStack } from "@/components/tech-stack";
import { OpenSource } from "@/components/open-source";
import { Docs } from "@/components/docs";
import { Footer } from "@/components/footer";

const JSONLD = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "Cyber Command Center OSS",
  applicationCategory: "SecurityApplication",
  operatingSystem: "Docker, Linux",
  description:
    "Open-source, self-hosted AI cybersecurity operations platform for threat intelligence, learning, automation and security operations.",
  offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
  license: "https://opensource.org/licenses/MIT",
};

export default function Home() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(JSONLD) }}
      />
      <Nav />
      <main>
        <Hero />
        <Stats />
        <Why />
        <Modules />
        <Architecture />
        <Roadmap />
        <Install />
        <Demo />
        <TechStack />
        <OpenSource />
        <Docs />
      </main>
      <Footer />
    </>
  );
}
