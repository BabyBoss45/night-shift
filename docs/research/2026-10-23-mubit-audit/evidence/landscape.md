# Mubit: competitive landscape (agent L, 2026-10-23)

Scope: alternatives to Mubit's "point your calls at a gateway, it trains and switches to a per-task open-weight adapter" loop, plus gateways, routers, memory and the status quo.
Tags: **[F]** = seen in a source (evidence id), **[I]** = my inference, **[E]** = my estimate or a cell judged from indirect evidence. Evidence ids (L-n) are rows in `evidence-L.csv`. Raw pages: `raw/L-*.md`.
Not covered in depth: Vertex / Bedrock custom models, Vercel AI Gateway, Arize, Braintrust, Zep, LangMem, Unsloth, Lamini (I found no primary source this run; listed as hypothesized).

---

## 0. The five things to know before tonight

1. **The 2024-25 "trace to fine-tune" generation is gone as standalone companies.** OpenPipe was bought by CoreWeave (Sep 2025) and its platform stopped training and inference on 30 Jul 2026 [F L-19, L-17]. Predibase went to Rubrik (Jun 2025) [F L-21]. Adaptive ML went to Datadog (30 Jun 2026) [F L-55]. TensorZero, the closest open-source match (gateway + feedback + optimization), wound down in Jun 2026 and returned its money to investors [F L-22, L-23].
2. **OpenAI is closing its fine-tuning and distillation platform.** New organisations blocked from 7 May 2026. Existing customers can create jobs until 6 Jan 2027 [F L-41, L-42]. So distilling into a smaller *OpenAI* model is no longer an option. Every distilled-on-OpenAI workload needs an open-weight home. [I] This helps Mubit's "own it" pitch, and it gives a hook with a real deadline.
3. **A new direct competitor has the same pitch: Experiential Labs (YC Summer 2026).** It is an open-source Rust gateway with zero markup. It "turns your traffic into better models", the model "earns more traffic", and the hard calls go back to the frontier model. It promises "at least 50% lower cost at the same or better quality, backed by an SLA" [F L-32, L-33, L-34, L-35]. Team of 2, training runs on Tinker [F L-37, L-38].
4. **Gateways and routers have consolidated or pivoted.** Portkey went to Palo Alto Networks [F L-49]. Helicone went to Mintlify and is in maintenance mode [F L-48]. Langfuse went to ClickHouse [F L-50]. Stripe agreed to buy OpenRouter, not yet closed [F L-47]. Martian moved to interpretability research, and Not Diamond narrowed to coding agents [F L-43, L-44]. [I] The traffic layer is cheap. Investors say the asset is "the feedback loop that teaches the router what 'good' means" [F L-46].
5. **The "stop renting intelligence" message is crowded.** Adaptive ML used almost the same words ("not merely rent static intelligence") [F L-56]. So do Applied Compute ("own models that keep getting better") [F L-52, quote not verified], Inference.net [F L-30] and Experiential [F L-32]. [I] Mubit cannot win on the slogan. It has to win on how it decides, and how it proves, when an owned model may take over.

---

## (a) Alternatives table (37 entries)

Status = 2026 status. O/H = **observed** (there is evidence that buyers consider it, switch from it, or that it competes for the same budget) or **hypothesized**.

