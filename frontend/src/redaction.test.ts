import { describe, expect, it } from "vitest";
import { changeList, markValues, stepMs, toLines, type Entity } from "./redaction";

const ent = (text: string, all: string, type: string, placeholder: string): Entity => {
  const start = all.indexOf(text);
  return { start, end: start + text.length, text, type, placeholder };
};

describe("toLines", () => {
  it("splits the text into numbered lines with their offsets", () => {
    const lines = toLines("Dear Jo\nThanks", []);
    expect(lines.map((l) => [l.index, l.start, l.segments])).toEqual([
      [0, 0, [{ kind: "text", text: "Dear Jo" }]],
      [1, 8, [{ kind: "text", text: "Thanks" }]],
    ]);
  });

  it("cuts a line around each hidden value", () => {
    const text = "Tenant: Raj Patel, sort code 20-45-77.";
    const lines = toLines(text, [
      ent("Raj Patel", text, "PERSON", "[PERSON_1]"),
      ent("20-45-77", text, "SORT_CODE", "[SORT_CODE_1]"),
    ]);
    expect(lines[0].segments).toEqual([
      { kind: "text", text: "Tenant: " },
      { kind: "value", text: "Raj Patel", type: "PERSON", placeholder: "[PERSON_1]", entity: 0 },
      { kind: "text", text: ", sort code " },
      { kind: "value", text: "20-45-77", type: "SORT_CODE", placeholder: "[SORT_CODE_1]", entity: 1 },
      { kind: "text", text: "." },
    ]);
    expect(lines[0].changes).toBe(2);
  });

  it("hides both parts of a value that runs over a line break", () => {
    const text = "Address: 14 Elm\nRoad, Leeds";
    const lines = toLines(text, [ent("14 Elm\nRoad", text, "ADDRESS", "[ADDRESS_1]")]);
    expect(lines[0].segments[1]).toMatchObject({ kind: "value", text: "14 Elm", entity: 0 });
    expect(lines[1].segments[0]).toMatchObject({ kind: "value", text: "Road", entity: 0 });
    expect(lines[0].changes + lines[1].changes).toBe(1);
  });
});

describe("changeList", () => {
  it("lists each hidden value once, in reading order, with the line it starts on", () => {
    const text = "Jo Smith\nemail jo@x.io\nJo Smith";
    const ents = [ent("jo@x.io", text, "EMAIL", "[EMAIL_1]"), { ...ent("Jo Smith", text, "PERSON", "[PERSON_1]") }];
    ents.push({ ...ents[1], start: text.lastIndexOf("Jo Smith"), end: text.length });
    const list = changeList(toLines(text, ents));
    expect(list.map((c) => [c.line, c.entity])).toEqual([[0, 1], [1, 0], [2, 2]]);
  });
});

describe("stepMs", () => {
  it("keeps the line-by-line pass between 70 and 380 ms per line", () => {
    expect(stepMs(5)).toBe(380);
    expect(stepMs(40)).toBe(150);
    expect(stepMs(1000)).toBe(70);
  });
});

describe("markValues", () => {
  it("marks the real values in an answer, longest first", () => {
    const parts = markValues("Raj Patel pays from 31926819.", ["Raj", "Raj Patel", "31926819"]);
    expect(parts).toEqual([
      { text: "Raj Patel", real: true },
      { text: " pays from ", real: false },
      { text: "31926819", real: true },
      { text: ".", real: false },
    ]);
  });
});
