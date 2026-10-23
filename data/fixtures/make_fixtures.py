#!/usr/bin/env python3
"""Regenerate the test fixtures in data/fixtures/ (docs/*.jsonl and results/*.jsonl).

All values are fake: phone numbers are from Ofcom's drama ranges, NI numbers use
the never-issued QQ prefix, emails use example domains.

Documents are written with inline markers <<TYPE:entity_id|value>>; this script
strips the markers and records the offsets, so the key is produced by code.
Fake teacher outputs are the document text with listed replacements applied:
- train: one missed entity (CUSTOM left visible), one malformed placeholder
  ([Person 1]), the address and postcode merged onto one line, and an earlier
  failed attempt (HTTP 529) before the successful row;
- fresh: a perfect output;
- eval: two over-redactions ("Rose Garden" as a PERSON and an ordinary date as a DOB).

Usage: python data/fixtures/make_fixtures.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARK_RE = re.compile(r"<<([A-Z_]+):([a-z0-9]+)\|(.*?)>>", re.S)

ACAS_URL = "https://www.acas.org.uk/templates-for-written-statements/written-statement-employee-template"
ICO_URL = "https://ico.org.uk/media2/migrated/4028636/sar-complaint-letter-or-email-template-v10.docx"

CLAUSES_3_TO_5 = """\
3. Hours. Your normal hours are 9am to 5pm, Monday to Friday, with one hour for lunch. Work at the Oak Road depot may need early starts.

4. Holiday. You are entitled to 28 days of paid holiday each year, including bank holidays. The holiday year runs from 1 January to 31 December.

5. Notice. After the probation period either party must give one month's written notice."""

C3_F1 = f"""\
WRITTEN STATEMENT OF EMPLOYMENT PARTICULARS

Employer: Brightwater Logistics Ltd
Employee: <<PERSON:p1|Will Hartley>>
Home address: <<ADDRESS:a1|Flat 2, 14 Mill Lane
Norwich>> <<POSTCODE:pc1|NR2 4QT>>
Date of birth: <<DOB:d1|14 March 1991>>
National Insurance number: <<NI_NUMBER:n1|QQ 12 34 56 C>>
Employee number: <<CUSTOM:c1|EMP-55821>>

1. Start date. Your employment starts on 1 November 2026. Mark the date in your diary.

2. Pay. You will be paid £2,450.00 per month into the account ending <<BANK_ACCOUNT:b1|4821>>, sort code <<SORT_CODE:s1|20-45-77>>.

{CLAUSES_3_TO_5}

Signed by the employee: <<PERSON:p1|W. Hartley>>
Questions: contact <<PERSON:p2|Grace Okafor>> on <<PHONE:ph1|07700 900123>> or <<EMAIL:e1|grace.okafor@example.com>>."""

C3_F4 = f"""\
WRITTEN STATEMENT OF EMPLOYMENT PARTICULARS

Employer: Brightwater Logistics Ltd
Employee: <<PERSON:p1|Siobhán Byrne>>
Home address: <<ADDRESS:a1|c/o 7 Rowan Court, Leeds>> <<POSTCODE:pc1|LS6 2AB>>
Date of birth: <<DOB:d1|2 June 1985>>
National Insurance number: <<NI_NUMBER:n1|QQ654321A>>
Employee number: <<CUSTOM:c1|EMP-70413>>

1. Start date. Your employment starts on 4 January 2027.

2. Pay. You will be paid £2,610.00 per month into the account ending <<BANK_ACCOUNT:b1|0937>>, sort code <<SORT_CODE:s1|40-11-62>>.

{CLAUSES_3_TO_5}

Signed by the employee: <<PERSON:p1|Ms Byrne>>
Questions: contact <<PERSON:p2|Rose Lambert>> on <<PHONE:ph1|020 7946 0018>> or <<EMAIL:e1|r.lambert@example.org>>."""

R7_F1 = """\
<<PERSON:p1|Olena Kovalenko>>
<<ADDRESS:a1|Flat 5, 22 Elm Street
Manchester>>
<<POSTCODE:pc1|M14 5TP>>
<<EMAIL:e1|o.kovalenko@example.net>>

12 October 2026

Data Protection Officer
Northgate Insurance plc

Dear Sir or Madam,

Subject access request: policy <<CUSTOM:c1|NGI/HH/448812>>

On 1 August 2026 I asked for a copy of my personal data. My date of birth is <<DOB:d1|9 May 1979>> and my customer reference is <<CUSTOM:c2|CR-118-4410>>. I also asked on behalf of my husband, <<PERSON:p2|Mark Tran>>. <<PERSON:p2|Mr Tran>>'s data was due by 1 September 2026.

We met your adviser at the Rose Garden Café in Didsbury, who said the delay was due to staff shortages. The fee of £10.00 was refunded.

Please reply within one month. You can call me on <<PHONE:ph1|0161 496 0734>>.

Yours faithfully,

<<PERSON:p1|O. Kovalenko>>"""

