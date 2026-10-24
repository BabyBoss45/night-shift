# Veil T1: training plan and data (start here)

Written Sat 24 Oct 2026, morning, after an overnight research and data run. Everything below is ready to use; nothing has been sent to Mubit yet and nothing is committed.
Labels: [F] fact from a source, [I] our inference, [ASK] confirm with the Mubit team.

## 0. Bottom line

1. **Data is ready:** 100,000 synthetic UK documents (1.05M labelled values, 20 document types) plus 387,965 converted open-licence documents. That is about 488,000 documents in our canonical format.
2. **Do not send 100,000 calls through Mubit.** Mubit trains on the teacher's answers, the daily training limit sets the pace, and more than about 2,000 diverse chunks a night is waste. A full round costs cents ($0.08 for 500 chunks on `gpt-6-luna`).
3. **Round files are built:** a 50-chunk teacher pilot, a 500-chunk round 1, two 500-chunk later rounds, 200 correction chunks and two eval sets. One chunk per document, no document in two files, eval documents never in training files (checked by code).
4. **Baseline to beat:** regex + validators hides only 38.5% of personal values on our synthetic eval (766 leaks per 100 documents) and 42.4% on the open UK eval. It finds numbers and misses every name, address and date of birth. That gap is why the model exists.
5. **Corrections and serving have no API [F]:** corrections are made in the Mubit console on the request (organisers' PagerPal sample). `evalkit.mistakes` prints each wrong reply with its request id and the corrected JSON ready to paste.
6. **Next action now (Saturday morning):** office-hours questions 1 to 3 (section 7), then the teacher pilot, then round 1. Today's training allowance is unused, so v1 can train today.

## 1. What we have

| Asset | Size | Path | Notes |
|---|---|---|---|
| Synthetic documents | 100,000 docs, 104,869 chunks, 1,047,420 spans | `data/synthetic/docs.jsonl`, `chunks.jsonl` | 20 doc types, 14.9% negatives, 36.6% short messages, 82.4% with planted hard cases, 3,004 template variants, 0 exact duplicates |
| Synthetic demo PDFs | 30 PDFs + gold JSON | `data/synthetic/pdfs/` | 0 of 405 spans lost after pdfplumber extraction |
| External pool A (Mubit-OK) | 387,965 docs (243,495 strict-clean) | `data/external/pool_mubit_ok.jsonl` | Nemotron-PII, Gretel x2, ai4privacy openpii-1m, QuantumAiuk UK, Bitext x2; all synthetic PII, CC BY 4.0 / Apache-2.0 / CDLA-Sharing |
| External pool B (local only) | 1,968 docs | `data/external/eval_local_only.jsonl` | TAB, RedactionBench, PII-TRACE. Real or mixed data: **never through Mubit** |
| Open UK eval | 260 docs | `data/rounds/eval_uk_external.jsonl` | QuantumAiuk test + two "wild" sets: the only open set with sort codes and NI numbers |
| Round files | see section 3 | `data/rounds/` | built by `evalkit.build_rounds` |
| Generator | 73 tests pass | `datagen/` | `uv run python -m datagen.generate --n 100000 --seed 42 --out ../data/synthetic` (about 45 s) |
| Converters | 21 tests pass | `dataconv/` | downloads pinned by revision; licences in `data/external/ATTRIBUTION.md` |
| Toolkit | 6 tests pass | `evalkit/` | frozen prompt, redact/restore, regex baseline, scoring, round builder, Mubit sender, mistakes list |

`data/` is gitignored (about 1.5 GB). Regenerate synthetic data with the command above; external data with the scripts in `dataconv/scripts/`.

Entity counts in the synthetic set: PERSON 440,625; ADDRESS 106,977; PHONE 101,395; POSTCODE 100,219; CUSTOM 86,766; EMAIL 73,794; BANK_ACCOUNT 39,091; SORT_CODE 34,182; DOB 20,616; CARD 14,461; NI_NUMBER 12,681; ID_DOC 11,819; IBAN 4,794.

## 2. Why not 100,000 calls through Mubit [F + I]
- **Imitation:** each adapter version is "tested against your provider model's answers" [F]. More teacher answers teach the teacher's mistakes more firmly.
- **Cadence:** daily training limit (resets 00:00 UTC = 01:00 BST), a pause between trainings, a new version only after N new examples, no retry button [F]. Extra examples only help the trainings we actually get.
- **Throughput and load:** an unknown in-flight cap on the starter credit; 100,000 calls is hours of traffic on a shared event gateway [F/E].
- **What the big corpus is for:** local evaluation, picking hard examples, a possible gold-label track (section 6), and any non-Mubit baseline.

## 3. Round files (`data/rounds/`)

| File | Chunks | Content | When | Send mode |
|---|---:|---|---|---|
| `r0_pilot.jsonl` | 50 | eval chunks covering all 13 types | first | `--record off` (no task, teacher only) |
| `r1_core.jsonl` | 500 | 400 synthetic (20 per doc type) + 100 external | round 1 | recorded |
| `r1_extra.jsonl` | 1,500 | more synthetic train chunks | only if Mubit waits for examples | recorded, in batches of 500 |
| `r2_fresh.jsonl` | 500 | 400 synthetic fresh + 100 external | round 2, Sat afternoon | recorded |
| `r3_reserve.jsonl` | 500 | same mix | after the Sun 01:00 reset | recorded |
| `corrections.jsonl` | 200 | hard cases and CUSTOM ids | correction demo | recorded, then corrected in the console |
| `eval_synthetic.jsonl` | 1,540 (1,459 docs) | whole eval documents + 60 with full card numbers | scoring | `--record off` for the teacher; adapter via the confirmed route |
| `eval_uk_external.jsonl` | 260 | open UK eval | scoring | as above |

Only the **inputs** of training traffic matter to Mubit (it learns the teacher's answers). External documents are there for variety: US and international forms, finance, medical and logistics document shapes.

## 4. Step by step

All commands run from `evalkit/` after `uv sync`. Set the key in the shell only: `export MUBIT_API_KEY=mbt_...` (never in files, never in chat).

**Step 0. Before any traffic (office hours, 10 minutes)**
- Ask questions 1 to 3 of section 7. Write the answers down verbatim.
- Decide where traffic goes: the product project. Claude Code side-quest traffic goes to a separate project.

**Step 1. Bake-off: design and teacher (about 20 minutes, under $1).** Since the teammates' pipeline landed, run `uv run python -m evalkit.bakeoff --live` first; see [BAKEOFF.md](BAKEOFF.md). The single-model pilot below is the older, smaller version of the same step.

**Step 1 (older). Teacher pilot (about 15 minutes, a few cents)**
```bash
for m in gpt-6-luna gemini-3.8-flash; do
  uv run python -m evalkit.send_batch --chunks ../data/rounds/r0_pilot.jsonl --out runs/pilot_$m.jsonl --model $m --record off --live
  uv run python -m evalkit.score --gold ../data/rounds/r0_pilot.jsonl --pred runs/pilot_$m.jsonl --name "pilot $m" --md-out runs/pilot.md
done
```
- `claude-haiku-4-5` uses the Anthropic route; add it only if we decide to support that path in `send_batch`.
- Pick the teacher with the best "values hidden" and the fewest parse errors. The adapter inherits the teacher's quality, so quality beats price here.
- If a model rejects an option (`starter_credit_option`), drop it and retry; do not change the prompt.

**Step 2. Freeze (5 minutes)**
- Freeze `evalkit/src/evalkit/prompts.py` (`PROMPT_VERSION = 1`), the chosen model and `response_format: json_object`.
- Send 10 recorded calls: `--chunks ../data/rounds/r1_core.jsonl --limit 10 --live`.
- In the console: one task named "Find personal data in one document chunk", no stray tasks. Check Settings for the first-training threshold.

**Step 3. Round 1 (about 30 minutes of sending)**
```bash
uv run python -m evalkit.send_batch --chunks ../data/rounds/r1_core.jsonl --out runs/r1_core.jsonl --model <teacher> --live
```
- Watch Tasks: Collecting examples, Reviewing, Training, Testing.
- If it reads "Waiting for more examples: k of need", send `r1_extra.jsonl` with `--limit 500`.
- If it reads "examples too long to train on", regenerate with `--max-chars 3000` in `datagen` and rebuild rounds. New examples are required; there is no retry.

**Step 4. Read v1 and measure**
- Console: v1's result (Passed / Below target / Prompt only).
- Teacher baseline on the eval set (record off, about $0.25 on luna):
```bash
uv run python -m evalkit.send_batch --chunks ../data/rounds/eval_synthetic.jsonl --out runs/eval_teacher.jsonl --model <teacher> --record off --live
uv run python -m evalkit.score --gold ../data/rounds/eval_synthetic.jsonl --pred runs/eval_teacher.jsonl --name teacher --md-out runs/results.md
```
- Adapter numbers: through whatever route Mubit confirms (serving on recorded calls, `metadata` mode, or Try models on a sample).

**Step 5. Corrections (the demo moment)**
```bash
uv run python -m evalkit.send_batch --chunks ../data/rounds/corrections.jsonl --out runs/corrections.jsonl --model <teacher> --live
uv run python -m evalkit.mistakes --gold ../data/rounds/corrections.jsonl --results runs/corrections.jsonl --out runs/corrections_todo.md --top 40
```
- Open `runs/corrections_todo.md`. For each item, find the request in the console (request id or Session filter) and replace the reply with the corrected JSON.
- Pick 3 to 5 corrections for the stage story, ideally CUSTOM ids (client codes, matter numbers) and signature-only names: the teacher misses them and regex cannot see them.

**Step 6. Round 2, v2 (Saturday afternoon)**
- Send `r2_fresh.jsonl` (recorded) to reach "Next: a new version after N new examples".
- When v2 passes, rerun Step 4 for v2 and the pre-correction cases.

**Step 7. Sunday 01:00 BST reset**
- Send `r3_reserve.jsonl` straight after the reset if a v3 is worth it. Code freeze at 05:00 (confirm).

**Step 8. Demo table**
| Arm | Source |
|---|---|
| Regex + validators | `docs/research/2026-10-24-pii-dataset/work/baseline-results.md` (done) |
| Optional open model: `openai/privacy-filter` or a GLiNER-PII model, run locally | `methods.md` recommendations |
| Teacher (frontier) | Step 4 |
| Adapter v1, v2 | Steps 4 and 6 |

Headline: leaks per 100 documents and zero-leak documents; then per-type recall, over-redaction on keep traps, p50 latency and cost per document.

## 5. Decisions (recommendations already applied in data and prompt)

| Decision | Our choice | Why |
|---|---|---|
| Organisation contact details (letterhead address, office phone, staff email) | **Label them** (generator and prompt v1) | A missed personal number is a leak; a redacted office number costs nothing because placeholders are restored. Research note `hard-cases.md` items 38 and 47 suggested keeping them; we chose privacy first. To switch, filter spans with `entity_refs == null` (see `datagen/README.md`) and edit the prompt before freezing |
| NHS number | ID_DOC | National number issued to the person |
| UTR | CUSTOM | Generator convention; a research note proposed ID_DOC. Either works; do not change after freezing |
| Card endings ("ending 4821") | Label the digits as CARD | Conservative; QuantumAiuk leaves them unlabelled, so its eval ignores them |
| Outward-only postcodes ("the LS6 area") | Not labelled | Not identifying on their own; ai4privacy rows that label them are excluded from rounds |
| Output format | `response_format: json_object`, values not offsets | One malformed tool call fails a version; code finds every occurrence |
| Placeholders | `[PERSON_1]`, `[ACCOUNT_1]`, consistent per conversation | Better answers than plain `[REDACTED]`; restore is exact then tolerant |
| Claims | "pseudonymised; direct identifiers replaced; measured leak rate on synthetic UK documents" | ICO: pseudonymised data is still personal data. Never say "anonymised" or "compliant" |

## 6. Optional: training on gold labels (only with Mubit's permission)
- Mubit can import past calls from Langfuse, Braintrust or Logfire, but only calls dated before a project's first live call [F].
- In principle: a fresh project, Langfuse generations whose output is our gold JSON, the same model id, system prompt and response format as live, then import. That would teach the adapter our labels instead of the teacher's.
- Four unknowns block it (one project per workspace in the docs vs five in our console; whether the importer reads `response_format`; session mapping; whether organisers allow it). Backdating traces to get under the cut is off limits without explicit permission.
- Full steps and risks: `work/mubit-training-guide.md` section 4.

## 7. Questions for office hours (top 6; full list in `work/mubit-training-guide.md` section 8)
1. When we correct a reply in the console, does the corrected answer become the training target (and a "required test case")? Is there an API for corrections by `mreq_` id? Does "Bad" drop the example?
2. After a version passes, are live calls served by the adapter automatically? How can our code tell per call? Can a call force the teacher, for measurement?
3. Trainings per UTC day, pause length, time per training; can the 25-example trigger be raised in Settings?
4. How is "matched" computed for a JSON answer, and what is the pass threshold?
5. Token limit behind "examples too long to train on".
6. Is eval traffic with `x-middleware-record: off` acceptable under "every call through Mubit"?

## 8. Risks
| Risk | Mitigation |
|---|---|
| Teacher already near perfect on synthetic data, so few corrections | The corrections file targets CUSTOM ids and signature-only names; check the pilot first |
| v1 "Prompt only" | Harder chunks from `r1_extra`; explain that it is a cost win |
| Synthetic data too clean | 108 hard cases planted; open UK "wild" sets and RedactionBench (local) as reality checks |
| Convention mismatch with external golds | External golds are used for scoring only; read per-type numbers with `work/external-datasets.md` in mind |
| CDLA-Sharing (Bitext) | Do not publish files containing Bitext rows; keep `data/` out of git |

## 9. Where everything is
- Research notes: `work/` in this folder. `datasets.md` (75 datasets, licences), `methods.md` (approaches, benchmarks, metrics), `uk-formats.md` (13 tested validators), `hard-cases.md` (108 cases), `mubit-training-guide.md`, `external-datasets.md`, `synthetic-stats.md`, `baseline-results.md`.
- Evidence tables: `work/evidence-*.csv`. Raw page copies stay in the local scratchpad (not in the repo).
- Code: `datagen/`, `dataconv/`, `evalkit/`.
- Product context: `docs/NIGHT-SHIFT-TEAM-PACK.md`.