| # | Name | Group | Status 2026 | Mechanism (one line) | O/H | Evidence |
|---|---|---|---|---|---|---|
| 1 | OpenPipe | Trace to fine-tune | **Acquired** by CoreWeave (Sep 2025). Platform shut 30 Jul 2026; customers moved to W&B Training/Inference | Logged calls, then SFT/RL (ART, Serverless RL), then hosted inference | O | L-17, L-18, L-19, L-20 |
| 2 | Predibase | Trace to fine-tune | **Acquired** by Rubrik (Jun 2025). Self-serve status after that: not found | LoRA fine-tuning + LoRAX multi-adapter serving | O | L-21 |
| 3 | TensorZero | Gateway + optimization (OSS) | **Wound down** Jun 2026, repo archived | Rust gateway, feedback store, SFT/GEPA/DICL, A/B tests, paid "Autopilot" | O | L-22 to L-26 |
| 4 | Inference.net | Trace to fine-tune | Active. "Inference platform" launched 14 Apr 2026 | Gateway records traffic, then datasets, LLM-judge evals, SFT recipes, dedicated GPU deploy, staged review | O | L-27 to L-31 |
| 5 | **Experiential Labs** | Gateway + router + owned model | Active. YC S26, 2 people, launched Aug 2026 | OSS zero-markup gateway. Traces feed a text "world model" simulation, a KNN router, then training on Tinker; the model "earns traffic" | O | L-32 to L-38 |
| 6 | Applied Compute | Enterprise custom post-training | Active. ~$50M annualised revenue; reportedly raising at ~$3B (Aug 2026) | Researchers embedded with the customer; RL post-training, online RL / self-distillation, serving in AC2 | O | L-52 to L-54 |
| 7 | Adaptive ML | RLOps platform | **Acquired** by Datadog (30 Jun 2026) | RL tuning, AI judges, A/B tests, production feedback | O | L-55, L-56 |
| 8 | Trajectory | Continual learning lab | Active. $15M seed, May 2026 | Post-training from user corrections; open-sourced concurrent multi-LoRA RL (C-LoRA) | O | L-57, L-58 |
| 9 | RELAI | Verified continual learning | Active. $6.9M, Jun 2026 | Failures become replayable environments; regression control inside the optimization loop; fixes routed to prompt, tool, memory, routing or model | O | L-59 |
| 10 | Datawizz | SLM platform | Active. "Continuous Learning" launched Jan 2026 | Production signals become labels and preference pairs; releases gated on real traffic slices | O | L-60 |
| 11 | Thinking Machines Tinker | Training API | Active. GA Dec 2025; full fine-tuning in beta (Oct 2026) | Per-token LoRA training/sampling API; you write the loop. Serverless inference is beta and only for its own models | O | L-39, L-40 |
| 12 | Fireworks RFT | Inference cloud + post-training | Active (Nov 2025 launch) | Managed RL: you supply evaluator and rollouts; deploy on Fireworks | O | L-64 |
| 13 | Together Post-Training | Inference cloud + post-training | Active. Launched 19 Oct 2026 | Your own SFT/RL loop on dedicated GPUs; multi-LoRA | O | L-65 |
| 14 | OpenAI distillation / SFT / RFT | Frontier provider fine-tuning | **Winding down**. Closed to new users May 2026; all new jobs end 6 Jan 2027 | Stored completions, then fine-tune a smaller OpenAI model | O | L-41, L-42 |
| 15 | Arcee AI | (was) post-training for enterprises | **Pivoted** to its own Trinity open-weight models; Series B >$1B (Sep 2026) | Now a model maker | O | L-66 |
| 16 | Parity Layer | "Prove before switch" | Active (vendor blog) | Proves a cheaper model matches yours on your prompts, then switches the prompts that pass | H | L-51 |
| 17 | Lamini | Fine-tuning | Unknown (only a 2026 listicle; not verified) | Memory tuning / MoME | H | none |
| 18 | Vertex AI / Bedrock custom models | Cloud incumbents | Not researched | Managed fine-tuning inside the cloud | H | none |
| 19 | Unsloth / Axolotl | DIY open-source training | Active (lead only) | Local LoRA/QLoRA/GRPO | H | none |
| 20 | Portkey | Gateway | **Acquired** by Palo Alto Networks (announced 30 Apr 2026); now the Prisma AIRS gateway | Gateway, guardrails, routing, governance | O | L-49 |
| 21 | Helicone | Gateway + observability | **Acquired** by Mintlify (3 Mar 2026), maintenance mode | Proxy logging | O | L-48 |
| 22 | Langfuse | Observability | **Acquired** by ClickHouse (16 Jan 2026); OSS continues | Tracing, evals, prompt management | O | L-50 |
| 23 | OpenRouter | Gateway / aggregator | Stripe agreed to acquire it (19 Aug 2026), not closed | Aggregator; "auto" router powered by Not Diamond | O | L-47, L-44 |
| 24 | LiteLLM | OSS gateway | Independent (lead source says it had a Mar 2026 PyPI compromise) | OpenAI-compatible proxy | H | raw L-42 |
| 25 | Cloudflare AI Gateway | Gateway (incumbent) | Auto Router public beta, 30 Sep 2026 | Per-request model pick, quality vs cost | H | raw L-41 |
| 26 | Vercel AI Gateway | Gateway (incumbent) | Not researched | Gateway | H | none |
| 27 | Braintrust / Arize | Evals / observability | Independent (lead only) | Evals, tracing | H | none |
| 28 | Martian | Router | **Pivoted** to interpretability research; router no longer documented | (was) learned router | O | L-43, L-44 |
| 29 | Not Diamond | Router | Active but narrowed to coding agents; powers OpenRouter auto; ~$0.05/M routed tokens (per a competitor page) | Learned per-prompt model recommendation + prompt adaptation | O | L-43 to L-45 |
| 30 | RouteLLM (LMSYS) | OSS router | Dormant since Aug 2024 | Preference-trained router | O | L-44 |
| 31 | Mem0 | Agent memory | Active. $24M (Oct 2025); exclusive memory provider for AWS Agent SDK | Fact extraction + retrieval API | O | L-62 |
| 32 | Letta | Agent memory / runtime | Active. Argues for learning "in token space, not weights" | Memory blocks, sleep-time compute, git-backed context | O | L-61 |
| 33 | Zep / LangMem / Cognee | Agent memory | Active (lead only) | Temporal graph / framework memory | H | raw L-56 |
| 34 | Native memory (Claude, ChatGPT, AWS AgentCore, Vertex Memory Bank) | Incumbent bundling | Shipping (lead only) | Memory as a platform primitive | H | L-63 |
| 35 | Status quo: frontier model + prompt caching | Status quo | Default | Long prompts + caching instead of fine-tuning | O | L-67, L-68 |
| 36 | Status quo: pick a cheaper model by hand | Status quo | Default | Manual A/B, rewrite prompts | O | L-70 |
| 37 | Status quo: DIY distill + fine-tune | Workaround | Common for high-volume narrow tasks | Log teacher outputs, filter, LoRA, gold set, retrain on drift | O | L-69, L-71 |

