"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const COLORS = { positive: "#16a34a", neutral: "#a3a3a3", negative: "#dc2626" };

export interface CompanySentimentRow {
  company: string;
  positive: number;
  neutral: number;
  negative: number;
}

export default function CompanySentimentChart({ data }: { data: CompanySentimentRow[] }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-black/10 dark:stroke-white/10" />
        <XAxis dataKey="company" tick={{ fontSize: 12 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="positive" stackId="s" fill={COLORS.positive} name="Positive" />
        <Bar dataKey="neutral" stackId="s" fill={COLORS.neutral} name="Neutral" />
        <Bar dataKey="negative" stackId="s" fill={COLORS.negative} name="Negative" />
      </BarChart>
    </ResponsiveContainer>
  );
}
