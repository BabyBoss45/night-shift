// Typed calls to the Veil backend (FastAPI in backend/, proxied at /api by Vite).

import type { Entity } from "./redaction";

export type DocPayload = {
  doc_id: string;
  kind: "pdf" | "text";
  filename: string;
  text: string;
  pages: { width: number; height: number }[];
};

export type Box = { page: number; x0: number; y0: number; x1: number; y1: number; type: string; placeholder: string };

export type RedactResult = {
  doc_id: string;
  redacted_text: string;
  entities: Entity[];
  boxes: Box[];
  chunks: { chunk_id: number; mreq_id: string | null; error: string | null; found: number }[];
  stats: Record<string, number>;
  model: "on" | "off";
};

export type AskResult = {
  answer: string;
  answer_with_placeholders: string;
  sent_text: string;
  unknown_placeholders: string[];
  mreq_id: string | null;
};

export type Health = { model: "on" | "off"; t1_model: string | null; t2_model: string | null };
export type Sample = {
  name: string;
  label: string;
  title: string;
  kind: string;
  pages: number;
  values: number | null;
  types: Record<string, number>;
};

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, init);
  } catch {
    throw new Error("The Veil backend is not running. Start it on port 8000 and try again.");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `The backend answered ${res.status}.`);
  }
  return res.json() as Promise<T>;
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const api = {
  health: () => call<Health>("/api/health"),
  samples: () => call<Sample[]>("/api/samples"),
  openSample: (name: string) => call<DocPayload>(`/api/samples/${encodeURIComponent(name)}`, { method: "POST" }),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return call<DocPayload>("/api/documents", { method: "POST", body: form });
  },
  paste: (text: string) => {
    const form = new FormData();
    form.append("text", text);
    return call<DocPayload>("/api/documents", { method: "POST", body: form });
  },
  redact: (id: string) => call<RedactResult>(`/api/documents/${id}/redact`, { method: "POST" }),
  correct: (id: string, action: "hide" | "unhide", text: string, type = "CUSTOM") =>
    call<RedactResult>(`/api/documents/${id}/corrections`, json({ action, text, type })),
  ask: (id: string, question: string) => call<AskResult>(`/api/documents/${id}/ask`, json({ question })),
  fileUrl: (id: string) => `/api/documents/${id}/file`,
  thumbUrl: (name: string) => `/api/samples/${encodeURIComponent(name)}/thumb.png`,
  pageUrl: (id: string, page: number) => `/api/documents/${id}/pages/${page}.png?scale=2`,
};
