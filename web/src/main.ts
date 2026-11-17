import type { DraftResult, TriageResult, CreatorProfile } from "./types";

const API = "http://127.0.0.1:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API ${res.status} on ${path}`);
  return res.json() as Promise<T>;
}

function el(id: string): HTMLElement {
  const node = document.getElementById(id);
  if (!node) throw new Error(`missing #${id}`);
  return node;
}

function show(id: string, text: string): void {
  el(id).textContent = text;
}

async function run(): Promise<void> {
  const subject = (el("subject") as HTMLInputElement).value;
  const body = (el("body") as HTMLTextAreaElement).value;
  show("status", "Working…");
  try {
    const triage = await post<TriageResult>("/triage", { subject, body });
    const draft = await post<DraftResult>("/draft", { subject, body });
    const extracted = await post<{ profile: CreatorProfile }>("/extract", { text: body });

    show("triage", `${triage.intent} · ${triage.priority} priority · human review: ${triage.needs_human_review}`);
    show("draft", draft.draft);
    show(
      "guardrails",
      draft.safe_to_send
        ? `PASS (${draft.provider} / ${draft.model}, effort ${draft.effort})`
        : `NEEDS HUMAN REVIEW: ${draft.guardrail_failures.join("; ")}`,
    );
    show("profile", JSON.stringify(extracted.profile, null, 2));
    show("status", "Done — draft was not sent, it is a preview only.");
  } catch (err) {
    show("status", `Could not reach the API at ${API}. Start it first: uvicorn backend.main:app --reload — ${err}`);
  }
}

document.getElementById("run")?.addEventListener("click", () => void run());