**Dead or pivoted, and why** [I from the facts above]:
- **OpenPipe and Adaptive ML** were absorbed by compute or observability platforms that own the data or the GPUs.
- **TensorZero's** CEO pointed to the cost of finding fit twice, once for the open-source project and once for the paid product (raw L-68 summary of the HN thread).
- **Martian and RouteLLM** show that per-prompt routing alone is not a business: savings shrink when cheap models cost $0.10-0.60/M (raw L-36).
- **Arcee** left customer post-training to make models.

Lesson: a thin "loop on top of someone else's traffic and GPUs" gets bought or squeezed unless it owns a decision layer people trust.

---

## (b) Teardowns of the closest 8

### 1. Experiential Labs: the most direct threat
- **Positioning (YC Launch, 6 Aug 2026):** "Train a model your company owns, guaranteed to match or beat frontier quality at 50% lower cost." [F L-32]
  - For AI budget holders who keep paying frontier prices for repetitive work, Experiential is an open-source gateway that turns traffic into an owned model.
  - Unlike paid gateways, it charges zero markup ("Simple routing doesn't warrant a 10% token markup", raw L-26) and guarantees savings in an SLA [F L-34, L-35].
- **Pricing / value metric:** gateway with zero markup; free tier; credits for other models; a flat "unlimited" plan for some models on the homepage (raw L-32). Savings guaranteed by SLA [F L-34]. Training price not public.
- **Mechanism (documented):**
  - OTel traces become representative tasks.
  - A text "world model" simulates tool responses.
  - Rollouts across candidate models are scored by an LLM judge.
  - A KNN router is trained on prompt embeddings, with confidence gating.
  - An open model is trained on Tinker, and traffic shifts to it as it improves [F L-33, L-37; raw L-26, L-28, L-29].
- **Momentum:** two Show HNs (Jul to Aug 2026, 71 and 222 points); GitHub repo star count ~10.5k seen in search metadata only (not saved, treat as lead); YC S26.
- **What users say:** "The title is misleading. This is model routing, not distillation." [F L-36]. Other commenters asked for benchmarks of a released fine-tuned model (raw L-28). Founder says router training costs "in the thousands" (raw L-28).
- **Versus Mubit [I]:** same promise. Experiential leads on the guarantee, OSS self-hosting and routing. Mubit leads on documented automatic task fingerprinting, adapters per task, the "Prompt only" honesty check, and memory/lesson heritage. Both are tiny teams.

