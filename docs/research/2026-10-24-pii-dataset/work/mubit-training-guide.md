# Mubit training guide for T1 (redaction)

Written Sat 24 Oct 2026, about 01:00-02:15 BST, by a research agent. No Mubit API calls were made; nothing was signed up for.

Labels: **[F]** fact seen in a source, **[I]** our inference, **[E]** estimate with the method stated, **[ASK]** must be confirmed with Mubit.

Paths used in citations:
- `DOCS` = `/private/tmp/claude-501/-Users-dima-Projects-night-shift/7874f7d6-0e72-4202-b5a3-cd6552420007/scratchpad/mubit/docs-llms-full.txt` (re-downloaded today from https://docs.mubit.ai/llms-full.txt: byte-identical, so the docs have not changed since the team pack; fresh copy also at `RAW/T-7.md` with 2 extra header lines).
- `RAW` = `/private/tmp/claude-501/-Users-dima-Projects-night-shift/7874f7d6-0e72-4202-b5a3-cd6552420007/scratchpad/pii/raw/` (all pages saved as `T-n.md`, first line is the URL).
- `SDK` = `/private/tmp/claude-501/-Users-dima-Projects-night-shift/7874f7d6-0e72-4202-b5a3-cd6552420007/scratchpad/dl-sdk/x/mubit/` (PyPI mubit-sdk 0.13.2).
- `PP` = `https://raw.githubusercontent.com/e1daru/pagerpal/HEAD/` (copies with original line numbers in `RAW/T-9.md` to `RAW/T-17.md`).

---

## 0. Key findings (read this first)

1. **Imitation is the default.** Adapters are "tested against your provider model's answers" [F, DOCS L13, L464]. The adapter's ceiling is roughly the teacher's quality, so the teacher choice and the corrections path matter more than volume [I].
2. **No public correction API exists.** The memory SDK's feedback endpoints (`/v2/control/feedback`, `/outcome`, `/step_outcome`) take handoff or lesson ids, never an `mreq_` id or a corrected answer, and the SDK has no reference to the gateway, adapters or `x-middleware-*` [F, SDK client.py L789, L803, L854-859, L2613-2672, L2947-2971; grep found nothing]. The only documented per-call feedback is the console's **Rate this reply: Good / Bad** [F, DOCS L2449]. PagerPal says corrections are made "in the Mubit console, on the request" [F, PP app.py L5-6, templates/alert.html L16-18].
3. **One hint about how corrections may be graded:** a Below-target line can read `Passed {a}% of {n} required test cases · needs 100%` [F, DOCS L986]. [I] "Required test cases" may be where console corrections land. [ASK]
4. **No way to tell from the API which model served a call.** Response headers are only `x-middleware-request-id`, `x-should-retry`, `retry-after` [F, DOCS L3071-3077]. "Served by" exists only in the console [F, DOCS L2414-2435]. There is no Mubit model id [F, DOCS L2681]. Pricing says "Models serve only after matching or beating your frontier model in evals" [F, RAW/T-31.md, pricing.md L12].
5. **Cost is not the constraint; training cadence is.** At ~1,200 in / 150 out tokens, 1,000 chunk calls cost about $0.20 on `gpt-6-luna`, $1.95 on `claude-haiku-4-5`, $1.46 on `gemini-3.8-flash` [E, from published prices, section 3.6]. The list-price Mubit fee would be $5 per 1,000 runs [F, pricing.md L9]. What limits us is the daily training limit, the pause between trainings and the 25-example trigger.
6. **Gold-label import is possible on paper but needs 4 confirmations.** Import reads only calls from before the project's first live call [F, DOCS L2725]. The docs say a workspace has exactly one project and you cannot add one [F, DOCS L2759-2761], which conflicts with the "up to 5 projects" our console screenshot showed. Whether Mubit reads `response_format` and the session from a Langfuse generation is unknown [ASK].
7. **Eval traffic:** `x-middleware-record: metadata` keeps the task fingerprint but no content; `off` drops the fingerprint too [F, DOCS L3058]. [I] Use `metadata` for eval calls that should still be routable to the adapter, and `off` for teacher-only baselines. [ASK] whether metadata-only calls can be served by the adapter.

---

## 1. How Mubit turns calls into adapters

### 1.1 Task fingerprint [F]
- A task = same instructions, tools, tool choice, output format and model. "The messages after the instructions, and settings such as `temperature` or `max_tokens`" do not count [DOCS L2519-2527].
- Instructions = `system`/`developer` messages on Chat Completions, `system` on Anthropic, `systemInstruction` on Gemini [DOCS L2529].
- Allowances: whitespace runs count as one space; "Numbers, dates, times and IDs don't split a task"; other changing words do [DOCS L2533-2537].
  - [I] Consequence: changing only a version number inside the prompt ("PROMPT_VERSION 1" to "2") does NOT start a new task. Changing any word does.
- Model: date or snapshot suffix and `-latest` are ignored; the same instructions on two models are two tasks [DOCS L2667-2669].
- Display name = first words of the instructions [DOCS L2531].
- `x-middleware-record: off` "also drops the call's task fingerprint" [DOCS L3058].

### 1.2 Kept examples and curation [F unless marked]
- "Not every call is kept" [DOCS L453, L463, L497]. A kept example is "A call Mubit accepts for training or testing" [DOCS L463].
- "A call recorded without its request and reply is never a kept example" [DOCS L1232]. So `x-middleware-store: false` or `record: metadata|off` calls never train.
- Status flow: `Collecting examples` (with a count such as `12 of 25 examples`), then `Reviewing examples`, `Training`, `Testing` [DOCS L955-957].
- First training at 25 kept examples by default; "the count your console shows is the source of truth" [DOCS L497].
- What gets a call rejected is not documented. "Near-duplicates are discarded" is in our team pack, but it is **not** in the docs [I; not found in DOCS]. Mubit's own first-adapter example is 40 calls built from 8 templates x 5 plan names [DOCS L525-537], so templated variety is enough for them to train.
- Settings: "**Settings** shows there once training is on for your workspace" (admins change it) [DOCS L2797]. Pricing: "Learning is on by default. Switch it off for any task and its requests stop counting" [RAW/T-31.md, pricing.md L130]. [ASK] whether Settings lets us raise the 25-example trigger.

### 1.3 Held-out test cases by session [F]
- "A session is the calls of one conversation. Mubit sets a task's test cases aside by session" [DOCS L2543].
- Session source order: `metadata.thread_id`, `metadata.session_id`, `metadata.conversation_id`, Anthropic `metadata.user_id`, Responses `prompt_cache_key`; otherwise derived from instructions plus first user message [DOCS L2545-2553]. Values over 200 characters are hashed [DOCS L2565].
- `Waiting for more examples: {k} of {need}` means "The task has too few examples to keep some back as test cases" [DOCS L1003].
- [I] Without `metadata.session_id`, each chunk becomes its own session (its first user message differs), so chunks of one document can land in both train and test. Always send `doc-<id>`.

### 1.4 Grading and verdicts [F]
| Verdict | Meaning (docs) |
|---|---|
| `Passed` | "answers close enough to your provider model"; Overview reads `v1 passed its tests` |
| `Below target` | `Matched {a}% of your provider model's answers on {n} test cases · needs {need}%`, or `Passed {a}% of {n} required test cases · needs 100%` |
| `Malformed tool calls` | `{k} of {n} tool calls were malformed · needs 0` |
| `Prompt only` | the base model with the task's prompt did as well as the adapter; cannot be tried in Try models |
| `Not tested` | no result; reason on hover |
Source: DOCS L983-991. While grading: `Waiting for grading on {k} test cases`; while below target: `Not ready yet` [DOCS L991].
- [I] The matching metric for JSON (exact string, field-level or semantic) and `{need}` are not published. [ASK]
- [I] "Prompt only" is a real risk for a well-prompted extraction task. It means no adapter to show. A task the base model finds hard (UK formats, CUSTOM identifiers, hard cases) protects against it.

### 1.5 Waits, limits, failures [F]
- `Waiting: today's training limit` (resets 00:00 UTC); `Waiting: the pause between trainings`; `Waiting for new examples` after a failed training ("It does not retry the same ones") [DOCS L999-1004].
- `Can't train` reasons: `too few examples to train on`, `examples too long to train on` ("Send calls with shorter requests and answers"), `the training run failed`, `the first training stopped` [DOCS L1010-1015].
- "There is no button that retries a training" [DOCS L1017].
- After a version that did not pass: `Next: a new version after {need} new examples` or `Next: retraining paused: {reason}` [DOCS L1021-1024]. N is not published.
- Try models: daily org call limit, resets 00:00 UTC; calls are `not stored · trains nothing`; first adapter start takes minutes (page resends every 15 s for up to 20 min); "3 adapter starts for this UTC day" per org [DOCS L971, L1030-1042].
- Not published anywhere: trainings per day, pause length, training duration, max tokens per example [not found].
  - Only size hint: pricing counts "A run is one request ... up to 8,000 tokens in and out" [RAW/T-31.md, pricing.md L128]. [I] Keeping request plus answer far below that (about 2,000 tokens) is the safe side.

### 1.6 Base model and adapter size
- [F] "trains adapters, small models each made for one task" [DOCS L13]; "the base model, the open model the adapter is built on" [DOCS L988].
- [F] `Not in Try models: its base model isn't served here` [DOCS L1037]. [I] So more than one base model exists, chosen per task or workspace.
- [F] mubit.ai/llms.txt: "Adaptation uses traces and outcome feedback to update open-weight models through versioned, reversible adapters. It does not modify hosted frontier-model weights" [RAW/T-30.md L23].
- [F] middleware.now: "lightweight model updates"; "Mubit will host the open models ... The base models stay fixed" [RAW/T-1.md L11, L54].
  - Its research describes "A shared model component ... A generator produces a small, application-specific update ... A change detector ... triggers a refresh when enough has changed".
  - It also admits "Generating updates for a new application without that fitting step is still under development" [RAW/T-1.md L81, L83].
- [F] Their only public model, Banyan Sapling, is a different product: Qwen3-30B-A3B base with "Attention LoRA and verification head" [RAW/T-29.md L5, L38-43].
- **Base model and adapter rank or size for Middleware: not found.** [ASK]

---

## 2. How corrections enter training (event build) and how serving shows

### 2.1 What PagerPal sends [F, file:line]
- Client: `anthropic.AsyncAnthropic(base_url=<host>+"/anthropic", api_key=MUBIT_API_KEY)` [PP src/pagerpal/llm.py L18-28]. Host comes from `MUBIT_BASE_URL`, defaulting to `https://api.mubit.ai`; comment "a US workspace: api-us" [llm.py L19; tests/test_llm.py L19-23].
- Model `claude-sonnet-4-5` [llm.py L13], which is not on the docs' starter-credit list. PagerPal expects the Anthropic key in Mubit's Provider keys [llm.py L3-5].
- **No system prompt.** The call has only one user message: alert, labels and the runbook catalogue, ending "Pick the one runbook that applies and its first three steps." [src/pagerpal/triage.py L41-48, L55-60].
  - [I] So PagerPal's task fingerprint is model + empty instructions + output format.
- Output format: `output_config={"format": {"type": "json_schema", "schema": SCHEMA}}` [triage.py L59]. SCHEMA = runbook, confidence, first_steps (maxItems 3), why; `additionalProperties: false` [triage.py L18-28]. `max_tokens=800`.
- No `metadata`, no session, no custom headers [triage.py L55-60]. [I] Each alert is its own session.
- Reads `x-middleware-request-id` via `messages.with_raw_response.create` then `raw.headers.get(...)` [triage.py L55, L61; llm.py L15].
- Fallback: on any error or unknown runbook it returns a keyword match with `source="keywords"` and confidence 0.3 [triage.py L64-72].
- Stores the suggestion JSON with `request_id` in SQLite [store.py L7-17; app.py L60-65]. The resolve form saves `resolved_with` [app.py L73-80]. `was_right` = suggested runbook equals resolved runbook [app.py L50-51]. `/history` shows "Right first time: {right} of {n}" [templates/history.html L4].
- Corrections are not made in the app: "Corrections aren't made here: they are made in the Mubit console, on the request the alert page names" [app.py L5-6]. The alert page hint says Mubit "turns corrections into a model update for the triage task" [templates/alert.html L16-18].
- Serving: the README says "later suggestions come from the updated model. PagerPal's code doesn't change" [RAW/T-17.md L20-22]. **No code anywhere detects which model served a call.**
- Tests fake the id as `mw-000001`, not the real `mreq_` format [tests/conftest.py L19].
- [F] The 7 commits are dated 2026-10-23T19:05Z to 2026-10-24T16:30Z on round minutes, the last one later than now [GitHub API commits, fetched 2026-10-24]. [I] This is a staged sample written for the event, so its README states the intended flow, not proof that the flow works.

### 2.2 Telling whether the adapter served a call
- [F] Response headers: only `x-middleware-request-id`, `x-should-retry`, `retry-after`; provider headers pass unchanged [DOCS L3071-3077].
- [F] Console Requests: columns `Model asked` and `Served by`, a Served by filter, and "Where the time went" [DOCS L2416-2448].
- [F] The console's Request ID is not the `mreq_` id [DOCS L2494]. The Session filter lives in the URL [DOCS L2424-2427].
- [F] latte-bench (Mubit's own gateway benchmark) sets "Set the actual model/route IDs provided by your gateway" and `MUBIT_EXTRA_BODY` "for documented gateway-specific routing. Learning/training is NOT assumed or enabled without your gateway's contract" [RAW/T-20.md, .env.example]. It reads `usage.cost` from the body when present [RAW/T-20.md, server.js L45].
- [I] Practical plan:
  - Log every response header and the body fields `model`, `system_fingerprint`, `id` and `usage` for every T1 call.
  - Diff them before and after a version passes.
  - Use console "Served by" (filtered by Session `doc-<id>`) as ground truth.
  - [ASK] for a header or body field.

### 2.3 Correction or feedback API on api.mubit.ai
- [F] SDK 0.13.2 endpoints are memory-product endpoints under `/v2/control/*` and `/v2/core/*` (60+, SDK client.py L26-1304). The feedback-like ones:
  - `/v2/control/feedback`: "Submit feedback verdict for an existing handoff" [client.py L854-859], params `handoff_id, verdict, comments` [L2947-2971];
  - `/v2/control/outcome`: "Record reinforcement outcome feedback for a lesson or action" [L789], params `reference_id, outcome, signal, rationale` [L2613-2638];
  - `/v2/control/step_outcome` [L803; L2647-2672]; `/v2/control/reflect` [learn/_client.py L192].
- [F] grep of the SDK for `mreq_`, `x-middleware`, `gateway`, `adapter`, `served` found nothing outside protobufs.
- [F] The API catalog points to `https://docs.mubit.ai/api-reference/control-http`, which returns 404 today [fetched 2026-10-24].
- [F] The pricing templates claim learning from app events: "Learns from every reassigned ticket", "what each user opens, archives or moves", "comments your reviewers keep or dismiss" [pricing.md L35-50]. [I] So some signal path from the app exists or is planned. [ASK]
- **Conclusion:** no documented API ties a correction to a gateway request. Plan on the console (PagerPal flow) plus our fallback (section 4.3).

---

## 3. Designing training traffic for T1

### 3.1 Chunk length [F + I]
- [F] "examples too long to train on": "Send calls with shorter requests and answers" [DOCS L1013]. There is no published limit.
- [I] Target 500-900 tokens per chunk (about 2,000-3,600 characters), hard cap 1,500. Split on paragraph or line boundaries, no overlap, and keep a table row or address block whole.
  - Shorter chunks give more examples per document. But all chunks of a document share one session, so the session count (documents), not the chunk count, sets the test split's size.
- [I] Put the entity list in the answer, not the rewritten text (already planned). Answers stay under about 200 tokens.

### 3.2 Diversity vs volume, near-duplicates [I]
- Use many documents with few chunks each in round 1 (about 2 chunks per document), so the held-out split has enough sessions.
- Cover all 10 doc types early. Vary templates, field order, names (Faker `en_GB` plus non-English and transliterated names) and formats.
- Avoid identical boilerplate chunks across documents (same clause text): one per type is enough.
- Mubit does not document de-duplication [F, not found], so treat it as unknown. Duplicates at least waste calls and can skew the test split.

### 3.3 JSON output: `response_format` vs tools [F + I]
- [F] `Malformed tool calls` applies to tool calls and requires 0 malformed [DOCS L987]. Output format is part of the fingerprint [DOCS L2519-2525].
- [I] Do **not** use tool calls for T1: one bad tool call fails a version.
- [I] Use `response_format`. `json_object` is the simplest. `json_schema` (strict, with `type` as an enum of our 13 types) makes the teacher more consistent, and Mubit's own latte-bench sends `response_format` with a JSON schema through the gateway [RAW/T-20.md, study-provider.js L16; server.js L40].
  - Decide once, test 1 call on the starter credit (it may refuse some options: `starter_credit_option` [DOCS L3310]), then freeze.
- [I] Validate the JSON in our code either way and fall back to regex plus teacher on parse failure (PagerPal's pattern, triage.py L64-72).
- [I] Make teacher answers deterministic so "Matched x%" is easier to reach:
  - `temperature: 0`;
  - "list entities in order of first appearance, each distinct text once";
  - return `{"entities": []}` when nothing is found;
  - the word "JSON" in the system prompt (OpenAI's JSON mode expects it; not re-checked here).

### 3.4 System prompt naming, sessions, mixture [F + I]
- [F] Start with the meaningful phrase "Find personal data in one document chunk." (task name = first words, DOCS L2531). Never put per-document text in it (DOCS L2537-2539).
- [F] `metadata={"session_id": f"doc-{doc_id}"}` on OpenAI (DOCS L2559, L2585-2592). On Anthropic use `metadata.user_id` (DOCS L2560-2563).
- [I] Do not send `doc_type` in the user message, since production uploads will not carry it.
- [I] Mixture per round:
  - about 10-15% chunks with no personal data (empty list);
  - about 20-30% chunks with "keep" traps (amounts, ordinary dates, public companies, place names);
  - about 25-30% hard cases from team pack 9.4.
  This is standard practice for extraction tasks, not a Mubit rule.

### 3.5 Calls per round and throughput [F + I]
- [F] Training triggers at 25 kept examples [DOCS L497]. [I] If the first training starts the moment 25 arrive, v1 may train on about 25-50 examples and use one of today's trainings.
  - Mitigations: (a) check Settings for a threshold; (b) send round 1 as one fast burst; (c) [ASK] whether training uses all kept examples present when it starts.
- [F] The starter credit has an in-flight cap: `starter_credit_busy` "already has {n} calls in flight ... its limit at once" (429 with `retry-after`) [DOCS L3313]. n is not published.
- [I] Sensible volumes: round 1 = 300-500 chunks; later rounds = 200-400 new chunks each. Beyond about 2,000 chunks per night the gain is limited by training cadence, not data.

### 3.6 Cost estimates (published prices) [F prices, E totals]
Prices per 1M tokens, standard tier:
- `gpt-6-luna`: $0.10 in, $0.50 out [F, RAW/T-22.md L964; also Mubit's latte-bench "standardRates" input 0.1 output 0.5, RAW/T-18.md];
- `claude-haiku-4-5`: $1 in, $5 out [F, RAW/T-21.md L38];
- `gemini-3.8-flash`: $0.75 in, $3.75 out through 31 Dec 2026, output "including thinking tokens" [F, RAW/T-23.md, section "Gemini 3.8 Flash"].

Mubit fee at list price: "$5 per 1,000 runs"; a run is one request in a learning task up to 8,000 tokens; "Never charged: ... Training, evals or storage" [F, pricing.md L9, L26-28, L128]. Whether runs are billed to hackers is unknown [ASK]. Assumption: 1,200 input + 150 output tokens per call, 1 run per call.

| Chunk calls | gpt-6-luna | claude-haiku-4-5 | gemini-3.8-flash | Mubit runs at list price |
|---:|---:|---:|---:|---:|
| 1,000 | $0.20 | $1.95 | $1.46 | $5 |
| 5,000 | $0.98 | $9.75 | $7.31 | $25 |
| 20,000 | $3.90 | $39.00 | $29.25 | $100 |
| 100,000 | $19.50 | $195.00 | $146.25 | $500 |

Method: calls x (1,200 x input price + 150 x output price) / 1e6.

Caveats:
- [I] `gpt-6-luna` accepts `reasoning_effort` (latte-bench sets it, RAW/T-18.md), so hidden reasoning may add output tokens.
  - Each +500 output tokens per call adds $0.25 per 1,000 calls on luna and $1.88 per 1,000 calls on Gemini.
  - Set the lowest reasoning effort the model allows, and record `usage` on every call.
- Tokenizers differ, so 1,200 tokens of text on one model is not exactly 1,200 on another.
- Batch discounts do not apply: the starter credit serves only `chat/completions`, `responses`, `embeddings`, `models` on OpenAI [F, DOCS L3049].

### 3.7 Why 100,000 documents through Mubit is not sensible tonight [I, with facts]
1. **Training cadence, not data, is the bottleneck.** Daily training limit, pause between trainings, no retry [DOCS L999-1017]. Extra examples only help the trainings we can get before 05:00 BST Sunday.
2. **Imitation ceiling.** More teacher answers teach the teacher's mistakes more firmly; they do not exceed it [DOCS L13].
3. **Throughput** [E]: at an assumed 10 calls in flight and 3 s per call, 100,000 calls take about 8.3 hours, and the in-flight cap is unknown [DOCS L3313].
4. **Template saturation.** 100,000 documents from about 10 templates are mostly near-copies. Diversity stops growing long before that.
5. **Money and shared capacity.** About $500 in runs at list price plus $20-195 in tokens, and load on a shared event gateway (`gateway_overloaded` exists, DOCS L3334).
6. **Reviewability.** We need to review answers and pick corrections. That works at hundreds of chunks, not 100,000.
- A large local corpus is still useful **offline** for our own eval and for a non-Mubit baseline. Send a few thousand at most through Mubit.

---

## 4. Import past calls: gold labels into a fresh project

### 4.1 Exact requirements [F, DOCS L2688-2744]
- Admin only [L2696].
- Sources: Langfuse (a project API key with the Viewer permission, pasted as `pk-lf-...:sk-lf-...`), Braintrust (service token in Viewers group) or Pydantic Logfire (read token) [L2700-2708].
- Steps: choose source, host, paste key, **Check key** (shows `Accepted`, newest call, models found), window **7 / 14 / 30 days**, tick `I may share these calls with Mubit.`, optionally keep the key, **Start import** [L2712-2720].
- Reads only "the calls from before your project's first call through Mubit": `Cut at the project's first live call.` [L2725]. Read-only requests only [L2726].
- One import at a time [L2728]. States `Queued`, `Running`, `Paused`, `Done`, `Failed`, `Cancelled`, with counts read / imported / skipped and tasks found [L2732-2738].
- Key deleted after the import unless kept [L2744].
- "Mubit treats imported calls like the calls your app sends: it finds tasks in them" [L2694].
- Langfuse key permissions: Full access / Viewer / Ingestion / Scores ingestion; Viewer = "Read-only access to the project's data"; permissions cannot be changed later [F, RAW/T-26.md, "Project API key permissions"]. So use two keys: Ingestion for writing, Viewer for Mubit.

### 4.2 Could imported gold labels train T1? [I unless marked]
- **In principle yes.** If imported generations carry the same model id, system prompt and output format as live calls, they form the same task. Their "provider answers" (the imported outputs) are then our gold JSON, so training and grading imitate gold, not GPT.
- Blockers to clear first:
  1. **A project with no live call.** [F] The docs say a workspace has one project and "You can't add a second project" [DOCS L2759-2761]. Our console screenshot showed up to 5 projects (team pack 3.7). If we cannot get a clean project, import is closed in the main project, because test calls have already been made there. [ASK]
  2. **Fingerprint mapping from Langfuse.** Not documented.
     - [F] Langfuse's OpenAI integration stores `messages` (incl. system) in `input`, `tools` in `input`, `response_format` in **metadata**, request `metadata` in metadata, and the response `model` as model [RAW/T-24.md, openai.py L195-196, L250-272, L307, L384-405, L550, L929].
     - [F] `tool_choice` is captured only for the Responses API, not Chat Completions [openai.py L195, L384-405].
     - [ASK] Does Mubit read output format from `metadata.response_format`? If not, imported calls (no format) and live calls (`json_object`) are two tasks.
  3. **Session mapping.** [ASK] Does Mubit use the Langfuse trace `sessionId`, or `metadata.session_id`? Otherwise each chunk is its own session and chunks leak between train and test.
  4. **Allowed?** Ask the organisers whether training on imported synthetic gold is acceptable for judging, and disclose it in the demo.
- Mixed targets risk: after import, live calls add GPT answers to the same task. Where GPT disagrees with gold, the adapter sees conflicting targets [I]. Keep live T1 traffic in the gold project small, or accept a blend.

### 4.3 What a Langfuse generation must contain (our best mapping)
| Mubit needs [F, DOCS L2519-2525] | Langfuse field | Value for T1 |
|---|---|---|
| model | generation `model` (OTel `langfuse.observation.model.name` or `gen_ai.request.model`) | exactly `gpt-6-luna` (a date suffix is ignored by Mubit) |
| instructions | `input` = list of messages, first `{"role":"system","content": SYSTEM_PROMPT}` | the frozen T1 prompt, byte-identical to live |
| user message | second message `{"role":"user","content": chunk_text}` | the chunk |
| output | `output` = `{"role":"assistant","content": "<gold JSON string>"}` | canonical gold JSON, same ordering rules as live |
| output format | `metadata.response_format` (where Langfuse's OpenAI wrapper puts it) | `{"type":"json_object"}` or the schema [ASK] |
| tools / tool choice | none | none |
| session | trace `sessionId` (`langfuse.session.id`) and `metadata.session_id` | `doc-<id>` |
| time | observation `startTime` / `endTime` | inside the 7-day window, before the first live call |
| usage | `usage_details` `{input, output}` | realistic token counts |
Langfuse OTel attribute names: RAW/T-25.md (observation-level attribute table) and RAW/T-28.md (`_set_observation_attrs`).

### 4.4 Step by step (if Mubit says yes)
1. **Get a clean project.** A second project or a second org with zero live calls [ASK]. An admin must do the import [DOCS L2696].
2. **Langfuse project.** A human creates it on Langfuse Cloud (agents must not sign up). Create two keys: Ingestion (write) and Viewer (for Mubit) [RAW/T-26.md].
3. **Option A, most faithful (recommended): use Langfuse's own OpenAI wrapper against a local mock.**
   - Run a tiny local OpenAI-compatible server on `localhost` that answers each request with `{"model":"gpt-6-luna","choices":[{"message":{"role":"assistant","content": GOLD}}],"usage":{...}}`.
   - Call it with `from langfuse.openai import openai`, `client = openai.OpenAI(base_url="http://localhost:PORT/v1", api_key="mock")`.
   - Pass exactly the live arguments: model `gpt-6-luna`, the system and user messages, the same `response_format`, `temperature`, plus `metadata={"langfuse_session_id": "doc-<id>", "session_id": "doc-<id>"}` [RAW/T-39.md].
   - Langfuse then records generations exactly as it records real OpenAI calls, which is presumably what Mubit's importer was built for [I]. Timestamps are real time, so no backdating is needed if the Mubit project has no live call yet.
   - No real OpenAI call and no Mubit call happen in this step.
4. **Option B: write OTLP spans yourself.**
   - POST to `{LANGFUSE_HOST}/api/public/otel/v1/traces` with `Authorization: Basic base64(pk:sk)` [RAW/T-28.md, cookbook L401-418].
   - Per chunk: a root span with `langfuse.session.id`, and a child span with:
     - `langfuse.observation.type = "generation"`;
     - `langfuse.observation.model.name`;
     - `langfuse.observation.input` (JSON string of messages);
     - `langfuse.observation.output` (JSON string);
     - `langfuse.observation.metadata.response_format`;
     - `langfuse.observation.usage_details`;
     - `start_time` / `end_time` in ns [RAW/T-25.md, mapping table and "Ingestion transformations" item 4; RAW/T-28.md].
   - Use OTLP, not the legacy REST ingestion: "The OTLP endpoint is the **only** way to set the authoritative `start_time` / `end_time` ... the legacy REST ingestion rewrites those fields" [RAW/T-28.md L393]. Legacy ingestion also stops accepting traces on Langfuse Cloud on 16 Nov 2026 [RAW/T-27.md L72; RAW/T-39.md].
   - Caveat: metadata values arrive as strings, not objects, which an importer may read differently [I].
5. **Check in Langfuse UI.** Generations show model `gpt-6-luna`, system and user messages, output, session.
6. **Mubit Import past calls.**
   - Source Langfuse, host, Viewer key, **Check key**: newest call and `gpt-6-luna` should appear.
   - Window 7 days, tick the consent box, **Start import**.
   - Watch read / imported / skipped / tasks found. Expect exactly 1 task named "Find personal data in one ...".
7. **Prove the join.** Send 5 live calls with the identical prompt, model, format and new chunks. The same task's kept-example count must rise. If a second task appears, the fingerprints differ: stop and ask.
8. **Then train.** Gold-imported examples plus live examples; read the verdict.
- Start small: import 50 gold chunks first (one import at a time; a bad import cannot be undone in the console [I, no delete control documented]).

### 4.5 Risks
- Docs say one project per workspace [F]. Without a clean project this route is closed.
- The fingerprint may not match (output format, session), giving a split task or session leakage [I].
- The importer may skip generations it cannot parse; "skipped" counts will show it [F, DOCS L2732].
- **Backdating** traces to slip under "cut at first live call" in a used project would game the rule. Do not do it without explicit permission [I].
- Judges may see training on our own labels as bypassing Mubit's teacher; disclose it. The upside: it is exactly "graded on outcomes, not imitation", which the team pack lists as a market gap.
- A Langfuse account is needed (human sign-up); Langfuse plan limits not checked.
- Import consent: "I may share these calls with Mubit." Only synthetic data.

---

## 5. How Mubit's demos and PagerPal measure improvement

| Source | What is compared | Held-out? | Counts / stats |
|---|---|---|---|
| **latte-bench** (gateway client) [F, RAW/T-19.md] | `no-notes` vs `notes` (plus `raw-history`, optimizer), same seeds | Separate "Held-out milk" and "Held-out shape" with frozen memory; "No held-out results are used to update memory" (L208-212) | Mean best of 5 attempts across 3 matched seeds; cost to first pass. They say what it does **not** prove: "these results do not establish learning or transfer" (L14); "does not establish held-out transfer or model-weight learning" (L58) |
| **demo** (13 memory demos) [F, RAW/T-32.md L5-8, L16-26] | "with and without the stored lessons" | e.g. "Six new requests (three paraphrases, three controls), memory off and on"; "Six held-out incidents" | First-route accuracy, handoffs, wasted probes |
| **care_coordination** [F, RAW/T-33.md L204-236] | 3 arms: no memory, full memory, one lesson category ablated | Fresh executions from a frozen, hashed snapshot | Deterministic scoring, no LLM judge; win/tie/regression; marks a run `invalid` if settings differ |
| **Voice agents demo** [F, RAW/T-34.md L86-107] | Arms on the same items, incl. an oracle ceiling | "Probe wording is held out" | Pre-registered experiments; Wilson intervals; exact McNemar; A/A noise floor; append-only scoreboard; "void runs stay on it marked void" |
| **PagerPal** [F, PP app.py L50-51, L83-89; history.html L4] | Suggested vs resolved runbook on live alerts | No | "Right first time: X of N"; no baseline, no version split |

Implications for our eval harness [I]:
- **Frozen eval split by document**, never sent with full recording. Report per adapter version on the same chunks.
- **Arms on identical items:** regex, Presidio, teacher (provider), adapter vN, oracle (gold). Also "reminded" (precedents in the prompt) vs "improved" (new version).
- **Two scores side by side:** Mubit's own "Matched x% of provider answers" (imitation) and our leak rate and recall vs gold (outcome). Explain the gap.
- **Paired stats:** McNemar on per-document zero-leak, Wilson 95% intervals on leak rate, and an A/A run of the teacher twice for the noise floor.
- **Provenance per run:** prompt hash, model id, response `model` field, all response headers, version label read from console, timestamp, Served by (from console). Append-only results file; keep failed runs marked void.
- **State what is not proved:** synthetic UK English only; adapter measured via the paths available (Try models samples and served calls).
- **Adapter measurement:** we cannot force the adapter [DOCS L2681].
  - (a) Try models side-by-side for 10-20 manual eval chunks (limited calls, not stored);
  - (b) after "Served by" shows the adapter, eval calls through the live task with `x-middleware-record: metadata` (keeps fingerprint, trains nothing) [ASK whether routable], then confirm by Served by on a few recorded calls.

---

## 6. Where adapters run, export, privacy, retention

- **Hosting:**
  - [F] "Mubit will host the open models" [RAW/T-1.md L54]. Pricing "Deployment: Pay as you go: Mubit cloud; Enterprise: Mubit cloud, your VPC or self-hosted" [pricing.md L90-92].
  - [F] DPA: "production infrastructure is hosted on Google Cloud Platform (GCP) in the United States and European Union" [RAW/T-2.md L558-560].
  - [F] Sub-processors listed: GCP, Clerk (auth), Cloudflare (console CDN) [RAW/T-2.md L605-609]. [I] OpenAI, Anthropic and Google as LLM sub-processors for starter-credit calls are not listed.
- **Export:** [F] "Download your models. No export fee" [pricing.md L13]; "You own what's built" [RAW/T-6.md]. No docs page explains how. [ASK]
- **Recording:**
  - [F] "Mubit records request and reply content by default. Use synthetic data" [DOCS L115].
  - [F] Up to 32 MiB of a request and the first 4 MiB plus last 256 KiB of an answer are recorded [DOCS L3124].
  - [F] Headers can lower recording, never raise it [DOCS L3057-3060].
- **Training on customer data:**
  - [F] DPA: "Mubit shall not use Customer Content or Customer Personal Data for model training or product improvement unless Customer expressly agrees in writing" [RAW/T-2.md L109-112]. The TOS says the same [RAW/T-3.md L103-108]; the privacy policy repeats it for processor data [RAW/T-4.md L30-34].
  - [F] Aggregated or de-identified use is allowed [RAW/T-2.md L111-115].
  - [I] Per-task adapters for the customer count as providing the Service under the customer's instructions. The ban reads as covering Mubit's own or shared models. [ASK] how they reconcile it.
- **Retention:**
  - [F] DPA: delete Customer Personal Data within 90 days of termination [RAW/T-2.md L351-353]. TOS: other content per "Mubit's documented retention schedule" [RAW/T-3.md L286-289], which we did not find published.
  - [F] The console lists calls for up to "Last 30 days" [DOCS L2420]. That is a filter, not a stated retention period.
- **Certifications conflict:**
  - [F] Homepage: "SOC 2 Compliant", "ISO 42001 Certified", "ISO 27001 Certified", "HIPAA Compliant" [RAW/T-5.md L81-89].
  - [F] DPA: "Mubit is SOC 2 Type I compliant" [RAW/T-2.md L563]; PHI only with written approval and a BAA [RAW/T-2.md L477].
  - [F] Pricing: SOC 2 / ISO 27001 / ISO 42001 "Not included" on Pay as you go [pricing.md].
  - [I] For Veil's pitch: say "synthetic data only during the event; enterprise path = VPC or self-hosted plus DPA", not "Mubit is certified X".

---

## 7. Recommended training plan for T1

Clock: 00:00 UTC = 01:00 BST until clocks go back at 02:00 BST on Sun 25 Oct. The 00:00 UTC Sunday reset is 01:00 BST Sunday.

**Round 0: freeze and pilot (now, Sat 01:00-02:30 BST)**
- Freeze the T1 system prompt (with entity definitions, ordering rule, empty-list rule, the word JSON), `response_format` and model.
- Pilot 50 eval chunks each on `gpt-6-luna`, `claude-haiku-4-5`, `gemini-3.8-flash` with `x-middleware-record: off` (no task is created, DOCS L3058). Score recall and leak vs gold. Pick the teacher with the best recall at acceptable cost.
  - [I] Prefer the teacher's quality over price: the adapter inherits its errors.
- Send 10 recorded calls with the frozen setup. Confirm one task with the right name, and read Settings (threshold?).

**Round 1: v1 (Sat 02:30-04:00 BST send; training when Mubit allows)**
- 300-500 chunks from 150-250 documents, all 10 types, mixture from 3.4, `session_id = doc-<id>`, `temperature 0`.
- Send as one burst within the in-flight cap. Respect `retry-after`.
- Log `mreq_`, all headers, `usage`, response `model`.
- Watch the count, `Reviewing examples`, `Training`, `Testing`. If `examples too long`, cut chunks to 600 tokens and resend new chunks (new examples are required; no retry).

**Round 2: corrections and v2 (Sat 09:00-18:00 BST)**
- Read v1's verdict. Run the eval harness: teacher vs v1 (Try models sample; Served-by calls).
- Corrections, in this order of preference:
  1. The console mechanism confirmed at office hours: correct the reply on the request. Find it via Requests, Session filter `doc-<id>` (deep link from our UI); note the console id differs from `mreq_`.
  2. Rate the teacher's wrong replies **Bad** [DOCS L2449] (hoping they leave the kept set [ASK]).
  3. Fallback "precedents": put up to 3 short corrected examples (under 300 tokens) in the **user** message of later calls. The teacher then answers correctly, Mubit records it, and the next version learns it. The system prompt stays frozen.
- Send 200-400 fresh chunks from new documents, with the correction patterns (e.g. CUSTOM ids, "Kind regards, Jo"), to reach `Next: a new version after {need} new examples`.
- If `Waiting: today's training limit`, stop sending and prepare round 3.

**Round 3: v3 after the reset (Sun 01:00-05:00 BST)**
- At 01:00 BST Sunday (00:00 UTC) the daily limit resets. Send the queued fresh batch plus corrections immediately.
- Re-run the eval if a version passes. Re-record the video only if the numbers improve. Freeze at 05:00.

**Optional gold track (parallel, only after Mubit says yes):** section 4.4 into a clean project, starting with 50 gold chunks. Report it as a separate arm ("trained on outcomes").

Weekend volume: about 1,000-2,000 recorded T1 calls in total [E]: under $0.40 on luna, under $4 on Haiku in tokens, plus runs if billed.

---

## 8. Questions for Mubit office hours (ordered)

1. **Corrections:** What exactly happens when we correct a reply in the console? Does the corrected answer replace the provider answer as the training target, and does it become one of the "required test cases" (`Passed {a}% of {n} required test cases · needs 100%`)? Is there an API so our UI can submit the correction with the `mreq_` id? Does "Rate this reply: Bad" remove the call from kept examples?
2. **Serving:** After a version passes, are live calls served by the adapter automatically? How can our app tell per call (header, body `model`, anything)? Can a call opt out, so we can measure the teacher? Are `x-middleware-record: metadata` calls still routed to the adapter?
3. **Training limits:**
   - How many trainings per UTC day, how long is the pause, and how long does one training take?
   - Can an admin raise the 25-example first-training trigger in Settings?
   - Does a training use all kept examples present when it starts?
   - What is `{need}` for the next version?
4. **Grading:** How is "matched" computed for a JSON answer (exact, per field, semantic)? What is `{need}%`? What share of sessions is held out?
5. **Length:** What is the token limit behind "examples too long to train on" (request plus answer)?
6. **Base model:** Which open model and adapter type or size? Does the adapter honour `response_format` at serving? Would `json_schema` strict be safer than `json_object`?
7. **Import of gold labels:**
   - Can we get a second project (or org) with no live calls?
   - Does the importer take the output format from Langfuse `metadata.response_format`, and the session from Langfuse `sessionId` or `metadata.session_id`?
   - Are imported outputs used as targets as-is?
   - Is this allowed for judging?
   - Is the cut based on observation start time?
8. **Curation:** Why might a call not be kept (duplicates, errors, length, JSON validity)?
9. **Starter credit:** How much is it, what is the in-flight cap `{n}`, and are "runs" billed to hackers?
10. **Eval traffic:** Is sending the eval split with `x-middleware-record: off` (teacher baseline) or `metadata` (adapter) acceptable under "every call through Mubit"?
11. **Try models:** How many calls per day for hackers? Can the 3 adapter starts per UTC day be raised for the demo morning?
12. **After the event:** How do we download the adapter ("Download your models")? Where does it run (GCP US or EU)? How long are recorded calls kept, and how do we delete our project data?

---

## 9. Sources (raw files)
- Mubit docs full text: `DOCS`, `RAW/T-7.md`; docs index `RAW/T-8.md`.
- middleware.now `RAW/T-1.md`; DPA `RAW/T-2.md`; TOS `RAW/T-3.md`; privacy `RAW/T-4.md`; mubit.ai home `RAW/T-5.md`; agents.md `RAW/T-6.md`; mubit.ai/llms.txt `RAW/T-30.md`; pricing.md `RAW/T-31.md`.
- PagerPal code `RAW/T-9.md` (llm.py), `T-10` (triage.py), `T-11` (app.py), `T-12` (store.py), `T-13` (alert.html), `T-14` (history.html), `T-15` (conftest.py), `T-16` (test_llm.py), `T-17` (README).
- latte-bench: model study and prices `RAW/T-18.md`, README `RAW/T-19.md`, provider code and .env `RAW/T-20.md`.
- Mubit demos: `RAW/T-32.md` (demo), `T-33` (care coordination), `T-34` (voice agents), `T-35` (loop demo), `T-36` (SRE demo), `T-37` (mubit-cli), `T-38` (plugins).
- Prices: Anthropic `RAW/T-21.md`, OpenAI `RAW/T-22.md`, Gemini `RAW/T-23.md`.
- Langfuse: openai.py `RAW/T-24.md`, OTel mapping `RAW/T-25.md`, RBAC and key permissions `RAW/T-26.md`, deprecated API migration `RAW/T-27.md`, data-migration cookbook `RAW/T-28.md`, context7 excerpts `RAW/T-39.md`, DeepWiki note `RAW/T-40.md` (summary; one claim corrected against source).
- Banyan Sapling card `RAW/T-29.md`.
- Mubit SDK: `SDK/client.py`, `SDK/learn/_client.py`.
- Not found or blocked: base model, adapter size, training limits, matching metric, served-by signal, correction API; `docs.mubit.ai/api-reference/control-http` returns 404; GitHub code search unavailable (no token).
