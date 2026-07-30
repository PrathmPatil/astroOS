"use client";

import Link from "next/link";
import { ChartStudio } from "@/components/ChartStudio";
import { ExplainStudio } from "@/components/ExplainStudio";
import { MarriageStudio } from "@/components/MarriageStudio";
import { MatchmakingStudio } from "@/components/MatchmakingStudio";
import { useLanguage } from "@/components/LanguageProvider";
import type { Lang } from "@/lib/i18n";

export default function Home() {
  const { language, setLanguage, t, options } = useLanguage();

  const layers = [
    { title: t("layer1_title"), body: t("layer1_body") },
    { title: t("layer2_title"), body: t("layer2_body") },
    { title: t("layer3_title"), body: t("layer3_body") },
  ];

  return (
    <main className="sky-wash min-h-screen">
      <header className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-6">
        <Link href="/" className="font-display text-2xl font-semibold tracking-tight text-ink">
          AstroOS
        </Link>
        <nav className="flex flex-wrap items-center gap-4 text-sm font-medium text-ink/75">
          <a href="#explain" className="hover:text-ink">
            {t("nav_explain")}
          </a>
          <a href="#chart" className="hover:text-ink">
            {t("nav_chart")}
          </a>
          <a href="#matchmaking" className="hover:text-ink">
            {t("nav_compat")}
          </a>
          <a href="#marriage" className="hover:text-ink">
            {t("nav_marriage")}
          </a>
          <label className="flex items-center gap-2 bg-deep px-3 py-2 text-paper">
            <span className="sr-only">{t("language")}</span>
            <span className="hidden text-xs font-semibold uppercase tracking-wide sm:inline">
              {t("language")}
            </span>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as Lang)}
              className="bg-deep text-sm font-semibold text-paper outline-none"
              aria-label={t("language")}
            >
              {options.map((o) => (
                <option key={o.code} value={o.code} className="bg-paper text-ink">
                  {o.label}
                </option>
              ))}
            </select>
          </label>
        </nav>
      </header>

      <section className="relative mx-auto grid min-h-[78vh] max-w-6xl items-center gap-10 px-6 pb-16 pt-8 lg:grid-cols-2">
        <div>
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-copper">
            {t("hero_eyebrow")}
          </p>
          <h1 className="font-display text-5xl font-semibold leading-[1.05] tracking-tight text-ink md:text-7xl">
            AstroOS
          </h1>
          <p className="mt-5 max-w-md text-lg leading-relaxed text-ink/70">{t("hero_tagline")}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a
              href="#explain"
              className="bg-clay px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink"
            >
              {t("hero_cta_explain")}
            </a>
            <a
              href="#chart"
              className="border border-ink/20 px-5 py-3 text-sm font-semibold text-ink transition hover:border-ink"
            >
              {t("hero_cta_chart")}
            </a>
          </div>
        </div>

        <div className="relative h-[28rem] overflow-hidden lg:h-[34rem]">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_40%,#243447_0%,transparent_42%),radial-gradient(circle_at_70%_30%,#b5673a_0%,transparent_35%),linear-gradient(160deg,#1a1510_0%,#243447_55%,#3d2a1c_100%)]" />
          <div className="absolute inset-[12%] rounded-full border border-paper/20" />
          <div className="absolute inset-[22%] rounded-full border border-paper/15" />
          <div className="absolute inset-[34%] rounded-full border border-copper/40" />
          <div className="absolute left-1/2 top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-sand" />
          <p className="absolute bottom-8 left-8 max-w-xs font-display text-2xl text-paper/90">
            {t("hero_visual")}
          </p>
        </div>
      </section>

      <section id="layers" className="border-t border-ink/10 bg-paper/70 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="font-display text-4xl font-semibold text-ink md:text-5xl">
            {t("layers_title")}
          </h2>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {layers.map((layer, i) => (
              <article key={layer.title} className="border-t border-ink/20 pt-5">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-copper">
                  {t("core")} 0{i + 1}
                </p>
                <h3 className="mt-3 font-display text-2xl font-semibold text-ink">
                  {layer.title}
                </h3>
                <p className="mt-3 text-ink/65">{layer.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <ExplainStudio />
      <ChartStudio />
      <MatchmakingStudio />
      <MarriageStudio />

      <footer className="border-t border-ink/10 px-6 py-10 text-center text-sm text-ink/55">
        {t("footer")}
      </footer>
    </main>
  );
}
