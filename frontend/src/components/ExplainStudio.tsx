"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { buildBirthPayload } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";
import type { Lang } from "@/lib/i18n";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000/api/v1";

const defaultForm = {
  name: "Sample Native",
  date: "1990-08-15",
  time: "10:30",
  place: "Mumbai",
  latitude: "19.0760",
  longitude: "72.8777",
  timezone: "Asia/Kolkata",
};

type ScannedConclusion = {
  conclusion_key: string;
  title: string;
  summary: string;
  confidence: number;
};

function sourceForLang(s: Record<string, string | undefined>, language: Lang) {
  const map: Record<Lang, string> = {
    en: "english",
    mr: "marathi",
    hi: "hindi",
    gu: "gujarati",
    kn: "kannada",
    ta: "tamil",
    te: "telugu",
  };
  return s[map[language]] || s.english || "";
}

export function ExplainStudio() {
  const { language, t } = useLanguage();
  const [form, setForm] = useState(defaultForm);
  const [conclusionKey, setConclusionKey] = useState("marriage_delay");
  const [loading, setLoading] = useState(false);
  const [scanLoading, setScanLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [available, setAvailable] = useState<ScannedConclusion[]>([]);
  const [data, setData] = useState<any>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (data?.found) {
      resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [data]);

  // Re-explain in the newly selected language when header language changes
  useEffect(() => {
    if (!data?.found || !conclusionKey) return;
    let cancelled = false;
    (async () => {
      try {
        const birth = buildBirthPayload(form);
        const res = await fetch(`${API_BASE}/evidence/explain`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ birth, conclusion_key: conclusionKey, language }),
        });
        const json = await res.json();
        if (!cancelled && res.ok) setData(json);
      } catch {
        /* keep previous */
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- only when language changes
  }, [language]);

  async function scanConclusions() {
    setScanLoading(true);
    setError(null);
    try {
      const birth = buildBirthPayload(form);
      const res = await fetch(`${API_BASE}/evidence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ birth, language }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(JSON.stringify(json));
      const list: ScannedConclusion[] = (json.conclusions || []).map((c: any) => ({
        conclusion_key: c.conclusion_key,
        title: c.title,
        summary: c.summary,
        confidence: c.confidence,
      }));
      setAvailable(list);
      if (list.length && !list.some((c) => c.conclusion_key === conclusionKey)) {
        setConclusionKey(list[0].conclusion_key);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setScanLoading(false);
    }
  }

  async function explainKey(key: string) {
    setConclusionKey(key);
    setLoading(true);
    setError(null);
    try {
      const birth = buildBirthPayload(form);
      const res = await fetch(`${API_BASE}/evidence/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          birth,
          conclusion_key: key,
          language,
        }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(JSON.stringify(json));
      setData(json);
      if (!json.found && json.available) {
        setAvailable(
          (json.available as string[]).map((k) => ({
            conclusion_key: k,
            title: k,
            summary: "",
            confidence: 0,
          })),
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Explain failed");
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    await explainKey(conclusionKey);
  }

  const fields = [
    ["name", "field_name"],
    ["date", "field_date"],
    ["time", "field_time"],
    ["place", "field_place"],
    ["latitude", "field_lat"],
    ["longitude", "field_lng"],
    ["timezone", "field_tz"],
  ] as const;

  return (
    <section id="explain" className="border-t border-ink/10 bg-[#e8dfd2]/80 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-10 max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-copper">
            {t("explain_eyebrow")}
          </p>
          <h2 className="mt-2 font-display text-4xl font-semibold text-ink md:text-5xl">
            {t("explain_title")}
          </h2>
          <p className="mt-3 text-lg text-ink/70">{t("explain_intro")}</p>
        </div>

        <form onSubmit={onSubmit} className="grid gap-8 lg:grid-cols-[0.9fr_1.2fr]">
          <div className="space-y-3">
            {fields.map(([key, labelKey]) => (
              <label key={key} className="block">
                <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink/55">
                  {t(labelKey)}
                </span>
                <input
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  className="w-full border border-ink/15 bg-white/60 px-3 py-2 outline-none focus:border-copper"
                  required
                />
              </label>
            ))}

            <label className="block">
              <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink/55">
                {t("field_conclusion")}
              </span>
              <input
                value={conclusionKey}
                onChange={(e) => setConclusionKey(e.target.value)}
                list="conclusion-keys"
                className="w-full border border-ink/15 bg-white/60 px-3 py-2 outline-none focus:border-copper"
              />
              <datalist id="conclusion-keys">
                {available.map((c) => (
                  <option key={c.conclusion_key} value={c.conclusion_key} />
                ))}
              </datalist>
            </label>

            <div className="flex flex-wrap gap-3 pt-2">
              <button
                type="button"
                onClick={scanConclusions}
                disabled={scanLoading}
                className="border border-ink/20 px-4 py-2.5 text-sm font-semibold text-ink"
              >
                {scanLoading ? t("scanning") : t("scan")}
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-deep px-4 py-2.5 text-sm font-semibold text-paper"
              >
                {loading ? t("explaining") : t("explain_btn")}
              </button>
            </div>
            {error && <p className="text-sm text-clay">{error}</p>}

            {!!available.length && (
              <div className="mt-4 space-y-2 border border-ink/10 bg-white/40 p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-ink/55">
                  {t("matched_list")}
                </p>
                <ul className="max-h-56 space-y-2 overflow-y-auto">
                  {available.map((c) => (
                    <li key={c.conclusion_key}>
                      <button
                        type="button"
                        onClick={() => explainKey(c.conclusion_key)}
                        className={`w-full border px-3 py-2 text-left text-sm transition ${
                          conclusionKey === c.conclusion_key
                            ? "border-copper bg-white"
                            : "border-ink/10 bg-white/50 hover:border-copper/50"
                        }`}
                      >
                        <span className="font-medium text-ink">{c.title}</span>
                        <span className="mt-0.5 block text-xs text-ink/50">
                          {c.conclusion_key}
                          {c.confidence ? ` · ${c.confidence}%` : ""}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div
            ref={resultRef}
            className="max-h-[70vh] min-h-[28rem] overflow-y-auto border border-ink/10 bg-white/50 p-6 scroll-mt-6"
          >
            {!data && <p className="text-ink/50">{t("explain_empty")}</p>}

            {data && !data.found && (
              <div>
                <p className="font-semibold text-clay">{t("not_found")}</p>
                <p className="mt-2 text-sm text-ink/60">{t("try_scan")}</p>
              </div>
            )}

            {data?.found && (
              <div className="space-y-6">
                <div className="border-2 border-deep bg-[#1a1510] px-5 py-5 text-paper">
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#e8c4a0]">
                    {t("final_conclusion")}
                  </p>
                  <h3 className="mt-2 font-display text-2xl font-semibold md:text-3xl">
                    {data.title_localized || data.title}
                  </h3>
                  <p className="mt-3 text-base leading-relaxed text-paper/90">
                    {data.final_conclusion}
                  </p>
                  <p className="mt-4 inline-block bg-paper px-3 py-1 text-sm font-semibold text-deep">
                    {t("confidence")} {data.confidence}%
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold">{t("evidence")}</h4>
                  <ul className="mt-2 space-y-1 text-sm">
                    {(data.evidence || []).map((e: string) => (
                      <li key={e}>{e}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold">{t("used_rules")}</h4>
                  <p className="mt-1 text-sm text-ink/70">{(data.used_rules || []).join(" · ")}</p>
                </div>

                <div>
                  <h4 className="font-semibold">{t("classical")}</h4>
                  <div className="mt-2 space-y-4">
                    {(data.classical_views || []).map((s: any, i: number) => {
                      const local = sourceForLang(s, language);
                      return (
                        <article key={i} className="border-l-2 border-copper pl-3 text-sm">
                          <p className="font-medium">
                            {s.book} · {s.chapter}
                          </p>
                          {s.sanskrit && <p className="mt-1 text-ink/80">{s.sanskrit}</p>}
                          {local && <p className="mt-1 text-ink/70">{local}</p>}
                          {language !== "en" && s.english && (
                            <p className="mt-1 text-xs text-ink/45">EN: {s.english}</p>
                          )}
                        </article>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold">{t("ai_explain")}</h4>
                  <p className="mt-2 text-sm leading-relaxed text-ink/75">{data.ai_explanation}</p>
                </div>

                <div>
                  <h4 className="font-semibold">{t("audit")}</h4>
                  <p className="mt-1 text-xs text-ink/50">ID: {data.audit?.audit_id}</p>
                  <ol className="mt-2 list-decimal space-y-1 pl-5 text-sm text-ink/70">
                    <li>
                      {t("final_conclusion")}: {data.title_localized || data.title}
                    </li>
                    <li>
                      {t("evidence")}: {(data.evidence || []).length}
                    </li>
                    <li>
                      {t("used_rules")}: {(data.used_rules || []).join(", ")}
                    </li>
                    <li>
                      {t("confidence")}: {data.confidence}%
                    </li>
                  </ol>
                </div>

                <p className="text-xs text-ink/50">{data.disclaimer}</p>
              </div>
            )}
          </div>
        </form>
      </div>
    </section>
  );
}
