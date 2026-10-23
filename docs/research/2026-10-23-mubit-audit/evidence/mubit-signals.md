# Mubit: company, people and public signals (agent M)

Date: 2026-10-23 (Night Shift starts tonight). Boundary: company, people, public output. docs.mubit.ai and competitors were not read.
Evidence ids (M-n) point to rows in evidence-M.csv; raw page files are raw/M-n.md (different numbering).
Tags: **[F]** = fact seen in a source (evidence id). **[I]** = my inference. Evidence: `evidence-M.csv`. Raw pages: `raw/M-*.md`.
Source weight: mubit.ai, Hugging Face, GitHub and the Luma page are primary. LinkedIn items are the founders' own claims (some saved from exa highlights only). Forbes reports company-supplied numbers. Dealroom, PitchBook and Caplight are only leads.

---

## 1. Founders and team

**Shankha (Subhra) Dutta, co-founder and CTO** [F, M-1]
- Mubit CTO since Nov 2025. Before that he was CTO at "Rice: Persistent Organisational Memory" (Sep–Nov 2025), CTO at a stealth company (Dec 2023–Sep 2025, Reading) and CTO at SwiftSkill (Valorant analytics, 2020–2023, about $202.6K raised).
- MSc Data Science at Lancaster (2019–20). Bachelor's at BIT Mesra (2016–19). Listed skills include CV, NLP, transfer learning, Go and edge AI.
- Wrote the field note "Why Request-Path Authority Matters More Than Model Choice" (signed "Shankha D", 28 Jul 2026) [F, M-13].

**Anil Peri, co-founder and CEO** [F, M-2, M-3]
- Co-founded SwiftSkill and the stealth company with Shankha. Claims SwiftSkill reached "1m+ users across 70 countries". Earlier founded ExternshipNow, which he says reached 100K users and exited (his own claim).
- MSc Management & Entrepreneurship at Cranfield. BIT Mesra. YC Startup School 2020.
- His LinkedIn headline still says "CEO @ Rice", with an unsourced "5x faster … 4.2x less tokens" [F, M-3].
- The founders have worked together since at least 2020. They went through SwiftSkill, then Rice (a wearable "private AI native device", then org memory), then Mubit [F, M-1; raw/M-11.md].
- Forbes 30 Under 30 Europe 2026, AI category. Forbes says both have "backgrounds in mathematics and computer science" [F, M-12, M-14].

**Team size: about 7** (LinkedIn company page: 5 UK, 1 US; 3 technical) [F, M-4].
- Hussein Kanji, the Hoxton partner, is listed as Non-Executive Director [F, M-4].
- Eldar Utiushev joined as "early technical staff" in May 2026. He was hired one day after they met him at their first hackathon (Unicorn Mafia). He is now a Night Shift host [F, M-5].
- Lily Jahan is a Night Shift host. A "Lily D" wrote the Minima field note. Whether they are the same person is **not verified**.
- The only open role is Founding Engineer, London, on site at WeWork, 30 Churchill Place, Canary Wharf [F, M-6]. The ad was posted on 2026-04-01 and still uses memory-layer wording ("sub-80ms retrieval", "ACL-gated shared state") [F, M-7].
- In June 2026 Shankha offered a $15K referral bonus for that role (raw/M-11.md) [F].
- HQ conflict: Hoxton and PitchBook say Aberdeen. The job ad says London (Canary Wharf). The LinkedIn enrichment says "Kita, Tokyo" (probably a data error). [F/I]

**What the founders say they care about. Phrases they repeat** [F unless marked]
- "agents have no experience" / "every run starts cold" / "systems of experience for agents". This is in both founders' LinkedIn taglines (M-8, M-1).
- "It has been reminded, not improved." Company post, Jun 2026: a note in a file does not make the model better (M-10). This is the thesis behind the pivot.
- "a set of corrections that keeps coming back. A field in an invoice. The wording in a support reply." Anil, Middleware launch, 28 Sep 2026 (M-11).
- "owning your intelligence layer" / "You own what's built" / "Your frontier models stay". From the event page and media kit (M-42, M-32).
- Shankha cares about an inspectable request path: "byte-level observability, deterministic serialization … reviewable edits", and "We would rather build the routing layer that cannot mark your requests than the one that promises it will not" (M-13).
- Shankha calls his work "unsupervised learning memory systems for AI agents" (M-12).
- The house style is rigour plus open limits. Latte Bench and the Sapling card both list what they do *not* prove (M-26, M-31). [I: they will respect honest, measured claims more than hype.]
- No podcasts, talks or interviews were found. I searched exa for founder interviews, talks and podcasts and found only LinkedIn posts and Forbes.

## 2. Funding

