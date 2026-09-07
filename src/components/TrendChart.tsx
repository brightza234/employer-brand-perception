"use client";

import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const PALETTE = ["#2563eb", "#7c3aed", "#db2777", "#ea580c", "#16a34a", "#0891b2", "#71717a"];

export interface TrendRow {
  period: string;
  [company: string]: string | number | null;
}

export default function TrendChart({ data, companies }: { data: TrendRow[]; companies: string[] }) {
  return (
    <ResponsiveContainer width="100%" height={360}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-black/10 dark:stroke-white/10" />
        <XAxis dataKey="period" tick={{ fontSize: 12 }} />
        <YAxis domain={[-1, 1]} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        {companies.map((company, i) => (
          <Line
            key={company}
            type="monotone"
            dataKey={company}
            stroke={PALETTE[i % PALETTE.length]}
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
