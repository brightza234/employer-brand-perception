import fs from "fs";
import path from "path";
import type { ContentThemes, KolScores } from "./types";

const SCORES_PATH = path.join(process.cwd(), "data", "kol_scores.json");
const THEMES_PATH = path.join(process.cwd(), "data", "content_themes.json");

export function getScores(): KolScores | null {
  if (!fs.existsSync(SCORES_PATH)) return null;
  const raw = fs.readFileSync(SCORES_PATH, "utf-8");
  return JSON.parse(raw) as KolScores;
}

export function getContentThemes(): ContentThemes | null {
  if (!fs.existsSync(THEMES_PATH)) return null;
  const raw = fs.readFileSync(THEMES_PATH, "utf-8");
  return JSON.parse(raw) as ContentThemes;
}
