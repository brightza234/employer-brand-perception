export type Sentiment = "positive" | "neutral" | "negative";

export interface TrendPoint {
  period: string; // "YYYY-MM"
  positive: number;
  neutral: number;
  negative: number;
}

export interface SampleComment {
  text: string;
  sentiment: Sentiment;
  source: string;
  url: string;
}

export interface CompanyInsights {
  total_comments: number;
  sentiment_distribution: Record<Sentiment, number>;
  theme_distribution: Record<string, number>;
  trend: TrendPoint[];
  sample_comments: Record<string, SampleComment[]>;
}

export interface ChiSquareTest {
  chi2: number;
  p_value: number;
  degrees_of_freedom: number;
  "significant_at_0.05": boolean;
  note: string;
}

export interface ProcessedInsights {
  generated_at: string;
  companies: Record<string, CompanyInsights>;
  chi_square_theme_test: ChiSquareTest | null;
}
