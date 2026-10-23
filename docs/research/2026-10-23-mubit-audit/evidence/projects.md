# Projects built with Mubit (agent P)

Researched 2026-10-23, evening. Sources: LinkedIn posts (via exa fetch), dev.to, GitHub READMEs and code (api.github.com and raw.githubusercontent.com), event pages. Evidence ids are `P-n` in `evidence-P.csv`, and raw pages are in `../raw/P-*.md`. Placements come from the builders' own posts unless a second source is named. Where a placement is not stated anywhere, it says "none stated", never a guess.

## 1. Summary table

| # | Project | Event (date) | Placement | One-line idea | Mubit usage | Demo moment | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | **Rentry** | Vercel Zero to Agent: London (2 May 2026, solo, 5 h) | 2nd main (London pool) **+ Mubit bonus prize** (self-reported); 2nd Bright Data track (sponsor post) | Rental agent for London that remembers your preferences across sessions | Memory: `/v2/control/ingest` (prefs as `intent: fact`, keyed by username) + `/v2/control/query` whose `final_answer` becomes the "remembered" line. `@mubit-ai/sdk` in package.json, raw HTTP in code | Second login: "Mubit recall: 14 preferences", plus a "remembered from last session" badge on the top card | P-1..P-9 |
| 2 | **joanie** | #popthebubble (June 2026, 36 h, 80+ builders) | **2nd** | AI phone receptionist for service businesses, after hours, with CRM handoff | "remembers customer context through Mubit" (operational/agent memory). API not public | Live call demo; team claims a paying customer, an LOI and a $5K deposit during the event | P-14..P-16 |
| 3 | **CafeTwin** | Unicorn Mafia "To The Americas" (25-26 Apr 2026, 24 h, 47 teams) | **4th overall + Render track** | Cafe CCTV → operational patterns → one layout change, checked for geometry | (a) memory of recommendations + operator accept/reject, stable fingerprint `item_id`s, activity recall with query fallback; (b) **agent registry + prompt versioning** (auto new prompt version on drift) | "seen 3× before" chip showing the prior recommendation and what the operator decided | P-17..P-21 |
| 4 | **Frame Mog** | Unicorn Mafia "To The Americas" (Apr 2026) | none stated | Real-time AI pose coach in the phone browser (AR outline) | Every accepted or skipped pose stored; suggestions adapt per user. Also Devin judged a live photo contest "with Mubit underneath" | "By session three, the suggestions had visibly adapted to that user's taste", shown live | P-10..P-12 |
| 5 | DEMEO (team ZBS) | Unicorn Mafia "To The Americas" (Apr 2026) | none stated | "AI office" that executes startup tasks with structured outputs | `mubit.learn.init()` auto-instrumentation (optional). The post describes Mubit vaguely ("execution layer") | none described | P-22, P-23 |
| 6 | AmericasAR | Unicorn Mafia "To The Americas" (Apr 2026) | none stated | AR cards anchored to your own objects (phone camera + voice) | Mubit mirrors the SSE event stream into a "live Mubit dashboard" for judges (peripheral) | Event stream shown next to AR view | P-35 |
| 7 | Delta | Zero to Agent London (May 2026) | did not win (builder says) | Predicts how each team member reacts to a manager's decision | "memory layer that learns your specific org over time" | none described | P-27 |
| 8 | Remy | Zero to Agent London (May 2026) | none stated | Voice memo about a new contact → structured follow-up context | Described as "voice-to-structured-data layer" (likely a misread of the product) | none | P-28 |
| 9 | Trial of Astronar | probably Zero to Agent London (repo created 2 May 2026; event not named) | none stated | Agentic dungeon-crawler RPG | Optional Mubit retrieval/writes for "Prophecy Fragments" (tactical lessons) | none | P-33 |
| 10 | Autonomous Claims Operator | {Tech: Europe} London (27 Jun 2026) | none stated | 3-agent logistics claims back office on Attio | "Mubit logs what resolved and why. System gets sharper every run." Repo link returns 404 | none | P-24 |
| 11 | EditDNA Rank Studio | {Tech: Europe} London (Jun 2026) | none stated | Copy the "editing DNA" of a ranking video to make a new one | Short/episodic/long-term memory written on approve, reject and feedback | none | P-29 |
| 12 | LegacyDecoder | {Tech: Europe} London (Jun 2026) | none stated | Legacy code → living docs in Notion | Mubit used as a persistent embedding cache / semantic search | none | P-30 |
| 13 | Patronus AI | {Tech: Europe} London (Jun 2026), Open Innovation | none stated | Meme "guardian" browser extension with voice | **Minima** picks the cheapest capable model per call | none | P-31 |
| 14 | Trace | {Tech: Europe} London (Jun 2026) | none stated | Security/trust layer for agent actions | Mubit "intercepts inter-agent messages". README calls it demo-level | none | P-32 |
| 15 | Guardrail Agent | event unknown (repo created Jun 2026, v0/Vercel) | none stated | Compliance scan of GitHub repos against GDPR/SOC 2 and others | Mubit as decision/audit log + approved-exception memory | none | P-34 |
| 16 | Sambung | Slack Agent Builder Challenge (online, Jun 2026), **not** {Tech: Europe} | none found | SMS from frontline workers → Slack routing/escalation + Linear | "site memory": learns which equipment/phrases meant real incidents | Example "Press 4 stopped. Smell of burning." | P-25 |
| — | ClearNest | startup, not a hackathon entry | — | Voice agent for elderly parents' affairs | Plans only (future tense) to add Mubit to an ElevenLabs pipeline | — | P-13 |
| — | Flash | {Tech: Europe} London (Jun 2026) | 3rd overall, 1st Superlinked, 2nd n8n | Active AI participant in Google Meet | **No evidence of Mubit use** (built with Superlinked, n8n + Gemini, SLNG) | — | P-26 |

