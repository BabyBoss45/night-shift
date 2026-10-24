#!/usr/bin/env python3
"""Measure how much personal data survives ingest.extract() on dataset documents.

Each sampled document is turned into a text-layer PDF, and into image-only PDFs of
five quality levels (clean scan, office scan, low-resolution scan, phone photo, page
turned sideways), using several fonts. Every PDF goes through ingest.extract(), and
every key entity on the drawn pages is checked: does its value appear in the output
(whitespace-insensitive), before and after the identifier repairs? A repair is
counted as harmful when the text it replaced was already correct in the source.

Usage (macOS, from the repo root):
    python scripts/ocr/eval_ocr.py [--per-group 6] [--max-pages 3] [--out data/results/ocr]
"""

from __future__ import annotations

import argparse
import difflib
import json
import random
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
sys.path.insert(0, str(Path(__file__).parent))

from app.ingest import extract, fix_identifiers  # noqa: E402
from render import FONTS, degrade, image_pdf, render_pages, text_layer_pdf  # noqa: E402

LEVELS = ["text_pdf", "clean_scan", "office_scan", "low_res_scan", "phone_photo", "sideways"]
GROUPS = ["contracts", "correspondence", "financial", "insurance"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def loose(s: str) -> str:
    """Content only: no whitespace, no accents, lower case ("0131 207" and "0131207", "É" and "E" match)."""
    decomposed = unicodedata.normalize("NFKD", s)
    return re.sub(r"\s+", "", "".join(ch for ch in decomposed if not unicodedata.combining(ch))).lower()


def load_docs() -> list[dict]:
    docs = []
    for path in sorted((REPO / "data" / "docs").glob("*.jsonl")):
        docs.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return docs


def sample(docs: list[dict], per_group: int, seed: int) -> list[dict]:
    """Up to per_group documents per group, one per source where possible."""
    rng = random.Random(seed)
    picked = []
    for group in GROUPS:
        by_source = defaultdict(list)
        for d in docs:
            if d["group"] == group and d["entities"]:
                by_source[d["source_id"]].append(d)
        sources = sorted(by_source)
        rng.shuffle(sources)
        for src in sources[:per_group]:
            picked.append(rng.choice(by_source[src]))
    return picked


def word_accuracy(truth: str, got: str) -> float:
    a, b = norm(truth).split(" "), norm(got).split(" ")
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def run(per_group: int, max_pages: int, seed: int) -> dict:
    docs = sample(load_docs(), per_group, seed)
    results = []
    for i, doc in enumerate(docs):
        font = FONTS[i % len(FONTS)]
        pages, drawn = render_pages(doc["text"], font, max_pages)
        truth = doc["text"][:drawn]
        entities = [e for e in doc["entities"] if e["end"] <= drawn]
        for level in LEVELS:
            t0 = time.time()
            if level == "text_pdf":
                pdf = text_layer_pdf(truth)
            else:
                degraded = [degrade(p, level, seed + i * 31 + n) for n, p in enumerate(pages)]
                pdf = image_pdf([img for img, _ in degraded], degraded[0][1])
            raw = extract(pdf, fix=False)
            secs = time.time() - t0
            fixed_pages, fixes = [], []
            for page in raw.pages:
                if page.source == "ocr":
                    text, page_fixes = fix_identifiers(page.text, page.number)
                    fixes.extend(page_fixes)
                    fixed_pages.append(text)
                else:
                    fixed_pages.append(page.text)
            before, after = norm(raw.text), norm("\n\n".join(t for t in fixed_pages if t))
            after_loose = loose(after)
            ent_rows = [
                {"type": e["type"], "value": e["value"], "before": norm(e["value"]) in before,
                 "after": norm(e["value"]) in after, "content": loose(e["value"]) in after_loose}
                for e in entities
            ]
            harmful = [{"before": f.before, "after": f.after, "kind": f.kind} for f in fixes
                       if norm(f.before) in norm(truth) and norm(f.after) not in norm(truth)]
            results.append({
                "doc_id": doc["doc_id"], "group": doc["group"], "font": font, "level": level, "pages": len(raw.pages),
                "sources": sorted({p.source for p in raw.pages}), "rotations": sorted({p.rotation for p in raw.pages}),
                "seconds": round(secs, 2), "word_acc_before": word_accuracy(truth, raw.text),
                "word_acc_after": word_accuracy(truth, "\n\n".join(fixed_pages)), "entities": ent_rows,
                "fixes": [{"kind": f.kind, "before": f.before, "after": f.after} for f in fixes], "harmful_fixes": harmful,
                "low_confidence_lines": sum(len(p.low_confidence_lines) for p in raw.pages),
            })
        print(f"  {i + 1}/{len(docs)} {doc['doc_id']} ({font}, {len(pages)} pages)", flush=True)
    return {"docs": len(docs), "results": results}


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "n/a"


def report(data: dict) -> str:
    rows = data["results"]
    out = [f"# OCR evaluation ({data['docs']} documents, {len(rows)} runs)", ""]
    out += ["Kept = the value appears verbatim (whitespace-insensitive). Content kept also ignores spaces, accents and case.", "",
            "| Level | Word accuracy | Kept before fixes | Kept after fixes | Content kept | Harmful fixes | Sec per page |",
            "|---|---:|---:|---:|---:|---:|---:|"]
    for level in LEVELS:
        lr = [r for r in rows if r["level"] == level]
        ents = [e for r in lr for e in r["entities"]]
        pages = sum(r["pages"] for r in lr) or 1
        out.append(
            f"| {level} | {sum(r['word_acc_after'] for r in lr) / len(lr):.3f} "
            f"| {pct(sum(e['before'] for e in ents), len(ents))} | {pct(sum(e['after'] for e in ents), len(ents))} "
            f"| {pct(sum(e['content'] for e in ents), len(ents))} "
            f"| {sum(len(r['harmful_fixes']) for r in lr)} of {sum(len(r['fixes']) for r in lr)} "
            f"| {sum(r['seconds'] for r in lr) / pages:.2f} |"
        )
    out += ["", "## Entities kept after fixes, by type", "", "| Type | " + " | ".join(LEVELS) + " |",
            "|---|" + "---:|" * len(LEVELS)]
    types = sorted({e["type"] for r in rows for e in r["entities"]})
    for t in types:
        cells = []
        for level in LEVELS:
            ents = [e for r in rows if r["level"] == level for e in r["entities"] if e["type"] == t]
            cells.append(f"{sum(e['after'] for e in ents)}/{len(ents)}")
        out.append(f"| {t} | " + " | ".join(cells) + " |")
    out += ["", "## By font (scans only, entities kept after fixes)", "", "| Font | " + " | ".join(LEVELS[1:]) + " |",
            "|---|" + "---:|" * (len(LEVELS) - 1)]
    for font in FONTS:
        cells = []
        for level in LEVELS[1:]:
            ents = [e for r in rows if r["level"] == level and r["font"] == font for e in r["entities"]]
            cells.append(pct(sum(e["after"] for e in ents), len(ents)))
        out.append(f"| {font.removesuffix('.ttf')} | " + " | ".join(cells) + " |")
    lost = Counter((r["level"], e["type"], e["value"]) for r in rows for e in r["entities"] if not e["content"])
    out += ["", "## Values whose content was lost (first 40)", ""]
    out += [f"- {lv} {t}: {v!r}" for (lv, t, v), _ in list(lost.items())[:40]] or ["None."]
    harmful = [(r["level"], h) for r in rows for h in r["harmful_fixes"]]
    out += ["", "## Harmful fixes", ""]
    out += [f"- {lv} {h['kind']}: {h['before']!r} -> {h['after']!r}" for lv, h in harmful] or ["None."]
    kinds = Counter(f["kind"] for r in rows for f in r["fixes"])
    out += ["", f"Fixes applied by kind: {dict(kinds) or 'none'}", ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--per-group", type=int, default=6)
    ap.add_argument("--max-pages", type=int, default=3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", type=Path, default=REPO / "data" / "results" / "ocr")
    args = ap.parse_args(argv)
    data = run(args.per_group, args.max_pages, args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "eval.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    md = report(data)
    (args.out / "eval.md").write_text(md)
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