DOCS = [
    {
        "file": "contracts",
        "doc_id": "contracts-C3-f1",
        "source_id": "C3",
        "group": "contracts",
        "subtype": "employment",
        "split": "train",
        "fill": 1,
        "marked": C3_F1,
        "hard_cases": ["common_word_names", "multiline_address", "partial_number", "same_person_many_forms", "over_redaction_trap"],
        "provenance": {"url": ACAS_URL, "licence": "OGL-UK-3.0", "kind": "template"},
    },
    {
        "file": "contracts",
        "doc_id": "contracts-C3-f4",
        "source_id": "C3",
        "group": "contracts",
        "subtype": "employment",
        "split": "fresh",
        "fill": 4,
        "marked": C3_F4,
        "hard_cases": ["transliterated_names", "c_o_address", "partial_number", "common_word_names"],
        "provenance": {"url": ACAS_URL, "licence": "OGL-UK-3.0", "kind": "template"},
    },
    {
        "file": "correspondence",
        "doc_id": "correspondence-R7-f1",
        "source_id": "R7",
        "group": "correspondence",
        "subtype": "letter",
        "split": "eval",
        "fill": 1,
        "marked": R7_F1,
        "hard_cases": ["possessive", "initials", "multiline_address", "same_person_many_forms", "over_redaction_trap"],
        "provenance": {"url": ICO_URL, "licence": "OGL-UK-3.0", "kind": "template"},
    },
]

# Fake teacher outputs: (old, new) replacements applied in order to the document text.
OUTPUTS = {
    "train": (
        "contracts-C3-f1",
        [
            ("Will Hartley", "[PERSON_1]"),
            ("Flat 2, 14 Mill Lane\nNorwich NR2 4QT", "[ADDRESS_1] [POSTCODE_1]"),
            ("14 March 1991", "[DOB_1]"),
            ("QQ 12 34 56 C", "[NI_NUMBER_1]"),
            ("ending 4821", "ending [BANK_ACCOUNT_1]"),
            ("20-45-77", "[SORT_CODE_1]"),
            ("W. Hartley", "[Person 1]"),
            ("Grace Okafor", "[PERSON_2]"),
            ("07700 900123", "[PHONE_1]"),
            ("grace.okafor@example.com", "[EMAIL_1]"),
        ],
    ),
    "fresh": ("contracts-C3-f4", None),  # None: the expected redaction, a perfect answer
    "eval": (
        "correspondence-R7-f1",
        [
            ("Olena Kovalenko", "[PERSON_1]"),
            ("Flat 5, 22 Elm Street\nManchester", "[ADDRESS_1]\n[ADDRESS_1]"),
            ("M14 5TP", "[POSTCODE_1]"),
            ("o.kovalenko@example.net", "[EMAIL_1]"),
            ("12 October 2026", "[DOB_2]"),
            ("NGI/HH/448812", "[CUSTOM_1]"),
            ("9 May 1979", "[DOB_1]"),
            ("CR-118-4410", "[CUSTOM_2]"),
            ("Mark Tran", "[PERSON_2]"),
            ("Mr Tran", "[PERSON_2]"),
            ("Rose Garden", "[PERSON_3]"),
            ("0161 496 0734", "[PHONE_1]"),
            ("O. Kovalenko", "[PERSON_1]"),
        ],
    ),
}


def unmark(marked: str) -> tuple[str, list[dict]]:
    out, entities, pos = [], [], 0
    length = 0
    for m in MARK_RE.finditer(marked):
        before = marked[pos:m.start()]
        out.append(before)
        length += len(before)
        etype, eid, value = m.groups()
        entities.append({"start": length, "end": length + len(value), "type": etype, "value": value, "entity_id": eid})
        out.append(value)
        length += len(value)
        pos = m.end()
    out.append(marked[pos:])
    return "".join(out), entities


def expected(text: str, entities: list[dict]) -> str:
    numbers: dict[str, dict[str, int]] = {}
    out, pos = [], 0
    for e in entities:
        ids = numbers.setdefault(e["type"], {})
        n = ids.setdefault(e["entity_id"], len(ids) + 1)
        ph = f"[{e['type']}_{n}]"
        out.append(text[pos:e["start"]])
        out.append(re.sub(r"\S(?:[^\n]*\S)?", ph, e["value"]) if "\n" in e["value"] else ph)
        pos = e["end"]
    out.append(text[pos:])
    return "".join(out)


def main() -> None:
    docs_by_id, files = {}, {}
    for spec in DOCS:
        text, entities = unmark(spec["marked"])
        doc = {k: spec[k] for k in ("doc_id", "source_id", "group", "subtype", "split", "fill")}
        doc.update({"text": text, "entities": entities, "hard_cases": spec["hard_cases"], "provenance": spec["provenance"]})
        docs_by_id[doc["doc_id"]] = doc
        files.setdefault(spec["file"], []).append(doc)
    for name, docs in files.items():
        path = HERE / "docs" / f"{name}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(d, ensure_ascii=False) + "\n" for d in docs), encoding="utf-8")

    base = {"stop_reason": "end_turn", "latency_ms": 900, "model": "claude-haiku-4-5", "prompt_version": 1, "record_off": False, "error": None}
    for split, (doc_id, replacements) in OUTPUTS.items():
        doc = docs_by_id[doc_id]
        if replacements is None:
            output = expected(doc["text"], doc["entities"])
        else:
            output = doc["text"]
            for old, new in replacements:
                assert old in output, (split, old)
                output = output.replace(old, new, 1)
        rows = []
        if split == "train":
            rows.append(dict(base, chunk_id=f"{doc_id}-c000", doc_id=doc_id, split=split, request_id="mreq_" + "0" * 32,
                             output=None, stop_reason=None, usage=None, error="HTTP 529 overloaded_error: Overloaded"))
        rows.append(dict(base, chunk_id=f"{doc_id}-c000", doc_id=doc_id, split=split, request_id="mreq_" + f"{len(rows) + 1:032x}",
                         output=output + "\n", usage={"input_tokens": 1200, "output_tokens": 320},
                         record_off=split == "eval"))
        path = HERE / "results" / f"{split}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


if __name__ == "__main__":
    main()
