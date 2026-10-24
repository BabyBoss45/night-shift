import type { AskResult, DocPayload, RedactResult } from "./api";

export type Status = "scanning" | "review" | "approved" | "declined" | "failed";

export type Turn = { question: string; answer?: AskResult; error?: string };

// One uploaded document. Kept in memory only: nothing about a document is stored in the browser.
export type Session = {
  id: string;
  doc: DocPayload;
  status: Status;
  result?: RedactResult;
  error?: string;
  revealed: boolean;
  at: number;
  turns: Turn[];
};
