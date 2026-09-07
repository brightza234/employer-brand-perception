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
summary (3-5 sentences, plain prose, no headers or bullet points) covering the overall
sentiment, the most prominent themes, and one notable risk or opportunity.

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

  const summary = response.content[0].type === "text" ? response.content[0].text : "";
  return NextResponse.json({ summary });
}
