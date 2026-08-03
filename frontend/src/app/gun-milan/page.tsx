import type { Metadata } from "next";
import Link from "next/link";
import { SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "Gun Milan — Ashtakoot Kundali Matching",
  description:
    "Learn Gun Milan (36-guna Ashtakoot) and run AstroOS compatibility with traditional scores plus modern dimensions.",
  alternates: { canonical: `${SITE_URL}/gun-milan` },
};

export default function GunMilanPage() {
  return (
    <main className="sky-wash min-h-screen">
      <header className="mx-auto flex max-w-3xl items-center justify-between px-6 py-6">
        <Link href="/" className="font-display text-2xl font-semibold text-ink">
          AstroOS
        </Link>
        <Link href="/#matchmaking" className="text-sm font-medium text-ink/70 hover:text-ink">
          Open matcher
        </Link>
      </header>

      <article className="mx-auto max-w-3xl px-6 pb-20 pt-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-copper">
          Kundali Matching
        </p>
        <h1 className="mt-3 font-display text-4xl font-semibold text-ink md:text-5xl">
          Gun Milan & Ashtakoot
        </h1>
        <p className="mt-6 text-lg leading-relaxed text-ink/75">
          Gun Milan is the traditional Vedic method of matching two charts using eight kootas
          (Ashtakoot) for a total of 36 gunas. AstroOS computes the classical score and adds
          modern compatibility dimensions for a clearer reading.
        </p>

        <h2 className="mt-12 font-display text-3xl font-semibold text-ink">
          The eight kootas (overview)
        </h2>
        <ul className="mt-4 list-disc space-y-2 pl-5 text-ink/75">
          <li>Varna — spiritual / temperament class</li>
          <li>Vashya — mutual attraction / influence</li>
          <li>Tara — birth star harmony</li>
          <li>Yoni — biological / instinctive compatibility</li>
          <li>Graha Maitri — planetary friendship</li>
          <li>Gana — nature (Deva / Manushya / Rakshasa)</li>
          <li>Bhakoot — Moon sign relationship</li>
          <li>Nadi — health / hereditary factor</li>
        </ul>

        <h2 className="mt-12 font-display text-3xl font-semibold text-ink">
          How AstroOS helps
        </h2>
        <p className="mt-4 text-ink/75">
          Enter both birth details to see traditional 36-guna results, modern dimensions
          (including attachment, lifestyle, and conflict themes), and a combined index. Use
          Explain on the home page when you want evidence-backed marriage conclusions for one
          chart.
        </p>

        <p className="mt-4 text-sm text-ink/55">
          Traditional matching is cultural guidance — not a guarantee of relationship outcomes.
        </p>

        <p className="mt-10 flex flex-wrap gap-3">
          <Link
            href="/#matchmaking"
            className="inline-block bg-clay px-5 py-3 text-sm font-semibold text-paper"
          >
            Run Gun Milan now
          </Link>
          <Link
            href="/about"
            className="inline-block border border-ink/20 px-5 py-3 text-sm font-semibold text-ink"
          >
            About AstroOS
          </Link>
        </p>
      </article>
    </main>
  );
}
