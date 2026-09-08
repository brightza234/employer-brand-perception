import fs from "fs";
import path from "path";
import type { ProcessedInsights } from "./types";

const DATA_PATH = path.join(process.cwd(), "data", "processed_insights.json");

export function getInsights(): ProcessedInsights | null {
  if (!fs.existsSync(DATA_PATH)) return null;
  const raw = fs.readFileSync(DATA_PATH, "utf-8");
  return JSON.parse(raw) as ProcessedInsights;
}
