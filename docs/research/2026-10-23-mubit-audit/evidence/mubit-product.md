# Mubit product mechanics (read first-hand, 2026-10-23 ~17:00 BST)

Sources: https://docs.mubit.ai/llms-full.txt (saved: scratchpad/mubit/docs-llms-full.txt), https://mubit.ai/agents.md, https://mubit.ai/llms.txt, PyPI mubit-sdk 0.13.2, npm @mubit-ai/sdk 0.13.2 / 0.14.0-rc.1 (2026-09-03), GitHub MubitLabs.

## Facts from the docs (gateway product)
- Gateway: base URL + Mubit key swap, OpenAI / Anthropic / Gemini / compat (openrouter, groq, together, mistral). Server-side only (no CORS).
- Task = same instructions (system prompt) + tools + tool choice + output format + model. Numbers/dates/IDs in instructions tolerated; other varying words split tasks. Model date suffixes and -latest ignored.
- Session = metadata.thread_id > session_id > conversation_id > Anthropic metadata.user_id > Responses prompt_cache_key; else derived from instructions + first user message. Test cases set aside BY SESSION.
- Kept examples: not every call kept. First training at 25 kept examples by default ("the count your console shows is the source of truth").
- Test result per version: Passed / Below target ("Matched {a}% of your provider model's answers on {n} test cases, needs {need}%") / Malformed tool calls / Prompt only (base model + prompt did as well) / Not tested.
- KEY: adapters are graded against the PROVIDER MODEL's answers, i.e. imitation (distillation). Docs never mention grading against human labels.
- Waits: daily training limit (resets 00:00 UTC), pause between trainings, "Waiting for more examples k of need". No retry button; recovery = new calls with new messages.
- Can't train reasons include "examples too long to train on".
- Try models: daily per-org call limit, 3 adapter starts per org per UTC day, first start takes minutes (page re-sends every 15 s for up to 20 min).
- "There is no Mubit model ID: you can't send a call to an adapter by naming it as the model." But Requests has a "Served by" column and filter, and the homepage promises "switching over only when it does better". So serving by adapter exists in the design, not exposed in public docs.
- Feedback documented: only "Rate this reply: Good or Bad" per call in the console Requests panel. No public API for it in docs.
- Settings page under Set up appears once training is on for the workspace (admins change it). Threshold may be configurable there (unknown).
- Import past calls: from Langfuse / Braintrust / Pydantic Logfire, read-only key, 7/14/30-day window, ONLY calls before the project's first live call ("Cut at the project's first live call"). One project per workspace.
- Headers: x-middleware-store:false or x-middleware-record: metadata|off (off also drops the task fingerprint). Response: x-middleware-request-id (mreq_ + 32 hex, sortable by time).
- Records up to 32 MiB of a request and first 4 MiB + last 256 KiB of an answer. Starter credit: body <= 8 MiB, plain JSON.
- Starter credit models named in docs: gpt-6-luna, claude-haiku-4-5, gemini-3.8-flash.