### 2. Inference.net
- **Positioning:** "Turn production data into specialized models that deliver 90% lower cost and 5x lower latency" (Train page, read 2026-10-23) [F L-31]. Launch post, 14 Apr 2026: "a platform for building continuously self-improving AI models" (raw L-17).
- **Pricing:** training runs "$25 up to several thousand dollars" [F L-29]. Dedicated GPU deploys (raw L-18).
- **Mechanism:**
  - Gateway records requests, which become datasets.
  - LLM-as-judge evals, then SFT "recipes" (preset base model and hyperparameters).
  - Deploy on a dedicated GPU with an OpenAI-compatible API.
  - The loop "ingests fresh production data…compares resulting models against the production baseline". New models are "staged for final review and deployment" [F L-27, L-28].
  - Weights are owned by the customer and can be exported to a private VPS [F L-30].
- **Momentum:** platform launch Apr 2026; Halo open-source agent optimizer (raw L-18); Schematron V2 and a NeMo case study also surfaced in search (not saved, leads only).
- **Complaints:** none found (2 searches).
- **Versus Mubit [I]:** most similar product loop. Inference.net has serving and recipes and is more mature. Its switch-over has a human in the loop. Its datasets are built by the user, not auto-fingerprinted.

### 3. OpenPipe (now CoreWeave / W&B)
- **Positioning (Sep 2025, archived):** helped customers save "millions of dollars by moving to smaller, faster, more reliable models" (raw L-8). Now: "build a world where every agent learns continually from its real-world experience" [F L-20].
- **Status:** platform shut 30 Jul 2026. Training and inference moved to W&B. Reward models, managed evals, criteria, pruning rules, relabeling pipelines and DPO were sunset [F L-17, L-18].
- **Pricing:** now CoreWeave/W&B pricing (not researched). Serverless RL charges only for incremental tokens (raw L-10).
- **Mechanism:** ART (open-source RL), RULER auto-rewards, Serverless RL on W&B Inference.
- **What users faced:** a forced migration and loss of eval/relabel features [F L-18]. [I] Ex-OpenPipe users are reachable and wary of vendor continuity.
- **Versus Mubit [I]:** OpenPipe's original SDK-logging-then-fine-tune is the "just another OpenPipe demo" pattern. Its RL successor now lives inside a GPU cloud.

### 4. TensorZero (archived, the closest architectural twin)
- **Positioning (README, archived Jun 2026):** "open-source LLMOps platform that unifies an LLM gateway, observability, evaluation, optimization, and experimentation" (raw L-14).
- **Pricing:** OSS free; Autopilot was the paid layer [F L-25].
- **Mechanism:**
  - Functions and variants are declared in config.
  - Feedback (metrics, human edits) is stored in your database.
  - Optimization by SFT, GEPA or DICL, plus adaptive A/B tests.
  - Autopilot = "automated AI engineer". Its published gains ran with fine-tuning disabled [F L-24].
- **Momentum:** none. Site says "no longer maintained" [F L-22]. The CEO is returning capital [F L-23].
- **Lesson [I]:** a full loop with strong engineering still failed commercially. A third-party review says what has no replacement is "the integrated loop that connected traces, feedback, evals, and optimization" [F L-26, lead source]. That gap is Mubit's opening, and a warning about how hard it is to monetize.

### 5. Predibase (Rubrik)
- **Positioning (Jun 2025):** "lowering cost by up to 80%"; LoRAX multi-adapter serving [F L-21].
- **Status after 2025:** not found. I searched Rubrik + Predibase 2026; no shutdown or product page surfaced.
- **Versus Mubit [I]:** LoRAX-style many-adapters-per-base is the serving pattern Mubit needs for "a model for every task". It now sits inside an enterprise security and data vendor.

### 6. OpenAI distillation + RFT
- **Positioning (2024 launch, dated):** Stored Completions, then Evals, then fine-tuning in one platform (not saved; dated).
- **2026 status:** "OpenAI is winding down the fine-tuning platform. The platform is no longer accessible to new users." [F L-41]. Fine-tuned models live only until their base model is deprecated. Several GPT-4.x bases shut on 23 Oct 2026 and 14 Jan 2027 (raw L-37).
- **[I]** This is the biggest status-quo shift in Mubit's favour: "distill inside your provider" is closing. Customers with OpenAI fine-tunes need a new home before 6 Jan 2027.

### 7. Routers: Martian and Not Diamond
- **Martian:** the router is no longer documented and the homepage leads with research [F L-43, L-44].
- **Not Diamond:** refocused on coding agents; Python SDK archived 2025-12-11 [F L-43]. ~$0.05 per million routed tokens and 100-150 ms added latency, both per a competitor's page (raw L-44) [F L-45, medium]. Powers OpenRouter auto (raw L-36).
- **Versus Mubit [I]:** Minima also only recommends and never proxies [F L-16], the same "beside the call" design. Routing alone is a fading category [F L-44, L-46]. Minima is useful as a feature, not as the pitch.

