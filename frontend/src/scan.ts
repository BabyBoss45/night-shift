// Live scan state: what the backend has really done so far, built from its stream events.
// Pure functions only, so the event-to-state logic can be unit tested.

import { normaliseChunk, type ChunkInfo, type RedactResult, type ScanEntity, type ScanEvent } from "./api";
import type { Entity } from "./redaction";
import type { Session } from "./session";

export type PartStatus = "pending" | ChunkInfo["status"];

export type Part = Omit<ChunkInfo, "status"> & {
  status: PartStatus;
  order: number | null; // the order this part finished in (parts finish out of index order)
};

export type Scan = {
  live: boolean; // false when the backend has no stream and the parts were rebuilt from one response
  model: "on" | "off" | null;
  t1Prompt: string | null;
  parts: Part[]; // by index
  finished: number;
  entities: ScanEntity[]; // regex + model so far, deduplicated by start and end
  done: boolean;
  error: string | null;
};

export const emptyScan = (): Scan => ({
  live: true,
  model: null,
  t1Prompt: null,
  parts: [],
  finished: 0,
  entities: [],
  done: false,
  error: null,
});

const key = (e: { start: number; end: number }) => `${e.start}:${e.end}`;

function addEntities(have: ScanEntity[], more: ScanEntity[]): ScanEntity[] {
  if (!more.length) return have;
  const seen = new Set(have.map(key));
  const out = [...have];
  for (const e of more) {
    if (seen.has(key(e))) continue;
    seen.add(key(e));
    out.push(e);
  }
  return out;
}

const pending = (c: Pick<ChunkInfo, "index" | "chunk_id" | "start" | "end">): Part => ({
  ...c,
  mreq_id: null,
  error: null,
  found: 0,
  latency_ms: null,
  status: "pending",
  order: null,
});

function finish(scan: Scan, c: ChunkInfo): Scan {
  const at = scan.parts.findIndex((p) => p.index === c.index);
  if (at >= 0 && scan.parts[at].status !== "pending") return scan; // a repeat: the first answer stands
  const part: Part = { ...c, order: scan.finished };
  const parts = at >= 0 ? scan.parts.map((p, i) => (i === at ? part : p)) : [...scan.parts, part].sort((a, b) => a.index - b.index);
  return { ...scan, parts, finished: scan.finished + 1 };
}

export function scanReducer(scan: Scan, ev: ScanEvent): Scan {
  switch (ev.type) {
    case "start": {
      const known = new Map(scan.parts.map((p) => [p.index, p]));
      const parts = [...ev.data.chunks].sort((a, b) => a.index - b.index).map((c) => known.get(c.index) ?? pending(c));
      return { ...scan, model: ev.data.model, t1Prompt: ev.data.t1_prompt, parts };
    }
    case "regex":
      return { ...scan, entities: addEntities(scan.entities, ev.data.entities) };
    case "chunk": {
      const { entities, ...chunk } = ev.data;
      const next = finish(scan, chunk);
      return { ...next, entities: addEntities(next.entities, entities) };
    }
    case "done": {
      let next: Scan = { ...scan, model: scan.model ?? ev.data.model, done: true, error: null };
      ev.data.chunks.forEach((c, i) => (next = finish(next, normaliseChunk(c, i, ev.data.model))));
      return next;
    }
    case "error":
      return { ...scan, error: ev.data.message };
  }
}

// ---------- Offsets ----------

// The backend counts characters as Python code points; JS strings count UTF-16 units. They differ only
// after an emoji or another character outside the Basic Multilingual Plane, so map offsets when one is there.
let memo: { text: string; map: (n: number) => number } | null = null;

export function unitMap(text: string): (n: number) => number {
  if (memo?.text === text) return memo.map;
  let map = (n: number) => n;
  if (/[\uD800-\uDBFF][\uDC00-\uDFFF]/.test(text)) {
    const units: number[] = [];
    let u = 0;
    for (const ch of text) {
      units.push(u);
      u += ch.length;
    }
    units.push(u);
    map = (n: number) => (n >= units.length ? u + (n - units.length + 1) : units[Math.max(0, n)]);
  }
  memo = { text, map };
  return map;
}

function moveSpan<T extends { start: number; end: number }>(x: T, map: (n: number) => number): T {
  return { ...x, start: map(x.start), end: map(x.end) };
}

export function resultInUnits(result: RedactResult, text: string): RedactResult {
  const map = unitMap(text);
  return {
    ...result,
    entities: result.entities.map((e) => moveSpan(e, map)),
    chunks: result.chunks.map((c, i) => moveSpan(normaliseChunk(c, i, result.model), map)),
  };
}

