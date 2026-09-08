"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ContentThemes } from "@/lib/types";

const THEME_COLORS: Record<string, string> = {
  Smartphone: "var(--chart-series-1)",
  "Laptop/PC": "var(--chart-series-2)",
  "Wearable/Gadget": "var(--chart-series-3)",
  "Home Appliance/Audio": "var(--chart-series-4)",
  "Tech News/Update": "var(--chart-series-5)",
  "Other/Lifestyle": "var(--chart-series-6)",
};
const THEME_ORDER = Object.keys(THEME_COLORS);

export default function ThemeBreakdownChart({ themes }: { themes: ContentThemes }) {
  const rows = Object.values(themes).map((entry) => ({
    name: entry.display_name,
    ...entry.theme_breakdown,
  }));

  return (
    <div className="space-y-4">
      <ResponsiveContainer width="100%" height={Math.max(280, rows.length * 44)}>
        <BarChart data={rows} layout="vertical" margin={{ top: 8, right: 16, left: 16, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" horizontal={false} />
          <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12, fill: "var(--chart-muted)" }} />
          <YAxis
            type="category"
            dataKey="name"
            width={160}
            tick={{ fontSize: 12, fill: "var(--chart-muted)" }}
          />
          <Tooltip />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {THEME_ORDER.map((theme) => (
            <Bar key={theme} dataKey={theme} stackId="themes" fill={THEME_COLORS[theme]} radius={2} />
          ))}
        </BarChart>
      </ResponsiveContainer>

      <details className="text-sm">
        <summary className="cursor-pointer text-foreground/60">View as table</summary>
        <div className="mt-2 overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-black/10 text-left dark:border-white/10">
                <th className="px-2 py-2">KOL</th>
                {THEME_ORDER.map((t) => (
                  <th key={t} className="px-2 py-2 text-right">
                    {t}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.name} className="border-b border-black/5 dark:border-white/5">
                  <td className="px-2 py-2">{row.name}</td>
                  {THEME_ORDER.map((t) => (
                    <td key={t} className="px-2 py-2 text-right tabular-nums">
                      {(row as Record<string, number | string>)[t] ?? 0}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