### 8. Gateways: Portkey and Helicone (plus Langfuse and OpenRouter)
- **Portkey (Apr 2026):** "Portkey will serve as the AI Gateway for Prisma AIRS"; the roadmap is now security and governance [F L-49].
- **Helicone:** maintenance mode under Mintlify [F L-48].
- **[I]** None of the consolidated gateways ships "train an owned model from my traffic". Their new owners care about security, docs and payments. That leaves room for a gateway whose value is the learning loop.

### Also close: Tinker (the engine others build on)
- **Positioning (Oct 2026):** "Turning your expertise into custom models" (raw L-31).
- **Pricing:** per million tokens for prefill, sample and train. Example: Qwen3-8B train at $0.44/M, as of 19 Oct 2026 [F L-40]. Storage $0.10/GB/month.
- **[I]** Tinker is the building block, not a competitor: Experiential trains on it [F L-37], and Mubit could too. It means training cost is commoditized. Mubit's value has to be curation, gating and switching.

---

## (c) Capability matrix

Cells: S = Strong, A = Adequate, W = Weak, X = Absent, ? = Unknown. [E] = judged from indirect evidence.
Mubit cells are as *documented on 2026-10-23*, not as pitched.
"Gateways" = Portkey / Helicone / LiteLLM / OpenRouter. "Memory" = Mem0 / Letta.

| Customer outcome (Kano) | Mubit | Experiential | Inference.net | OpenPipe→W&B | TensorZero (archived) | Tinker | Applied Compute | Gateways | Not Diamond | Memory | Status quo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Zero-code integration: base URL swap (Must-be) | **S** (L-3) | S (L-35) | S (raw L-18) | A [E] | A, needs function config [E] | X | W, embedded engagement (L-54) | S | A, SDK beside the call (L-43) | A, SDK | S (nothing to change) |
| Automatic task discovery (Attractive) | **S**, fingerprint of model+prompt+tools+format (L-4) | A, mines "representative real tasks" (raw L-26) | W, user builds datasets [E] (L-27) | W [E] | W, user declares functions [E] | X | W, humans co-design [E] | X | X | X | X |
| Distillation from frontier (Performance) | **A**: trains toward provider answers (L-5, L-9), gated rollout (L-7) | A, simulation + Tinker; called "routing, not distillation" (L-36, L-37) | S (L-27) | S, historic (L-19) | A [E] | A, DIY (L-39) | S [E] (L-52) | X | X | X | X (OpenAI path closing, L-41) |
| Learning from human corrections (Performance) | A, claims "tests, application checks or human feedback"; outcome attribution in memory (L-15) | ? | A, eval failures feed curation (raw L-16) | W, relabeling sunset (L-18) | S, human edits as feedback (raw L-14) [E] | A, DIY | S [E] | X | W | A, lessons | W, manual prompt edits |
| Eval gate + rollback (Must-be for switching) | **A**: held-out tests, version history, "Prompt only" check (L-5, L-8); pass = "close enough to your provider" (L-9) | S, judge replay + SLA guarantee (L-34) | A, auto evals + staged human review (L-28) | A [E] | S, evals + adaptive A/B [E] | X | S, A/B release candidates [E] | W, fallbacks only | A | W | W (L-70) |
| Serving the trained model (Must-be) | A, "Try models" documented; production infra not documented (L-5) | S, in its gateway [E] | S, dedicated GPU (L-27) | S, W&B Inference (L-17) | X, bring your own | W, serverless beta for its own models only (L-40) | S [E] | A, route to endpoints | X | X | S (provider serves) |
| Memory / lessons (Attractive) | **S**, heritage (L-14, L-15) | X | X | X | A, DICL [E] | X | A ("memory" in AC2) [E] | X | X | S (L-61, L-62) | W |
| Routing across models (Performance) | A, Minima advises only (L-16) | S (L-33) | W | X | S, A/B + routing [E] | X | W | S | S (L-45) | X | W, by hand |
| Data ownership / weight export (Must-be now) | ?, "You own what's built" (L-1); export not documented | S, own weights, run anywhere (L-32) | S (L-30) | A, migration only to W&B (L-17) | S, self-hosted | S [E] | S [E] (L-52) | A | n/a | A | W, rented |
| Privacy / on-prem (Must-be for enterprise) | ? (nothing documented) | A, OSS self-host [E] | A, own VPS (L-30) | ? | S, fully self-hosted | W [E] | S, VPC [E] | A-S (LiteLLM self-host) | A | A | A, provider ZDR [E] |

