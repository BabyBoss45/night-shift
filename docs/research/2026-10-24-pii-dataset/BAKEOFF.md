# Bake-off: pick one T1 design and one teacher before training

Written Sat 24 Oct 2026 after the teammates' pipeline landed in `main`. Labels: [F] from Mubit's docs, [I] our inference, [ASK] confirm with Mubit.

## 1. Teacher vs student (what "train on GPT-6 Luna" means)
- **Teacher:** the frontier model our calls go to through Mubit (`gpt-6-luna`, `claude-haiku-4-5`, `gemini-3.8-flash` on the starter credit [F]). Its answers become the training targets.
- **Student (adapter):** a small open model that Mubit picks and trains on its own GPUs [F]. We do not choose it.
- "Train on Haiku" therefore means "use Haiku as the teacher". Price per 1M tokens [F, provider pages]: luna $0.10 in / $0.50 out, Gemini Flash $0.75 / $3.75, Haiku $1 / $5. **Luna is the cheapest**, Haiku the most expensive of the three.
- The adapter inherits the teacher's quality, so pick the teacher by measured quality first, price second.

## 2. What Mubit expects as data [F unless marked]
- There is **no dataset upload**. Training data is the calls themselves: request + provider answer, recorded by the gateway. The only other way in is "Import past calls" from Langfuse, Braintrust or Logfire (before a project's first live call).
- So the format is **the provider's own API JSON**: OpenAI chat/completions or responses, Anthropic messages, Gemini generateContent. Our document goes in the user message as **plain text**. XML, JSONB or binary bring nothing: the adapter learns text in, text out [I].
- **PDFs:** send extracted text, not files. Hosted file search and other billed tools are refused on the starter credit (`starter_credit_tools`), and the adapter learns from text [F + I].
- **Starter credit limits:** request body at most 8 MiB, plain JSON, sent whole within 60 s; routes only OpenAI `/chat/completions`, `/responses`, Anthropic `/v1/messages`, Gemini native `:generateContent`. The OpenAI-compatible Gemini URL gets `403 starter_credit_route` [F]. An in-flight cap per project (`starter_credit_busy`, number not published) [F].
- **Task = model + system prompt + tools + tool choice + output format** [F]. So each design x model pair is a separate task.
- **Output format:** JSON is safest. OpenAI `response_format: json_object`, Gemini `responseMimeType: application/json`, Anthropic has no JSON switch (prompt only). Avoid tool calls: one malformed tool call fails a version [F].
- **Length:** "examples too long to train on" exists, limit not published [F]. Keep chunks at 500 to 1,000 tokens [I].
- **Sessions:** OpenAI `metadata.session_id`, Anthropic `metadata.user_id`, Gemini has none (Mubit derives it from instructions + first user message) [F]. Test cases are held out by session.
- **Language:** English UK documents throughout (all our data and the teammates' data).

## 3. Two pipelines now in the repo
| | Teammates (`backend/app/prompts.py`, `scripts/dataset/`) | Ours (`evalkit/`, `datagen/`, `dataconv/`) |
|---|---|---|
| T1 prompt | "Redact personal data in one document chunk." | "Find personal data in one document chunk." |
| Answer | the whole chunk rewritten with `[TYPE_N]` | JSON list of values; code replaces |
| Teacher | `claude-haiku-4-5` | pick by bake-off |
| Data | 180 documents from real templates (contracts C1 to C8, Enron-shaped emails with fake values, Gretel finance, insurance) | 100,000 synthetic + 387,965 open-licence |
| Chunks | about 1,000 tokens | up to 6,000 chars (about 1,500 tokens); round files curated |
| Strength | the model links "Jane Smith" and "Ms Smith" to one placeholder | short answers: cheaper, faster, easier to match the teacher, the text cannot be altered |

Label conventions differ slightly (a title inside or outside the placeholder; organisation contact details). Scoring uses "is every gold value fully hidden", so these differences do not change the leak numbers.

The teammates' documents are now also in our format: `data/rounds/team_train.jsonl` (300 chunks) and `team_eval.jsonl` (155 chunks), produced by `evalkit.team_docs`.

## 4. Strategy: three people, three approaches?
- **Training three tasks at once is risky.** Each task needs its own 25+ kept examples, its own trainings and its own corrections, and the daily training limit may be per organisation [ASK]. Three half-trained models are worse than one finished one. Judges want one product.
- **Comparing three approaches is cheap and smart.** With `x-middleware-record: off`, calls are forwarded but no task is created and nothing trains [F]. We can compare designs and teachers on the same 120 chunks for under $1 in about 20 minutes, then train ONE.
- The comparison itself is a good slide: "we measured 3 teachers x 2 designs on the same gold set and picked the best". It matches how Mubit presents its own benchmarks [I].
- If Mubit confirms the training limit is per project, a second arm can train in a separate project (we have up to 5 projects in the console) [ASK].

**Update: each of us has a separate Mubit account with its own credits.** Then the training limits and credits are separate too, and three arms can train in parallel without competing. That turns the bake-off into a real experiment on adapters, not only teachers:

| Account | Arm | Data | What it isolates |
|---|---|---|---|
| A (Dmytro) | list x `gpt-6-luna` | `r1_core` + `team_train`, then `r2_fresh` | our design, cheapest teacher |
| B (Nick) | rewrite x `claude-haiku-4-5` | the teammates' pipeline and documents (+ our chunks if they want volume) | the rewrite design |
| C (Mykola) | list x `claude-haiku-4-5` or `gemini-3.8-flash` | same as A | the teacher, with the design fixed |

Rules that keep the comparison fair:
- **Score everyone on the same files:** `bakeoff.jsonl` and `eval_synthetic.jsonl`, with `evalkit.score`.
- **No account ever sends eval files as recorded traffic.** Use `--record off`.
- **Pick one adapter for the demo app** by Saturday evening. The app switches by Mubit key, so changing accounts is one setting.
- **Split the corrections work.** Each account corrects its own top mistakes (`evalkit.mistakes`).
- `data/` is gitignored. Hand the round files to teammates directly (AirDrop or Drive), or have them rebuild: `datagen` in about a minute; the external part needs the `dataconv` downloads.

## 5. Run it
```bash
cd /Users/dima/Projects/night-shift/evalkit && uv sync
export MUBIT_API_KEY=mbt_...
uv run python -m evalkit.bakeoff --live
```
- Set: `data/rounds/bakeoff.jsonl` = 50 synthetic eval + 40 teammates' eval + 30 open UK eval chunks (99 documents, 687 gold values).
- Default arms: list x gpt-6-luna, list x claude-haiku-4-5, list x gemini-3.8-flash, rewrite x claude-haiku-4-5.
- Estimated cost: about $0.02 + $0.21 + $0.16 + $0.40.
- Output: `evalkit/runs/bakeoff/RESULTS.md`, with one table of leaks per 100 documents, zero-leak documents, hidden share, precision, keep-trap hits, text changed, $ per 1,000 chunks, p50 latency, and per-type hidden share.
- Regex baseline on the same set (already run): 37.9% hidden, 431 leaks per 100 documents.

## 6. Decide, then train
1. Lowest leaks wins. Break ties on zero-leak documents, then cost and latency. Rewrite answers that change text outside placeholders count against that arm.
2. Freeze that design's prompt and the teacher model.
3. Training data for round 1:
   - our `r1_core.jsonl` (500);
   - plus the teammates' `team_train.jsonl` (300 realistic chunks).
   
   If the rewrite design wins, use their `scripts/dataset/send_batch.py` with the same files converted, or `evalkit.send_batch --design rewrite`.
4. Continue with `TRAINING-PLAN.md` from step 2.
