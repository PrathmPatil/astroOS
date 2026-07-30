"use client";

type Planet = {
  name: string;
  longitude: number;
  sign: string;
  house: number;
  retrograde?: boolean;
};

const GLYPH: Record<string, string> = {
  Sun: "Su",
  Moon: "Mo",
  Mars: "Ma",
  Mercury: "Me",
  Jupiter: "Ju",
  Venus: "Ve",
  Saturn: "Sa",
  Rahu: "Ra",
  Ketu: "Ke",
  Lagna: "As",
};

export function HoroscopeWheel({
  lagnaLongitude,
  planets,
}: {
  lagnaLongitude: number;
  planets: Planet[];
}) {
  const size = 360;
  const cx = size / 2;
  const cy = size / 2;
  const outer = 160;
  const inner = 108;

  const toXY = (lon: number, r: number) => {
    // Put 0° Aries at the right (east)
    const rad = ((180 - lon) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy - r * Math.sin(rad) };
  };

  const signs = Array.from({ length: 12 }, (_, i) => i * 30);
  const bodies = [
    { name: "Lagna", longitude: lagnaLongitude },
    ...planets.filter((p) =>
      ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"].includes(
        p.name,
      ),
    ),
  ];

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      className="h-auto w-full max-w-md drop-shadow-sm"
      role="img"
      aria-label="South Indian style circular horoscope wheel"
    >
      <circle cx={cx} cy={cy} r={outer} fill="#f7f0e6" stroke="#1a1510" strokeWidth="2" />
      <circle cx={cx} cy={cy} r={inner} fill="#efe4d4" stroke="#1a1510" strokeWidth="1.5" />
      {signs.map((deg) => {
        const a = toXY(deg, outer);
        const b = toXY(deg, inner);
        return (
          <line
            key={deg}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            stroke="#1a1510"
            strokeOpacity="0.35"
          />
        );
      })}
      {bodies.map((body, idx) => {
        const r = inner - 18 - (idx % 3) * 10;
        const { x, y } = toXY(body.longitude, r);
        return (
          <g key={`${body.name}-${idx}`}>
            <circle cx={x} cy={y} r={11} fill="#243447" />
            <text
              x={x}
              y={y + 3.5}
              textAnchor="middle"
              fill="#f3ebe0"
              fontSize="9"
              fontFamily="var(--font-sans)"
            >
              {GLYPH[body.name] || body.name.slice(0, 2)}
            </text>
          </g>
        );
      })}
      <text
        x={cx}
        y={cy + 4}
        textAnchor="middle"
        fill="#8b4513"
        fontSize="14"
        fontFamily="var(--font-display)"
      >
        AstroSutra
      </text>
    </svg>
  );
}
