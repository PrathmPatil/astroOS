import type { Metadata } from "next";
import Link from "next/link";
import { SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "About",
  description:
    "AstroOS is an auditable Vedic astrology operating system. Evidence → Rule → Classical Source → AI Explanation → Confidence. AI never invents predictions.",
  alternates: { canonical: `${SITE_URL}/about` },
};

export default function AboutPage() {
  return (
    <main className="sky-wash min-h-screen">
      <header className="mx-auto flex max-w-3xl items-center justify-between px-6 py-6">
        <Link href="/" className="font-display text-2xl font-semibold text-ink">
          AstroOS
        </Link>
        <Link href="/" className="text-sm font-medium text-ink/70 hover:text-ink">
          Open app
        </Link>
      </header>

      <article className="mx-auto max-w-3xl px-6 pb-20 pt-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-copper">About</p>
        <h1 className="mt-3 font-display text-4xl font-semibold text-ink md:text-5xl">
          Vedic Astrology Operating System
        </h1>
        <p className="mt-6 text-lg leading-relaxed text-ink/75">
          AstroOS is built for transparent Jyotish analysis. It does not sell mystery. Every
          conclusion is tied to chart evidence, classical rules, and book references — then
          explained by AI without inventing new predictions.
        </p>

        <h2 className="mt-12 font-display text-3xl font-semibold text-ink">USP pipeline</h2>
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-ink/75">
          <li>Evidence from the birth chart (planets, houses, dignity, dasha, transits)</li>
          <li>YAML rules matched against that evidence</li>
          <li>Classical sources (BPHS, Phaladeepika, and related packs)</li>
          <li>AI explanation that only rephrases matched inputs</li>
          <li>Confidence score for the matched conclusion</li>
        </ol>

        <h2 className="mt-12 font-display text-3xl font-semibold text-ink">What you can do</h2>
        <ul className="mt-4 list-disc space-y-2 pl-5 text-ink/75">
          <li>Generate a Vedic birth chart</li>
          <li>Run Gun Milan / Ashtakoot compatibility</li>
          <li>Review marriage timing themes</li>
          <li>Explain any matched prediction with full audit trail</li>
        </ul>

        <h2 className="mt-12 font-display text-3xl font-semibold text-ink">Disclaimer</h2>
        <p className="mt-4 text-ink/75">
          Outputs are traditional Vedic interpretive analysis for education and culture. They
          are not scientifically proven predictions, and not medical, financial, or legal
          advice.
        </p>

        <p className="mt-10">
          <Link
            href="/"
            className="inline-block bg-deep px-5 py-3 text-sm font-semibold text-paper"
          >
            Launch AstroOS
          </Link>
        </p>
      </article>
    </main>
  );
}
