# PII detection and redaction: methods, models, evaluation (for Veil)

Agent: R (methods). Date: 24 Oct 2026. Boundary: methods, models, papers, formats, evaluation (datasets, Mubit and the generator are other agents' work).
Raw pages: `scratchpad/pii/raw/R-<n>.md` (first line = URL). arXiv abstracts for 30 papers are in `R-36.md`; four more in `R-66.md`. Evidence rows: `evidence-R.csv`.
Tags: **KNOWN** = number seen in the source (source, dataset, date given); **INFERENCE** = my reasoning. Vendor numbers are claims by a party that sells the fix.

## 0. Key takeaways
1. **Numbers do not transfer across datasets.** The same detectors score 0.93 F1 on their own test split and 0.38 to 0.48 on an out-of-distribution benchmark (SPY). Rule-based Presidio is last or near last on every 2025-2026 benchmark found (TAB, PIIBench, REDACT, PII-TRACE, RAT-Bench). We must report our own numbers on our own held-out set and say they are synthetic.
2. **LLMs are the strongest detectors in recent benchmarks** (REDACT: Claude Sonnet 4.6 0.636, GPT-4.1 0.597 partial micro-F1; PII-TRACE: frontier LLMs 0.49 to 0.61 character F1), but none is near perfect. A distilled small model (our Mubit adapter) learning from a frontier teacher is a sound plan; OpenAI's Privacy Filter shows that fine-tuning on a little in-domain data moves F1 from 0.545 to 0.962 (SPY).
3. **Entity-level, all-mentions recall is the metric that matches "leaks".** TAB counts an entity as protected only if every mention is masked. Presidio's mention recall on TAB looked like 0.70 while its entity recall on direct identifiers was 0.46.
4. **Typed, indexed, reversible placeholders preserve LLM answer quality better than redaction** (2609.11335). Over-masking non-personal entities causes wrong answers.
5. **Pseudonymised is not anonymised** (ICO). Veil's honest claim: direct identifiers are replaced before text leaves; the provider sees pseudonymised text; quasi-identifiers can remain.

---

## 1. State of the art (2024 to 2026)

### 1.1 Rules + classic NER (Presidio, spaCy, Flair)
**Mechanism.** Presidio runs "recognizers": regex patterns with checksums and context words, plus an NER model (spaCy, Stanza or transformers) for PERSON, LOCATION, NRP; an anonymizer then applies operators (replace, mask, hash, encrypt). Docs have moved from microsoft.github.io to `data-privacy-stack.github.io/presidio` (R-13). UK recognizers exist for `UK_NHS` (regex + mod 11), `UK_NINO`, `UK_PASSPORT`, `UK_POSTCODE`, `UK_DRIVING_LICENCE`, `UK_VEHICLE_REGISTRATION` (R-13; source files R-19 to R-23). The UK folder has no sort code, UK account, VAT, UTR or Companies House recognizer (KNOWN from the folder listing; `IBAN_CODE` and `CREDIT_CARD` are global). Presidio also documents "Using GLiNER as an external PII model" (R-13).

**Known defects for our use.** `UK_PASSPORT` matches `[A-Z]{2}\d{7}`, but HM Passport Office says all series use 9 digits (R-22, R-24, open issue R-25). The driving licence check characters cannot be verified because "the DVLA check digit algorithm is not public" (R-19).

**Reported numbers (KNOWN).**
| Benchmark (date) | Presidio result | Comparison | Source |
|---|---|---|---|
| TAB, ECHR court cases, test set (2022) | ER_di 0.460, ER_qi 0.758, mention recall 0.707, WP 0.790 (default config, v2.2.23) | RoBERTa OntoNotes NER: ER_di 0.940, precision 0.441; fine-tuned Longformer: ER_di 1.000, ER_qi 0.916 | R-37 Tables 7, 9 |
| PIIBench, 10 merged datasets (Apr 2026) | best of 8 systems, span F1 0.1385, "zero recall on most entity types" | spaCy, BERT NER, Piiranha, others lower | R-36 (2604.15776) |
| REDACT, 25 languages, 1,000 records (Jun 2026) | partial micro-F1 0.195; HIGH-sensitivity recall 0.07 | GPT-4.1 0.74, Claude Sonnet 4.6 0.77 HIGH-tier recall | R-40 |
| PII-TRACE, multi-turn dialogues (Aug 2026) | character P 0.045, R 0.762; "marks 16 times the gold volume" | OpenAI PF char F1 0.492 | R-46 Table 3 |
| RAT-Bench, re-identification after anonymisation (Feb 2026) | 41% (easy) / 77% (hard) of profiles re-identified | GPT-4.1 prompt: 26% / 58%; Azure 22% / 33% | R-39 Table 1 |

Why Presidio fails on TAB: it "fails to detect all court case numbers (a category it was not trained on)" (R-37). This is our `CUSTOM` problem exactly (client codes, matter numbers).

**spaCy / Flair.** `en_core_web_trf` reports NER F 0.902 (R-63); Flair `ner-english-large` reports F1 94.36 on corrected CoNLL-03 (R-64). These are general NER scores: they find every PERSON/ORG/GPE, not "personal data about the subject". In TAB the generic NER model over-masked ("more than half of the tagged entities did not need to be masked", precision 0.441) (R-37).

**Strengths:** deterministic, fast, explainable, checksums for structured IDs. **Failure modes:** unseen ID formats, non-standard writing (RAT-Bench: "312, then 480, then 3820"; slang "C-way" for Conway), missed duplicates, poor precision when ORG/LOCATION are enabled (R-37, R-39).

### 1.2 Small encoder models (GLiNER family, token classifiers)
**Mechanism.** GLiNER is a bidirectional encoder that takes text plus a list of label names and scores spans for each label, so the label set is chosen at inference time (R-36, 2311.08526; R-3). Token classifiers (DeBERTa, OpenAI Privacy Filter) tag each token with BIO/BIOES labels from a fixed taxonomy.

| Model (HF id) | Size | Licence (verbatim tag) | Reported numbers (dataset, date) | Notes |
|---|---|---|---|---|
| `openai/privacy-filter` | 1.5B total, 50M active | `apache-2.0` | PII-Masking-300k token F1 0.960 (span 0.926); corrected labels 0.974 (0.942). SPY zero-shot token F1 0.545, 0.962 after fine-tuning on 10% of SPY train (Apr/Aug 2026) | 8 labels (account_number, private_address, private_email, private_person, private_phone, private_url, private_date, secret); banded attention, effective window 257 tokens; 128k context; Viterbi decoding with tunable operating points (R-10, R-11, R-12) |
| `fastino/gliner2-privacy-filter-PII-multi` (GLiNER2-PII) | 205M (card); "0.3B" (paper) | `apache-2.0` | SPY exact span avg F1 0.477 (P 0.35 to 0.37, R 0.69 to 0.75) vs nvidia 0.400, urchade 0.398, OpenAI PF 0.380 (May 2026, model author's own eval) | 42 labels; trained on 4,910 synthetic texts made by GPT-5.4; "tends to over-predict name entities" (R-1, R-36) |
| `nvidia/gliner-PII` | 5.7 x 10^8 params | `other` (NVIDIA Open Model License; card says ready for commercial use) | strict F1: Argilla PII 0.70, AI4Privacy 0.64, Nemotron-PII 0.87 at threshold 0.3 (Oct 2025) | trained on ~100k synthetic records, 55+ types, US and international formats (R-4) |
| `knowledgator/gliner-pii-{edge,small,base,large}-v1.0` | not stated in card | `apache-2.0` | F1 75.50 / 76.84 / 80.99 / 83.25 on `synthetic-multi-pii-ner-v1` (vendor benchmark) | the card's text calls base the best while its own table shows large higher (R-3) |
| `urchade/gliner_multi_pii-v1` | not stated | `apache-2.0` | F1 76.86 (knowledgator's benchmark, R-3); SPY avg 0.398 (R-1) | trained on synthetic Mistral data (R-2) |
| `E3-JSI/gliner-multi-pii-domains-v1` | not stated | `apache-2.0` | F1 76.36 (knowledgator's benchmark) | fine-tune of urchade model (R-6, R-3) |
| `iiiorg/piiranha-v1-detect-personal-information` | mDeBERTa-v3-base | `cc-by-nc-nd-4.0` | token F1 93.12 on its own ~73k-sentence test split; PII vs non-PII recall 98.27% (R-5) | 256-token context ("just split it up"); **non-commercial, no derivatives: do not ship or fine-tune it** |
| `lakshyakh93/deberta_finetuned_pii` | DeBERTa | `mit` | no metrics reported (R-7) | |

**Out-of-distribution reality (KNOWN).** "Unmasking the Reality of PII Masking Models" (17k semi-synthetic sentences incl. UK formats, Apr 2025): models output no PII at all in 28% of 51k predictions; Piiranha returned nothing for 47.4% of passport and 61.4% of vehicle-registration cases (R-38 Table 4). REDACT: GLiNER 0.320, OpenAI PF 0.512 partial micro-F1 (R-40). PII-TRACE: GLiNER2-PII 0.292, NVIDIA GLiNER-PII 0.392, OpenAI PF 0.492 character F1 (R-46).

**Context matters (KNOWN).** OpenAI PF recall overall: 0.584 with no category clue, 0.863 with the clue before the value; `private_address` 0.214 vs 0.414; `private_phone` 0.318 vs 0.919 (R-12 Table 5). Bare values without a label word are much harder.

**Failure modes stated by OpenAI (R-10):** "under-detection of uncommon personal names, regional naming conventions, initials, honorific-heavy references, or domain-specific identifiers; over-redaction of public entities, organizations, locations, or common nouns"; "fragmented or shifted span boundaries in mixed-format text, long documents, or text with heavy punctuation and layout artifacts".

### 1.3 LLM-based extraction
- **Mechanism:** prompt a general LLM (zero/few-shot) to list PII spans or rewrite text; or iterate with an attacker LLM.
- **REDACT (Jun 2026):** Claude Sonnet 4.6 0.636, GPT-4.1 0.597 partial micro-F1, ahead of OpenAI PF 0.512, GLiNER 0.320, Presidio 0.195. LLM predictions had to be "matched after offset relocation" (R-40). INFERENCE: this supports our T1 design (model returns text + type; code finds offsets).
- **PII-TRACE (Aug 2026):** GPT-5.6-sol 0.611, Claude Sonnet 5 0.567, Claude Opus 4.8 0.528, GPT-5.4 0.512 character F1, zero-shot; a 0.6B detector trained with conversation-level supervision had the best coverage (0.830 of gold characters) (R-46).
- **RAT-Bench (Feb 2026):** LLM anonymizers give "a better privacy-utility trade-off albeit at a higher computational cost" and "work well across languages" (R-36, R-39).
- **RECAP (Oct 2025):** regex + LLM hybrid beats fine-tuned NER by 82% and zero-shot LLMs by 17% weighted F1 in 13 low-resource locales (R-36). Hybrid is the common recipe.
- **PII-Bench (Feb 2025):** LLMs are adequate at basic detection but struggle to decide query relevance, especially with several people in one text (R-36).
- **Adversarial anonymisation (Staab et al., 2024):** LLM-based anonymizer beat commercial anonymizers on utility and privacy, human study n=50 (R-36, R-47).
- **Failure modes:** non-determinism, invented or normalised spans (offset relocation), cost and latency, and teacher errors become student errors (INFERENCE for the Mubit adapter, since it is graded on matching the teacher).

### 1.4 Privacy-preserving prompting (papers)
| Idea | Paper | Mechanism | Reported result (KNOWN) |
|---|---|---|---|
| Sanitise then restore | HaS, 2309.03057 (2023) | small local "Hide" model anonymises, "Seek" model de-anonymises the LLM answer | evaluated on translation and classification (R-36, R-43) |
| Browser-side sanitiser | Casper, 2408.07004 (2024) | rule filter + NER + local LLM topic detector | 98.5% PII and 89.9% topic filtering on 4,000 synthetic prompts (R-36) |
| Local + cloud delegation | PAPILLON, 2410.17127 (2024) | local model writes a privacy-preserving prompt for the cloud model | quality kept for 85.5% of queries, leakage 7.5% (PUPA) (R-36) |
| Pseudonymisation framework | 2502.15233 (2025) | detect, generate replacements, restore after generation | "optimal balance" claimed (R-36, R-44) |
| Format-preserving encryption + metric DP | Prεεmpt, 2504.05147 (2025) | FPE for format-only values (card numbers), mDP for values the answer depends on (age, salary) | "high utility" vs unsanitised prompts (R-36) |
| Graph-guided sanitisation | PromptGraph, 2607.10709 (2026) | span privacy scores + pairwise utility dependencies; placeholders restored "only after passing local consistency checks" | better trade-off than baselines (R-66) |
| DP rewriting | DP-Prompt, 2310.16111 (2023) | LLM paraphrase with local DP | 46% lower author identification F1 with sentiment F1 kept (IMDB) (R-36) |
| Attacks on sanitisation | 2410.17052 (2024) | optimal reconstruction attacks on DP token replacement | one attack improves 46.4% over baseline (R-36) |

**Leakage and inference risks (why redaction alone is not anonymity):**
- LLMs infer personal attributes from text "achieving up to 85% top-1 and 95% top-3 accuracy" on real Reddit profiles; text anonymisation did not stop it (2310.07298, R-36).
- When summarising 100 cover letters, ChatGPT kept PII verbatim in 57.4% of cases (2305.15008, R-36).
- Even with an anonymising proxy, prompt content re-identified 50 to 75% of SWE-Chat users at 10% false acceptance (2609.33903, R-36).
- DIRI: an LLM re-identified 9% of clinical notes after the best de-identifier masked all detected PII (2410.17035, R-36).

**Contextual integrity:** ConfAIde: GPT-4 and ChatGPT reveal private information in contexts where humans would not, 39% and 57% of the time (2310.17884, R-36). PrivacyLens: models answer probing questions well but leak when acting as agents (2409.00138, R-36). "Say Something Else" (2604.06409): free-text pseudonymisation gives the best privacy-utility trade-off, and single-message evaluation underestimates leakage (up to 16.3 pp) (R-66). INFERENCE: out of scope for the demo, but cite as roadmap (spec 7.8 already excludes inference attacks).

### 1.5 Commercial approaches (high level, vendor claims)
- **Private AI** (docs now branded "Limina"): "over 50 unique entity types", subtypes (e.g. LOCATION_CITY), international variants mapped to one type (sort codes listed under a banking type), custom entity types on the Scale plan (R-58). No accuracy number saved.
- **Nightfall Firewall for AI:** API scans outgoing prompt text and returns findings plus a redacted payload; claims "≥95% precision/recall" and "≤100ms P99 latency" (vendor page, R-61). Low weight: seller of the fix, no method.
- **Skyflow LLM Privacy Vault:** "De-identify prompts, retrieved context, and agent payloads before they reach any model, then re-identify responses through policy-gated detokenization" (R-60, page as fetched 24 Oct 2026); docs list "more than 40 languages with support for 60 entity types" and token styles such as vault tokens `NAME_ABC123`, entity-unique counters, format-preserving tokens (R-65).
- **Cloud DLP:** Google Sensitive Data Protection has UK infoTypes (UK_NATIONAL_INSURANCE_NUMBER, UK_NATIONAL_HEALTH_SERVICE_NUMBER, UK_PASSPORT, UK_DRIVERS_LICENSE_NUMBER, UK_TAXPAYER_REFERENCE, UK_ELECTORAL_ROLL_NUMBER) (R-53) and pseudonymisation by deterministic AES-SIV encryption, format-preserving encryption, hashing, with optional surrogate annotation for re-identification (R-54). AWS Comprehend lists UK_NATIONAL_INSURANCE_NUMBER, UK_UNIQUE_TAXPAYER_REFERENCE_NUMBER, UK_NATIONAL_HEALTH_SERVICE_NUMBER (R-55). Azure AI Language lists UK NI, NHS, passport, driving licence, UTR and electoral roll numbers (R-56). On RAT-Bench Azure had the largest risk reduction "at the cost of aggressive text redaction" and low BLEU (R-39).
- **Pattern across vendors (INFERENCE):** detection = regex/checksum + ML; protection = consistent tokens + vault + policy-gated restore. Veil's difference is the trainable, correction-driven model and org-specific `CUSTOM` identifiers.

---

## 2. What makes redaction hard
Concrete, plantable patterns with labels are in `hard-cases.md` (108 cases). Mechanisms, with evidence:

| Difficulty | Evidence | What to plant |
|---|---|---|
| Names that are common words, places, months; lowercase names in chat | GLiNER2-PII over-predicts names, "confusing common nouns, organisation names, and product names" (R-1); OpenAI PF over-redacts "common nouns when local context is ambiguous" (R-10) | Will/will, Rose Cottage, April, Grace period, "mark as paid" |
| Uncommon, transliterated, non-English names; initials; honorifics | OpenAI PF under-detects "uncommon personal names, regional naming conventions, initials, honorific-heavy references" (R-10); Unmasking lists nicknames, aliases, typos (R-38) | Oleksandr/Aleksandr/Alexander; Siobhán Ní Bhriain; "O.K."; "Mr P." |
| Non-standard forms (split, spelled out, obfuscated) | RAT-Bench: re-id risk 44% easy vs 69% hard across tools; NER fails on "312, then 480, then 3820" and slang (R-39) | "seven seven double-oh..."; "o.kovalenko [at] example [dot] com" |
| Bare values without a clue word | OpenAI PF recall 0.584 without clue vs 0.863 with clue; phone 0.318 vs 0.919 (R-12) | table cells, footers, CSV rows |
| Consistency across mentions | TAB: entity masked only if all mentions masked (R-37); RAT-Bench: a tool "may remove some but not all mentions of a name" (R-39); PII-TRACE: recurring identifiers across turns (R-46) | full name once, then surname only, nickname, initials, possessive |
| Long documents and chunk boundaries | PII-TRACE: "single-pass reading loses a third of the gold characters on long dialogues" (R-36); OpenAI PF effective attention window 257 tokens (R-10); Piiranha 256 tokens (R-5) | value cut by chunk edge; name defined in chunk 1 used in chunk 4 |
| PDF and layout artefacts | OpenAI PF: shifted spans with "layout artifacts" (R-10); PDF parsers differ by document type and all struggle on some categories (2410.09871, R-66) | hyphenation, two columns, headers/footers, tables, ligatures, no-break spaces |
| Personal vs non-personal entity of the same type | SPY "labels only information about the question author as PII" (R-12); TAB: many persons, places, organisations in court cases need no masking (R-37); SPY paper: tools "often fail to distinguish between personal and non-personal entities" (R-48) | company vs sole trader, public helpline vs personal phone, signatory vs judge |
| Quasi-identifiers | TAB: 4.4% of entities direct identifiers, 63% quasi-identifiers (R-37); RAT-Bench: with 9 indirect identifiers and no direct ones, Presidio re-id reaches 60% (R-39); Sweeney (cited in R-39): ZIP code, birth date and gender uniquely identify 87% of Americans | job title + employer + town; DOB + postcode |
| Weak checksums and examples that fail them | local test: 9.1% of random 10-digit strings pass NHS mod 11; 18.2% pass the UTR check; NHS's own examples `999 123 4567` and `999 123 4566` fail mod 11; HMRC's `QQ 12 34 56 A` fails NINO rules (uk-formats.md) | transaction IDs, invoice numbers, template examples |

---

## 3. Evaluation

### 3.1 Matching levels
- **Token level:** each token is PII or not (or typed). Lenient to boundary errors; inflated by easy tokens. Piiranha's 99.44% accuracy is token-level with mostly non-PII tokens (R-5).
- **Span / entity level (SemEval-2013 schemes, as in nervaluate):** *strict* = exact boundary and type; *exact* = exact boundary, any type; *partial* = overlapping boundary, any type; *type* = overlap with correct type (R-62). OpenAI PF shows the gap: 0.960 token F1 vs 0.926 span F1 on the same data (R-12).
- **Character level and containment:** PII-TRACE scores character P/R/F1 plus span overlap and span containment (gold fully covered) (R-46). Containment is closest to "did it leak".
- **Entity across mentions:** TAB ER_di / ER_qi: an entity is a true positive only if all of its mentions are masked; recall is micro-averaged over annotators; separate recall for direct and quasi identifiers (R-37).
- **Utility-weighted precision:** TAB WP_di+qi weights each wrongly masked token by its information content from BERT, so masking informative words costs more (R-37).
- **Recall over precision:** privacy-first work often uses F2 (recall weighted double) (R-37).

### 3.2 Utility after redaction
- Downstream task score on redacted vs original input (2306.05561 for classification and summarisation, R-36; 2609.11335 for 11 benchmarks, R-67). 2609.11335: reversible techniques that keep entity uniqueness "significantly outperform irreversible ones like redaction", and "explicitly prompting models about anonymization offers no discernible benefit"; more capable models dropped more (R-66, R-67).
- Text similarity (BLEU) between original and anonymised text (RAT-Bench, R-39). Weak proxy for answer quality.
- Response quality vs leakage pairs (PAPILLON: 85.5% quality, 7.5% leakage, R-36).

### 3.3 Re-identification risk
- **Attacker LLM inference:** RAT-Bench lets an LLM infer attributes from anonymised text and turns them into population-level re-identification risk using US demographic statistics (R-39). Staab et al. measure what an adversarial LLM can still infer (R-47). DIRI asks an LLM to pick the patient for a redacted note (R-36).
- **Motivated intruder test:** ICO's recommended starting point for identifiability (R-18).
- **Survey (2512.01109):** 47 papers, six privacy notions: identifier removal, dataset membership, attribute inference, reconstruction attacks, semantic inference, theoretical bounds (R-42).

### 3.4 Recommended metric set for the Veil demo
All computed by code on the held-out eval split (synthetic, document-level sessions). Normalise before string matching (case, spaces, hyphens; digits-only for numbers).

| Metric | Definition | Why | Target / note |
|---|---|---|---|
| **Leaks per 100 documents** (headline) | count of ground-truth values (any surface form, normalised) found in the text sent to T2, per 100 docs | matches the threat model; independent of span boundaries | report per type; NFR-1: 0 for account, card, NI, IBAN |
| **Documents with zero leaks** | share of eval docs with 0 leaked values | easy for judges | |
| **Entity-level all-mentions recall per type** (TAB-style ER) | entity protected only if every mention is replaced; split direct (PERSON, IDs, account) vs quasi (DOB, address parts) | consistency failures show up here | |
| **Span precision / recall / F1 per type, strict and partial** (nervaluate) | strict for regex types; partial for PERSON, ADDRESS | comparability with papers | |
| **Over-redaction rate** | placeholders on keep-trap spans (amounts, ordinary dates, clause numbers, public companies) / number of keep-trap spans planted | utility; judges see it in the three-panel view | plant keep traps on purpose (hard-cases.md) |
| **Answer parity** | per-document Q&A with known answers; exact match on fields, original vs redacted+restored | the real utility claim (NFR-2) | include questions whose answer IS a personal value ("Who is the landlord?") to test restoration |
| **Restoration success** | share of placeholders in T2 answers mapped back; count of unknown or malformed placeholders | detects paraphrased placeholders | |
| **Latency p50 / p95 per chunk** and **cost per document** | redaction step only, adapter vs teacher | NFR-3 | |
| **Served-by-adapter share** | share of T1 calls served by our model | Mubit story | |
| **Time to fix** | from correction to first version that catches the pattern | learning story | |

Say what the numbers do not prove: synthetic UK English documents only; quasi-identifier inference not measured (RAT-Bench and DIRI show this risk is real).

---

## 5. Consistent pseudonymisation and restoration

### 5.1 Placeholder design
- **Typed + indexed + bracketed:** `[PERSON_1]`, `[ACCOUNT_1]`. Evidence: uniqueness-preserving placeholders (`<LOC>-1`, `<LOC>-2`) keep LLM performance better than plain redaction (R-67); llm-guard uses `[REDACTED_PERSON_1]` (R-51); Skyflow offers entity-unique counters and vault tokens like `NAME_ABC123` (R-65).
- **Placeholders vs fake surrogates:** llm-guard (`use_faker`) and LangChain's `PresidioReversibleAnonymizer` can substitute realistic fake values (R-51, R-52). Surrogates read naturally and avoid tipping the model off, but (INFERENCE) they can collide with real text, are harder to restore unambiguously, and the user cannot see what was hidden. For the demo, brackets are clearer in the "what the provider saw" panel.
- **One value, one placeholder, per conversation** (FR-5). Canonicalise before lookup: case, whitespace, digits-only for numbers (`3192 6819` = `31926819`), postcode spacing.
- **Aliases of the same person** (full name, surname, nickname, initials): map to the same `[PERSON_n]` when the link is certain (same surname + title in the same document), else a new index. Store each original surface form so restoration can put back the form that was replaced at that position, or the fullest form in answers (decision; INFERENCE).
- **Possessives and punctuation:** replace the name only: `Kovalenko's` → `[PERSON_1]'s`.
- **Keep the type in the token** so the LLM can still reason ("[PERSON_1] is the landlord").
- **Do not over-mask:** replacing non-personal entities ("Earth", "Sun", "Europe") made GPT-4o mini answer wrongly or invent a placeholder-style answer `<COUNTRY NAME>` (R-67).
- **Format-preserving option for numbers** (later): FPE keeps shape for format-only tasks (Prεεmpt, Google FPE) (R-36, R-54).

### 5.2 Handling a model that paraphrases placeholders
Restoration pipeline (tested strategies exist in llm-guard and LangChain):
1. Exact match `[PERSON_1]` (llm-guard default `EXACT`) (R-50).
2. Case-insensitive and tolerant regex: `\[?\s*PERSON[\s_-]*1\s*\]?`, also `Person 1`, `PERSON-1`, `[Person_1]` (FR-7).
3. Fuzzy match with a small Levenshtein distance (LangChain `fuzzy_matching_strategy`, default `max_l_dist=3`; `combined_exact_fuzzy_matching_strategy` recommended there) (R-52); llm-guard offers `CASE_INSENSITIVE`, `FUZZY`, `COMBINED_EXACT_FUZZY` (R-50).
4. Validate: any placeholder-like token in the answer that is not in the vault (e.g. `[PERSON_7]` when only 3 exist, or `<NAME>`) is flagged in the UI, not guessed. PromptGraph restores only after local consistency checks (R-66).
5. Plural/merged references ("[PERSON_1] and [PERSON_2]'s flat") must restore both; possessive suffix kept.

Note: telling the model that input is anonymised did not improve task accuracy in 2609.11335 (R-67); our T2 instruction "keep every placeholder exactly as written" is still useful for restoration, but measure it (restoration success metric).

### 5.3 Vault design
- Per conversation: `value_canonical → placeholder`, `placeholder → [surface forms]`, type, first-seen chunk, `mreq_` id. Never sent to the provider.
- ICO: the "additional information" must be kept separately and protected with technical and organisational measures; attacks that obtain "the pseudonymisation key or mapping table" reverse everything (R-16). So: encrypt at rest, short retention, access only by the restore step, never log raw values next to placeholders.
- Document-level propagation: once any chunk finds a value, replace all its occurrences in the whole document before sending (fixes chunk misses; TAB-style all-mentions recall).

---

## 6. UK GDPR and ICO: pseudonymisation vs anonymisation
- UK GDPR definition quoted by the ICO: pseudonymisation is processing so that data "can no longer be attributed to a specific data subject without the use of additional information", kept separately and protected (R-16).
- "Pseudonymised data is personal data in the hands of someone who holds the additional information" (R-16). "Pseudonymous information is still personal data and the law applies to it" (R-17).
- "If you share pseudonymised data (but not the additional information) with another organisation, it may be anonymous information in their hands" (R-16), but identifiability is judged on "means reasonably likely to be used", on a spectrum, and the ICO suggests a "motivated intruder" test (R-18). Other people's knowledge (colleagues, family) counts (R-18).
- Re-identification of pseudonymised or ineffectively anonymised data is a criminal offence under section 171 DPA 2018 (R-16).
- The ICO anonymisation guidance banner says it is under review "Due to changes made by the Data (Use and Access) Act" (R-15). Check for updates before quoting it in the deck.

**What this means for Veil's claims (INFERENCE):**
- Say: "Veil replaces direct identifiers with placeholders before the prompt leaves; the provider receives pseudonymised text and never the mapping." Do not say "anonymised", "GDPR compliant" or "no personal data reaches the provider": quasi-identifiers can remain, and the ICO asks for a reasonably-likely-means test.
- Veil (and Mubit, which sees raw chunks in T1) process personal data; the vault is the "additional information" and needs separation and access control.
- Financial data is sensitive but not special category; health data is special category (R-76). NHS numbers and health conditions in documents deserve the high-risk treatment.

---

## Recommendations for Veil

**Regex layer (FR-3)**
- Implement the 13 validators in `uk-formats.md` (tested) as `find → validate → context → label`. High-risk types (card, account, sort code, IBAN, NI) are labelled by regex + context even if the checksum fails; the model can add spans but never remove a regex hit.
- Use the corrected postcode regex, not the gov.uk PDF version (it rejects `W1A 0AX`). Do not trust Presidio `UK_PASSPORT` (wrong format).
- Context words for bare numbers: "sort code", "account", "a/c", "acc no", "NI", "National Insurance", "passport", "licence", "NHS", "UTR", "policy", "matter", "client". Keep-context words: "Company number", "Registered in England and Wales", "VAT Reg" (for companies), "Invoice", "Clause".

**Model layer (T1 adapter)**
- Keep T1 returning `{text, type}` and let code find all occurrences (LLM offsets are unreliable; REDACT needed offset relocation, R-40).
- Pre-process PDFs before chunking: de-hyphenate line ends, join wrapped lines, normalise no-break spaces and ligatures, drop repeated headers/footers after recording them once, linearise tables as `label: value` rows (INFERENCE from R-10, R-66).
- Chunk on paragraph boundaries with ~200-character overlap; merge entities per document; propagate every found value to the whole document (fixes PII-TRACE-style misses).
- Training data: plant the 108 hard cases, about 30% keep traps, aliases of the same person, bare values without clue words (OpenAI PF clue ablation shows that is where recall drops), and `CUSTOM` formats with context. Labels: span excludes honorifics and possessive `'s`; ADDRESS and POSTCODE are separate adjacent spans.

**Metrics:** the table in 3.4. Headline: leaks per 100 documents and zero-leak documents; per-type strict/partial P/R/F1; TAB-style all-mentions recall; over-redaction on planted keep traps; answer parity; restoration success; p50/p95 latency.

**Demo baselines (spec 9.6)**
1. Regex only (our validators).
2. Presidio default + UK recognizers (note the passport bug; optionally patch it and report both).
3. One open small model: `openai/privacy-filter` (Apache-2.0, strong, runs on a laptop) or a GLiNER model (`knowledgator/gliner-pii-base-v1.0` or `urchade/gliner_multi_pii-v1`, both Apache-2.0). Map their labels to our 13 types; `CUSTOM` will be near zero for them, which is our point.
4. GPT teacher (T1 on the provider).
5. Adapter v1, v2 (after corrections).
Skip Piiranha in anything shipped (CC BY-NC-ND 4.0).

**Claims:** "pseudonymised, direct identifiers removed, measured leak rate on synthetic UK documents"; never "anonymised" or "compliant".

**Gaps / not found:** no peer-reviewed benchmark on UK-specific identifiers in business documents (closest: Unmasking, which includes UK formats, R-38); no published accuracy for Private AI/Limina or Skyflow detection; no primary source on what the Data (Use and Access) Act changes for pseudonymisation (only the ICO "under review" banner).
