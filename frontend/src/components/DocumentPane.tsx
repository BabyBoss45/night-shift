import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { changeList, stepMs, toLines, type Line } from "../redaction";
import type { Session } from "../session";
import { Button, Chip, Icon, LinkButton, Tabs } from "../ui/kit";

const TYPES: [string, string][] = [
  ["CUSTOM", "Client or case reference"], ["PERSON", "Person"], ["ADDRESS", "Address"], ["POSTCODE", "Postcode"],
  ["EMAIL", "Email"], ["PHONE", "Phone"], ["DOB", "Date of birth"], ["BANK_ACCOUNT", "Account number"],
  ["SORT_CODE", "Sort code"], ["IBAN", "IBAN"], ["CARD", "Card number"], ["NI_NUMBER", "NI number"], ["ID_DOC", "ID document"],
];

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const isHeading = (t: string) => t.length > 0 && t.length < 60 && /[A-Z]/.test(t) && t === t.toUpperCase();
const lineText = (l: Line) => l.segments.map((s) => s.text).join("");

type Pop = { entity: number; x: number; y: number };
type Pick = { text: string; x: number; y: number };

export function DocumentPane({ session, modelOn, onRevealed, onApprove, onDecline, onRetry, onCorrect }: {
  session: Session;
  modelOn: boolean;
  onRevealed: () => void;
  onApprove: () => void;
  onDecline: () => void;
  onRetry: () => void;
  onCorrect: (action: "hide" | "unhide", text: string, type?: string) => Promise<void>;
}) {
  const { doc, result, status } = session;
  const lines = useMemo(() => toLines(doc.text, result?.entities ?? []), [doc.text, result]);
  const changes = useMemo(() => changeList(lines), [lines]);
  const done = session.revealed || status === "approved" || status === "declined";
  const passing = status === "review" && !session.revealed && !!result;
  const editable = status === "review" && session.revealed;

  const [cursor, setCursor] = useState(-1);
  const [view, setView] = useState<"lines" | "pages">("lines");
  const [focus, setFocus] = useState<number | null>(null);
  const [pop, setPop] = useState<Pop | null>(null);
  const [pick, setPick] = useState<Pick | null>(null);
  const [pickType, setPickType] = useState("CUSTOM");
  const [note, setNote] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [fixing, setFixing] = useState(false);
  const lineEls = useRef<(HTMLDivElement | null)[]>([]);
  const body = useRef<HTMLDivElement>(null);
  const revealed = useRef(onRevealed);
  revealed.current = onRevealed;

  useEffect(() => {
    setView("lines");
    setFocus(null);
    setPop(null);
    setPick(null);
    setNote(null);
    setFixing(false);
    body.current?.scrollTo({ top: 0 });
  }, [session.id]);

  // The line-by-line pass: one line per tick, values flash and turn into bars, then the review bar comes up.
  useEffect(() => {
    if (!passing) return;
    if (reducedMotion()) {
      revealed.current();
      return;
    }
    let i = -1;
    setCursor(-1);
    const timer = window.setInterval(() => {
      i += 1;
      setCursor(i);
      lineEls.current[i]?.scrollIntoView({ block: "nearest", behavior: "smooth" });
      if (i >= lines.length) {
        window.clearInterval(timer);
        window.setTimeout(() => revealed.current(), 250);
      }
    }, stepMs(lines.length));
    return () => window.clearInterval(timer);
  }, [passing, session.id, lines.length]);

  const at = done ? lines.length : cursor;
  const hiddenSoFar = done ? changes.length : lines.slice(0, Math.max(0, at + 1)).reduce((n, l) => n + l.changes, 0);
  const progress = status === "scanning" ? 0 : done ? 1 : Math.max(0, at + 1) / Math.max(1, lines.length);
  const distinct = new Set(result?.entities.map((e) => e.placeholder)).size;
  const failedChunks = modelOn ? (result?.chunks.filter((c) => c.error).length ?? 0) : 0;

  function goTo(next: number) {
    if (!changes.length) return;
    const i = (next + changes.length) % changes.length;
    setFocus(i);
    body.current?.querySelector(`[data-entity="${changes[i].entity}"]`)?.scrollIntoView({ block: "center", behavior: "smooth" });
  }

  async function correct(action: "hide" | "unhide", text: string, type?: string) {
    setWorking(true);
    try {
      await onCorrect(action, text, type);
      setNote(action === "hide" ? "Hidden. The AI gets a placeholder." : "Shown. The AI will see this value.");
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setWorking(false);
      setFixing(false);
      setPop(null);
      setPick(null);
      window.getSelection()?.removeAllRanges();
    }
  }

  function onMouseUp() {
    if (!editable) return;
    const sel = window.getSelection();
    const text = sel?.toString().trim() ?? "";
    if (!sel || !text || !body.current?.contains(sel.anchorNode)) return setPick(null);
    if (text.includes("\n")) return setNote("Select text within one line, then press Hide.");
    const r = sel.getRangeAt(0).getBoundingClientRect();
    setPop(null);
    setPick({ text, x: r.left, y: r.bottom + 10 });
  }

  const popEntity = pop && result ? result.entities[pop.entity] : null;

  return (
    <section className="relative flex min-h-0 flex-col bg-bone">
      <header className="flex flex-wrap items-center gap-x-3 gap-y-2 border-b-4 border-ink bg-paper px-5 py-3.5">
        <h2 className="min-w-0 max-w-full truncate font-pixel text-[22px] leading-tight font-bold" title={doc.filename}>
          {doc.filename}
        </h2>
        <Chip>{status === "scanning" ? "Reading" : `${hiddenSoFar} changes`}</Chip>
        {failedChunks > 0 && <Chip tone="red">{failedChunks} part{failedChunks > 1 ? "s" : ""} rules only</Chip>}
        <span className="ml-auto flex items-center gap-3">
          {doc.kind === "pdf" && done && (
            <Tabs label="View" value={view} options={[["lines", "Lines"], ["pages", "Pages"]]} onChange={setView} />
          )}
          {!done && (
            <span className="relative block h-3 w-[142px] text-stone/40 segments" role="progressbar" aria-label="Redaction progress" aria-valuenow={Math.round(progress * 100)}>
              <span
                className={`absolute inset-y-0 left-0 block text-signal segments ${status === "scanning" ? "indeterminate w-full" : ""}`}
                style={status === "scanning" ? undefined : { width: `${progress * 100}%`, transition: "width .3s ease-out" }}
              />
            </span>
          )}
        </span>
      </header>

      <div ref={body} onMouseUp={onMouseUp} className={`relative min-h-0 flex-1 overflow-y-auto px-3 pt-6 pb-44 sm:px-6 ${fixing ? "cursor-text" : ""}`}>
        {status === "failed" ? (
          <div className="mx-auto max-w-[760px] bg-paper p-5 px-frame px-frame-red">
            <p className="font-semibold text-signal-deep">The redaction did not finish.</p>
            <p className="mt-1 text-quiet">{session.error}</p>
            <Button className="mt-4" icon="right" onClick={onRetry}>
              Try again
            </Button>
          </div>
        ) : view === "pages" ? (
          <div className="flex flex-col items-center gap-8">
            {doc.pages.map((p, n) => (
              <div key={n} className="relative w-full max-w-[760px] bg-white px-frame">
                <img src={api.pageUrl(doc.doc_id, n)} alt={`Page ${n + 1} with personal data covered`} className="block w-full" />
                {result?.boxes.filter((b) => b.page === n).map((b, i) => (
                  <span key={i} title={b.placeholder} className="absolute bg-ink"
                    style={{ left: `${(b.x0 / p.width) * 100}%`, top: `${(b.y0 / p.height) * 100}%`, width: `${((b.x1 - b.x0) / p.width) * 100}%`, height: `${((b.y1 - b.y0) / p.height) * 100}%` }} />
                ))}
              </div>
            ))}
          </div>
        ) : (
          <article className="paper-sheet mx-auto max-w-[860px] bg-paper py-6 px-frame" aria-label="Document text">
            {lines.map((line) => {
              const text = lineText(line);
              if (!text.trim()) return <div key={line.index} className="h-3" />;
              const current = passing && line.index === cursor;
              const passed = done || line.index <= cursor;
              const cls = [
                "doc-line grid grid-cols-[48px_12px_1fr] items-center",
                status === "scanning" ? "is-reading" : "",
                current ? "is-current" : "",
                passed ? "is-passed" : "",
              ].join(" ");
              return (
                <div key={line.index} ref={(el) => { lineEls.current[line.index] = el; }} className={cls} style={{ ["--i" as string]: line.index }}>
                  <span className="pr-3 text-right font-label text-[10px] text-quiet tabular-nums">{String(line.index + 1).padStart(2, "0")}</span>
                  <i className={`gutter-mark block h-[22px] w-1 ${line.changes ? "bg-signal" : ""}`} />
                  <span className={`min-h-[30px] py-1 pr-6 leading-[22px] whitespace-pre-wrap ${isHeading(text.trim()) ? "font-serif text-[13px] font-semibold tracking-[0.06em]" : "font-serif text-[15px]"}`}>
                    {line.segments.map((s, i) =>
                      s.kind === "text" ? (
                        <Fragment key={i}>{s.text}</Fragment>
                      ) : (
                        <button
                          key={i}
                          type="button"
                          data-entity={s.entity}
                          data-p={s.placeholder.replace(/[[\]]/g, "")}
                          style={{ ["--tag" as string]: `${s.placeholder.length * 7 + 2}px` }}
                          tabIndex={editable ? 0 : -1}
                          aria-label={passed ? `${s.placeholder}, hidden` : undefined}
                          onClick={(e) => {
                            if (!editable) return;
                            const r = e.currentTarget.getBoundingClientRect();
                            setPick(null);
                            setPop({ entity: s.entity, x: r.left, y: r.bottom + 10 });
                          }}
                          className={[
                            "val",
                            passed ? "is-hidden" : "",
                            current ? "is-flash" : "",
                            editable ? "is-live" : "",
                            focus !== null && changes[focus]?.entity === s.entity ? "is-focus" : "",
                          ].join(" ")}
                        >
                          {s.text}
                        </button>
                      ),
                    )}
                  </span>
                </div>
              );
            })}
          </article>
        )}
      </div>

      {popEntity && pop && (
        <div role="dialog" aria-label="Hidden value" className="pop fixed z-30 w-72 bg-paper p-3 px-frame" style={{ left: pop.x, top: pop.y }}>
          <p className="px-label text-signal-deep">{popEntity.placeholder.replace(/[[\]]/g, "")}</p>
          <p className="mt-1 font-serif text-[16px] break-words">{popEntity.text}</p>
          <p className="mt-2 text-xs text-quiet">Only you see this value. The AI gets the placeholder.</p>
          <div className="mt-3 flex gap-2">
            <Button size="sm" icon="eye" disabled={working} onClick={() => correct("unhide", popEntity.text)}>
              Not personal, show it
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setPop(null)}>
              Close
            </Button>
          </div>
        </div>
      )}

      {pick && (
        <div role="dialog" aria-label="Hide selected text" className="pop fixed z-30 flex flex-wrap items-center gap-2 bg-paper p-2 px-frame" style={{ left: pick.x, top: pick.y }}>
          <span className="max-w-48 truncate font-serif">“{pick.text}”</span>
          <label className="sr-only" htmlFor="pick-type">Type</label>
          <select id="pick-type" value={pickType} onChange={(e) => setPickType(e.target.value)} className="px-frame-thin bg-bone px-1.5 py-1 text-[13px]">
            {TYPES.map(([v, label]) => <option key={v} value={v}>{label}</option>)}
          </select>
          <Button size="sm" variant="primary" icon="marker" loading={working} onClick={() => correct("hide", pick.text, pickType)}>
            Hide
          </Button>
        </div>
      )}

      {status === "review" && (
        <div className={`review-bar absolute right-4 bottom-4 left-4 z-20 flex flex-col gap-3 bg-ink px-4 py-3 text-bone px-frame ${session.revealed ? "is-up" : ""}`}>
          <p className={`min-w-0 truncate text-[14px] ${fixing ? "font-semibold text-signal-soft" : "text-bone/85"}`} aria-live="polite">
            {fixing ? "Select the missed text on the page, then press Hide." : (note ?? "Check the changes. Missed one? Use Fix a miss.")}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <span className="mr-auto font-label text-[12px] whitespace-nowrap tabular-nums">
              {changes.length} changes · {distinct} values
            </span>
            <Button size="sm" icon="up" onClick={() => goTo((focus ?? 0) - 1)}>Prev</Button>
            <Button size="sm" icon="down" onClick={() => goTo(focus === null ? 0 : focus + 1)}>Next</Button>
            <Button size="sm" icon="marker" aria-pressed={fixing} onClick={() => setFixing((f) => !f)}>Fix a miss</Button>
            <Button size="sm" variant="ghost" icon="close" onClick={onDecline}>Decline</Button>
            <Button variant="primary" icon="check" onClick={onApprove}>Approve all</Button>
          </div>
        </div>
      )}
      {status === "approved" && (
        <div className="absolute right-4 bottom-4 left-4 z-20 flex flex-wrap items-center gap-3 bg-paper px-4 py-3 px-frame">
          <span className="mr-auto flex items-center gap-2 text-[15px]">
            <Icon name="check" className="text-signal" />
            Approved. Ask about it on the right; the AI only sees the placeholders.
          </span>
          <LinkButton href={api.fileUrl(doc.doc_id)} download variant="dark" icon="download">
            Download redacted {doc.kind === "pdf" ? "PDF" : "text"}
          </LinkButton>
        </div>
      )}
      {status === "declined" && (
        <div className="absolute right-4 bottom-4 left-4 z-20 flex items-center gap-2 bg-paper px-4 py-3 px-frame">
          <Icon name="close" />
          Declined. Nothing from this document was sent.
        </div>
      )}
    </section>
  );
}
