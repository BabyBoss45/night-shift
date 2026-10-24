"""Find personal data in a Document and turn it into placeholders and page rectangles.

1. Regex layer over the whole text (cards, accounts, sort codes, IBAN, NI, postcodes, phones, emails).
2. T1 (the Mubit-trained model) per chunk; every value it returns is then located across the WHOLE
   document, so a name found in chunk 2 is hidden in chunk 5 too.
3. Overlapping spans are merged into one, so a regex hit is never uncovered by a shorter model span.
4. A per-document vault gives each distinct value one placeholder; PDF words that overlap a span
   become one rectangle per line.
"""

from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from evalkit import regex_baseline
from evalkit.redact import Vault, apply
from evalkit.spans import Span, locate

from .extract import Document

MAX_CHARS = 4000  # about 1,000 tokens per T1 call


@dataclass
class T1Result:
    entities: list[dict]
    mreq_id: str | None
    error: str | None


@dataclass
class ChunkInfo:
    chunk_id: str
    start: int
    end: int
    mreq_id: str | None
    error: str | None
    found: int = 0


@dataclass
class Box:
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    type: str
    placeholder: str
    span_index: int


@dataclass
class PipelineResult:
    spans: list[Span]
    redacted_text: str
    vault: Vault
    boxes: list[Box]
    chunks: list[ChunkInfo]
    stats: dict[str, int] = field(default_factory=dict)
    model_values: dict[str, str] = field(default_factory=dict)  # what T1 returned: value -> type
    hidden: dict[str, str] = field(default_factory=dict)  # reviewer: value -> type to hide
    unhidden: set[str] = field(default_factory=set)  # reviewer: values to show


def chunk_ranges(text: str, max_chars: int = MAX_CHARS) -> list[tuple[int, int]]:
    """Paragraph-based chunks of at most max_chars; a longer paragraph is cut at a line break or space."""
    ranges: list[tuple[int, int]] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + max_chars)
        if end < n:
            for sep in ("\n\n", "\n", " "):
                cut = text.rfind(sep, start + 1, end)
                if cut > start:
                    end = cut + len(sep)
                    break
        ranges.append((start, end))
        start = end
    return ranges or [(0, 0)]


def _merge(spans: list[Span], text: str) -> list[Span]:
    """Union overlapping spans; the type comes from the longest original span in each group."""
    out: list[Span] = []
    for sp in sorted(spans, key=lambda s: (s.start, -(s.end - s.start))):
        if out and sp.start < out[-1].end:
            last = out[-1]
            longest = max((last, sp), key=lambda s: s.end - s.start)
            s, e = last.start, max(last.end, sp.end)
            out[-1] = Span(s, e, longest.type, text[s:e])
        else:
            out.append(sp)
    return out


def _boxes(doc: Document, spans: list[Span], vault: Vault) -> list[Box]:
    boxes: list[Box] = []
    for i, sp in enumerate(spans):
        ph = vault.placeholder_for(sp.text, sp.type)
        by_line: dict[tuple, list] = {}
        for w in doc.words:
            if w.start < sp.end and sp.start < w.end:
                by_line.setdefault(w.line, []).append(w)
        for line_words in by_line.values():
            boxes.append(Box(
                page=line_words[0].page,
                x0=min(w.bbox[0] for w in line_words), y0=min(w.bbox[1] for w in line_words),
                x1=max(w.bbox[2] for w in line_words), y1=max(w.bbox[3] for w in line_words),
                type=sp.type, placeholder=ph, span_index=i,
            ))
    return boxes


def run_pipeline(doc: Document, t1: Callable[[str], T1Result] | None, max_chars: int = MAX_CHARS,
                 workers: int = 6) -> PipelineResult:
    text = doc.text
    ranges = chunk_ranges(text, max_chars)

    def run_chunk(i: int) -> tuple[ChunkInfo, list[dict]]:
        s, e = ranges[i]
        cid = f"{doc.doc_id}-c{i:02d}"
        if t1 is None:
            return ChunkInfo(cid, s, e, None, "model off"), []
        if not text[s:e].strip():
            return ChunkInfo(cid, s, e, None, None), []
        try:
            r = t1(text[s:e])
        except Exception as exc:  # noqa: BLE001 - one bad chunk must not stop the document
            return ChunkInfo(cid, s, e, None, f"{type(exc).__name__}: {exc}"), []
        return ChunkInfo(cid, s, e, r.mreq_id, r.error, found=len(r.entities)), r.entities

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        results = list(pool.map(run_chunk, range(len(ranges))))
    chunks = [c for c, _ in results]

    values: dict[str, str] = {}
    for _, ents in results:
        for e in ents:
            values.setdefault(e["text"], e["type"])
    return _build(doc, values, chunks, {}, set())


def rebuild(doc: Document, prev: PipelineResult, hide: dict[str, str] | None = None,
            unhide: set[str] | None = None) -> PipelineResult:
    """Apply reviewer fixes on top of an earlier run, reusing the model's answers (no new T1 calls)."""
    hidden = {**prev.hidden, **(hide or {})}
    unhidden = (prev.unhidden | set(unhide or ())) - set(hide or {})
    for v in unhide or ():
        hidden.pop(v, None)
    return _build(doc, prev.model_values, prev.chunks, hidden, unhidden)


def _build(doc: Document, values: dict[str, str], chunks: list[ChunkInfo], hidden: dict[str, str],
           unhidden: set[str]) -> PipelineResult:
    text = doc.text
    wanted = {**values, **hidden}
    model_spans = locate(text, [{"text": v, "type": t} for v, t in wanted.items()])
    spans = _merge(regex_baseline.detect(text) + model_spans, text)
    if unhidden:
        spans = [s for s in spans if s.text not in unhidden]

    vault = Vault()
    redacted = apply(text, spans, vault)
    return PipelineResult(
        spans=spans, redacted_text=redacted, vault=vault, boxes=_boxes(doc, spans, vault),
        chunks=chunks, stats=dict(Counter(s.type for s in spans)),
        model_values=values, hidden=hidden, unhidden=unhidden,
    )
