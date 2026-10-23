# Night Shift idea scan: recurring LLM tasks for Mubit (agent I, 2026-10-23)

Evidence: `work/evidence-I.csv` (59 rows; every quote checked against its raw page). Raw pages: `raw/I-1.md` to `raw/I-51.md` (I-45 failed to fetch and is not cited).
How to read the labels: **fact** means seen in the source. **est.** means my own calculation, with the method shown. **inf.** means my inference. **not verified** means I did not open a source for it this session.
Citations look like `[ev I-n]` and point to rows in evidence-I.csv.

## 0. The short answer

| Rank | Idea | Track | Why it wins |
|---|---|---|---|
| 1 | **Financial complaint triage + "will the ombudsman uphold it?"** (DISP / Consumer Duty) | 1 + 3 | 362,195 public FOS decisions with an upheld/not-upheld label, about 3,000 words each. Firms get about 1.7–1.8m complaints per half-year. Banking data makes the privacy case strong, and the topic fits the team's finance background. |
| 2 | **Motor finance redress eligibility checker** (FCA CONRED rules) | 1 (+3 when the tribunal rules) | 12.1m eligible agreements. The rules are numeric (39% / 10% commission thresholds, £120/£150 floor, 0% APR). No other team is likely to pick this. Risk: the scheme is partly suspended until a hearing in Feb 2027. |
| 3 | **APP scam reimbursement claim triage** (PSR rules) | 1 | 248,070 APP cases in 2025. Every claim needs an in-scope or exception decision. The labels are fixed scam types. A public synthetic scam-dialogue dataset (Apache-2.0) exists. |
| 4 | **Employment claim / grievance coding** (Employment Rights Act phases) | 1 + 3 | 134,956 public tribunal decisions tagged with jurisdiction codes. New duties started 1 Oct and start 30 Oct 2026, with more on 1 Jan 2027. Single tribunal claims rose 39% to 50k. Almost no competition. |
| 5 | **Awaab's Law hazard triage** (social housing repairs) | **3** (best live story) | Phase 2 adds 7 hazard types on **30 Nov 2026**. That lets us demo a model update when a new rule arrives. The response clocks are fixed (24h / 10 working days). Weakness: no public dataset, so the data must be synthetic. |
| 6 | Tenancy agreement checker for the Renters' Rights Act (RRA) — the current lead idea | 1 / 3 | **Weak.** At least 7 AI tools already do this, some for free. The big one-off deadline (31 May 2026) has passed. The privacy angle is weak. See section C. |

Possible combination of #1 and #2: **car-finance complaint triage**. The real inputs are FOS motor hire-purchase decisions (76,160 FOS complaints in 2024/25) and the CONRED rules supply the checkable fields. That gives a real dataset plus a fixed rule set.

## A. Long-list (22 candidates)