## 2. Details for each project

### Rentry (the clearest Mubit win)
- **Event / placement:** Vercel Zero to Agent: London, 2 May 2026. Solo builds, 5 hours, about 100 builders. The builder says it "won 2nd place in main track + BONUS Mubit track" (P-2). The Bright Data sponsor lists it as 2nd in the Bright Data track, for $500 in credits (P-3). These two claims do not conflict: the event's Mubit prize ($100k credits) went to "one of the top 3" for "the best build on the Mubit platform" (P-4).
- **Problem and users:** renting in London means stale listings and re-explaining what you want every time. The users are renters.
- **What Mubit did:** long-term preference memory. The code (P-7) writes preferences with `POST /v2/control/ingest` (items `{id, intent: fact|lesson|rule, text}`, run_id = username). It reads them with `POST /v2/control/query`, uses the evidence for the "Mubit recall" block and shows `final_answer` as the "remembered from last session" line. There is a local JSON fallback, and `@mubit-ai/sdk ^0.7.0` is in package.json.
- **Demo moment:** a returning user logs in, the trace shows "🧠 Mubit recall — 14 preferences", and a "Mubit · 2 sessions ago" pill sits on a checkmark. The README says "the one that makes the room laugh" (P-6). A rent-hike beat follows: a new Vercel Workflow run whose memory still carries over.
- **Stack:** Next.js 16, Bun, AI SDK on Vercel AI Gateway, Vercel Workflow, Vercel Postgres, Bright Data, Mubit. Repo: https://github.com/shumengliu/zero-to-agent (app in `apps/rentry`). Live: rentry-zero-to-agent.vercel.app.
- **How it was pitched (PITCH.md, P-8, P-9):** one verb for each sponsor ("Bright Data SEES / Vercel RUNS / Mubit REMEMBERS"). "Mubit's job is to be loud about being silent": a branded badge on every remembered item, three verbal namedrops, and an optional log strip like `mubit.recall("shumeng") → 14 prefs · 240ms` for technical judges. The demo user was pre-seeded with about 6 months of fake history, and the key line was hardcoded as a fallback, so part of the memory moment was staged.
- **What judges said:** no judge quote found. The organiser commented "congrats on winning". The builder claims 60%+ of the audience found it relevant (P-1).