**Table stakes** [I]: base-URL integration, weight ownership/export, an eval before switching. Most active players have them.
**Mubit's candidate differentiators** [I]:
- (1) Automatic task discovery by fingerprint, so many small adapters appear without setup.
- (2) Memory/lessons and adapters in one loop with outcome attribution.
- (3) The explicit "Prompt only" verdict: it tells you when training was not needed.

User-demand evidence for (1)-(3) is **indirect** (buyers want proof before switching, per L-51 and L-70, and cost per successful task, per L-70). I found no direct VoC asking for auto-discovery.

---

## (d) Where Mubit is differentiated, and where it is weak or unproven

**Differentiated (documented)**
- **Auto task discovery.** A task is defined by matching model, instructions, tools, tool choice and output format [F L-4]. No competitor documents automatic per-task fingerprinting this explicitly. [I] This is the real "a model for every task" capability.
- **Honest gating.** Five verdicts (Passed / Below target / Malformed tool calls / Prompt only / Not tested), held-out test cases, version history [F L-5, L-8]. "Prompt only" admits the base model plus the prompt already did as well. [I] Rare, and builds trust.
- **Low threshold to first training.** 25 kept examples by default [F L-6].
- **Several layers in one loop.** Memory with outcome attribution, prompt/skill improvement, and adapters [F L-1, L-15]. Only RELAI claims a comparable multi-layer approach [F L-59]. Letta argues for the token layer only [F L-61].
- **Ecosystem pieces.**
  - Minima: open, advice-only router with feedback [F L-16].
  - Banyan Sapling and Latte Bench: **not found** in public sources (L-72). Treat as unverified until the founders show them.

**Weak or unproven**
- **No measured results in public.** The site says illustrations are "conceptual, not measured" and "no fixed improvement is promised" [F L-2, L-3]. Experiential offers an SLA instead [F L-34].
- **The success metric is imitation, not outcome.** "Passed" means "answers close enough to your provider model" [F L-9]. The homepage says it switches "only when it does better" [F L-1]. [I] With imitation grading, an adapter can at best tie the teacher. Beating the teacher needs outcome or correction signals, and the adapter docs do not show that path.
- **Training not on for everyone.** "Training must be on for your workspace" [F L-7]. There is no retry button [F L-10].
- **Serving, export and privacy not documented** (matrix cells marked ?). [I] Enterprise buyers and ex-OpenPipe users will ask about these first.
- **Tiny and early.** ~$2.1M raised, closed beta, ~1,500 waitlist (Apr 2026) [F L-11, L-12].
- **HQ conflict.** Investor pages list Aberdeen; the product card says London [F L-13].
- **Category name.** "Agentic runtime calibration" is unique but unexplained. Databases still call Mubit a "memory layer" [F L-14]. [I] There is a risk of being read as a memory tool or as an OpenPipe clone.
- **Crowded slogan** (see §0.5) [F L-56].

---

## (e) Market gaps nobody fills well

1. **Proof before switch, graded on outcomes, with automatic rollback on drift.**
   - Routers recommend before the answer exists. Parity Layer, a self-interested source, names the gap: nobody proves "the cheaper model…is actually good enough on your prompts before it switches" [F L-51].
   - Practitioners: maintenance and drift are the hidden bill [F L-69]. A CIO team "pulled it out" after production drift [F L-71].
   - Experiential's SLA is a promise, not a mechanism [I].
2. **Deciding which layer to fix.** A failure might need a memory lesson, a prompt change, a route change or a weight update. Only RELAI claims this [F L-59]. Nobody demonstrates it on live traffic [I].
3. **Cost per *successful* task, not cost per token.** CIOs say retries, human review and escalation erase small-model savings [F L-70]. Mubit's homepage already names this metric (raw L-2). Few products report it [I].
4. **The mid-market, self-serve version of Applied Compute.**
   - Applied Compute sells consulting plus compute [F L-54].
   - Tinker, Fireworks and Together are DIY loops [F L-39, L-64, L-65].
   - Nobody serves "zero ML team, many small recurring tasks" well, now that OpenPipe and TensorZero are gone [I].
