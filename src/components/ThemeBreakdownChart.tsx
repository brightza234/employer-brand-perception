"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const PALETTE = ["#2563eb", "#7c3aed", "#db2777", "#ea580c", "#16a34a", "#0891b2", "#71717a"];

export interface ThemeBreakdownRow {
  theme: string;
  [company: string]: string | number;
}

export default function ThemeBreakdownChart({
  data,
  companies,
}: {
  data: ThemeBreakdownRow[];
  companies: string[];
}) {
  return (
    <ResponsiveContainer width="100%" height={380}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-black/10 dark:stroke-white/10" />
        <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
        <YAxis type="category" dataKey="theme" width={180} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        {companies.map((company, i) => (
          <Bar key={company} dataKey={company} fill={PALETTE[i % PALETTE.length]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