### joanie
- **Event / placement:** #popthebubble, June 2026. 2nd place out of 80+ builders in 36 h (P-14). Judges included "OpenAI devs and Andreessen Horowitz scouts" (P-16). Sponsors were Cognition, Mubit, Accelerate ME, Zuba and The Residency.
- **Problem and users:** service businesses miss calls after hours. joanie answers, remembers the caller's context, captures the job and hands it to the CRM.
- **What Mubit did:** "remembers customer context through Mubit" (operational/agent memory). The exact API is unknown and no public repo from June was found.
- **Demo moment / traction (self-reported, not verified):** a paying customer, a white-label partnership, an "LOI with minimum 20 licenses (approx. $440K)" and a $5K Stripe deposit by Sunday (P-15). Commenters wrote "It was an incredible demo".
- **Stack:** ElevenLabs (Procedures alpha), Twilio, Mubit, Supabase, Vercel/v0, Lovable (deck).
- **Note:** the same team has a repo `a new repo` created today, so they seem to be competing at Night Shift (P-48).

### CafeTwin
- **Event / placement:** Unicorn Mafia "To The Americas" (hosted with Encode Club, London, 120 builders, 47 teams). 4th overall and winner of the Render track (P-17). No Mubit-specific prize is mentioned.
- **Problem and users:** cafe operators. Video → KPI engine (queue obstruction, crossings, detours) → one layout change at a time, with a digital twin simulator.
- **What Mubit did:** (1) memory of patterns, recommendations and operator accept/reject, written to `/v2/control/ingest` with stable fingerprint `item_id`s for dedup, recalled through `/v2/control/activity` with `/v2/control/query` as a fallback, and ingest jobs polled for read-after-write (P-18). (2) Registry of 3 PydanticAI agents with their system prompts; a prompt change automatically minted a new prompt version (P-19). The author: "The agent registry alone is worth the price of admission."
- **Demo moment:** a "seen 3× before" chip showing the prior recommendation and the operator's decision.
- **Friction they reported (P-20, P-21):** inconsistent response shapes, unclear docs on activity vs query, a 422 on missing fields, and no SDK used. Every write was mirrored to JSONL, so the offline demo "can't fairly attribute" its results to Mubit.
- **Stack:** PydanticAI, Logfire, Render, Vercel, Devin CLI. Code link "in the comments" (not opened).

### Frame Mog
- **Event:** Unicorn Mafia "To The Americas", Apr 2026. No placement stated (P-10, P-12).
- **Idea:** a pose coach in the phone browser. You get AI pose suggestions, match an AR outline and shoot.
- **What Mubit did:** stored every pose a user accepted or skipped and fed it back into recommendations. It also ran under a Devin agent that judged a live $100 photo contest during the build (200+ photos).
- **Demo moment:** "By session three, the suggestions had visibly adapted to that user's taste". The team showed this live.
- **Stack:** Pydantic, Render, Devin, Mubit, Flux, Stripe (live payments). The team claims 2,000+ impressions in 24 h.
- **Follow-on:** the same builder is moving Mubit into ClearNest, a voice agent startup, and built Sambung (below).

### Sambung (lead corrected)
- The lead said "Sambung / team Flash, {Tech: Europe} London". That is wrong. Sambung was built for the **online Slack Agent Builder Challenge** by the Frame Mog builder (P-25). **Flash** is a different team that came 3rd at {Tech: Europe} London, and no source says Flash used Mubit (P-26). A Mubit staffer only congratulated them.
- **Sambung idea:** workers text one number, the agent classifies, routes to Slack, escalates and creates Linear issues. Mubit "site memory" learns local equipment names and what turned serious before. No placement found.

