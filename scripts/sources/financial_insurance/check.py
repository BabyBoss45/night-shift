"""Check documents JSONL files against the schema invariants. Fails loudly.

Usage: python3 scripts/sources/financial_insurance/check.py [FILE ...]
Defaults to data/docs/financial.jsonl and data/docs/insurance.jsonl.
Also sweeps for structured identifiers that are not inside an entity: fatal in
rendered templates, a warning in Gretel documents.
"""

import sys
from collections import Counter
from pathlib import Path

from common import DOCS_DIR, check_file, read_jsonl, uncovered_hits


def main(argv):
    paths = [Path(p) for p in argv] or [DOCS_DIR / "financial.jsonl", DOCS_DIR / "insurance.jsonl"]
    failed = False
    for path in paths:
        if not path.exists():
            print(f"FAIL {path}: file does not exist")
            failed = True
            continue
        n, errors = check_file(path)
        try:
            records = [r for r in read_jsonl(path) if isinstance(r, dict) and isinstance(r.get("text"), str)
                       and isinstance(r.get("entities"), list) and isinstance(r.get("fill"), int)]
        except ValueError:
            records = []
        hits = [(r, h) for r in records
                for h in uncovered_hits(r["text"], [e for e in r["entities"] if isinstance(e, dict) and {"start", "end"} <= e.keys()])]
        # Rendered templates must have no leftover structured identifier. Gretel documents
        # were swept at build time against labels this file no longer carries (a dropped
        # date label can look like a sort code), and a bare 8-digit number can be a public
        # company number, so those are warnings for review.
        leaks = [(r.get("doc_id"), h) for r, h in hits if h[2] != "ACCOUNT8" and r["fill"] > 0]
        warns = [(r.get("doc_id"), h) for r, h in hits if (r.get("doc_id"), h) not in leaks]
        for doc_id, (s, e, kind, value) in warns[:20]:
            print(f"  warn {doc_id}: unlabelled {kind}-like {value!r} at {s}")
        if errors or leaks:
            failed = True
            print(f"FAIL {path}: {n} records, {len(errors)} schema errors, {len(leaks)} unlabelled identifiers")
            for e in errors[:50]:
                print("  " + e)
            for doc_id, (s, e, kind, value) in leaks[:50]:
                print(f"  {doc_id}: unlabelled {kind} {value!r} at {s}")
            continue
        types = Counter(e["type"] for r in records for e in r["entities"])
        splits = Counter(r["split"] for r in records)
        print(f"OK   {path}: {n} records, splits {dict(sorted(splits.items()))}, "
              f"entities {sum(types.values())} {dict(sorted(types.items()))}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