| # | Task (recurring) | Buyer | Volume evidence | Data source (36h) | Track | Crowding risk |
|---|---|---|---|---|---|---|
| 1 | Complaint triage: product, root cause, DISP deadline, likely FOS outcome, draft final response | Banks, lenders, insurers | 1.74m complaints at firms in H2 2025 [ev I-24]. FOS got 305,726 new complaints in 2024/25 [ev I-19]. | FOS decisions site: 362,195 decisions with upheld/not-upheld labels [ev I-22]. HF `CFPB/consumer-finance-complaints` (CC0) [ev I-52] | 1, 3 | Med: vendors exist (Ctrl AI, ResolveCX, Good Outcomes, Malted) [ev I-25..28]. Hackathon teams: medium. |
| 2 | Motor finance redress eligibility: pull commission type, amount, APR and dates from agreements, then apply CONRED rules | Motor lenders | 12.1m eligible agreements, about £7.5bn redress [ev I-16]. 76,160 FOS motor HP complaints [ev I-20] | Synthetic agreements plus FOS motor decisions | 1 (3 later) | Low (Ctrl AI mentions it [ev I-25]) |
| 3 | APP scam reimbursement triage: scam type, in scope?, exceptions, vulnerability, reimburse/decline | Banks, EMIs, PSPs | 248,070 APP cases in 2025 [ev I-29]. 89% of in-scope losses reimbursed under PSR rules [ev I-30] | HF `BothBosu/multi-agent-scam-conversation` (Apache-2.0) [ev I-57] plus synthetic claims | 1 | Med: fraud is a popular hackathon theme |
| 4 | Employment claim coding: jurisdiction codes, time-limit check, risk | Employment law firms, HR, legal-expenses insurers | 50k single tribunal claims in 2025/26, up 39% [ev I-36]. About 40k worker-led Acas early-conciliation cases per quarter (est., sum of 4 tracks) [ev I-37] | gov.uk Employment tribunal decisions: 134,956 [ev I-38] | 1, 3 | Low |
| 5 | Harassment / grievance report triage under the new "all reasonable steps" duty (30 Oct 2026) | HR teams, HR software | Duty starts 30 Oct 2026 [ev I-34]. Report counts not found. | Synthetic | 1, 3 | Low |
| 6 | Awaab's Law hazard triage: in scope?, hazard type, emergency vs significant, deadlines | 1,670 social landlords, about 5m households [ev I-41] | 4.1m social-rented households [ev I-6]. 34% of repairs complaints are damp/mould [ev I-42]. Number of repair reports per year: not found | Synthetic tenant messages. HOS reports for realism. | **3** | Med in the market (Engage-Me, Aareon Aidenn, Plentific, Ingentive) [ev I-45..47]. Low in the hackathon. |
| 7 | RRA tenancy agreement compliance check | Letting agents, landlords | 4.7m PRS households [ev I-5]. About 955k PRS households moved in a year (2021-22, dated) [ev I-7] | Synthetic plus public templates. `coastalcph/lex_glue` unfair_tos (CC-BY-4.0) as a stand-in [ev I-54] | 1, 3 | **High**: 7+ live AI tools [ev I-8..14] |
| 8 | MTD Income Tax: put transactions and receipts into HMRC expense categories | Sole traders, landlords, accountants, MTD software | 864k mandated from Apr 2026, another 1.077m from Apr 2027 [ev I-32]. 436k first updates sent [ev I-33] | HF `DoDataThings/us-bank-transaction-categories-v2` (MIT, synthetic US) [ev I-58]. UK mapping is synthetic. | 1, 3 | High in the market (accounting software already auto-categorises: inf., not verified). Short inputs, so small savings. |
| 9 | Data protection complaint + DSAR handling (DUAA: acknowledge within 30 days, from 19 Jun 2026) | Every UK controller | Mandatory from 19 Jun 2026 [ev I-48, I-49]. Volume not found. | Synthetic emails plus PII datasets (not verified) | 1 | Med (redaction vendors; Ctrl AI does SARs) |
| 10 | Insurance "am I covered?": policy wording + claim, answer covered/excluded + clause | Insurers, brokers, MGAs | 45,606 FOS insurance complaints in 2024/25 [ev I-21]. Claim volumes: not found | Public policy wordings (synthetic questions) | 1 | Med-High |
| 11 | NDA triage (ContractNLI hypotheses) | In-house legal | Not found | HF `kiddothe2b/contract-nli` (CC-BY-NC-SA) [ev I-56] | 1 | **High** (generic contract review) |
| 12 | Commercial contract clause extraction | Legal, procurement | Not found | HF `theatticusproject/cuad-qa` (CC-BY-4.0) [ev I-53] | 1 | High |
| 13 | Vulnerable-customer detection in calls and emails (Consumer Duty) | Banks, insurers, utilities | Part of the 1.7m+ complaints per half-year [ev I-24] | Synthetic | 1 | Med-High (Good Outcomes, ResolveCX) [ev I-26, I-27] |
| 14 | Banking intent routing | Banks | Not found | HF `PolyAI/banking77` (CC-BY-4.0) [ev I-55] | 1 | High (classic task) |
| 15 | EU AI Act use-case risk-tier classifier (Annex III / Art 50) | EU compliance teams | High-risk rules now start **2 Dec 2027**. Transparency rules apply from Aug 2026 [ev I-50] | Synthetic | 1, 3 | Med. The 2026 trigger is weaker than it first looked. |
| 16 | Turn invoices into structured e-invoices | B2B suppliers | UK mandate only from **2029** [ev I-51] | Receipt/invoice datasets (not verified) | 1 | High (classic hackathon) |
| 17 | Online Safety Act moderation to Ofcom codes | Platforms | Dates and volumes not verified this session | Many toxicity datasets | 3 | High |
| 18 | Housing Ombudsman-style social-housing complaint handling | Social landlords | 20,016 findings in 2025-26 (raw I-18) | Synthetic | 1 | Med |
| 19 | Tenancy deposit dispute evidence summary (award split) | TDS/DPS adjudicators, agents | Not verified | Synthetic | 1 | Low |
| 20 | KYC adverse-media screening (relevant? risk type) | Banks, fintechs | Not verified | News plus synthetic | 3 | Low-Med |
| 21 | Public tender bid/no-bid + CPV coding (Procurement Act) | SMEs bidding for public work | Not verified | Find a Tender open data (not verified) | 3 | Low |
| 22 | SaaS cancellation-reason + save-offer routing | SaaS CS teams | Not verified | Synthetic / support datasets | 1 | High (support bots) |

