"use client";

import { FormEvent, useState } from "react";
import { buildBirthPayload, fetchMatchmaking } from "@/lib/api";
import { useLanguage } from "@/components/LanguageProvider";

type PersonForm = {
  name: string;
  date: string;
  time: string;
  place: string;
  latitude: string;
  longitude: string;
  timezone: string;
};

const boyDefault: PersonForm = {
  name: "Rahul",
  date: "1990-08-15",
  time: "10:30",
  place: "Mumbai",
  latitude: "19.0760",
  longitude: "72.8777",
  timezone: "Asia/Kolkata",
};

const girlDefault: PersonForm = {
  name: "Priya",
  date: "1992-03-21",
  time: "14:15",
  place: "Pune",
  latitude: "18.5204",
  longitude: "73.8567",
  timezone: "Asia/Kolkata",
};

function PersonFields({
  title,
  form,
  setForm,
  t,
}: {
  title: string;
  form: PersonForm;
  setForm: (f: PersonForm) => void;
  t: (key: string) => string;
}) {
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
    <div>
      <h3 className="mb-3 font-display text-xl font-semibold text-ink">{title}</h3>
      <div className="space-y-3">
        {fields.map(([key, labelKey]) => (
          <label key={key} className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-ink/55">
              {t(labelKey)}
            </span>
            <input
              type="text"
              value={form[key]}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              className="w-full border border-ink/15 bg-white/60 px-3 py-2 outline-none transition focus:border-copper"
              required
            />
          </label>
        ))}
      </div>
    </div>
  );
}

function ScoreRing({ score, label }: { score: number; label: string }) {
  const pct = Math.max(0, Math.min(100, score));
  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className="relative grid h-28 w-28 place-items-center rounded-full"
        style={{
          background: `conic-gradient(#8b4513 ${pct * 3.6}deg, rgba(26,21,16,0.08) 0deg)`,
        }}
      >
        <div className="grid h-[5.35rem] w-[5.35rem] place-items-center rounded-full bg-[#f7f0e6]">
          <span className="font-display text-2xl font-semibold text-ink">{pct.toFixed(0)}</span>
        </div>
      </div>
      <p className="text-center text-xs font-semibold uppercase tracking-wide text-ink/55">{label}</p>
    </div>
  );
}

function bandColor(band: string) {
  if (band === "strong" || band === "good") return "text-deep";
  if (band === "mixed") return "text-copper";
  return "text-clay";
}