### Smaller or vague uses (no placement found)
- **DEMEO / ZBS:** `mubit.learn.init()` drop-in (P-23). The post misdescribes Mubit as an "execution layer" (P-22).
- **Autonomous Claims Operator** (Tech Europe): Mubit "logs what resolved and why". The GitHub repo is gone (P-24).
- **Delta, Remy, Trial of Astronar** (Zero to Agent): org-specific learning, voice-to-structured data (misread) and RPG lessons (P-27, P-28, P-33).
- **EditDNA, LegacyDecoder, Patronus AI, Trace** (Tech Europe): approve/reject memory, an embedding cache, Minima model picking and agent-message interception (P-29..P-32). Mubit offered **Minima** at this event and gave credits to finalists, but no Mubit-specific track was found (P-49).
- **Guardrail Agent, AmericasAR:** audit log/exception memory, and an event-stream HUD (P-34, P-35).

## 3. Mubit's own demos (what they showcase)

Note: the GitHub org `MubitLabs` now redirects to `mubit-ai`. In every demo below, Mubit shows the same "with vs without" comparison on held-out cases and counts calls, tokens and dollars.

| Repo | Use case | What Mubit does | "Improvement" shown |
|---|---|---|---|
| `demo` (P-36) | 13 small agents: support routing, supply-chain recovery, care coordination, on-call triage, policy adjudication (bi-temporal), team review pipeline, **prompt self-tuner**, lesson consolidation, checkpoint/restore, data analyst, IT helpdesk, SOC triage, code reviewer | remember / reflect → lessons, `record_outcome` with step attribution, checkpoints, guardrails, prompt + skill optimisation, events | Teaching phase, then new cases run with no memory, with full memory, and with one lesson removed; reports accuracy, handoffs, wasted probes |
| `mubit-harvey-lab` (P-37) | Harvey LAB legal benchmark (1,027 tasks) | Memory from zero on GPT-5.4, with reflection every 8 tasks | 83.0% vs 82.4% (+0.6), a 429–347–251 task record, +5.7 on repeated firm-knowledge tasks. Small but positive learning curve |
| `mubit-sre-demo` (P-38) | 5-agent SRE fleet, 12 incidents | Approved fix stored as a runbook lesson. On a repeat incident it is recalled, so the probes are skipped. `record_outcome` adjusts the lesson's confidence | Repeat incidents need 2 fewer LLM calls, or **zero** in the standalone loop. UI shows LLM calls, tokens and $ per resolution |
| `Mubit-x-Voice-Agents-Demo` (P-39) | Callback voice agent that should remember the caller | **Keyed lookup by caller** (p95 27 ms) rather than semantic query (152 ms) | Prior-call questions answered correctly: 87.2% vs 10.9% with no memory; the oracle scores 89.9% |
| `mubit-bsm-demo` (P-40) | Radio spectrum monitoring with concept drift | `recall` before each report, `remember` (upsert) after it, for a transmitter registry | Three arms (off / context replay / on): the score climbs while prompt size stays bounded; replay cost grows |
| `mubit-loop-demo` (P-41) | Expense-report agent + support chat (fictional products) | Stores lessons learned from API rejections and escalation notes; reports reuse | Cold ticket → escalation; warm ticket of the same kind → answered first time. Lesson board + live SDK call feed |
| `mubit-stulife-bench` (P-42) | StuLife lifelong-learning benchmark | Memory callback in the harness | 2.0× score for gpt-5.5 (394 vs 197 of 939) |
| `mubit-cl-bench` (P-43) | Continual Learning Bench | Assistive memory | Vendor claims ranks #1–#3; it is the vendor's own claim |
| `meetingcrew-demo` (P-44) | Notion meeting → action items (listener/router/escalator) | Outcomes (done / missed / reassigned) → **prompt-improvement proposals** shown as diffs; a human approves or rejects in Notion | Prompts change based on real outcomes |
| `latte-bench` (P-45, newest, Oct 2026) | Simulated latte-pour planning | **Gateway**: `MUBIT_BASE_URL=https://api.mubit.ai/openai/v1/` next to a frontier route | With vs without notes; helps some models and hurts others |
| `e1daru/pagerpal` (P-46) — **Night Shift rehearsal "test team" entry** (the repo says so; account `e1daru` is probably the host Eldar Utiushev, which is an inference) | On-call alert → runbook + first 3 steps | Anthropic client pointed at `api.mubit.ai/anthropic`; each suggestion shows its `x-middleware-request-id`; the engineer **corrects in the Mubit console** → model update for the triage task | `/history` shows whether each suggestion was right, so the team "sees the updates working" |

