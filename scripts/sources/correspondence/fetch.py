#!/usr/bin/env python3
"""Fetch the correspondence sources (design section 4, R1 to R11) and write the manifest.

Usage (from the repo root):
    python scripts/sources/correspondence/fetch.py [--raw /tmp/raw/correspondence]

Raw files and extracted text go to --raw, which must be outside the repo: they
contain real people's data and are never committed. The script writes
data/sources/correspondence/manifest.json with one entry per source, including
sources whose host could not be reached (fetched: false, with the error).

R1 to R5 are Enron messages. The CMU archive (1.7 GB) and the Hugging Face
mirrors were not reachable from the build sandbox, so the messages come from the
copy of the same corpus inside the HPI Quagga repository on GitHub, pinned to a
commit, with a blobless sparse clone (only the five message files are read).
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import shutil
import subprocess
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "data" / "sources" / "correspondence" / "manifest.json"
UA = "night-shift-hackathon dataset build (github.com/BabyBoss45/night-shift)"
ENRON_URL = "https://www.cs.cmu.edu/~enron/"
ENRON_LICENCE = "Enron email corpus, research release of the FERC public record"
QUAGGA = "https://github.com/HPI-Information-Systems/Quagga"
QUAGGA_COMMIT = "4ba5be0fd4a0a5954527ea93cf6592f54f4fc3f0"
QUAGGA_DIR = "Datasets/Enron/annotated_all"
ENRON_FILES = {
    "R1": "train/shackleton-s_inbox_343.txt",
    "R2": "train/dasovich-j_interconnection_12.txt",
    "R3": "eval/heard-m_inbox_master_netting_185.txt",
    "R4": "train/hernandez-j_inbox_297.txt",
    "R5": "test/kaminski-v_all_documents_1882.txt",
}
WEB_SOURCES = {
    "R6": ("https://www.justice.gov.uk/courts/procedure-rules/civil/protocol/prot_hou",
           "Crown copyright, Open Government Licence", "template",
           "Housing disrepair pre-action protocol, annex letter templates"),
    "R7": ("https://ico.org.uk/media2/migrated/4028636/sar-complaint-letter-or-email-template-v10.docx",
           "Open Government Licence", "template", "ICO subject access request complaint template"),
    "R8": ("https://www.acas.org.uk/job-offer-templates/job-offer-letter-template-with-written-statement",
           "Open Government Licence", "template", "Acas job offer letter template"),
    "R9": ("https://www.acas.org.uk/disciplinary-outcome-letter-templates/"
           "notice-of-disciplinary-outcome-letter-template-dismissal-disciplinary-action-or-no-action",
           "Open Government Licence", "template", "Acas disciplinary outcome letter template"),
    "R10": ("https://www.sec.gov/Archives/edgar/data/858446/000095010309002490/filename1.htm",
            "Public filing, SEC EDGAR", "filled_real", "IHG letter to the SEC"),
    "R11": ("https://api.parliament.uk/committees/publications/7750",
            "Open Parliament Licence", "filled_real",
            "Parliament committee correspondence listing; letters to pick by hand"),
}


class TextExtractor(HTMLParser):
    BLOCKS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section"}

    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def extract_text(data, url):
    """Plain text from an HTML, DOCX or PDF download."""
    if url.endswith(".docx"):
        import docx
        return "\n".join(p.text for p in docx.Document(io.BytesIO(data)).paragraphs)
    if url.endswith(".pdf"):
        import pypdf
        return "\n".join(page.extract_text() or "" for page in pypdf.PdfReader(io.BytesIO(data)).pages)
    parser = TextExtractor()
    parser.feed(data.decode("utf-8", errors="replace"))
    lines = [ln.rstrip() for ln in "".join(parser.parts).splitlines()]
    out = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    return "\n".join(out).strip() + "\n"


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def fetch_enron(raw):
    clone = raw / "quagga"
    if not (clone / ".git").exists():
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", QUAGGA, str(clone)],
                       check=True)
    subprocess.run(["git", "-C", str(clone), "sparse-checkout", "set", "--no-cone", QUAGGA_DIR + "/*"],
                   check=True)
    subprocess.run(["git", "-C", str(clone), "checkout", QUAGGA_COMMIT], check=True)
    entries = []
    for sid, rel in ENRON_FILES.items():
        text = (clone / QUAGGA_DIR / rel).read_text(encoding="latin-1").replace("\r", "")
        (raw / f"{sid}.txt").write_text(text, encoding="utf-8")
        entries.append({
            "source_id": sid, "url": ENRON_URL, "licence": ENRON_LICENCE, "kind": "filled_real",
            "fetched": True, "fetched_at": now(), "sha256": sha(text),
            "notes": f"Enron message from the copy in {QUAGGA} at commit {QUAGGA_COMMIT}, "
                     f"file {QUAGGA_DIR}/{rel}; sha256 is of the message text with CR removed",
        })
    return entries


def fetch_web(raw):
    entries = []
    for sid, (url, licence, kind, what) in WEB_SOURCES.items():
        entry = {"source_id": sid, "url": url, "licence": licence, "kind": kind, "fetched": False,
                 "fetched_at": now(), "sha256": None, "notes": what}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            text = extract_text(data, url)
            (raw / f"{sid}.txt").write_text(text, encoding="utf-8")
            entry.update(fetched=True, sha256=sha(text))
        except Exception as exc:  # record the failure and carry on with the other sources
            entry["notes"] += f"; NOT FETCHED from the build sandbox: {type(exc).__name__}: {exc}"
        entries.append(entry)
    return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", default="/tmp/raw/correspondence")
    args = ap.parse_args()
    raw = Path(args.raw).resolve()
    if ROOT in raw.parents or raw == ROOT:
        raise SystemExit("--raw must be outside the repository")
    raw.mkdir(parents=True, exist_ok=True)
    if not shutil.which("git"):
        raise SystemExit("git is required")
    entries = fetch_enron(raw) + fetch_web(raw)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for e in entries:
        print(e["source_id"], "fetched" if e["fetched"] else "NOT fetched")


if __name__ == "__main__":
    main()