- **About $2.1M** "from investors including Hoxton Ventures and Heavybit". Source: Forbes 30U30 profile, dated 14 Apr 2026. The figure is company-reported ("Peri says" for the waitlist) [F, M-14].
- Hoxton portfolio page: Fund Hoxton IV, invested 2026, partners Hussein Kanji and Rishabh Kaul [F, M-15].
- mubit.ai shows Hoxton Ventures, Heavybit and Techstars logos, "and angels from Cloudflare, AWS and Mistral" [F, M-16].
- Heavybit partner Amir Zohrenejad (ex-CTO Dataherald, YC W21) promoted the team in Apr 2026 [F, M-21]. [I: he is probably the Heavybit deal lead.]
- Round label and date differ by source:
  - Nordic9, 16 Dec 2025: "to raise pre-seed … with Hoxton" (M-17).
  - PitchBook: seed, 01-Jan-2026 (M-20).
  - Caplight: seed, 14 Apr 2026 (M-18). This is probably just the Forbes date.
  - Dealroom: Techstars $120k in **Jun 2024** (M-19), which is before Mubit existed.
  - [I] Most likely there was one pre-seed/seed round of about $2.1M, closed around Dec 2025 to Q1 2026, and the Techstars cheque went to the predecessor (Rice/stealth).
- Teammate's note checked: "seed from Hoxton + Heavybit" is **confirmed**. Add Techstars and the angels. The amount is only company-reported.
- Traction claim: "nearly 1,500 engineers" on the waitlist (Apr 2026, Forbes) [F, M-14]. Closed beta. The homepage still says "Join the waitlist" [F, M-16].

## 3. Public output

**Field Notes: only 2 posts** [F, M-22]
1. *Wiring Model Selection In Without Owning It*. Undated (newest), author Lily D, 3 min. Claim: hardcoded model strings and static routers never check themselves. Minima is a lookup "that learns from reported outcomes". It sits *beside* the call, adds about 100–300 ms, is not a proxy, and degrades gracefully if memory is down [F, M-23].
2. *Why Request-Path Authority Matters More Than Model Choice*. 28 Jul 2026, author Shankha D, 10 min. Claim: coding agents are runtime systems. Prompt construction is part of the trust boundary; the example is a reverse-engineered Claude Code prompt-byte mutation. Components that don't need request-path authority should stay out of the path. "That is the Minima position" [F, M-13].

**latte/bench (mubit.ai/bench + GitHub MubitLabs/latte-bench)** [F, M-24..M-27]
- What it measures: can a model turn a target into an executable 33-parameter plan for a simulated latte pour (heart shape), read the measured feedback, and improve on later attempts? It compares runs with and without a self-written "note".
- Setup: matched milk conditions (3 seeds × 5 attempts). Scores are best-of-5 shape quality (0–100) plus a strict pass. A CMA-ES baseline is included. 330 valid pours.
- Headlines:
  - "Feedback can help—or hurt": notes raised scores for 7 of 11 models and lowered them for 4.
  - "Quality is not reliability": GPT-6 Astra passes went 2→5 of 15 with notes, yet its mean best fell 78.7→74.7.
  - Claude Opus 5.5 rose 38.8→67.0 with notes.
  - CMA-ES scored 32.4.
  - GPT-5.5 Pro produced no valid plan.
  - Two of seven numerical passes were weak visual matches.
- Scope note on the page: it "does not establish held-out transfer, model-weight learning, or real-world pouring skill".
- Repo: created 2026-10-20, 2 stars. It runs through `MUBIT_BASE_URL=https://api.mubit.ai/openai/v1/` and compares `MUBIT_MODEL` with `FRONTIER_MODEL` [F, M-27].
- Teammate's note checked: "benchmark of whether models improve from feedback" is **confirmed**. More exactly, it measures whether *retained text notes* help planning, and the answer is "mixed".

**Banyan Sapling (HF MubitLabs/banyan-sapling)**: every point in the teammate's note is **confirmed** [F, M-29..M-31]
- Base Qwen3-30B-A3B-Instruct-2507. Pruned MoE (96 experts/layer, 23.0B stored params). Attention LoRA plus a "TriVector" interaction head. Apache-2.0. Research preview. Uploaded 2026-10-22. 4 downloads, 1 like.
- Input is policy, evidence and claim. Labels are `supported`, `violation`, `insufficient_information` and `inconsistent_context`, plus a calibrated `status` that can be `unsure` (conformal prediction sets).
- Trained on 50,000 examples: 42,809 synthetic plus 7,191 ContractNLI.
- Evaluation:
  - 94.22% raw accuracy.
  - Calibrated answers cover only 45% of cases overall, and only **0.82% of ContractNLI** (6 of 731).
  - Zero false `supported` decisions after calibration.
  - 97 ms median latency on an H200.
  - About 46 GB in BF16.