## B. Top 6 deep-dives

### Scoring (1 = poor, 5 = strong)

| Idea | Long inputs | Checkable | Data in 36h | Privacy | Buyer volume | Demo wow | Low crowding | Team fit | **Total /40** |
|---|---|---|---|---|---|---|---|---|---|
| 1 Complaint triage + FOS outcome | 5 | 4 | 5 | 5 | 5 | 4 | 3 | 5 | **36** |
| 2 Motor finance redress eligibility | 4 | 5 | 3 | 5 | 5 | 3 | 5 | 5 | **35** |
| 3 APP scam reimbursement triage | 3 | 4 | 4 | 5 | 5 | 4 | 3 | 5 | **33** |
| 4 Employment claim coding | 5 | 4 | 4 | 5 | 4 | 3 | 5 | 2 | **32** |
| 5 Awaab's Law hazard triage | 3 | 5 | 3 | 4 | 4 | 5 | 4 | 3 | **31** |
| 6 RRA tenancy checker | 5 | 4 | 3 | 2 | 3 | 3 | 1 | 2 | **23** |

The scores are my judgement, based on the evidence below.

### 1. Complaint triage + "will the ombudsman uphold it?"
- **Who runs it, how often:** FCA-regulated firms handled 1.74m complaints in H2 2025 and 1.83m in H1 2025 [ev I-24]. That is about 3.5m a year (est. = sum of two halves). Complaints the firm does not resolve go to the FOS: 305,726 in 2024/25, the most for 6 years [ev I-19].
- **Current cost / effort:** in our sources, no number for cost per complaint (not found). Vendors selling AI for this job (Ctrl AI, ResolveCX, Good Outcomes, Malted [ev I-25..28]) show buyers pay for it (inf.).
- **Why it's checkable:** the output schema is product group (FCA list), root cause, upheld yes/no, redress band, DISP deadline (rule-based). Every FOS decision carries an upheld/not-upheld label and a sector [ev I-22].
- **Data:** the FOS decision database has 362,195 decisions since 1 Apr 2013 [ev I-22]. A Lloyds engineer's hackathon repo says decisions run about 3,000 words each, about 25k a year [ev I-23]. That is long input, so the savings argument is real. FOS terms of reuse: **not verified** (decisions are anonymised by FOS). Fallback: HF `CFPB/consumer-finance-complaints`, CC0, 1M–10M rows with product/issue labels [ev I-52].
- **Privacy:** customer financial data, regulated by the FCA, so a self-hosted model is a real selling point (inf.).
- **Correction moment:** the complaint handler changes "not upheld → upheld, root cause = affordability checks". Mubit retrains, and the adapter now catches the pattern on the next 20 cases.
- **Track:** 1. Track 3 when new redress events or products arrive (e.g. motor finance).
- **Crowding:** medium. Vendors exist. At the hackathon, "complaint bot" teams will likely build chat, not FOS-grounded outcome prediction (inf.).

### 2. Motor finance redress eligibility (CONRED)
- **Who runs it, how often:** motor lenders, across 12.1m eligible agreements (6 Apr 2007 – 1 Nov 2024). Expected redress is about £7.5bn and the total cost £9.1bn [ev I-16]. The FCA's own table puts non-redress cost at £1.6bn. That is about £130 of handling cost per eligible agreement (est. = £1.6bn / 12.1m).
- **Why it's checkable:** fixed tests. Was there a discretionary commission arrangement (DCA)? Was commission ≥39% of the total cost of credit **and** ≥10% of the loan? Was there a contractual tie (unless visible manufacturer links)? Fair by default if commission was ≤£120 (pre-2014) or ≤£150, or if APR was 0% [ev I-18]. The LLM pulls these fields out of messy agreements and complaint letters. The rules engine then gives the verdict.
- **Data:** synthetic agreements and commission records (believable). FOS motor-finance decisions add realism.
- **Privacy:** consumer credit files. **Team fit:** finance ops.
- **Risk (important):** parts of the scheme are suspended after a legal challenge. The hearing is 16–26 Feb 2027, and until then "lenders do not need to calculate or pay compensation" [ev I-17]. Complaints still arrive (76,160 FOS motor HP complaints in 2024/25 [ev I-20]), and lenders must be ready by 2027.
- **Correction moment:** the analyst fixes the extracted "commission = £410 (not £41)" and the verdict flips. The adapter learns the document layout.
- **Demo wow risk:** judges may ask "why not just a rules engine?". Answer: extraction from scanned or varied documents is the hard part.

