export interface KolMetrics {
  handle: string;
  display_name: string;
  subscriber_count: number;
  video_sample_size: number;
  avg_views: number;
  avg_likes: number;
  avg_comments: number;
  engagement_rate: number;
  upload_consistency: number;
  z_engagement_rate: number;
  z_avg_views: number;
  z_upload_consistency: number;
  composite_score: number;
  rank: number;
}

export interface CorrelationPair {
  r: number;
  p_value: number;
}

export interface RegressionSummary {
  intercept: number;
  coef_subscriber_count: number;
  coef_upload_consistency: number;
  r_squared: number;
  n: number;
}

export interface KolScores {
  collected_at: string;
  computed_at: string;
  weights: {
    engagement_rate: number;
    avg_views: number;
    upload_consistency: number;
  };
  kols: KolMetrics[];
  correlation_matrix: Record<string, CorrelationPair>;
  regression_engagement_on_size_and_consistency: RegressionSummary;
  limitations: string;
}

export interface ContentThemeEntry {
  display_name: string;
  video_themes: Record<string, string>;
  theme_breakdown: Record<string, number>;
}

export type ContentThemes = Record<string, ContentThemeEntry>;