## Facts: site vs docs drift
- mubit.ai/agents.md (marketing, "Agentic runtime calibration") describes memory + outcome attribution + prompt/skill improvement + task models, and links to docs.mubit.ai/patterns/outcome-attribution-loop, /patterns/self-optimizing-prompts, /sdk/llm-providers, /sdk/framework-integrations. All four return 404 today. The docs now only cover the gateway + adapters.
- The older "memory + continual learning" product still ships: PyPI mubit-sdk 0.13.2 ("Durable memory + continual learning for AI agents"), npm @mubit-ai/sdk 0.13.2, next 0.14.0-rc.1 (2026-09-03). Surface: remember / recall / get_context / checkpoint / reflect / record_outcome / record_step_outcome / feedback / surface_strategies / optimize_prompt / activate_prompt_version / skills (create/optimize/activate/diff), Projects + Agent Cards. Endpoints under /v2/control/* and /v2/core/*. mubit.learn = zero-config instrumentation that auto-ingests, auto-injects lessons and auto-reflects; feedback(good=True/False | score) credits recalled memory entries.
- GitHub MubitLabs: mubit-cl-bench (4 stars, pushed 2026-08-23), mubit-cli (binaries), plugins ("persistent, typed, self-improving memory for Claude Code and the Codex CLI", pushed 2026-09-29), claude-plugins (archived).

## Inferences (ours)
- I1. Default training = distillation from the provider model. A human correction that disagrees with the provider would LOWER "Matched X%" unless the hackathon build grades on corrections. So "corrections become model updates" needs a mechanism we must confirm at kickoff. Most likely candidates: (a) Bad rating removes a call from kept examples (negative curation), (b) an edit-the-reply feature, (c) a corrections API added for the event.
- I2. Fallback that needs no new Mubit feature: improve the TEACHER. Put retrieved past corrections ("precedents") into the user message (never the system prompt, so the task stays one task). The frontier model then answers correctly, Mubit records those answers, and the adapter distils the corrected behaviour. Fast path = instant (precedent retrieval), slow path = adapter update. This is exactly the "memory + task model" loop on Mubit's own homepage.
- I3. Second fallback: Import past calls with corrected outputs written to Langfuse. Blocked by "cut at first live call" unless used in a fresh workspace before any live call. Hacky; ask first.
- I4. Mubit is mid-pivot from "agent memory" to "gateway + task adapters". The founders will value a project that reunites both halves ("runtime calibration"): corrections land in memory immediately and in the adapter on the next version.
- I5. Since serving by adapter is not public, a router in our app can only be simulated unless the event build exposes it. Honest framing: "the router is the production step".

## Own idea checks (orchestrator, ~17:10)
- Adverse media / negative news triage (KYC/AML):
  - UK financial crime compliance cost £38.3bn in 2023, 66% of it customer due diligence (LexisNexis Risk Solutions + Oxford Economics, survey of 254 UK firms). https://risk.lexisnexis.co.uk/about-us/press-room/press-release/20240718-fighting-financial-crime-and-fraud  [vendor that sells the fix: weight lower]
  - Screening false positives 85-95% (Facctum report, via zyphe.com 2026-03-26, vendor-reported, not adverse-media specific). Sanctions screening FP up to 99% (Capgemini POV 2025). Quantifind 2021: legacy negative news finds wrong people or irrelevant mentions (witness, victim, keyword in other context).
  - Taktile KYBench (Apr 2026, updated 2026-09-07): 47 businesses, 31 agent configs; 69% of AI false positives = over-flagging real but marginal evidence (allegation stage, too old, peripheral role); entity confusion 1.5%; 0% hallucination; "A human review queue built around this reality should focus on threshold adjudication". Mid-size bank estimate ~200,000 investigator-hours/yr at 30 min per investigation. https://labs.taktile.com/benchmarks/kybench
  - => The frontier model's error is calibration to the firm's risk appetite, which is exactly what analyst corrections teach. Strong "corrections are the asset" story.
  - Data: Webz.io adverse media news (HF rangeva/adverse-media-dataset, weekly ~1,000 articles, TOU: academic/research/journalistic). Safer: synthetic articles about fictional people (no defamation, no real PII through Mubit's recorder).
- Complaints: HF CFPB/consumer-finance-complaints, CC0, 1M-10M rows, product / sub-product / issue labels (US, labels chosen by complainants, noisy).
- Contact-centre QA with calibration:
  - COPC Global Benchmarking 2022 (QA): 89% of centres have a calibration process; 79% use speech analytics; ~1/3 still fully manual QA. https://cx.copc.com/hubfs/Global%20Benchmarking%20Series%202022_Contact%20Center%20Quality%20Assurance.pdf
  - QATC survey summer 2026: 44% hold calibration sessions monthly, 59% last one hour, most review 2 calls per session. https://qatc.org/newsletter/qatc-survey-results-summer-2026/
  - Call Centre Helper poll 2016 (n=113): 68% evaluate 2% or less of interactions. Telonic (2026-09-30) says the 1-2% figure has no measured source; measured: about 5-6 evaluations per adviser per month. https://telonic.ai/en/research/conversation-quality (Telonic sells auto-QA: incumbent signal).
  - Incumbents: Tethr, MaestroQA, Observe.AI, Level AI, Zendesk QA (Klaus), Telonic.

## Middleware (the actual hackathon product), read 2026-10-23 ~17:05 https://middleware.now/
- "Middleware generates lightweight model updates from your calls and feedback. Built for fast refresh as your workload changes." $100 free credits on the waitlist.
- Placement: between app and model calls, BEFORE the router (OpenRouter / LiteLLM still handle provider access). Open models hosted by Mubit.
- "Middleware uses application memory to refresh task-specific model behavior." Memory records corrections, conventions, policies, examples of completed work. "Memory remains the source of record."
- Research design: shared model component + a generator that produces a small app-specific update + a change detector that monitors memory and triggers a refresh "when enough has changed". Example given: escalation policy change updates escalation behaviour.
- Honest limit on their page: demonstrated path uses a brief fitting step before generating the update; generating updates for a new app without fitting is still under development.
- Founders' examples of recurring corrections: a document parser misreading the same field; a support tool needing the same wording changed. These will be the most crowded ideas.
- Implication: corrections probably enter via memory (the memory SDK surface: remember / record_outcome / feedback) or a new event-specific path. Ask at kickoff. Our two-speed design (correction -> memory now -> weights next refresh) matches their architecture word for word, and lets us show "reminded vs improved".