- They ask for community cases "where `unsure` prevents a useful answer" [F, M-31].

**Minima (GitHub MubitLabs/minima)** [F, M-28]
- 2 stars, 0 forks. Created 2026-06-08. Last push 2026-10-23. Last default-branch commit 2026-08-10 (v0.15.1). The licence says "Other". GitHub reports TypeScript, but the README is Python/uv.
- What it does: "only recommends — it never proxies a call". Endpoints are `/v1/recommend`, `/v1/recommend/workflow`, `/v1/feedback`, `/v1/models` and `/v1/strategies`.
- A `cost_quality_tradeoff` 0–10 sets the bar. Cost is ranked on an estimate→observed→rescaled basis that is aware of reasoning tokens. Memory comes from Mubit.
- Teammate's note checked: "open-source cheapest-model-per-task recommender" is **confirmed**, though the licence is not a standard OSS SPDX licence.

**Other output**
- **Middleware** (middleware.now, waitlist opened 28 Sep 2026) [F, M-33, M-11]:
  - "lightweight model updates from your calls and feedback".
  - Sits before the router, with one base URL change and open models hosted by Mubit.
  - A "change detector" triggers a refresh. Their example: "when your escalation policy changes…".
- **Launch week** 26–30 Oct 2026: "Five days. Five major features." It starts the day after Night Shift [F, M-34].
- **GitHub org** (21 repos): claude-plugins (11★), codaph (12★), plugins (4★), mubit-cl-bench and mubit-stulife-bench (lifelong-learning benchmarks), demos (SRE, Harvey lab, voice agents, meetingcrew), and a fork of paperclip [F, raw/M-38.md].
- **Media kit** [F, M-32]: headline "Build reliable agents with a model for every task." Legal owner: Reliable AI, Inc.
- **Careers**: mubit.ai/careers returns 404. Ashby lists 1 role. Inference [I]: they are not scaling hiring right now. The team is small and the event has to do double duty for marketing and recruiting (Eldar was hired from a hackathon).

## 4. Customers, design partners, case studies

- **No named customers, logos or case studies on mubit.ai** [F, M-35]. The homepage says "Results depend on the workload; no fixed improvement is promised."
  - It shows SOC 2, ISO 42001, ISO 27001, GDPR and HIPAA badges. These are not verified, and they look large for a 7-person closed beta [I].
- Anil thanked "investors, customers, and supporters" (Apr 2026) and the job ad mentions "early customers". **None are named** [F, raw/M-16.md, M-6].
- Only rough numbers exist:
  - About 1,500 on the waitlist (Forbes).
  - Rice "5x faster / 4.2x less tokens" (unsourced headline).
  - Sapling evaluation figures (above).
- Third-party usage is all from hackathons [F]:
  - CafeTwin: a dev.to review saying "Sub-100ms recall in practice", with rough edges noted (M-36).
  - Frame Mog → ClearNest voice agent (M-37).
  - joanie: 2nd place at #popthebubble (M-38).
  - Rentry: 2nd in the Zero to Agent main track plus the Mubit track (M-39).
  - Sambung, the "Flash" team's triple win at {Tech: Europe} London (raw/M-11.md; Sambung from a search snippet only, lead).
- [I] Every one of these used the **old memory product** ("it remembered my preferences"). None showed a model update.

## 5. Night Shift hackathon (23–25 Oct 2026)

- **Event facts** [F, M-40..M-44]:
  - Size and prizes: 42 h, 500 builders. Cash $15k / $10k / $5k, plus $35k in credits (OpenAI and others), plus $1.5M in Mubit credits. Hosts: Eldar Utiushev, Anil Peri, Lily Jahan.
  - Tracks: (1) Recurring tasks: extraction, triage, support replies, review, routing. (2) Own your intelligence layer: closed model → task-adapted open model, "quality, cost and latency side by side". (3) Fast refresh: new data, customers or domains.
  - Judging, 4 equal criteria: Use of Mubit ("Show a correction turning into a model update in your demo"), Usefulness, Technical execution ("holds up under questions"), and a live Demo within the time limit.
  - Rule: every project must route its LLM calls through Mubit. The FAQ says "Mubit runs adapter fine-tuning for you, automatically."
- **Judges: not announced** ("Judges will be announced later", as of today) [F, M-41].
- **Sponsors:** only OpenAI credits are mentioned. No other sponsors are named.
- **Side quests:** none published.
- **X / @MubitLabs:** I found no posts. Exa returned nothing, and X was not reachable directly. "Not found" here means none were visible, not that none exist.
- **Crowding:** I found **no public posts** from Night Shift hackers sharing ideas. I searched LinkedIn, X, GitHub and Devpost through exa. Inference [I]: the founders' own examples (invoice fields, support reply wording, escalation policy) and the track list (extraction, triage, support) will be the most crowded ideas.
- **Past Mubit hackathon pattern** [F]: they sponsored or ran Unicorn Mafia (first, Apr 2026), Zero to Agent (Vercel, May; $100k "Mubit prize"), #popthebubble (Jun) and {Tech: Europe} London (Jun). Winners were praised for simplicity and visible live adaptation (M-37, M-39).

