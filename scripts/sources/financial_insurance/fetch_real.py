"""Download the two real insurance sources to a directory OUTSIDE the repo and
convert them to plain text, so the templates can be written from them.

INS1: Pre-Action Protocol for Personal Injury Claims (annexes B1, B2 and D: letters of
      claim to an insurer and responses), Crown copyright.
INS2: Lloyd's blanket bond for PIMCO Funds (policy and schedule), SEC EDGAR filing.

Raw files contain real parties (INS2) and must never be committed.

Usage: python3 fetch_real.py [--raw /tmp/raw/financial_insurance]
"""

import argparse
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin

from common import REPO

USER_AGENT = "night-shift-hackathon dataset build (github.com/BabyBoss45/night-shift)"
SOURCES = {
    "INS1": "https://www.justice.gov.uk/courts/procedure-rules/civil/protocol/prot_pic",
    "INS2": "https://www.sec.gov/Archives/edgar/data/1190935/000095013607000199/file8.htm",
}
ANNEX_RE = re.compile(r"annex\s*(b\s*1|b\s*2|d)\b", re.I)
BLOCK_TAGS = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "pre", "hr"}


class TextAndLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self.links, self._href, self._skip = [], [], None, 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "td":
            self.parts.append("\t")
        if tag == "a":
            self._href, self._link_text = dict(attrs).get("href"), []

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip -= 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "a" and self._href:
            self.links.append((self._href, "".join(self._link_text).strip()))
            self._href = None

    def handle_data(self, data):
        if self._skip:
            return
        self.parts.append(data)
        if self._href:
            self._link_text.append(data)

    def text(self):
        t = re.sub(r"[ \t\xa0]+", " ", "".join(self.parts))
        return re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip() + "\n"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def to_text(name, data):
    if name.endswith(".docx"):
        xml = zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml").decode("utf-8")
        xml = re.sub(r"</w:p>", "\n", xml)
        return re.sub(r"<[^>]+>", "", xml)
    if name.endswith((".htm", ".html")) or b"<html" in data[:2000].lower():
        p = TextAndLinks()
        p.feed(data.decode("utf-8", errors="replace"))
        return p.text()
    return None


def save(raw, name, data, log):
    path = raw / name
    path.write_bytes(data)
    text = to_text(name, data)
    if text is not None:
        path.with_suffix(".txt").write_text(text, encoding="utf-8")
    log.append(dict(file=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), text=text is not None))
    print(f"  saved {path} ({len(data):,} bytes){' + .txt' if text is not None else ' (convert by hand)'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=Path("/tmp/raw/financial_insurance"))
    args = ap.parse_args()
    raw = args.raw.resolve()
    if raw.is_relative_to(REPO):
        sys.exit("raw files must be kept outside the repo")
    raw.mkdir(parents=True, exist_ok=True)
    log, failed = [], []
    for sid, url in SOURCES.items():
        print(f"{sid}: {url}")
        try:
            data = get(url)
        except (HTTPError, URLError, OSError) as ex:
            print(f"  FAILED: {ex}")
            failed.append(dict(source=sid, url=url, error=str(ex)))
            continue
        save(raw, f"{sid}.html", data, log)
        if sid == "INS1":
            parser = TextAndLinks()
            parser.feed(data.decode("utf-8", errors="replace"))
            for href, label in parser.links:
                if ANNEX_RE.search(label) or ANNEX_RE.search(href.replace("-", " ").replace("_", " ")):
                    link = urljoin(url, href)
                    name = f"INS1-annex-{re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')[:40]}{Path(link).suffix or '.html'}"
                    try:
                        save(raw, name, get(link), log)
                    except (HTTPError, URLError, OSError) as ex:
                        failed.append(dict(source=sid, url=link, error=str(ex)))
                        print(f"  FAILED {link}: {ex}")
    (raw / "fetch_log.json").write_text(json.dumps(dict(saved=log, failed=failed), indent=2), encoding="utf-8")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
