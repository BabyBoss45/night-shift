"""Select about 100 English UK documents from gretelai/synthetic_pii_finance_multilingual,
map their PII labels to our 13 types, validate them, and merge them into
data/docs/financial.jsonl and data/docs/insurance.jsonl.

The label mapping is read from label_map.md (the committed table is the only copy).
The dataset is streamed and pinned to a commit hash; nothing is written inside the
repo except the two JSONL files and the manifest section "gretel".

Usage:
  python3 build_gretel.py [--revision SHA] [--n 100]
  python3 build_gretel.py --rows FILE.jsonl --out-dir DIR   # local rows, for tests
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from common import (
    POSTCODE_RE, assert_valid, check_entities, merge_write, stable_rng, sweep, update_manifest,
)

DATASET = "gretelai/synthetic_pii_finance_multilingual"
URL = f"https://huggingface.co/datasets/{DATASET}"
LABEL_MAP_MD = Path(__file__).with_name("label_map.md")
SEED = "night-shift-gretel-v1"
SPLIT_SHARES = (("train", 0.5), ("fresh", 0.3), ("eval", 0.2))
TEXT_COLS = ("generated_text", "text")
SPAN_COLS = ("pii_spans", "spans")
ID_COLS = ("uid", "id", "index", "level_0")
LOCALE_COLS = ("locale", "region", "country")

# Document types: insurance first, then a deny list of machine formats, then financial.
INSURANCE_RE = re.compile(r"insur|claim|policyholder|underwrit|indemnity|annuit", re.I)
MACHINE_RE = re.compile(r"\bfix\b|xbrl|swift|\bbai\b|\bedi\b|fpml|iso ?20022|json|xml|csv|data feed|"
                        r"\blog\b|api|code|protocol|schema|message format|sql", re.I)
PRIORITY_RE = re.compile(r"statement|invoice|loan|credit card|pay ?slip|pay ?stub|payroll|mortgage|"
                         r"insurance policy|insurance claim|claim", re.I)

# UK signals and non-UK signals (used only when the dataset has no locale column).
UK_SIGNALS = [re.compile(p, re.I if i > 1 else 0) for i, p in enumerate([
    r"£|\bGBP\b",
    r"\bGB\d{2} ?[A-Z]{4}",
    r"\bsort code\b|\bnational insurance\b|\bHMRC\b|\bpostcode\b",
])] + [POSTCODE_RE, re.compile(r"(?:\+44\s?(?:\(0\)\s?)?|\b0)(?:1\d{2,4}|2\d|7\d{3})[\s-]?\d{3,4}[\s-]?\d{3,4}\b")]
NON_UK_SIGNALS = [re.compile(p) for p in [
    r"\$\s?\d|\bUSD\b|\bEUR\b|€|\bCHF\b|\bSEK\b",
    r"\b\d{3}-\d{2}-\d{4}\b",
    r"\brouting number\b|\bZIP\b|\bSocial Security\b",
    r"\b[A-Z]{2} \d{5}(?:-\d{4})?\b",
]]
UK_RULE = ("language column is English; then the locale column if the dataset has one (value names GB or UK), "
           "otherwise at least one UK signal (GBP or £, GB IBAN, UK postcode, UK phone, 'sort code', "
           "'National Insurance', 'HMRC', 'postcode') and no non-UK signal ($, USD, EUR, €, CHF, SEK, "
           "US SSN pattern, 'routing number', 'ZIP', 'Social Security', US state plus ZIP)")


def load_label_map():
    """Parse the markdown table: | gretel label | our type or 'keep visible' or 'drop document' | why |"""
    mapping = {}
    for line in LABEL_MAP_MD.read_text(encoding="utf-8").splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or not re.fullmatch(r"[a-z0-9_]+", cells[0]):
            continue
        target = cells[1]
        if target == "keep visible":
            mapping[cells[0]] = "KEEP"
        elif target == "drop document":
            mapping[cells[0]] = "DROP_DOC"
        else:
            mapping[cells[0]] = target
    if not mapping:
        sys.exit(f"no label rows found in {LABEL_MAP_MD}")
    return mapping


def pick_col(row, names, what, required=True):
    for n in names:
        if n in row:
            return n
    if required:
        sys.exit(f"dataset has no {what} column (looked for {names}); columns are {sorted(row)}")
    return None


def is_uk(text, row, locale_col):
    if locale_col:
        return bool(re.search(r"\b(GB|UK|United Kingdom|en[-_]GB)\b", str(row[locale_col]), re.I))
    return any(p.search(text) for p in UK_SIGNALS) and not any(p.search(text) for p in NON_UK_SIGNALS)


def classify(doc_type):
    if INSURANCE_RE.search(doc_type) and not re.search(r"privacy|disclaimer", doc_type, re.I):
        return "insurance"
    if MACHINE_RE.search(doc_type):
        return None
    return "financial"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "unknown"


def mid_word(text, s, e):
    return (s > 0 and text[s - 1].isalnum() and text[s].isalnum()) or (e < len(text) and text[e - 1].isalnum() and text[e].isalnum())


def split_address(text, s, e):
    """Split a street address span into ADDRESS parts and POSTCODE spans."""
    out, cur = [], s
    for m in POSTCODE_RE.finditer(text, s, e):
        out.append((cur, m.start(), "ADDRESS"))
        out.append((m.start(), m.end(), "POSTCODE"))
        cur = m.end()
    out.append((cur, e, "ADDRESS"))
    res = []
    for a, b, t in out:
        while a < b and text[a] in " ,;\n\t":
            a += 1
        while b > a and text[b - 1] in " ,;\n\t":
            b -= 1
        if a < b:
            res.append((a, b, t))
    return res


def convert(text, raw_spans, label_map):
    """Return (entities, None, notes) or (None, drop_reason, notes)."""
    notes = Counter()
    if isinstance(raw_spans, str):
        raw_spans = json.loads(raw_spans)
    hidden, visible = [], []  # (start, end, type, group key)
    for n, sp in enumerate(raw_spans):
        label = str(sp.get("label", sp.get("type", ""))).lower()
        s, e = sp.get("start"), sp.get("end")
        if label not in label_map:
            return None, f"unmapped_label:{label}", notes
        if label_map[label] == "DROP_DOC":
            return None, "contains_password_or_api_key", notes
        if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e <= len(text)):
            return None, "span_offsets_invalid", notes
        value = sp.get("value", sp.get("text"))
        if value is not None and text[s:e] != value:
            return None, "span_text_mismatch", notes
        while s < e and text[s] in " \n\t":
            s += 1
        while e > s and text[e - 1] in " \n\t.,;:":
            e -= 1
        if s == e or mid_word(text, s, e) or (label == "email" and "@" not in text[s:e]):
            return None, "span_text_mismatch", notes
        target = label_map[label]
        if target == "KEEP":
            visible.append((s, e, label))
        elif target == "ADDRESS" and label == "street_address":
            hidden += [(a, b, t, f"addr{n}:{t}") for a, b, t in split_address(text, s, e)]
        else:
            hidden.append((s, e, target, None))

    # One person per span: merge PERSON spans separated only by spaces (first_name + last_name).
    hidden.sort(key=lambda h: (h[0], -h[1]))
    merged = []
    for h in hidden:
        p = merged[-1] if merged else None
        if p and p[2] == h[2] == "PERSON" and p[1] <= h[0] and re.fullmatch(r" +", text[p[1]:h[0]]):
            merged[-1] = (p[0], h[1], "PERSON", None)
            notes["merged_name_parts"] += 1
        else:
            merged.append(h)

    # Overlaps among hidden spans: same span or nested with the same type is a duplicate,
    # anything else is ambiguous and drops the document.
    clean = []
    for h in merged:
        p = clean[-1] if clean else None
        if p and h[0] < p[1]:
            if h[1] <= p[1] and h[2] == p[2]:
                notes["nested_duplicate_removed"] += 1
                continue
            return None, "overlapping_spans", notes
        clean.append(h)
    for s, e, t, _ in clean:
        for vs, ve, vl in visible:
            if s < ve and vs < e and vl == "company":
                return None, "person_data_inside_company_name", notes

    # Regex sweep for unlabelled structured identifiers.
    for s, e, kind, value in sweep(text):
        if any(a <= s and e <= b for a, b, _, _ in clean):
            continue
        if any(s < b and a < e for a, b, _, _ in clean):
            return None, f"sweep_partial_overlap:{kind}", notes
        if any(s < ve and vs < e for vs, ve, _ in visible):
            continue
        before = text[max(0, s - 40):s]
        if kind in ("EMAIL", "IBAN", "NI_NUMBER", "POSTCODE"):
            typ = kind
        elif kind == "PHONE" and (re.search(r"[\s()+-]", value) or re.search(r"tel|phone|mobile|call|fax|contact", before, re.I)):
            typ = "PHONE"
        elif kind == "CARD" and re.search(r"card", before, re.I):
            typ = "CARD"
        elif kind == "SORT_CODE" and re.search(r"sort", before[-25:], re.I):
            typ = "SORT_CODE"
        elif kind == "ACCOUNT8" and re.search(r"(account|acct|a/c)\b[^\n]{0,20}$", before, re.I):
            typ = "BANK_ACCOUNT"
        else:
            return None, f"sweep_ambiguous:{kind}", notes
        clean.append((s, e, typ, None))
        notes[f"sweep_added:{typ}"] += 1
    clean.sort()

    # entity_id: same type and value share an id; address parts of one span share an id;
    # a one-word PERSON mention joins the only longer PERSON name containing that word.
    norm = lambda v: re.sub(r"\s+", " ", v).strip().lower()
    key_of = {}
    for s, e, t, g in clean:
        key_of[(s, e)] = g or (t, norm(text[s:e]))
    full_names = {norm(text[s:e]) for s, e, t, _ in clean if t == "PERSON" and " " in norm(text[s:e])}
    for s, e, t, _ in clean:
        v = norm(text[s:e])
        if t == "PERSON" and " " not in v:
            owners = [f for f in full_names if v in f.split(" ")]
            if len(owners) == 1:
                key_of[(s, e)] = ("PERSON", owners[0])
    ids = {}
    entities = []
    for s, e, t, _ in clean:
        eid = ids.setdefault(key_of[(s, e)], f"e{len(ids) + 1}")
        entities.append(dict(start=s, end=e, type=t, value=text[s:e], entity_id=eid))
    if check_entities(text, entities):
        return None, "invalid_after_processing", notes
    return entities, None, notes


def iter_rows(args):
    if args.rows:
        for n, line in enumerate(args.rows.read_text(encoding="utf-8").splitlines()):
            yield "local", n, json.loads(line)
        return
    from datasets import load_dataset
    for split, ds in load_dataset(DATASET, revision=args.revision, streaming=True).items():
        for n, row in enumerate(ds):
            yield split, n, row


def resolve_revision(args):
    if args.rows:
        return "local-rows"
    from huggingface_hub import HfApi
    info = HfApi().dataset_info(DATASET, revision=args.revision or "main", files_metadata=True)
    for f in info.siblings:
        print(f"  {f.rfilename}: {(f.size or 0) / 1e6:.1f} MB")
    return info.sha


def select(cands, n, rng):
    """Round-robin over (group, subtype) buckets for variety; priority types take 2 per round."""
    buckets = defaultdict(list)
    for c in sorted(cands, key=lambda c: c["doc_id"]):
        buckets[(c["group"], c["subtype"])].append(c)
    for b in buckets.values():
        rng.shuffle(b)
    order = sorted(buckets)
    chosen, cap = [], max(6, n // 8)
    while len(chosen) < n and any(buckets.values()):
        for k in order:
            take = 2 if PRIORITY_RE.search(k[1].replace("_", " ")) else 1
            for _ in range(take):
                if buckets[k] and len(chosen) < n and sum(1 for c in chosen if (c["group"], c["subtype"]) == k) < cap:
                    chosen.append(buckets[k].pop())
            if sum(1 for c in chosen if (c["group"], c["subtype"]) == k) >= cap:
                buckets[k] = []
    return chosen


def assign_splits(docs, rng):
    by_group = defaultdict(list)
    for d in sorted(docs, key=lambda d: d["doc_id"]):
        by_group[d["group"]].append(d)
    for group_docs in by_group.values():
        rng.shuffle(group_docs)
        n, i = len(group_docs), 0
        for k, (split, share) in enumerate(SPLIT_SHARES):
            j = n if k == len(SPLIT_SHARES) - 1 else i + round(n * share)
            for d in group_docs[i:j]:
                d["split"] = split
            i = j


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", help="dataset commit hash (default: current main, recorded in the manifest)")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--rows", type=Path, help="local JSONL rows instead of the Hugging Face dataset (tests)")
    ap.add_argument("--out-dir", type=Path, help="write financial.jsonl / insurance.jsonl here instead of data/docs")
    args = ap.parse_args()
    label_map = load_label_map()
    revision = resolve_revision(args)
    args.revision = revision if not args.rows else None

    stats, drops, notes, types_seen = Counter(), Counter(), Counter(), Counter()
    cands, cols = [], None
    for split, n, row in iter_rows(args):
        if cols is None:
            cols = dict(text=pick_col(row, TEXT_COLS, "text"), spans=pick_col(row, SPAN_COLS, "PII spans"),
                        lang=pick_col(row, ("language",), "language"), type=pick_col(row, ("document_type",), "document type"),
                        id=pick_col(row, ID_COLS, "row id", required=False),
                        locale=pick_col(row, LOCALE_COLS, "locale", required=False))
            print("columns used:", cols)
        stats["rows"] += 1
        if not str(row[cols["lang"]]).lower().startswith(("english", "en")):
            continue
        stats["english"] += 1
        text = row[cols["text"]]
        if not is_uk(text, row, cols["locale"]):
            continue
        stats["english_uk"] += 1
        doc_type = str(row[cols["type"]])
        types_seen[doc_type] += 1
        group = classify(doc_type)
        if group is None:
            drops["document_type_not_a_document"] += 1
            continue
        entities, reason, nt = convert(text, row[cols["spans"]], label_map)
        notes.update(nt)
        if reason:
            drops[reason] += 1
            continue
        row_id = f"{split}-{row[cols['id']] if cols['id'] else n}"
        cands.append(dict(
            doc_id=f"{group}-gretel-{row_id}", source_id=f"gretel-{row_id}", group=group, subtype=slug(doc_type),
            split=None, fill=0, text=text, entities=entities,
            provenance=dict(url=URL, licence="Apache-2.0", kind="synthetic",
                            attribution="Gretel.ai, gretelai/synthetic_pii_finance_multilingual"),
        ))
    stats["valid_candidates"] = len(cands)
    rng = stable_rng(SEED)
    chosen = select(cands, args.n, rng)
    assign_splits(chosen, rng)

    for group in ("financial", "insurance"):
        recs = [c for c in chosen if c["group"] == group]
        if args.out_dir:
            assert_valid(recs, group, group)
            args.out_dir.mkdir(parents=True, exist_ok=True)
            (args.out_dir / f"{group}.jsonl").write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sorted(recs, key=lambda r: r["doc_id"])),
                encoding="utf-8")
        else:
            merge_write(group, recs, lambda r: r["source_id"].startswith("gretel-"))

    summary = dict(
        dataset=DATASET, url=URL, revision=revision, licence="Apache-2.0", attribution="Gretel.ai",
        seed=SEED, uk_rule=UK_RULE if not cols["locale"] else f"locale column {cols['locale']!r} names GB/UK",
        label_map="scripts/sources/financial_insurance/label_map.md",
        counts=dict(
            rows_seen=stats["rows"], english=stats["english"], english_uk=stats["english_uk"],
            valid_candidates=stats["valid_candidates"], selected=len(chosen),
            drop_reasons=dict(drops.most_common()), fixes=dict(notes.most_common()),
            by_group_split={g: dict(Counter(c["split"] for c in chosen if c["group"] == g)) for g in ("financial", "insurance")},
            by_subtype=dict(Counter(f"{c['group']}/{c['subtype']}" for c in chosen).most_common()),
            entities_by_type=dict(Counter(e["type"] for c in chosen for e in c["entities"]).most_common()),
            uk_document_types_seen=dict(types_seen.most_common()),
        ),
    )
    if not args.out_dir:
        update_manifest("gretel", summary)
    print(json.dumps(summary["counts"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
