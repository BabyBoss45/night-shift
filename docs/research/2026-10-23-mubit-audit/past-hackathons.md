# Mubit's past hackathons: what they reward

Date: 2026-10-23, evening. Two research agents (events, projects) plus first-hand checks. Evidence: `evidence/evidence-H.csv` (events, 61 rows), `evidence/evidence-P.csv` (projects), details in `evidence/events.md` and `evidence/projects.md`. Labels: [F] fact seen in a source, [I] our inference.

## 1. Events (all London, Apr to Oct 2026)

| Event | Date | Mubit role | Mubit prize | Mubit-prize winner |
|---|---|---|---|---|
| Unicorn Mafia "To The Americas" | 25-26 Apr | Sponsor; "our FIRST event" (Anil) | "Best use of Mubit": £500 + $8k credits (participant copy, pre-event) | Not found |
| Vercel Zero to Agent | 2 May | Sponsor + track; "2nd hackathon" | $100k credits for "the best build on the Mubit platform" | **Rentry** (also 2nd overall) |
| Pop the Bubble | 5-7 Jun | Sponsor | Bonus points: "+4 for bolted-on use", "+10 when the core product genuinely relies on Mubit" | No separate prize; best Mubit user **joanie** (2nd overall) |
| {Tech: Europe} London | 27 Jun | Technology partner, Minima on offer | Credits for top 3 overall | No Mubit track; top 3 did not use Mubit |
| Night Shift | 23-25 Oct | Host | $15k / $10k / $5k + credits | Tonight |

Nothing found before April or in Jul to Sep. [F]

## 2. Projects that placed while using Mubit

| Project | Event, place | Idea | What Mubit did | Demo moment |
|---|---|---|---|---|
| **Rentry** | Zero to Agent, 2nd + Mubit prize | London rental agent | Remembered the user's preferences across sessions | "remembered from last session" badge; "it still knows you" |
| **joanie** | Pop the Bubble, 2nd | AI phone receptionist for service businesses | Remembered each caller's context | Live call; a paying customer and an LOI during the event (self-reported) |
| **CafeTwin** | Unicorn Mafia, 4th + Render track | Cafe CCTV → layout changes | Memory of operator accept/reject + prompt versioning | "seen 3× before" chip |
| Frame Mog | Unicorn Mafia, no placement | Pose coach | Remembered accepted/skipped poses | "By session three, the suggestions had visibly adapted" |

13 more projects used Mubit with no placement on record. Most used it as invisible plumbing (cache, log, "execution layer"). [F/I]

Rentry's own pitch notes are a playbook: one verb per sponsor ("Mubit REMEMBERS"), a branded badge on every remembered item, a log strip of real API calls for technical judges, a pre-seeded returning user, and a hardcoded fallback line. [F]

## 3. What Mubit itself showcases (its demo repos)

Every Mubit demo compares **with vs without** the learning loop on held-out cases and counts **LLM calls, tokens, $ and latency**: SRE incident fleet (repeat incidents need fewer calls), voice callback agent (87.2% vs 10.9% recall of prior calls), radio-spectrum monitoring under drift, expense-report agent, legal benchmark, lifelong-learning benchmarks, meeting action items with prompt-change diffs approved by a human. [F]

**PagerPal** (a public repo by the account e1daru; that this is the host Eldar is our inference) shows the Night Shift flow in the organisers' own words: every Claude call goes through `api.mubit.ai/anthropic`; each suggestion shows its `x-middleware-request-id`; "the engineer corrects that answer in the Mubit console, and Mubit turns the correction into a model update"; "later suggestions come from the updated model"; a `/history` page shows whether each suggestion was right. [F, README read 2026-10-23]

## 4. What they reward (patterns)

1. **A learning loop you can see on stage.** It never changed: "by session three" (Apr), "it still knows you" (May), now "Show a correction turning into a model update in your demo". Invisible use scored lower (+4 vs +10 at Pop the Bubble). [F]
2. **A real person or small business with a recurring job**, ideally with real users or money during the event. Staff praise "self-learning" agents "talking to actual people" and "bold, innovative thinking". [F]
3. **A small stack and a demo that cannot break.** [F]
4. **Measured with-vs-without numbers**, the way their own demos and Latte Bench do it. [F/I]
5. **An audit trail:** request id on every answer, a history of right and wrong. [F]

## 5. What nobody has done yet (openings for tonight)

- A correction turning into a **model update** (all past projects were memory era).
- **Adapter vs frontier side by side** on quality, cost and latency.
- **Fast refresh under drift** (new client, new rules, new document type).
- **Correcting inside the product's own UI** tied to the request id (even PagerPal corrects in the Mubit console).
- Voice served by a small adapter.

Already crowded tonight or too close to Mubit's own examples: on-call / incident triage (their reference demo), invoice and company-accounts readers, claim verification with Banyan Sapling, AI phone receptionists. [F/I]

## 6. What this means for our two candidates [I]

| | PII redaction middleware for documents | Background-check screening |
|---|---|---|
| Visible before/after | Very strong: names blacked out, then restored in the answer | Good: verdict with evidence |
| Correction moment | Crisp: "you missed this account number" | Rich but judgement-based |
| Measurable | Leaks per 100 documents, analysis quality vs original | Accuracy vs ground truth, missed fails |
| Fits Mubit values | Request-path trust (Shankha's theme), adapter must serve | Recurring regulated job, privacy |
| Main risk | Many existing tools; adapter must serve before real documents | Decisions about people; synthetic labels |

Both fit. The pattern from past events slightly favours the redaction middleware for its crisp, visual correction moment, **if** the adapter serves calls (PagerPal's README says later answers "come from the updated model", which suggests it does).

Practical takeaways for either idea:
- Show the request id on every result, and link to the document's session in the Mubit console (Requests filters, including Session, live in the page URL). Note the console's own request ID differs from `x-middleware-request-id`, so link by session, not by request id.
- Build a `/history` view: right vs wrong over time, before and after each model update.
- If Mubit exposes an API for corrections, put the correction button in our UI. Nobody has done that yet.
- Keep the stack small and pre-seed a demo state that cannot fail.
