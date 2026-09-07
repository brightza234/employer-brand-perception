import Anthropic from "@anthropic-ai/sdk";
import { NextRequest, NextResponse } from "next/server";
import { getInsights } from "@/lib/data";

export async function POST(request: NextRequest) {
  const { company } = await request.json();

  const insights = getInsights();
  const companyInsights = insights?.companies?.[company];
  if (!companyInsights) {
    return NextResponse.json({ error: "no data for company" }, { status: 404 });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return NextResponse.json({ error: "ANTHROPIC_API_KEY not configured" }, { status: 500 });
  }

  const client = new Anthropic({ apiKey });

  const prompt = `You are an HR/employer-branding analyst. Given this aggregated data about how
people talk about "${company}" as an employer on social media, write a concise executive
summary (3-5 sentences) covering the overall sentiment, the most prominent themes, and one
notable risk or opportunity. Respond with ONLY the paragraph itself: plain prose, no title,
no markdown formatting (no #, no **, no bullet points) — just sentences.

Data:
${JSON.stringify(
  {
    total_comments: companyInsights.total_comments,
    sentiment_distribution: companyInsights.sentiment_distribution,
    theme_distribution: companyInsights.theme_distribution,
  },
  null,
  2
)}`;

  const response = await client.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 512,
    messages: [{ role: "user", content: prompt }],
  });

  const rawSummary = response.content[0].type === "text" ? response.content[0].text : "";
  // strip a stray markdown heading/bold if the model adds one despite instructions —
  // the panel renders this as plain text, not markdown
  const summary = rawSummary
    .replace(/^#{1,6}\s+.*\n+/, "")
    .replace(/\*\*/g, "")
    .trim();
  return NextResponse.json({ summary });
}