export function eventInUnits(ev: ScanEvent, text: string): ScanEvent {
  const map = unitMap(text);
  switch (ev.type) {
    case "start":
      return { ...ev, data: { ...ev.data, chunks: ev.data.chunks.map((c) => moveSpan(c, map)) } };
    case "regex":
      return { ...ev, data: { entities: ev.data.entities.map((e) => moveSpan(e, map)) } };
    case "chunk":
      return { ...ev, data: { ...moveSpan(ev.data, map), entities: ev.data.entities.map((e) => moveSpan(e, map)) } };
    case "done":
      return { ...ev, data: resultInUnits(ev.data, text) };
    case "error":
      return ev;
  }
}

// One stream event applied to a session: the scan state, plus the result and status when the run ends.
export function applyEvent(s: Session, raw: ScanEvent): Partial<Session> {
  const ev = eventInUnits(raw, s.doc.text);
  const scan = scanReducer(s.scan ?? emptyScan(), ev);
  if (ev.type === "done") return { scan, status: "review", result: ev.data };
  if (ev.type === "error") return { scan, status: "failed", error: ev.data.message };
  return { scan };
}

// ---------- What the page shows ----------

// Live values merged the way the backend merges them (overlaps become one span, typed by the longest),
// with a type-only tag until the final result numbers them.
export function liveEntities(found: ScanEntity[], text: string): Entity[] {
  const out: Entity[] = [];
  for (const e of [...found].sort((a, b) => a.start - b.start || b.end - a.end)) {
    const last = out[out.length - 1];
    if (last && e.start < last.end) {
      const type = e.end - e.start > last.end - last.start ? e.type : last.type;
      const end = Math.max(last.end, e.end);
      out[out.length - 1] = { start: last.start, end, text: text.slice(last.start, end), type, placeholder: `[${type}]` };
    } else {
      out.push({ start: e.start, end: e.end, text: text.slice(e.start, e.end), type: e.type, placeholder: `[${e.type}]` });
    }
  }
  return out;
}

// The parts of a session: from the live scan, else from a finished result.
export function partsOf(s: Pick<Session, "scan" | "result">): Part[] {
  if (s.scan?.parts.length) return s.scan.parts;
  return (s.result?.chunks ?? []).map((c, i) => ({ ...c, order: i }));
}

// The part an offset falls in: the last one starting at or before it (parts are contiguous).
export function partAt(parts: Part[], offset: number): Part | undefined {
  let found: Part | undefined;
  for (const p of parts) if (p.start <= offset) found = p;
  return found;
}

// Values the backend has reported in parts that have finished: the real count so far.
export function hiddenSoFar(entities: Entity[], parts: Part[]): number {
  if (!parts.length) return 0;
  return entities.filter((e) => {
    const p = partAt(parts, e.start);
    return !!p && p.status !== "pending";
  }).length;
}

// ---------- The pass ----------

// Line range of each part: a line belongs to the part its first character is in.
export function partLines(parts: Part[], lineStarts: number[]): Map<number, [number, number]> {
  const out = new Map<number, [number, number]>();
  lineStarts.forEach((start, line) => {
    const p = partAt(parts, start);
    if (!p) return;
    const span = out.get(p.index);
    if (span) span[1] = line;
    else out.set(p.index, [line, line]);
  });
  return out;
}

// One tick of the pass. Each finished part sweeps its own lines, one per tick, from its first line to one
// past its last; parts that finish later start later. "calm" (reduced motion) resolves a part at once.
export function advancePasses(
  cursors: Record<number, number>,
  parts: Part[],
  lines: Map<number, [number, number]>,
  calm: boolean,
): Record<number, number> {
  let next = cursors;
  for (const p of parts) {
    if (p.status === "pending") continue;
    const [first, last] = lines.get(p.index) ?? [0, -1];
    const at = cursors[p.index];
    const to = calm ? last + 1 : at === undefined ? first : at <= last ? at + 1 : at;
    if (to !== at) {
      if (next === cursors) next = { ...cursors };
      next[p.index] = to;
    }
  }
  return next;
}

export function passesDone(cursors: Record<number, number>, parts: Part[], lines: Map<number, [number, number]>): boolean {
  return parts.every((p) => {
    if (p.status === "pending") return false;
    const [, last] = lines.get(p.index) ?? [0, -1];
    return (cursors[p.index] ?? -Infinity) > last;
  });
}