### 3. APP scam reimbursement triage
- **Volume:** 248,070 APP cases and £576.4m losses in 2025 [ev I-29]. Mandatory PSR reimbursement covered 89% of in-scope losses in its first 15 months [ev I-30]. So every claim needs a decision.
- **Why it's checkable:** UK Finance uses 8 scam types (purchase, investment, romance, advance fee, invoice/mandate, CEO, impersonation ×2; from the report's methodology, not in the saved raw). Plus in scope yes/no and exception flags. The exact PSR value cap and claim window: **not verified** here.
- **Data:** HF `BothBosu/multi-agent-scam-conversation` (Apache-2.0, synthetic phone dialogues) [ev I-57] plus synthetic claim forms.
- **Correction moment:** the fraud analyst relabels "impersonation → investment scam" or "vulnerable = yes", and the adapter updates.
- **Crowding:** fraud detection is popular. Reimbursement triage is narrower and more defensible (inf.).

### 4. Employment claim coding (ERA 2025 phases)
- **Triggers:** the tribunal time limit went from 3 to 6 months on 1 Oct 2026. The harassment "all reasonable steps" duty starts 30 Oct 2026. The 6-month unfair-dismissal qualifying period applies from 1 Jan 2027 [ev I-34, I-35].
- **Volume:** 50k single tribunal claims in 2025/26, up 39% [ev I-36]. Acas: 39,822 worker-led individual early-conciliation cases in Jan–Mar 2026 (est. = sum of 4 track tables) [ev I-37].
- **Data:** 134,956 public decisions since Feb 2017, filterable by jurisdiction code [ev I-38]. The text is long and the labels are fixed. Licence: gov.uk default OGL (**not verified** for decisions). Cost: scraping PDFs takes a few hours.
- **Privacy:** HR and special-category data. **Team fit:** weak (no employment-law background).

### 5. Awaab's Law hazard triage (best Track 3 story)
- **Rules:** emergency hazards must be investigated and made safe within 24h. Significant hazards must be investigated within 10 working days, with a written summary in 3 days and safety work in 5 days [ev I-40]. **Phase 2 on 30 Nov 2026** adds excess cold/heat, falls, structural collapse, fire, electrical and domestic hygiene [ev I-39, I-44]. Phase 3 will add all remaining HHSRS hazards.
- **Buyer and volume:** 1,670 member landlords covering about 5m households [ev I-41]. The Ombudsman says early 2026-27 cases show landlord teams "are struggling" to spot when Awaab applies [ev I-43]. That pain matches the task exactly.
- **Demo:** run the phase-1 schema, then switch on the phase-2 hazard list live. Officers correct mislabels, Mubit retrains, and accuracy on the new hazards climbs. Track 3 in one picture.
- **Weak points:** tenant messages are short (less saving per call; add repair history to make inputs longer). No public dataset. Vendors exist (Engage-Me, Aareon Aidenn, Plentific) [ev I-45..47].

### 6. RRA tenancy checker: see C.

## C. Honest check of the tenancy idea

- **Volume:** 4.7m private-rented households in England in 2024-25 [ev I-5]. 955k PRS households had moved within the last year in 2021-22 (dated): 620k moves within the sector plus about 219k new households [ev I-7]. So roughly 0.6–1.0m new tenancies a year (est.). **Each landlord or agent issues few templates and reuses them.** The recurring volume is in agent template reviews and new-tenancy written statements, not millions of distinct documents (inf.).
- **The trigger has peaked:** the one-off wave was the Information Sheet for existing tenancies, due by **31 May 2026** [ev I-2, I-4]. What remains: written key-terms information for new tenancies (fine up to £7,000) [ev I-3], the PRS database from late 2026, the landlord ombudsman in 2028, and Awaab's Law / Decent Homes for the PRS (date TBC) [ev I-1]. Landlord HQ says database registration runs "region by region from 15 December 2026" (vendor claim).
- **Who pays, and how much:** prices are low and falling. Landlord HQ from £9.99/mo [ev I-8]. Contract Icks £49/scan or £299/month for agents [ev I-9]. RightTo.Rent £99/property [ev I-12]. LeaseScan $4.99 [ev I-11]. HomeLet/letting.zone and PAM are free [ev I-10, I-13].
- **Competitors already doing AI lease review in the UK (7+):** Landlord HQ (check plus "fix my agreement"), Contract Icks, HomeLet/letting.zone, LeaseScan, RightTo.Rent, PAM, HomeThink. Rent Fix also appeared in search (page not opened).
- **Legal risk:** reviewing a tenancy is not a reserved legal activity under the Legal Services Act 2007 s.12. The reserved list covers rights of audience, litigation, reserved instruments, probate, notarial work and oaths [ev I-15]. So it is lawful to offer (inf.). The risk is liability: a false "compliant" verdict could expose a landlord to a £7,000 penalty or a failed possession claim. Every competitor disclaims "not legal advice".
- **Privacy:** agreements hold names, addresses and rent. That is personal but low-sensitivity, so "own your model" is weaker than for banking or HR data (inf.).
- **Verdict:** in a hackathon of 100+ teams, this idea is easy to explain, but it scores low on crowding and on privacy, and the deadline spike has passed. If you keep housing, **switch to Awaab's Law triage** (#5): it has a live rule change on 30 Nov 2026 and stricter clocks. Or reframe it for the agent side, as **portfolio re-checking whenever a rule changes** (Track 3), not a one-off scan.

