// Turns the backend's character spans into numbered lines for the line-by-line redaction pass.

export type Entity = { start: number; end: number; text: string; type: string; placeholder: string };

export type Segment =
  | { kind: "text"; text: string }
  | { kind: "value"; text: string; type: string; placeholder: string; entity: number };

export type Line = { index: number; start: number; segments: Segment[]; changes: number };

export function toLines(text: string, entities: Entity[]): Line[] {
  const order = entities.map((e, i) => ({ e, i })).sort((a, b) => a.e.start - b.e.start);
  const lines: Line[] = [];
  let start = 0;
  text.split("\n").forEach((raw, index) => {
    const end = start + raw.length;
    const segments: Segment[] = [];
    let at = start;
    let changes = 0;
    for (const { e, i } of order) {
      if (e.end <= start || e.start >= end) continue;
      const from = Math.max(e.start, start);
      const to = Math.min(e.end, end);
      if (from > at) segments.push({ kind: "text", text: text.slice(at, from) });
      segments.push({ kind: "value", text: text.slice(from, to), type: e.type, placeholder: e.placeholder, entity: i });
      if (e.start >= start) changes += 1;
      at = to;
    }
    if (at < end || segments.length === 0) segments.push({ kind: "text", text: text.slice(at, end) });
    lines.push({ index, start, segments, changes });
    start = end + 1;
  });
  return lines;
}

export type Change = { line: number; entity: number; text: string; type: string; placeholder: string };

export function changeList(lines: Line[]): Change[] {
  const seen = new Set<number>();
  const out: Change[] = [];
  for (const line of lines) {
    for (const s of line.segments) {
      if (s.kind !== "value" || seen.has(s.entity)) continue;
      seen.add(s.entity);
      out.push({ line: line.index, entity: s.entity, text: s.text, type: s.type, placeholder: s.placeholder });
    }
  }
  return out;
}

export function stepMs(lineCount: number): number {
  return Math.min(380, Math.max(70, Math.round(6000 / Math.max(1, lineCount))));
}

const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

export function markValues(answer: string, values: string[]): { text: string; real: boolean }[] {
  const wanted = [...new Set(values.filter((v) => v.trim()))].sort((a, b) => b.length - a.length);
  if (!wanted.length) return [{ text: answer, real: false }];
  const parts = answer.split(new RegExp(`(${wanted.map(escape).join("|")})`, "g"));
  return parts.filter((p) => p !== "").map((p) => ({ text: p, real: wanted.includes(p) }));
}