5. **Refugees from OpenAI fine-tuning.** Deadline 6 Jan 2027, plus base-model shutdowns [F L-41, L-42]. No one markets a migration path yet (not found in 1 search) [I].
6. **Vendor continuity and portability.** OpenPipe forced a migration [F L-17]. TensorZero was archived [F L-22]. Helicone is frozen [F L-48]. [I] Buyers will reward exportable adapters, datasets and eval history.
7. **Surviving base-model turnover.** Experiential claims it transfers what a model learned to new bases (raw L-27). Letta argues for memory in tokens because weights churn [F L-61]. [I] Mubit has both layers and could own "lessons survive model upgrades; adapters get rebuilt automatically".

---

## (f) Implications for the hackathon project (judged by Mubit's founders)

**What would showcase Mubit's unique strengths** [I, built on the facts above]:

1. **Multi-task agent, auto-discovered.** Build an agent whose workflow makes 4-6 different kinds of calls (for example triage, extraction, tool-calling, summarisation, reply drafting), all through Mubit's base URL. Show the console finding the tasks by itself [L-4], each at a different stage: collecting, training, Passed, Prompt only. That is "a model for every task", not one distillation.
2. **Make the gate the hero, not the saving.**
   - Show one task where Mubit refuses to switch (Below target or Prompt only) and say why [L-8, L-9].
   - Then inject drift (new input type, a policy change) and show detection and rollback to the frontier or the previous version [L-1].
   - Judges built this; competitors only promise it (gap 1).
3. **Close the outcome loop, not just imitation.**
   - Feed verified outcomes (tests, app checks, human corrections) back through memory outcome attribution [L-15], so the agent improves *before* any adapter trains.
   - Then show the adapter taking over. Lessons fix it now; the adapter makes it cheap later.
   - Use an open verifier as the grader if the founders can provide Banyan Sapling (not publicly verified, L-72). This targets Mubit's weakest documented point, the imitation-only pass metric (§d).
4. **Report cost per successful task** across frontier-only, Minima-routed and adapter-served, with retries and escalations counted [L-70]. Not tokens.
5. **Timely hook: "OpenAI fine-tuning shuts on 6 Jan 2027, here is the one-line migration"** [L-41, L-42]. Take a workload that used OpenAI distillation, point it at Mubit, and get an owned open-weight adapter with an eval report. Show the export/ownership story explicitly, because it is undocumented today (§d).
6. **Lessons survive a model swap.** Swap the base or frontier model mid-demo. Memory lessons carry over; the adapter retrains automatically from kept examples (gap 7).

**What would look like "just another OpenPipe demo"** [I]:
- One task, one distillation: "we fine-tuned Llama on GPT outputs and it is 90% cheaper", on a toy dataset with no held-out test. This is OpenPipe, Inference.net and Experiential's homepage pitch [L-19, L-31, L-32].
- A cost dashboard of routing between models. Minima, Not Diamond and Experiential already do this, and routing is a fading category [L-44, L-46].
- A chatbot that "remembers the user". That is Mem0, Letta or native memory [L-62, L-63].
- Any demo where the switch-over is shown and the gate is not, or which quotes savings without a failure case.

**Suggested demo metric set:** tasks discovered; per-task verdicts; % of traffic on owned adapters; cost per successful task; regressions caught; time from correction to fix (memory) vs to adapter.

---

## Confidence, gaps, conflicts
- **High confidence:** acquisitions and shutdowns (primary press releases and vendor pages), OpenAI wind-down (OpenAI docs), Mubit mechanism (Mubit docs).
- **Medium confidence:** router and gateway status from secondary or competitor pages (L-43 to L-48; incentives noted), Applied Compute revenue (journalism, L-53).
- **Conflicts:**
  - Mubit HQ: Aberdeen per investors vs London per the card.
  - Mubit success definition: "does better" (homepage) vs "close enough to your provider" (docs).
  - OpenRouter price: PitchBook "reportedly $10B talks" vs another source ">$7bn" (raw L-42). Deal agreed, not closed.
- **Not found:**
  - Banyan Sapling, Latte Bench (1 search).
  - Predibase product status in 2026.
  - Complaints about Inference.net.
  - Lamini, Vertex/Bedrock, Vercel status (not searched, out of budget).
- **Unverified quote:** L-52 (Applied Compute homepage; the curl text differed).