## 6. Positioning over time

| When | Headline / framing | Source |
|---|---|---|
| Feb 2026 | "MuBit, Memory + State Infra for AI Agents": focus/commit/reminisce, shared state for parallel agents, <80 ms | Wayback 2026-02-13 [F, M-45] |
| Mar 2026 | "agents have no experience"; argues fine-tuning is offline and blind; "One line of code" | Anil post [F, M-8, M-9] |
| Apr 2026 | "Operational Memory for Agent Systems", an execution memory SDK (`mubit.learn.init`); comparison table *against* fine-tuning ("No GPU costs"); "Observability tells you what happened. Mubit makes sure the agent remembers." | Wayback 2026-04-18 [F, M-46] |
| Jun 2026 | "It has been reminded, not improved": memory notes are not enough | company post [F, M-10] |
| Jul–Aug 2026 | Minima (outcome-learned model choice); request-path trust | field notes [F] |
| Sep 2026 | Middleware: "task-adapted open models from your model calls" | middleware.now [F, M-33] |
| Oct 2026 | "Agentic runtime calibration. Build reliable agents with a model for every task", "builds and refreshes a dedicated model for each task … switching over only when it does better"; Banyan models; LinkedIn: "decision-attribution and agent calibration" | mubit.ai, LinkedIn [F, M-47, M-4] |

[I] The biggest shift is a full reversal on weights. In April they sold "no retraining, no GPU cost". Now the product *is* automatic adapter training on open models. Memory has become the data source (corrections and outcomes) for model updates.
[I] There is also an open tension. Shankha's July post argues a router should not hold request-path authority, while Night Shift requires routing every call through Mubit's gateway.

## 7. What would most impress them as judges [all I, grounded in facts above]

1. **Hit the literal criterion live.** Show a human correction → an adapter update → the *same* input fixed on the next call, with the before and after visible on stage. They wrote this into the judging rule (M-40). Memory-only demos ("it remembered my preference") match their *old* product. Past winners did that, but it will now score low on "Use of Mubit".
2. **Measure it like latte/bench.** Use matched held-out inputs, with and without the update. Report several numbers: quality, pass rate, cost per *successful* task and latency (their homepage FAQ uses exactly these). Say what the demo does *not* prove. This team prizes "quality is not reliability" style rigour (M-25, M-26), and "holds up under questions" is a criterion.
3. **Contrast "reminded" with "improved".** On one recurring task, compare (a) the correction stored as a note or prompt with (b) an adapter update. This is a mini version of their own thesis (M-10) and of latte/bench's notes arm. It directly answers the question their benchmark leaves open ("does not establish … model-weight learning").
4. **Build on their launches:**
   - **Banyan Sapling as the eval gate.** On a policy-bound recurring task (support replies vs refund policy, contract or claims review), Sapling labels each output. `violation` and `unsure` route to a human, the human's correction becomes the training signal, and the adapter is only promoted when Sapling and held-out checks pass, with rollback. This uses their newest model (2 days old), their "eval before rollout" story and their open request for `unsure` cases (M-31).
     - Risk: Sapling needs about 46 GB on an H200, and it is not known whether Mubit hosts it. Ask at office hours.
     - Sapling is weak on contracts (0.82% coverage), so prefer synthetic or controlled policy tasks.
   - **Minima for the "Own your intelligence layer" track.** Feed outcomes to Minima so it decides when the task-adapted open model beats the frontier model per task, and show cost/quality/latency side by side. This is their "switching over only when it does better" promise.
   - **Fast refresh with a change detector.** Change the policy mid-demo (their own Middleware example is an escalation policy) and show the update keeping pace (M-33).
5. **Respect Shankha's trust-boundary view.** A small audit view that shows, for each call, what was sent, which correction produced which adapter version, and a one-click rollback. It speaks to "inspectable request path" and "versioned, reversible updates" (M-13, M-4).
6. **Avoid the crowded centre.** Generic invoice extraction or support-reply bots copy the founders' own examples. If you use one, add a sharp vertical, a real user, or the Sapling gate to stand apart.

**Gaps:**
- Judges and sponsors are not public.
- No @MubitLabs X posts were reachable.
- No named customers.
- The funding amount is only company-reported.
- Whether Lily D and Lily Jahan are the same person is unverified.
- Whether Sapling is hosted for hackers is unknown.
