"use client";

import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import type { KolMetrics } from "@/lib/types";

interface Point {
  x: number;
  y: number;
  z: number;
  name: string;
  composite_score: number;
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: { payload: Point }[] }) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <div className="rounded-md border border-black/10 bg-background px-3 py-2 text-xs shadow-sm dark:border-white/10">
      <div className="font-medium">{p.name}</div>
      <div className="text-foreground/60">{p.x.toLocaleString()} subscribers</div>
      <div className="text-foreground/60">{(p.y * 100).toFixed(2)}% engagement rate</div>
    </div>
  );
}

export default function EngagementScatter({ kols }: { kols: KolMetrics[] }) {
  const above: Point[] = [];
  const below: Point[] = [];
  for (const k of kols) {
    const point: Point = {
      x: k.subscriber_count,
      y: k.engagement_rate,
      z: Math.abs(k.composite_score) + 1,
      name: k.display_name,
      composite_score: k.composite_score,
    };
    (k.composite_score >= 0 ? above : below).push(point);
  }

  return (
    <ResponsiveContainer width="100%" height={380}>
      <ScatterChart margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid)" />
        <XAxis
          dataKey="x"
          type="number"
          scale="log"
          domain={["auto", "auto"]}
          tickFormatter={(v: number) => new Intl.NumberFormat("en-US", { notation: "compact" }).format(v)}
          tick={{ fontSize: 12, fill: "var(--chart-muted)" }}
          name="Subscribers"
          label={{ value: "Subscribers (log scale)", position: "insideBottom", offset: -4, fontSize: 12 }}
        />
        <YAxis
          dataKey="y"
          type="number"
          tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
          tick={{ fontSize: 12, fill: "var(--chart-muted)" }}
          name="Engagement rate"
          label={{ value: "Engagement rate", angle: -90, position: "insideLeft", fontSize: 12 }}
        />
        <ZAxis dataKey="z" range={[60, 300]} />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Scatter name="Above-average score" data={above} fill="var(--chart-positive)" />
        <Scatter name="Below-average score" data={below} fill="var(--chart-negative)" />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
