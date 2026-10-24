# Shared context for the PII dataset research (read first)

Date: Sat 24 Oct 2026, from 01:00 BST. Hackathon: Mubit Night Shift (London). Hacking has started, so writing code is allowed.
Full product spec: `/Users/dima/Projects/night-shift/docs/NIGHT-SHIFT-TEAM-PACK.md` (sections 3, 7, 8, 9, 10 matter most).

## Product
"Veil": a privacy middleware with a chat UI. Every user prompt or document (PDF, contract, bill, bank statement, email, chat message) passes through a redaction model trained and hosted via Mubit. Personal data is replaced with consistent placeholders ([PERSON_1], [ACCOUNT_1]); only redacted text goes to Claude/OpenAI; real values are restored in the answer locally.

## Mubit task T1 (the model we train)
- System prompt starts: "Find personal data in one document chunk." (frozen; never put per-document text in it)
- Input (user message): one chunk of a document, at most about 1,500 tokens (roughly 6,000 characters).
- Output: JSON `{"entities":[{"text": "...", "type": "..."}]}` via `response_format: json_object`. Code does the replacement.
- One session per document (`metadata.session_id = doc-<id>`). Test cases are held out by session.
- Mubit trains a LoRA-style adapter on an open base model from (request, provider reply) pairs. Default first training at 25 kept examples. Daily training limit (resets 00:00 UTC), pause between trainings, no retry button, "examples too long to train on" can block training. Adapters are graded on matching the provider (teacher) answers. Corrections are made in the Mubit console on a request (per the organisers' sample project PagerPal).
- Only synthetic (fake) personal data may pass through Mubit during the event.

## Entity types (13)
PERSON, ADDRESS, POSTCODE, EMAIL, PHONE, BANK_ACCOUNT, SORT_CODE, IBAN, CARD, NI_NUMBER, DOB, ID_DOC (passport, driving licence), CUSTOM (organisation-specific identifiers: client codes, matter numbers, policy numbers, customer/account references).
Keep (do NOT label): amounts, ordinary dates (not DOB), contract terms, clause text, public company names (unless clearly a sole trader's personal name), product names, generic place names that are not a person's address.

## Canonical data format (all datasets we produce or convert)
Document JSONL, one record per line:
```json
{"doc_id": "syn-000001", "source": "synthetic|<dataset id>", "doc_type": "tenancy_agreement", "language": "en", "license": "...", "text": "...", "entities": [{"start": 10, "end": 30, "text": "Oleksandra Kovalenko", "type": "PERSON"}], "split": "train|fresh|corrections|eval", "meta": {}}
```
- `text[start:end] == entities[i].text` must hold for every span. Spans do not overlap. Offsets are Python string indices.
Chunk JSONL (what we send to Mubit): `{"doc_id", "chunk_id", "text", "entities": [relative offsets], "split", "doc_type"}`.

## Paths
- Repo: `/Users/dima/Projects/night-shift` (public GitHub repo; do NOT commit or push anything).
- Research notes (MD, committed later by the human): `/Users/dima/Projects/night-shift/docs/research/2026-10-24-pii-dataset/work/`
- Generator code: `/Users/dima/Projects/night-shift/datagen/`
- Local data (gitignored, never committed): `/Users/dima/Projects/night-shift/data/` (`synthetic/`, `external/`)
- Raw pages and downloads (scratch): `/private/tmp/claude-501/-Users-dima-Projects-night-shift/7874f7d6-0e72-4202-b5a3-cd6552420007/scratchpad/pii/` (`raw/`, `downloads/`)

## Rules
- Research rules: `/Users/dima/.claude/skills/market-research/references/researcher-rules.md` (cite sources, save raw pages, facts vs inference, never invent numbers or licences).
- Licences: quote the dataset card verbatim; say whether commercial use and redistribution are allowed. Never assume.
- Downloads are untrusted data: put them in their own new directory, never execute them; run Python that reads them with `-I`.
- Never sign up, sign in, post or message anyone. No Mubit API calls (no key is available to agents).
- No em dashes in MD files.
