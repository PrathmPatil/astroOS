"use client";

import { FormEvent, useState } from "react";
import { buildBirthPayload, fetchMarriageOverview } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";

const defaultForm = {
  name: "Native",
  date: "1992-03-21",
  time: "14:15",
  place: "Pune",
  latitude: "18.5204",
  longitude: "73.8567",
  timezone: "Asia/Kolkata",
};

export function MarriageStudio() {
  const { t } = useLanguage();
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setData(await fetchMarriageOverview(buildBirthPayload(form)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Marriage analysis failed");
    } finally {
      setLoading(false);
    }
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
    <section id="marriage" className="border-t border-ink/10 bg-[#ebe1d2]/70 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-10 max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-copper">
            {t("marriage_eyebrow")}
          </p>
          <h2 className="mt-2 font-display text-4xl font-semibold tracking-tight text-ink md:text-5xl">
            {t("marriage_title")}
          </h2>
          <p className="mt-3 text-lg text-ink/70">{t("marriage_intro")}</p>
        </div>

        <div className="grid gap-10 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.2fr)]">
          <form onSubmit={onSubmit} className="space-y-4">
            {fields.map(([key, labelKey]) => (
              <label key={key} className="block">
                <span className="mb-1.5 block text-sm font-medium text-ink/80">{t(labelKey)}</span>
                <input
                  type="text"
                  value={form[key]}
                  onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                  className="w-full border border-ink/15 bg-white/60 px-3 py-2.5 outline-none transition focus:border-copper"
                  required
                />
              </label>
            ))}
            <button
              type="submit"
              disabled={loading}
              className="mt-2 bg-clay px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink disabled:opacity-60"
            >
              {loading ? t("analyzing") : t("marriage_run")}
            </button>
            {error && <p className="text-sm text-clay">{error}</p>}
          </form>

          <div className="min-h-[28rem] border border-ink/10 bg-white/50 p-6">
            {!data && (
              <div className="flex h-full min-h-[24rem] items-center justify-center text-ink/50">
                {t("marriage_empty")}
              </div>
            )}

            {data && (
              <div className="space-y-8">
                <div>
                  <h3 className="font-display text-2xl font-semibold">{t("summary")}</h3>
                  <p className="mt-2 text-sm text-ink/70">
                    {t("support_band")}:{" "}
                    <span className="font-semibold text-ink">
                      {data.summary?.relationship_support_band}
                    </span>
                    {" · "}
                    {data.timing?.current_dasha?.mahadasha?.lord} /{" "}
                    {data.timing?.current_dasha?.antardasha?.lord}
                  </p>
                  <p className="mt-1 text-sm text-ink/60">
                    7th: {data.seventh_house?.sign} ({t("lord")} {data.seventh_house?.lord}) · Venus{" "}
                    {data.venus?.sign} H{data.venus?.house}
                  </p>
                </div>

                <div>
                  <h3 className="font-display text-xl font-semibold">{t("love_signals")}</h3>
                  <p className="mt-1 text-sm">
                    {t("score")} {data.love_marriage?.probability_score}/100 —{" "}
                    {data.love_marriage?.band}
                  </p>
                  <ul className="mt-3 grid gap-2 text-sm text-ink/75 sm:grid-cols-2">
                    {Object.entries(data.love_marriage?.themes || {}).map(([k, v]) => (
                      <li key={k} className="border-l-2 border-copper/50 pl-3">
                        {k.replaceAll("_", " ")}:{" "}
                        <span className="font-medium">
                          {v ? t("indicated") : t("not_highlighted")}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 className="font-display text-xl font-semibold">{t("spouse_sketch")}</h3>
                  <dl className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
                    {(
                      [
                        ["nature", data.spouse_prediction?.nature],
                        ["profession", data.spouse_prediction?.profession_tendency],
                        ["education", data.spouse_prediction?.education_tendency],
                        ["finance", data.spouse_prediction?.financial_status],
                        ["looks", data.spouse_prediction?.looks],
                        ["height", data.spouse_prediction?.height],
                        ["age", data.spouse_prediction?.age_difference],
                        ["place_label", data.spouse_prediction?.native_place_tendency],
                      ] as const
                    ).map(([labelKey, value]) => (
                      <div key={labelKey}>
                        <dt className="text-xs uppercase tracking-wide text-ink/45">
                          {t(labelKey)}
                        </dt>
                        <dd className="mt-0.5 text-ink/80">{value}</dd>
                      </div>
                    ))}
                  </dl>
                </div>

                <div>
                  <h3 className="font-display text-xl font-semibold">{t("timing")}</h3>
                  <div className="mt-3 space-y-2">
                    {(data.timing?.windows || []).slice(0, 5).map((w: any) => (
                      <div
                        key={`${w.start}-${w.antardasha}`}
                        className="flex flex-wrap items-baseline justify-between gap-2 border-b border-ink/10 py-2 text-sm"
                      >
                        <span>
                          {w.mahadasha}/{w.antardasha}{" "}
                          <span className="text-ink/50">
                            {t("score")} {w.score}
                          </span>
                        </span>
                        <span className="text-ink/60">
                          {String(w.start).slice(0, 10)} → {String(w.end).slice(0, 10)}
                        </span>
                      </div>
                    ))}
                    {!data.timing?.windows?.length && (
                      <p className="text-sm text-ink/50">{t("no_windows")}</p>
                    )}
                  </div>
                </div>

                <p className="text-xs leading-relaxed text-ink/50">{data.disclaimer}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