## D. The 3 best datasets

| Dataset | Id / location | Size | Labels | Licence | Best for |
|---|---|---|---|---|---|
| CFPB Consumer Complaint Database | HF `CFPB/consumer-finance-complaints` (fresher mirror `Mouwiya/cfpb-consumer-complaints`, licence "other") | 1M–10M | product, sub-product, issue, company response | **CC0-1.0** [ev I-52] | #1 (fallback with a clean licence) |
| FOS ombudsman decisions | financial-ombudsman.org.uk/decisions-case-studies/ombudsman-decisions/search | 362,195 since Apr 2013, about 3,000 words each | upheld/not upheld, sector, firm | **Not verified** (anonymised and public; check the site terms before scraping) [ev I-22, I-23] | #1, #2 (UK, long inputs, real outcomes) |
| Scam / non-scam phone dialogues | HF `BothBosu/multi-agent-scam-conversation` | 1K–10K | scam / non-scam (+ personality) | **Apache-2.0** [ev I-57] | #3 |

Also usable: gov.uk Employment tribunal decisions (134,956, jurisdiction codes, OGL not verified) [ev I-38]. `coastalcph/lex_glue` unfair_tos (CC-BY-4.0) [ev I-54]. `nguha/legalbench` (CC-BY-4.0) [ev I-59]. `theatticusproject/cuad-qa` (CC-BY-4.0) [ev I-53]. `PolyAI/banking77` (CC-BY-4.0) [ev I-55]. `DoDataThings/us-bank-transaction-categories-v2` (MIT, synthetic) [ev I-58]. `kiddothe2b/contract-nli` (CC-BY-NC-SA, non-commercial) [ev I-56].

## E. Triggers checked: which are live in 2026

| Trigger | Status (source) | Effect on ideas |
|---|---|---|
| Renters' Rights Act phase 1 | Live 1 May 2026. Info Sheet due 31 May 2026. Database late 2026 [ev I-1..4] | Spike passed |
| Employment Rights Act | 6 Apr, 1 Oct, 30 Oct 2026 and 1 Jan 2027 phases [ev I-34, I-35] | Live and rising |
| MTD Income Tax | Live 6 Apr 2026 for 864k. Next wave Apr 2027 [ev I-31..33] | Live, but crowded and short inputs |
| PSR APP reimbursement | Running since Oct 2024 [ev I-30] | Steady high volume |
| FCA motor finance scheme | Rules made Mar 2026. Partly suspended, hearing Feb 2027 [ev I-16, I-17] | Big, but uncertain timing |
| Consumer Duty / complaints | About 1.7–1.8m complaints per half-year [ev I-24] | Steady high volume |
| Awaab's Law | Phase 1 since 27 Oct 2025. Phase 2 on 30 Nov 2026 [ev I-39, I-44] | Live rule change, ideal for Track 3 |
| DUAA complaints duty | 19 Jun 2026 [ev I-48, I-49] | Live, volume unknown |
| EU AI Act | High-risk delayed to 2 Dec 2027. Transparency Aug 2026 [ev I-50] | Weaker than expected |
| UK e-invoicing | Mandate from 2029 [ev I-51] | Too early |
| Online Safety Act, EAA, CSRD, leasehold | Not verified this session | Low priority |

## Gaps
- Cost per complaint, per APP claim and per repair triage: not found.
- FOS decision reuse terms: not checked.
- UK Finance scam-type list and PSR thresholds: taken from the report PDF's search highlight, not saved.
- Insurance claim volumes, NDA volumes and Online Safety Act dates: not verified.
