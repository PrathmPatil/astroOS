const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000/api/v1";

export type BirthPayload = {
  name?: string;
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second?: number;
  latitude: number;
  longitude: number;
  timezone: string;
  place?: string;
  ayanamsha?: "lahiri" | "raman" | "krishnamurti";
  house_system?: string;
};

export type BirthFormFields = {
  name: string;
  date: string;
  time: string;
  place: string;
  latitude: string;
  longitude: string;
  timezone: string;
};

function formatValidationError(text: string, status: number): string {
  try {
    const data = JSON.parse(text);
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((d: { loc?: string[]; msg?: string }) => {
          const field = (d.loc || []).filter((x) => x !== "body").join(".");
          return field ? `${field}: ${d.msg}` : d.msg;
        })
        .join("; ");
    }
    if (typeof data.detail === "string") return data.detail;
  } catch {
    /* plain text */
  }
  return text || `API error ${status}`;
}

async function postJSON(path: string, payload: unknown) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(formatValidationError(text, res.status));
  }
  return res.json();
}

/** Build a validated API payload from form strings (avoids NaN → null → 422). */
export function buildBirthPayload(form: BirthFormFields): BirthPayload {
  const dateParts = form.date.trim().split("-").map((x) => Number(x));
  if (dateParts.length !== 3 || dateParts.some((n) => !Number.isFinite(n))) {
    throw new Error("Enter a valid date (YYYY-MM-DD).");
  }
  const [year, month, day] = dateParts;

  const timeParts = form.time.trim().split(":").map((x) => Number(x));
  if (timeParts.length < 2 || !Number.isFinite(timeParts[0]) || !Number.isFinite(timeParts[1])) {
    throw new Error("Enter a valid time (HH:MM).");
  }
  const [hour, minute] = timeParts;
  const second = Number.isFinite(timeParts[2]) ? timeParts[2] : 0;

  const latitude = Number(form.latitude);
  const longitude = Number(form.longitude);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    throw new Error("Latitude and longitude must be numbers.");
  }
  if (!form.timezone.trim()) {
    throw new Error("Timezone is required (e.g. Asia/Kolkata).");
  }
  if (year < 1800 || year > 2200) {
    throw new Error("Year must be between 1800 and 2200.");
  }

  return {
    name: form.name || undefined,
    year,
    month,
    day,
    hour,
    minute,
    second,
    latitude,
    longitude,
    timezone: form.timezone.trim(),
    place: form.place || undefined,
    ayanamsha: "lahiri",
    house_system: "W",
  };
}

export async function fetchBirthChart(payload: BirthPayload) {
  return postJSON("/birth-chart", payload);
}

export async function fetchMarriageOverview(payload: BirthPayload) {
  return postJSON("/marriage/overview", payload);
}

export async function fetchMatchmaking(payload: {
  boy: BirthPayload;
  girl: BirthPayload;
}) {
  return postJSON("/matchmaking", payload);
}

export async function fetchGunMilan(payload: {
  boy: BirthPayload;
  girl: BirthPayload;
}) {
  return postJSON("/gun-milan", payload);
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("API unavailable");
  return res.json();
}
