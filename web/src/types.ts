export interface TriageResult {
  intent: string;
  priority: "low" | "medium" | "high";
  needs_human_review: boolean;
  reason: string;
}

export interface DraftResult {
  draft: string;
  provider: "openai" | "mock";
  model: string;
  effort: string;
  guardrail_failures: string[];
  safe_to_send: boolean;
  needs_human_review: boolean;
}

export interface CreatorProfile {
  handle: string | null;
  email: string | null;
  platform: string | null;
  niche: string | null;
  followers: number | null;
  links: string[];
  confidence: number;
}