export function MatchmakingStudio() {
  const { t } = useLanguage();
  const [boy, setBoy] = useState(boyDefault);
  const [girl, setGirl] = useState(girlDefault);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);
  const [tab, setTab] = useState<"traditional" | "modern" | "combined">("combined");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        boy: buildBirthPayload(boy),
        girl: buildBirthPayload(girl),
      };
      setData(await fetchMatchmaking(payload));
      setTab("combined");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Matchmaking failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="matchmaking" className="border-t border-ink/10 py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-10 max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-copper">
            {t("match_eyebrow")}
          </p>
          <h2 className="mt-2 font-display text-4xl font-semibold tracking-tight text-ink md:text-5xl">
            {t("match_title")}
          </h2>
          <p className="mt-3 text-lg text-ink/70">{t("match_intro")}</p>
        </div>

        <form onSubmit={onSubmit} className="grid gap-8 lg:grid-cols-2">
          <PersonFields title={t("boy")} form={boy} setForm={setBoy} t={t} />
          <PersonFields title={t("girl")} form={girl} setForm={setGirl} t={t} />
          <div className="lg:col-span-2">
            <button
              type="submit"
              disabled={loading}
              className="bg-deep px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink disabled:opacity-60"
            >
              {loading ? t("matching") : t("match_run")}
            </button>
            {error && <p className="mt-3 text-sm text-clay">{error}</p>}
          </div>
        </form>

        {data && (
          <div className="mt-12 space-y-8">
            <div className="flex flex-wrap items-end justify-between gap-6 border border-ink/10 bg-white/45 p-6">
              <div>
                <p className="text-sm text-ink/60">
                  {data.profiles.boy.name || t("boy")} · {data.profiles.boy.moon.sign}{" "}
                  {t("moon")} / {data.profiles.boy.moon.nakshatra}
                </p>
                <p className="text-sm text-ink/60">
                  {data.profiles.girl.name || t("girl")} · {data.profiles.girl.moon.sign}{" "}
                  {t("moon")} / {data.profiles.girl.moon.nakshatra}
                </p>
                <p className="mt-3 font-display text-2xl font-semibold text-ink">
                  {data.ai_combined.verdict}
                </p>
              </div>
              <div className="flex flex-wrap gap-6">
                <ScoreRing score={data.modes.traditional_score} label={t("traditional")} />
                <ScoreRing score={data.modes.modern_score} label={t("modern")} />
                <ScoreRing score={data.modes.ai_combined_score} label={t("combined")} />
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {(
                [
                  ["combined", "tab_combined"],
                  ["traditional", "tab_traditional"],
                  ["modern", "tab_modern"],
                ] as const
              ).map(([id, labelKey]) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => setTab(id)}
                  className={`px-4 py-2 text-sm font-semibold transition ${
                    tab === id
                      ? "bg-clay text-paper"
                      : "border border-ink/15 text-ink/70 hover:border-ink"
                  }`}
                >
                  {t(labelKey)}
                </button>
              ))}
            </div>

            {tab === "combined" && (
              <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="border border-ink/10 bg-white/40 p-6">
                  <h3 className="font-display text-2xl font-semibold">{t("combined_reading")}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-ink/75">
                    {data.ai_combined.narrative}
                  </p>
                  <ul className="mt-5 space-y-2 text-sm text-ink/70">
                    {data.ai_combined.highlights.map((h: string) => (
                      <li key={h} className="border-l-2 border-copper/60 pl-3">
                        {h}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="border border-ink/10 bg-white/40 p-6">
                  <h3 className="font-display text-xl font-semibold">{t("flags_title")}</h3>
                  {data.ai_combined.flags?.length ? (
                    <ul className="mt-3 space-y-2 text-sm text-ink/70">
                      {data.ai_combined.flags.map((f: string) => (
                        <li key={f}>{f}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-3 text-sm text-ink/55">{t("no_flags")}</p>
                  )}
                </div>
              </div>
            )}

            {tab === "traditional" && (
              <div className="space-y-6">
                <div className="flex flex-wrap gap-6 text-sm">
                  <p>
                    <span className="font-semibold">{data.traditional.total}</span> /{" "}
                    {data.traditional.maximum} · {data.traditional.verdict}
                  </p>
                </div>

                <div className="overflow-x-auto border border-ink/10 bg-white/40">
                  <table className="w-full min-w-[36rem] text-left text-sm">
                    <thead>
                      <tr className="border-b border-ink/15 text-ink/50">
                        <th className="px-4 py-3 font-medium">{t("koota")}</th>
                        <th className="px-4 py-3 font-medium">{t("score")}</th>
                        <th className="px-4 py-3 font-medium">{t("fill")}</th>
                        <th className="px-4 py-3 font-medium">{t("notes")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.traditional.kootas.map((k: any) => {
                        const pct = (k.obtained / k.maximum) * 100;
                        return (
                          <tr key={k.name} className="border-b border-ink/8">
                            <td className="px-4 py-3 font-medium">{k.name}</td>
                            <td className="px-4 py-3">
                              {k.obtained}/{k.maximum}
                            </td>
                            <td className="px-4 py-3">
                              <div className="h-2 w-28 bg-ink/10">
                                <div className="h-2 bg-clay" style={{ width: `${pct}%` }} />
                              </div>
                            </td>
                            <td className="px-4 py-3 text-ink/60">{k.notes}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="border border-ink/10 bg-white/40 p-5">
                    <h4 className="font-semibold text-ink">{t("strengths")}</h4>
                    <ul className="mt-2 space-y-1 text-sm text-ink/70">
                      {(data.traditional.strengths || []).map((s: string) => (
                        <li key={s}>{s}</li>
                      ))}
                      {!data.traditional.strengths?.length && (
                        <li className="text-ink/45">{t("no_strengths")}</li>
                      )}
                    </ul>
                  </div>
                  <div className="border border-ink/10 bg-white/40 p-5">
                    <h4 className="font-semibold text-ink">{t("weaknesses")}</h4>
                    <ul className="mt-2 space-y-1 text-sm text-ink/70">
                      {(data.traditional.weaknesses || []).map((s: string) => (
                        <li key={s}>{s}</li>
                      ))}
                      {!data.traditional.weaknesses?.length && (
                        <li className="text-ink/45">{t("no_weaknesses")}</li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {tab === "modern" && (
              <div className="grid gap-4 md:grid-cols-2">
                {data.modern.dimensions.map((d: any) => (
                  <article key={d.key} className="border border-ink/10 bg-white/40 p-5">
                    <div className="flex items-baseline justify-between gap-3">
                      <h4 className="font-display text-xl font-semibold">{d.label}</h4>
                      <span className={`text-sm font-semibold ${bandColor(d.band)}`}>
                        {d.score} · {d.band}
                      </span>
                    </div>
                    <div className="mt-3 h-2 bg-ink/10">
                      <div className="h-2 bg-deep" style={{ width: `${d.score}%` }} />
                    </div>
                    <p className="mt-3 text-sm text-ink/65">{d.detail}</p>
                  </article>
                ))}
              </div>
            )}

            <p className="text-xs leading-relaxed text-ink/50">{data.disclaimer}</p>
          </div>
        )}
      </div>
    </section>
  );
}
