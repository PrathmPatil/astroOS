"use client";

import { FormEvent, useState } from "react";
import { buildBirthPayload, fetchBirthChart } from "@/lib/api";
import { HoroscopeWheel } from "@/components/HoroscopeWheel";
import { useLanguage } from "@/components/LanguageProvider";

const defaultForm = {
  name: "Sample Native",
  date: "1990-08-15",
  time: "10:30",
  place: "Mumbai",
  latitude: "19.0760",
  longitude: "72.8777",
  timezone: "Asia/Kolkata",
};

export function ChartStudio() {
  const { t } = useLanguage();
  const [form, setForm] = useState(defaultForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chart, setChart] = useState<any>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = buildBirthPayload(form);
      const data = await fetchBirthChart(payload);
      setChart(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate chart");
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
    <section id="chart" className="mx-auto max-w-6xl px-6 py-20">
      <div className="mb-10 max-w-2xl">
        <h2 className="font-display text-4xl font-semibold tracking-tight text-ink md:text-5xl">
          {t("chart_title")}
        </h2>
        <p className="mt-3 text-lg text-ink/70">{t("chart_intro")}</p>
      </div>

      <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
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
            className="mt-2 inline-flex items-center justify-center bg-deep px-5 py-3 text-sm font-semibold tracking-wide text-paper transition hover:bg-ink disabled:opacity-60"
          >
            {loading ? t("calculating") : t("generate")}
          </button>
          {error && (
            <p className="text-sm text-clay">
              {error.includes("Failed to fetch") ? t("api_down") : error}
            </p>
          )}
        </form>

        <div className="min-h-[28rem] border border-ink/10 bg-white/40 p-6">
          {!chart && (
            <div className="flex h-full min-h-[24rem] flex-col items-center justify-center text-center text-ink/55">
              <div className="mb-4 h-40 w-40 rounded-full chart-ring opacity-80" />
              <p>{t("chart_empty")}</p>
            </div>
          )}

          {chart && (
            <div className="space-y-6">
              <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
                <HoroscopeWheel
                  lagnaLongitude={chart.lagna.longitude}
                  planets={chart.planets}
                />
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-semibold">{t("lagna")}:</span> {chart.lagna.sign} (
                    {chart.lagna.dms})
                  </p>
                  <p>
                    <span className="font-semibold">{t("lord")}:</span> {chart.lagna.lord}
                  </p>
                  <p>
                    <span className="font-semibold">{t("moon")}:</span> {chart.moon.sign} ·{" "}
                    {chart.moon.nakshatra} Pada {chart.moon.pada}
                  </p>
                  <p>
                    <span className="font-semibold">{t("ayanamsha")}:</span>{" "}
                    {chart.ayanamsha_value}°
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full min-w-[32rem] text-left text-sm">
                  <thead>
                    <tr className="border-b border-ink/15 text-ink/60">
                      <th className="py-2 pr-3 font-medium">{t("planet")}</th>
                      <th className="py-2 pr-3 font-medium">{t("sign")}</th>
                      <th className="py-2 pr-3 font-medium">{t("house")}</th>
                      <th className="py-2 pr-3 font-medium">{t("nakshatra")}</th>
                      <th className="py-2 font-medium">{t("flags")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chart.planets
                      .filter((p: any) =>
                        [
                          "Sun",
                          "Moon",
                          "Mars",
                          "Mercury",
                          "Jupiter",
                          "Venus",
                          "Saturn",
                          "Rahu",
                          "Ketu",
                        ].includes(p.name),
                      )
                      .map((p: any) => (
                        <tr key={p.name} className="border-b border-ink/8">
                          <td className="py-2 pr-3 font-medium">{p.name}</td>
                          <td className="py-2 pr-3">{p.sign}</td>
                          <td className="py-2 pr-3">{p.house}</td>
                          <td className="py-2 pr-3">
                            {p.nakshatra} ({p.pada})
                          </td>
                          <td className="py-2 text-xs text-ink/70">
                            {[
                              p.retrograde && "R",
                              p.exalted && "Ex",
                              p.debilitated && "Deb",
                              p.combust && "Comb",
                            ]
                              .filter(Boolean)
                              .join(" · ") || "—"}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>

              <p className="text-xs leading-relaxed text-ink/55">{chart.disclaimer}</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