## 4. Patterns

**Domains so far.** Consumer personalisation (renting, photo poses). Voice and phone agents (joanie, ClearNest, Remy, Sambung over SMS). Ops and back office (cafe layouts, logistics claims, frontline incidents, CRM). Dev and security tooling (legacy code, agent security, compliance). Voice plus memory comes up again and again, and Mubit staff publicly called self-learning voice agents "a huge differentiator".

**The central Mubit feature in past wins was cross-session memory of user feedback.** The pattern is accept/skip (Frame Mog), accept/reject (CafeTwin), or stated preferences (Rentry, joanie), recalled on the next session. CafeTwin also used the prompt registry and versioning. Nobody used `record_outcome`, lessons or reflection explicitly. Nobody used the gateway, because it did not exist before September–October 2026.

**What made the placed projects stand out:**
1. **A visible before/after memory moment inside the demo.** Examples: "remembered from last session" + "Mubit · 2 sessions ago" badge (Rentry), the "seen 3× before" chip (CafeTwin), "by session three" (Frame Mog). Projects that used Mubit as invisible plumbing (embedding cache, event HUD, "execution layer") have no placement on record.
2. **Each sponsor gets one clear role with a visible artifact.** Rentry's PITCH.md is an explicit playbook: one verb for each sponsor, branded badges, verbal namedrops, a log strip of real API calls for technical judges.
3. **Real users or money during the event:** joanie's customer and LOI, Frame Mog's live contest and payments, Rentry's audience poll.
4. **A simple stack and a demo that cannot break:** a pre-seeded returning user, cached data, JSONL/local fallbacks, a hardcoded "money line".
5. **A real recurring job** where memory obviously matters (repeat renters, repeat callers, repeat cafe patterns).

**What Mubit itself showcases**, and so likely rewards: (a) **with vs without arms** on held-out cases, with paraphrases and controls; (b) **counted savings** (LLM calls, tokens, $ per resolution, latency); (c) a learning curve over time, including through a **drift boundary**; (d) a human correction or outcome that changes later behaviour, with an audit trail (request id, history page, approve/reject diffs). Night Shift judging is "Use of Mubit. Show a correction turning into a model update in your demo." (P-47). Every project must route its LLM calls through the gateway.

**Not yet done in any past hackathon project (gaps for the new model-update product):**
- No project has shown a **correction turning into a model update**. All past projects were memory or prompt-injection era.
- No project has shown **adapter vs frontier side by side** (quality, cost, latency) for the same recurring task. That is the "Own your intelligence layer" track.
- No project has shown **fast refresh under drift** (new customer, domain or schema) with updates keeping pace. Mubit's own BSM and data_analyst demos model this, but no hackathon team has.
- No **in-app correction UX** that sends feedback tied to the `x-middleware-request-id`. Even Mubit's PagerPal makes the user correct in the Mubit console. A one-click "fix it" in the product's own UI is still open.
- **Voice plus adapters** (latency budget on a voice turn served by a small task model) is untouched. Voice was the strongest domain in the memory era, and Mubit's voice demo stresses the 800 ms budget.
- **Banyan Sapling** (verdict model) is only just appearing in tonight's projects.

**Already being built tonight:** omitted from the public repo (other teams' in-progress work).


## 5. Not found / limits
- No judge quotes about Mubit were found for any project. Feedback seen is only from organisers and commenters.
- No public repo for joanie (June), Frame Mog, CafeTwin (the link is only in a LinkedIn comment, not opened) or the Claims Operator (404).
- Not found: projects using Mubit at other events (Devpost, X). Searches on X/devpost returned nothing relevant. GitHub code search needs auth, so repo search on "mubit" in name, README and description was used instead. The GitHub API rate limit was hit late in the run, and the remaining READMEs were read via raw.githubusercontent.com.
- Placement claims for Rentry, joanie, CafeTwin and Flash come from the teams themselves. Only Rentry (Bright Data post) and Flash (techeurope.io page) have a second source.
