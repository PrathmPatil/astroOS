import type { Metadata } from "next";
import { HomeApp } from "@/components/HomeApp";
import { JsonLd } from "@/components/JsonLd";
import { SITE_NAME, SITE_TAGLINE, SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: `${SITE_NAME} — Vedic Astrology Operating System`,
  description: SITE_TAGLINE,
  alternates: { canonical: SITE_URL },
};

export default function HomePage() {
  return (
    <>
      <JsonLd />
      {/* SSR-visible copy for crawlers before client hydration */}
      <noscript>
        <main>
          <h1>AstroOS — Vedic Astrology Operating System</h1>
          <p>{SITE_TAGLINE}</p>
          <p>
            Birth charts, Gun Milan, marriage analysis, and Explain Every Prediction with
            classical sources.
          </p>
        </main>
      </noscript>
      <HomeApp />
    </>
  );
}
