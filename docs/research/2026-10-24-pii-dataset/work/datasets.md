# Open datasets for the Veil PII redaction model (UK English)

Date: 24 Oct 2026. Researcher prefix: D. Scope: open datasets to train and evaluate the Mubit T1 redaction model (13 entity types, see `CONTEXT.md`).

How to read this file
- Every size, label list and licence below was read from a saved raw page (column `Raw`, files in the scratch `raw/` folder, index `raw/D-index.tsv`). Licence text is quoted from the card, LICENSE file or official page.
- Text marked "(inference)" is our reasoning, not a stated fact. "not stated" or "not found" means we looked and found nothing.
- Dashes inside quotes were normalised to "-" (house style: no em dashes) and Markdown formatting (bold, links) was removed; words are unchanged. `...` marks a cut. Machine-checkable quotes are in `evidence-D.csv`.
- Sample rows were read through the Hugging Face dataset viewer API (`first-rows`, `filter`); no full dataset was downloaded.
- Hard rule from CONTEXT.md: only synthetic PII may pass through Mubit. So use code (b) is only given to synthetic sets with a permissive licence. Real-person data (court cases, emails, essays, SMS, CVs, real web documents) is at most (a) local eval or (c) local template source.

Counts: 75 catalogue entries (some entries group 2 to 7 related repos), about 95 repos and pages inspected, 128 raw files.


## Summary table

| # | Dataset | Size | Type | Licence | Real / synthetic | Our use |
|---|---|---|---|---|---|---|
| 1 | ai4privacy/pii-masking-openpii-1m | 1,428,143 rows (train 1,143,397 / val 284,746); 35,830 tr... | 1 PII masking: short synthetic texts: emails, letters, ch... | CC BY 4.0 (HF tag says 'other', license_na... | synthetic (card: 'This dataset contai... | (b)+(a) |
| 2 | ai4privacy/pii-masking-openpii-1.5m | 1,636,375 rows (datasets-server) | 1 PII masking: short synthetic texts | CC BY 4.0 | synthetic | (b) |
| 3 | ai4privacy/open-pii-masking-500k-ai4privacy | 580,227 rows (train 464,150 / val 116,077); GB region 37,... | 1 PII masking: short synthetic texts (avg 17.37 words per... | other: Llama 3.1/3.3 Community License + A... | synthetic | (a) |
| 4 | ai4privacy/pii-masking-400k | 406,896 rows (train 325,517 / val 81,379); GB locale 41,8... | 1 PII masking: short synthetic texts, HTML snippets, forms | other: AI4Privacy academic licence | synthetic | (d) |
| 5 | ai4privacy/pii-masking-300k | 225,405 rows (train 177,677 / val 47,728) | 1 PII masking: synthetic texts; OpenPII-220k + FinPII-80k | other: AI4Privacy academic licence | synthetic | (d) |
| 6 | ai4privacy/pii-masking-200k | 209,261 rows; 13.6m tokens per card | 1 PII masking: AI-assistant style requests | other: Ai4Privacy free/corporate licence (... | synthetic | (a) |
| 7 | ai4privacy legacy and previews (pii-masking-65k, -43k, financial-pfi-preview, health-phi-400k) | 65k: 21,588 rows in viewer; 43k: not in viewer; pfi-previ... | 1 PII masking: synthetic texts | none / CC BY 4.0 (preview) / other (gated) | synthetic | (d) |
| 8 | gretelai/synthetic_pii_finance_multilingual | 55,940 rows (train 50,346 / test 5,594); avg 1,357 charac... | 1 PII masking: full-length financial documents: 100 docum... | Apache-2.0 | synthetic (Gretel Navigator) | (b)+(c) |
| 9 | gretelai/gretel-pii-masking-en-v1 | 60,000 rows (train 50,000 / val 5,000 / test 5,000) | 1 PII masking: domain document passages (banking, healthc... | Apache-2.0 | synthetic (Gretel Navigator) | (b)+(a) |
| 10 | nvidia/Nemotron-PII | card: 100,000 records (50k train / 50k test); datasets-se... | 1 PII masking: 50+ industries; structured and unstructure... | CC BY 4.0 | synthetic, persona-grounded (NeMo Dat... | (b)+(a) |
| 11 | QuantumAiuk/uk-pii-redaction-synthetic | card: train 3,000 / valid 200 / test 200 (20 unseen templ... | 1 PII masking: short UK messages and sentences (90 templa... | Apache-2.0 | synthetic (Ofcom drama phone ranges,... | (b)+(a)+(c) |
| 12 | RedactionBench/RedactionBench (mirror A10Networks/RedactionBench) | 200 documents (test only) | 1 PII masking: 11 categories incl. Financial (bank_statem... | CC BY 4.0 | mixed: 101 real-world documents from... | (a) |
| 13 | perplexity-ai/PII-TRACE | 500 conversations, 2,653 spans (450 with PII, 50 empty) | 1 PII masking: multi-turn LLM chat conversations | MIT | synthetic | (a) |
| 14 | nutrientdocs/DocPII-redaction-benchmark | 1,101 rows | 1 PII masking: longer synthetic domain documents (healthc... | MIT | synthetic (GPT-4.1-nano context) | (a) |
| 15 | DataikuNLP/kiji-pii-training-data | 51,495 rows (train 46,345 / test 5,150); 397,441 entity a... | 1 PII masking: LLM-generated texts with coreference | Apache-2.0 | synthetic | (b) |
| 16 | E3-JSI/synthetic-multi-pii-ner-v1 | 2,971 rows | 1 PII masking: LLM-generated texts | MIT | synthetic | (b) |
| 17 | urchade/synthetic-pii-ner-mistral-v1 | not stated on card (data.json); 19,635 rows reused by gra... | 1 PII masking: Mistral-generated texts | Apache-2.0 | synthetic | (d) |
| 18 | gravitee-io/pii-detection-dataset | 175,881 rows | 1 PII masking: merged synthetic sets (Gretel finance 25,9... | Apache-2.0 (sources listed per row) | synthetic | (d) |
| 19 | piimb/pii-masking-benchmark | 175,055 test rows (150,022 sentences / 25,033 full_text) | 1 PII masking: mix of OpenPII 1M, Gretel en v1, Nemotron-... | CC BY-NC 4.0 | synthetic (+ relabelled legal text) | (a) |
| 20 | piimb/mapa-eur-lex-pii | 42 documents (2 legal opinions x 21 languages) | 1 PII masking: EU legal opinions | CC BY 4.0 | real public legal text | (a) |
| 21 | ScienceSoft/piibench | 3,500 test rows | 1 PII masking: third-party gold sets transformed into 'ca... | mixed per row | per source | (a) |
| 22 | Pritesh-2711/pii-bench (PIIBench) | 999,940 rows (train 799,948 / val 99,990 / test 100,002) | 1 PII masking: merge of ~10 sources incl. Gretel finance... | tag apache-2.0, but inherits source licences | mixed | (d) |
| 23 | mks-logic/SPY | 4,491 medical consultations + 4,197 legal questions | 1 PII masking: informal legal questions, online medical c... | CC BY 4.0 (tag) | synthetic: Llama-3-70B text with plac... | (c) |
| 24 | srirxml/PANORAMA | 384,789 samples from 9,674 profiles (paper); cardData lis... | 1 PII masking: wiki-style bios, social posts, forum posts... | CC BY 4.0 | synthetic (OpenAI o3-mini + Faker) | (c) |
| 25 | Kaggle PII Data Detection (PIILO) / CRAPII | ~22,000 essays (PIILO); 22,688 essays (CRAPII); HF mirror... | 1 PII masking: student essays (one design-thinking prompt) | CC BY 4.0 (PIILO) / CC BY-NC 4.0 (CRAPII) | real essays; CRAPII states identifier... | (a) |
| 26 | beki/privy | not stated on the fetched card (no viewer) | 1 PII masking: protocol traces from OpenAPI specs: JSON,... | MIT | synthetic | (d) |
| 27 | NHSEDataScience/synthetic_clinical_notes | HF tag 1K<n<10K (viewer did not report rows) | 1 PII masking: synthetic NHS admissions and clinical note... | MIT | synthetic ('All data found in this re... | (c)+(b) |
| 28 | hyunjunian/RedacBench | 514 texts, 187 policies, 8,053 propositions (3,591 sensit... | 1 PII masking: public research texts incl. PIILO essays | CC BY 4.0 | real public research text | (d) |
| 29 | guneeshv/REDACT-PII-Benchmark | 13,427 records, 324,078 entities; locked eval split 1,000 | 1 PII masking: generated records across domains and formats | other (terms not read) | synthetic | (a) |
| 30 | PII-Bench (Shen et al., arXiv 2502.18545) | 2,842 test samples, 55 PII categories (abstract) | 1 PII masking: query + context, single and multi-party | not found | crafted | (d) |
| 31 | microsoft/presidio-research (data generator) | code + templates (no fixed dataset) | 1 PII masking: template sentences ('My name is {{name}}') | MIT (code); CC BY-SA 3.0 US (bundled fake... | synthetic (Faker / Fake Name Generator) | (c) |
| 32 | AIxBlock/92k-real-world-call-center-scripts-english | 91,706 transcripts (~10,500 hours audio, audio not included) | 1 PII masking: real inbound/outbound call-centre transcripts | CC BY-NC 4.0 + extra terms | real, redacted for PII | (d) |
| 33 | AIxBlock/stimulated-chatbot-conversations-PII-detection-7languages | n<1K (tag) | 1 PII masking: human-written support chats with PII | CC BY-NC 4.0 | human-generated synthetic | (d) |
| 34 | RobinSta/SynthPAI | 7,823 comments in 103 threads | 1 PII masking: synthetic forum comments (GPT-4 agents) | CC BY-NC-SA 4.0 | synthetic personal attributes | (d) |
| 35 | bigcode/bigcode-pii-dataset | tag 10K<n<100K | 1 PII masking: source code | not read | real code with PII | (d) |
| 36 | Other screened, not useful (scanpatch Ukrainian/Russian NER, hivetrace Russian bench, vkatg streaming PHI, paperboy desktop screenshots, capitaletech resume images, AdamLucek en-us-30k, MedOtter/PANORAMA) | 5,318 / 1,810 / 328 / 500 / 2,875 / 29,595 / 2,238 rows | 1 PII masking: various | various | synthetic or n/a | (d) |
| 37 | Text Anonymization Benchmark (TAB) | 1,268 ECHR cases (card); HF ildpil/text-anonymization-ben... | 2 Anonymisation: European Court of Human Rights judgments | MIT | real (public court judgments) | (a) |
| 38 | i2b2 / n2c2 de-identification (2006, 2014) | not checked | 2 Anonymisation: US clinical notes (Partners Healthcare) | DUA | real (de-identified with surrogates) | (d) |
| 39 | MIMIC-IV-Note (PhysioNet) | not checked | 2 Anonymisation: de-identified US clinical notes | PhysioNet credentialed DUA | real (de-identified) | (d) |
| 40 | PhysioNet deid (software + gold standard) | not checked | 2 Anonymisation: nursing notes and discharge summaries (de-... | GPL-2.0 (software) | real (surrogates) | (d) |
| 41 | joelniklaus/mapa (MAPA anonymisation corpus) | 41,767 rows (27,823 / 3,354 / 10,590) | 2 Anonymisation: EUR-Lex legal documents | CC BY 4.0 | real public legal text | (a) |
| 42 | CoNLL-2003 (eriktks/conll2003) | 14,041 / 3,250 / 3,453 sentences | 3 NER: Reuters news | Reuters Corpus agreements (research) | real (public figures) | (d) |
| 43 | OntoNotes 5.0 (LDC2013T19) | tner/ontonotes5: 76,714 rows (59,924 / 8,528 / 8,262) | 3 NER: news, conversation, web | LDC licence | real | (d) |
| 44 | DFKI-SLT/few-nerd | supervised: 131,767 / 18,824 / 37,648 sentences | 3 NER: Wikipedia | CC BY-SA 4.0 | real (public entities) | (c) |
| 45 | Babelscape/multinerd | 3,349,186 rows | 3 NER: Wikipedia + WikiNews | CC BY-NC-SA 4.0 | real (public) | (d) |
| 46 | WikiNER / Babelscape/wikineural | WikiNEuRal: 1,027,506 rows | 3 NER: Wikipedia | CC BY-NC-SA 4.0 (WikiNEuRal); WikiNER not... | real (public) | (d) |
| 47 | WNUT-17 (leondz/wnut_17) | 3,394 / 1,009 / 1,287 sentences | 3 NER: social media (emerging entities) | CC BY 4.0 (tag) | real (social media) | (a) |
| 48 | Broad Twitter Corpus (tner/btc) | 9,339 (6,338 / 1,001 / 2,000) | 3 NER: tweets | unclear | real | (d) |
| 49 | Enron personal-name NER (Minkov et al., CMU) | Enron-Meetings + Enron-Random subsets (counts in paper, n... | 3 NER: real emails | research use (no formal licence) | real | (a) |
| 50 | CUAD (theatticusproject/cuad, cuad-qa) | 510 contracts, 13,000+ labels, 41 clause categories; cuad... | 4 Documents: commercial contracts from SEC EDGAR | CC BY 4.0 | real (company names, some signatories) | (c) |
| 51 | ContractNLI | 607 NDAs, 17 hypotheses | 4 Documents: non-disclosure agreements | CC BY 4.0 (official) | real (parties) | (c) |
| 52 | LEDGAR (coastalcph/lex_glue, config ledgar) | 60,000 / 10,000 / 10,000 provisions | 4 Documents: contract provisions from EDGAR | CC BY 4.0 (tag) | real (rare) | (c) |
| 53 | theatticusproject/maud | 39,231 rows (25,827 / 6,753 / 6,651) | 4 Documents: merger agreements (Q&A) | CC BY 4.0 | real (companies) | (c) |
| 54 | SEC EDGAR / eloukas/edgar-corpus | yearly configs from 1993; e.g. 220,375 rows in one listed... | 4 Documents: 10-K annual report sections | Apache-2.0 tag; SEC terms not verified | real (executives) | (c) |
| 55 | Kleister NDA + Kleister Charity (applicaai) | HF mirror orgrctera/kleister_charity_train: 1,729 rows | 4 Documents: Charity: annual reports of British chariti... | not stated | real (trustees, addresses) | (c) |
| 56 | GOV.UK model agreement for a shorthold assured tenancy | 1 template | 4 Documents: tenancy agreement template | OGL v3 (Crown copyright) | none (blank template) | (c) |
| 57 | legislation.gov.uk (othertales/uklegislation) | 43,070 items | 4 Documents: UK Acts and SIs | OGL v3 (per card) | none | (c) |
| 58 | Find Case Law (The National Archives) | not checked | 4 Documents: UK court judgments and tribunal decisions | Open Justice Licence + separate computatio... | real (parties, witnesses) | (d) |
| 59 | Companies House Free Company Data Product | monthly snapshot; BasicCompanyDataAsOneFile-2026-10-01.zi... | 4 Documents: CSV of live companies (name, number, regis... | statutory public register (not OGL) | real (registered addresses; officer d... | (c) |
| 60 | Enron email corpus (CMU; HF mirrors corbt/enron-emails, LLM-PBE/enron-email, Yale-LILY/aeslc) | ~0.5M messages from ~150 users (CMU); corbt 517,401; LLM-... | 4 Documents: corporate emails | research resource (no formal licence) | real | (a) |
| 61 | SAMSum (knkarthick/samsum) | 16,368 (14,731 / 818 / 819) | 4 Documents: messenger-style dialogues + summaries | CC BY-NC-ND 4.0 | names only | (d) |
| 62 | DialogSum (knkarthick/dialogsum) | 14,460 (12,460 / 500 / 1,500) | 4 Documents: spoken-style dialogues | CC BY-NC-SA 4.0 | names | (d) |
| 63 | bitext/Bitext-retail-banking-llm-chatbot-training-dataset | 25,545 rows | 4 Documents: banking customer-support instructions and... | CDLA-Sharing-1.0 | none (placeholders) | (c)+(b) |
| 64 | bitext/Bitext-customer-support-llm-chatbot-training-dataset | 26,872 rows | 4 Documents: general customer-support chats with {{plac... | CDLA-Sharing-1.0 | none (placeholders) | (c)+(b) |
| 65 | MultiWOZ 2.1 / 2.2 (ConvLab/multiwoz21, pfb30/multi_woz_v22) | v2.2: 8,437 / 1,000 / 1,000 dialogues | 4 Documents: task dialogues in Cambridge UK (restaurant... | MIT (GitHub) / Apache-2.0 (HF mirrors) | business data; booking references | (c) |
| 66 | UCI SMS Spam Collection (ucirvine/sms_spam) | 5,574 SMS | 4 Documents: SMS (425 spam from UK forum Grumbletext, 4... | CC BY 4.0 (UCI) | real | (c) |
| 67 | apptek-com/apptek_callcenter_dialogues | 2,619 rows (1,746 + 873 diarization) | 4 Documents: call-centre dialogues (audio + text) | CC BY-SA 4.0 | none ('No personally identifiable inf... | (c) |
| 68 | SROIE (ICDAR 2019) | 1,000 scanned receipts (600 trainval / 400 test); HF dare... | 4 Documents: receipts | unknown (data) | real shops | (d) |
| 69 | CORD (naver-clova-ix/cord-v2) | 1,000 released (800 / 100 / 100) of 11,000+ collected | 4 Documents: Indonesian receipts | CC BY 4.0 | minimal | (d) |
| 70 | FUNSD (nielsr/funsd) | 199 forms, 31,485 words, 9,707 semantic entities | 4 Documents: scanned forms | unknown | real (old forms) | (d) |
| 71 | AgamiAI/Indian-Bank-Statements | tag 10K<n<100K (viewer did not report) | 4 Documents: synthetic Indian business current-account... | Apache-2.0 | synthetic | (c) |
| 72 | Bankstatemently/bank-statement-parsing-benchmark | 15 synthetic statements (card); viewer 5 rows | 4 Documents: bank and card statement PDFs | MIT | synthetic | (c) |
| 73 | buthaya/payslips | 611 pages (485 / 126) | 4 Documents: payslip OCR pages | MIT | masked/synthetic values (seen 'MMM CCC') | (c) |
| 74 | Resume / CV sets (opensporks/resumes, datasetmaster/resumes, d4rk3r/resumes-raw-pdf) | 2,484 / 4,817 / 1,940 PDFs | 4 Documents: CVs | CC0 / MIT / MIT tags | real or mixed (opensporks: 'Resume Ex... | (c) |
| 75 | Suspicious leaked-data repos on HF (PhisherJR/Truecaller, PhisherJR/phonebook, PhisherJR/850M-India-data) | not opened | 4 Documents: unknown (names suggest scraped phone/ident... | n/a | likely real (inference from names) | (d) |

Use codes: (a) eval only, (b) training traffic through Mubit (synthetic PII and permissive licence only), (c) template or text source for our generator, (d) avoid.

## Datasets

### 1. ai4privacy/pii-masking-openpii-1m

- URL: https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m  |  Group: 1 PII masking  |  Raw: D-5.md; D-76.md
- Size: 1,428,143 rows (train 1,143,397 / val 284,746); 35,830 train rows with region=GB (datasets-server filter)
- Documents: short synthetic texts: emails, letters, checklists, forms (seen in GB samples)  |  Language: 23 European languages incl. en
- PII: synthetic (card: 'This dataset contains synthetic PII only')
- Labels: 19: DATE, GIVENNAME, SURNAME, EMAIL, CITY, TITLE, TELEPHONENUM, AGE, STREET, BUILDINGNUM, ZIPCODE, IDCARDNUM, CREDITCARDNUMBER, DRIVERLICENSENUM, GENDER, TAXNUM, SEX, SOCIALNUM, PASSPORTNUM
- Mapping to our 13 types: PERSON<-GIVENNAME+SURNAME (merge adjacent); ADDRESS<-BUILDINGNUM+STREET+CITY (merge, only personal addresses); POSTCODE<-ZIPCODE; EMAIL; PHONE<-TELEPHONENUM; CARD<-CREDITCARDNUMBER; ID_DOC<-PASSPORTNUM, DRIVERLICENSENUM, IDCARDNUM. Drop DATE, AGE, GENDER, SEX, TITLE. Gaps: BANK_ACCOUNT, SORT_CODE, IBAN, NI_NUMBER (SOCIALNUM/TAXNUM are not UK-shaped), DOB (no separate label), CUSTOM.
- Format: source_text, masked_text, privacy_mask [{value,start,end,label}] char spans, mBERT BIO tokens
- Licence (verbatim): 'License: CC-BY-4.0. Copyright © 2026 Ai Suisse SA.' / 'Permitted Use: Research, commercial use, redistribution, and modification - subject to attribution requirements under CC-BY-4.0.'
- Commercial: yes, with attribution  |  Redistribution: yes, with attribution  |  Access: open
- Quality / known issues: Fact (D-76, GB rows): outward-only postcodes ('YO19', 'YO60'), non-UK phone shapes ('7456.428.8083', '+321.69 984-9693'), DOB-like dates labelled DATE, unusual names ('Hyon Davran'). Inference: template generation, short rows vs our 1,500-token chunks.
- UK relevance: medium: GB subset exists, UK formats weak
- Our use: **(b)+(a)** Largest permissive synthetic set. Filter region=GB / language=en, remap and merge spans, drop keep-classes, then use as Mubit training traffic; keep a held-out slice for eval.

### 2. ai4privacy/pii-masking-openpii-1.5m

- URL: https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1.5m  |  Group: 1 PII masking  |  Raw: D-6.md
- Size: 1,636,375 rows (datasets-server)
- Documents: short synthetic texts  |  Language: 30 languages (adds Asia Pacific)
- PII: synthetic
- Labels: same 19 labels as openpii-1m
- Mapping to our 13 types: as openpii-1m
- Format: as openpii-1m
- Licence (verbatim): 'License: CC-BY-4.0. Copyright © 2026 Ai Suisse SA.' / 'Permitted Use: Research, commercial use, redistribution, and modification, subject to attribution requirements under CC-BY-4.0.'
- Commercial: yes, with attribution  |  Redistribution: yes, with attribution  |  Access: open
- Quality / known issues: Card: 'with a new Asia Pacific corpus, bringing global coverage to 30 languages'. Inference: superset of 1m; extra rows are non-UK.
- UK relevance: low-medium
- Our use: **(b)** Use only if 1m is not enough; the added languages do not help UK English.

### 3. ai4privacy/open-pii-masking-500k-ai4privacy

- URL: https://huggingface.co/datasets/ai4privacy/open-pii-masking-500k-ai4privacy  |  Group: 1 PII masking  |  Raw: D-4.md
- Size: 580,227 rows (train 464,150 / val 116,077); GB region 37,092 (6.39%) per card
- Documents: short synthetic texts (avg 17.37 words per card)  |  Language: 8 incl. en, hi, te
- PII: synthetic
- Labels: 20 classes (Open PII labelset)
- Mapping to our 13 types: similar to openpii-1m
- Format: source_text, masked_text, privacy_mask spans, mBERT tokens
- Licence (verbatim): 'its use and distribution are subject to the Llama Community License Agreement.' / 'Your use of this dataset must comply with the Llama Acceptable Use Policy'
- Commercial: unclear: depends on Llama licence terms (read them)  |  Redistribution: yes, must include Llama licence copies (card)  |  Access: open
- Quality / known issues: Rows are very short (17.37 words average per card).
- UK relevance: medium
- Our use: **(a)** Licence inheritance makes it weaker than openpii-1m; use for eval only, or skip.

### 4. ai4privacy/pii-masking-400k

- URL: https://huggingface.co/datasets/ai4privacy/pii-masking-400k  |  Group: 1 PII masking  |  Raw: D-3.md; D-74.md; D-76.md
- Size: 406,896 rows (train 325,517 / val 81,379); GB locale 41,853 per card (33,493 in train via filter)
- Documents: short synthetic texts, HTML snippets, forms  |  Language: en, it, fr, de, nl, es
- PII: synthetic
- Labels: 17 public classes (63 in paid extension); seen: USERNAME, DATEOFBIRTH, CITY, EMAIL, BUILDINGNUM, GIVENNAME, SURNAME, STREET, TELEPHONENUM, ZIPCODE, SOCIALNUM
- Mapping to our 13 types: as openpii-1m plus DOB<-DATEOFBIRTH
- Format: source_text, masked_text, privacy_mask spans, mBERT tokens
- Licence (verbatim): 'Access to this dataset is granted exclusively for academic research and non-commercial purposes' / 'including any form of redistribution ... an explicit written license must be obtained from AI4Privacy.' / 'This dataset is watermarked'
- Commercial: no  |  Redistribution: no  |  Access: open download, restrictive licence
- Quality / known issues: Fact (D-76): names labelled USERNAME ('BF6'), 'Social Number: 318 667 0376', ZIPCODE 'RG23'.
- UK relevance: medium
- Our use: **(d)** Non-commercial and watermarked; do not use in a product or send through Mubit.

### 5. ai4privacy/pii-masking-300k

- URL: https://huggingface.co/datasets/ai4privacy/pii-masking-300k  |  Group: 1 PII masking  |  Raw: D-2.md; D-73.md
- Size: 225,405 rows (train 177,677 / val 47,728)
- Documents: synthetic texts; OpenPII-220k + FinPII-80k  |  Language: 6: English (UK and USA), fr, de, it, es, nl
- PII: synthetic
- Labels: 27 classes (OpenPII) plus ~20 finance/insurance (FinPII)
- Mapping to our 13 types: as openpii-1m
- Format: source_text, target_text, privacy_mask, span_labels, mBERT BIO
- Licence (verbatim): 'Access to this dataset is granted exclusively for academic research and non-commercial purposes' (LICENSE.md, same text as 400k)
- Commercial: no  |  Redistribution: no  |  Access: open download, restrictive licence
- Quality / known issues: Card: '~98.3% token label accuracy of a random sample of 216 entries'; Known issues: 'country, time, and titles' mislabelled.
- UK relevance: medium
- Our use: **(d)** Non-commercial; avoid.

### 6. ai4privacy/pii-masking-200k

- URL: https://huggingface.co/datasets/ai4privacy/pii-masking-200k  |  Group: 1 PII masking  |  Raw: D-1.md; D-75.md
- Size: 209,261 rows; 13.6m tokens per card
- Documents: AI-assistant style requests  |  Language: en, fr, de, it
- PII: synthetic
- Labels: 54 PII classes
- Mapping to our 13 types: partial (fine-grained classes need collapsing)
- Format: source_text, target_text, privacy_mask, span_labels, mBERT BIO
- Licence (verbatim): 'You're qualified to use Ai4Privacy at no cost if you're: An individual / A for-profit entity with a staff count of up to 3 / A non-profit' / 'It's not permissible to duplicate or alter Ai4Privacy's code with the intention to distribute, sell, rent, license, re-license, or sublicense your own derivative of Ai4Privacy.'
- Commercial: only for individuals or companies with up to 3 staff  |  Redistribution: no derivatives  |  Access: open
- Quality / known issues: Card: FIRSTNAME class 'still overrepresented'.
- UK relevance: low
- Our use: **(a)** Eval only, and only if the team qualifies for the free licence; otherwise avoid.

### 7. ai4privacy legacy and previews (pii-masking-65k, -43k, financial-pfi-preview, health-phi-400k)

- URL: https://huggingface.co/ai4privacy  |  Group: 1 PII masking  |  Raw: D-7.md; D-8.md; D-9.md; D-10.md
- Size: 65k: 21,588 rows in viewer; 43k: not in viewer; pfi-preview: 50 rows; health-phi-400k: gated
- Documents: synthetic texts  |  Language: en (+fr/de/it for 65k); previews 24 languages
- PII: synthetic
- Labels: 65k: 58 types; pfi-preview: financial labels
- Mapping to our 13 types: n/a
- Format: mixed
- Licence (verbatim): 65k and 43k cards: no licence stated. pfi-preview: 'license: cc-by-4.0'. health-phi-400k: gated 'manual', license 'other'.
- Commercial: unclear  |  Redistribution: unclear  |  Access: open / gated manual
- Quality / known issues: Superseded releases.
- UK relevance: low
- Our use: **(d)** No licence or gated; pfi-preview (50 rows) only useful to read label ideas.

### 8. gretelai/synthetic_pii_finance_multilingual

- URL: https://huggingface.co/datasets/gretelai/synthetic_pii_finance_multilingual  |  Group: 1 PII masking  |  Raw: D-11.md
- Size: 55,940 rows (train 50,346 / test 5,594); avg 1,357 characters
- Documents: full-length financial documents: 100 document types x 20 subtypes (loan agreements, statements, swaps...)  |  Language: en, fr, de, nl, es, it (English described as US, UK or Canada)
- PII: synthetic (Gretel Navigator)
- Labels: 29 types incl. name, first_name, last_name, street_address, email, phone_number, iban, bban, swift_bic_code, bank_routing_number, credit_card_number, credit_card_security_code, account_pin, customer_id, employee_id, passport_number, driver_license_number, ssn, date_of_birth, company, date, time, password, api_key, user_name
- Mapping to our 13 types: PERSON<-name/first_name/last_name; ADDRESS<-street_address; EMAIL; PHONE; IBAN<-iban; BANK_ACCOUNT<-bban (inference: check UK BBAN embeds sort code); CARD<-credit_card_number; DOB<-date_of_birth; ID_DOC<-passport_number, driver_license_number; CUSTOM<-customer_id, employee_id. Drop company, date, time, swift_bic_code. Gaps: SORT_CODE, NI_NUMBER, POSTCODE.
- Format: generated_text + pii_spans [{start,end,label}] char spans, plus quality scores
- Licence (verbatim): 'released under Apache 2.0' / 'The data used to train these LLMs contains no usage restrictions.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card: 'A NER library labeled the PII, which may introduce false negatives (missed labels) or false positives (incorrect labels)... Some errors may still be present.' 'company' and 'date' are labelled as PII (conflicts with our keep rule).
- UK relevance: medium: long finance docs, some UK English
- Our use: **(b)+(c)** Closest to our contracts and bank documents with document-length texts; remap labels, drop keep-classes, re-check spans.

### 9. gretelai/gretel-pii-masking-en-v1

- URL: https://huggingface.co/datasets/gretelai/gretel-pii-masking-en-v1  |  Group: 1 PII masking  |  Raw: D-12.md; D-76.md
- Size: 60,000 rows (train 50,000 / val 5,000 / test 5,000)
- Documents: domain document passages (banking, healthcare, insurance, government, telecom...)  |  Language: en
- PII: synthetic (Gretel Navigator)
- Labels: 40+ types incl. medical_record_number, date_of_birth, ssn, first_name, last_name, name, email, customer_id, employee_id, street_address, address, phone_number, credit_card_number, account_number, postcode (955 train), national_id, tax_id, swift_bic, cvv, pin, company_name, date
- Mapping to our 13 types: PERSON, ADDRESS, POSTCODE, EMAIL, PHONE, CARD, BANK_ACCOUNT<-account_number, DOB, CUSTOM<-customer_id/employee_id/medical_record_number; drop company_name, date, time. Gaps: SORT_CODE, IBAN (only swift), NI_NUMBER.
- Format: text + entities list (entity string + types); offsets must be recomputed (inference from schema)
- Licence (verbatim): 'license: apache-2.0' (card metadata; no separate licence section)
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Fact (D-76): a bank-domain row labels 'ZZ287351T' (NI-number shape) as a Social Security Number; US-style addresses dominate. Gretel's own GLiNER paper is cited on the card.
- UK relevance: low-medium
- Our use: **(b)+(a)** Clean permissive English set with many identifier types; good secondary training traffic and a held-out test split.

### 10. nvidia/Nemotron-PII

- URL: https://huggingface.co/datasets/nvidia/Nemotron-PII  |  Group: 1 PII masking  |  Raw: D-13.md; D-76.md
- Size: card: 100,000 records (50k train / 50k test); datasets-server: 200,000 rows (100,000 train / 100,000 test); 50,000 train rows with locale 'intl'
- Documents: 50+ industries; structured and unstructured documents (applications, forms, bills of lading, emergency contact forms)  |  Language: en (US and international locales)
- PII: synthetic, persona-grounded (NeMo Data Designer)
- Labels: 55+ PII/PHI categories (seen: first_name, date_of_birth, street_address, employment_status...)
- Mapping to our 13 types: rich: PERSON, ADDRESS, PHONE, EMAIL, DOB, CARD, account numbers, IDs; drop non-identifying classes (employment_status etc.). Gaps: SORT_CODE, NI_NUMBER and UK formats.
- Format: text + spans [{start,end,text,label}] char spans + text_tagged
- Licence (verbatim): 'This dataset is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0)' / 'This dataset is ready for commercial use.'
- Commercial: yes  |  Redistribution: yes, with attribution  |  Access: open
- Quality / known issues: Size conflict between card and viewer (inference: an 'intl' locale half was added later). Fact (D-76): 'intl' rows use non-UK formats ('074-498-651').
- UK relevance: low-medium
- Our use: **(b)+(a)** Commercial-ready, document-shaped, char spans in our format; strong training traffic after label remap.

### 11. QuantumAiuk/uk-pii-redaction-synthetic

- URL: https://huggingface.co/datasets/QuantumAiuk/uk-pii-redaction-synthetic  |  Group: 1 PII masking  |  Raw: D-23.md
- Size: card: train 3,000 / valid 200 / test 200 (20 unseen templates) / test_meta 200 / wild_meta 30 / wild2_meta 30
- Documents: short UK messages and sentences (90 templates), ~20% with no personal data, look-alike negatives  |  Language: en-GB
- PII: synthetic (Ofcom drama phone ranges, check-digit-valid NHS numbers, valid-format NI numbers)
- Labels: [NAME] [ADDRESS] [POSTCODE] [PHONE] [EMAIL] [NI_NUMBER] [NHS_NUMBER] [SORT_CODE] [ACCOUNT_NUMBER] [DATE_OF_BIRTH]
- Mapping to our 13 types: PERSON<-NAME; ADDRESS; POSTCODE; PHONE; EMAIL; NI_NUMBER; SORT_CODE; BANK_ACCOUNT<-ACCOUNT_NUMBER; DOB<-DATE_OF_BIRTH; NHS_NUMBER -> CUSTOM (our decision). Gaps: IBAN, CARD, ID_DOC.
- Format: chat messages (system/user/assistant), assistant = masked text with tags; no offsets (spans must be recovered by diffing user vs assistant)
- Licence (verbatim): 'license: apache-2.0' / 'Every record is synthetic. No real person's data is included.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card: 'Synthetic templates cannot capture the full variety of real documents, and the same team wrote the generator and the hand-written tests.' Uploaded 2026-10-09, 66 downloads (low adoption).
- UK relevance: high: the only open set found with SORT_CODE, NI_NUMBER, UK postcodes and Ofcom phone ranges
- Our use: **(b)+(a)+(c)** Convert to our span format; use train as Mubit traffic, the unseen-template test and wild sets as UK eval, and copy its look-alike negative ideas.

### 12. RedactionBench/RedactionBench (mirror A10Networks/RedactionBench)

- URL: https://huggingface.co/datasets/RedactionBench/RedactionBench  |  Group: 1 PII masking  |  Raw: D-21.md; D-116.md
- Size: 200 documents (test only)
- Documents: 11 categories incl. Financial (bank_statement, card_statement, invoice, receipt), Legal (lease_agreement, offer_letter, promissory_note), Medical (discharge_summary, prescription), Government forms  |  Language: en
- PII: mixed: 101 real-world documents from the public web (transcribed, augmented) + 99 synthetic
- Labels: untyped spans: 'mandatory' (must redact) or 'contextual' (may redact)
- Mapping to our 13 types: untyped only: score span recall/precision, not types
- Format: raw_text + spans [{start,end,label}] char spans + category, genre, is_synthetic, original_document_url
- Licence (verbatim): 'License: CC BY 4.0' / 'RedactionBench is an evaluation-only benchmark'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Manually annotated; US-centric genres (1040, I-9, DS-160, social_security). arXiv 2606.18782.
- UK relevance: low-medium (document types match ours, formats US)
- Our use: **(a)** Best open document-level redaction eval; never send through Mubit because half the documents come from real web sources.

### 13. perplexity-ai/PII-TRACE

- URL: https://huggingface.co/datasets/perplexity-ai/PII-TRACE  |  Group: 1 PII masking  |  Raw: D-20.md
- Size: 500 conversations, 2,653 spans (450 with PII, 50 empty)
- Documents: multi-turn LLM chat conversations  |  Language: en
- PII: synthetic
- Labels: 9: private_person, private_date, private_url, private_address, account_number, private_email, private_phone, other_pii, secret
- Mapping to our 13 types: PERSON, ADDRESS, EMAIL, PHONE, BANK_ACCOUNT/CUSTOM<-account_number; private_date is not DOB-specific; drop url/secret. Gaps: UK types.
- Format: turns + spans {label, turn, source, start, end, text} code-point offsets per message
- Licence (verbatim): 'License: MIT.' / 'This subset may be used for training, evaluation, and error analysis in PII span detection research.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card: 'identifier formats are more regular than production traffic, and current gold spans occur in user messages.' arXiv 2609.22200.
- UK relevance: low
- Our use: **(a)** Small but the only clean multi-turn chat benchmark; fits Veil's chat UI.

### 14. nutrientdocs/DocPII-redaction-benchmark

- URL: https://huggingface.co/datasets/nutrientdocs/DocPII-redaction-benchmark  |  Group: 1 PII masking  |  Raw: D-22.md
- Size: 1,101 rows
- Documents: longer synthetic domain documents (healthcare, finance...) embedding Gretel entities  |  Language: en
- PII: synthetic (GPT-4.1-nano context)
- Labels: Gretel en v1 entity types
- Mapping to our 13 types: as gretel-pii-masking-en-v1
- Format: text + entities + document_type, domain, redaction_query
- Licence (verbatim): 'license: mit'
- Commercial: yes (check OpenAI output terms, inference)  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card limitations: 'Documents are synthetic (though highly realistic)'.
- UK relevance: low
- Our use: **(a)** Document-length eval in our style; small.

### 15. DataikuNLP/kiji-pii-training-data

- URL: https://huggingface.co/datasets/DataikuNLP/kiji-pii-training-data  |  Group: 1 PII masking  |  Raw: D-28.md
- Size: 51,495 rows (train 46,345 / test 5,150); 397,441 entity annotations
- Documents: LLM-generated texts with coreference  |  Language: da, de, en, es, fr, nl (+ country field)
- PII: synthetic
- Labels: 26: FIRSTNAME, SURNAME, CITY, BUILDINGNUM, STREET, ZIP, STATE, COUNTRY, COMPANYNAME, PHONENUMBER, EMAIL, DATEOFBIRTH, URL, DRIVERLICENSENUM, SSN, SECURITYTOKEN, PASSPORTID, IBAN, PASSWORD, NATIONALID, LICENSEPLATENUM, TAXNUM, IDCARDNUM, AGE, CREDITCARDNUMBER, USERNAME
- Mapping to our 13 types: PERSON, ADDRESS (merge), POSTCODE<-ZIP, PHONE, EMAIL, DOB, IBAN, CARD, ID_DOC<-PASSPORTID/DRIVERLICENSENUM/IDCARDNUM; drop COMPANYNAME, COUNTRY, AGE. Gaps: SORT_CODE, NI_NUMBER, BANK_ACCOUNT.
- Format: text + privacy_mask spans + coreferences
- Licence (verbatim): 'license: apache-2.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card: LLM generation with optional LLM review pass.
- UK relevance: low-medium (GB country share not checked)
- Our use: **(b)** Permissive, has IBAN and DOB; use as extra traffic.

### 16. E3-JSI/synthetic-multi-pii-ner-v1

- URL: https://huggingface.co/datasets/E3-JSI/synthetic-multi-pii-ner-v1  |  Group: 1 PII masking  |  Raw: D-25.md
- Size: 2,971 rows
- Documents: LLM-generated texts  |  Language: en, fr, de, el, nl, it, sl
- PII: synthetic
- Labels: person, organization, phone number, address, passport number, email, credit card number, social security number, health insurance id number, date of birth, mobile phone number, bank account number, medication, cpf, driver's license...
- Mapping to our 13 types: PERSON, PHONE, ADDRESS, ID_DOC, EMAIL, CARD, DOB, BANK_ACCOUNT; drop organization, medication
- Format: text + entities + GLiNER tokens
- Licence (verbatim): 'license: mit'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Small.
- UK relevance: low
- Our use: **(b)** Minor extra traffic.

### 17. urchade/synthetic-pii-ner-mistral-v1

- URL: https://huggingface.co/datasets/urchade/synthetic-pii-ner-mistral-v1  |  Group: 1 PII masking  |  Raw: D-24.md; D-17.md
- Size: not stated on card (data.json); 19,635 rows reused by gravitee
- Documents: Mistral-generated texts  |  Language: en, fr, it, de, es
- PII: synthetic
- Labels: free-form PII types (GLiNER style)
- Mapping to our 13 types: needs manual mapping
- Format: data.json (tokenized_text + ner)
- Licence (verbatim): 'license: apache-2.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card is two lines.
- UK relevance: low
- Our use: **(d)** Low value vs larger sets.

### 18. gravitee-io/pii-detection-dataset

- URL: https://huggingface.co/datasets/gravitee-io/pii-detection-dataset  |  Group: 1 PII masking  |  Raw: D-17.md
- Size: 175,881 rows
- Documents: merged synthetic sets (Gretel finance 25,948; urchade 19,635; own synthetic 10,000; others)  |  Language: en
- PII: synthetic
- Labels: 25 Presidio-style classes: PERSON, LOCATION, EMAIL_ADDRESS, PHONE_NUMBER, CREDIT_CARD, IBAN_CODE, US_SSN, US_BANK_NUMBER, US_PASSPORT, US_DRIVER_LICENSE, DATE_TIME, ORGANIZATION...
- Mapping to our 13 types: coarse; LOCATION mixes addresses and places; US_* types not UK
- Format: text + spans [{start,end,label}]
- Licence (verbatim): 'license: apache-2.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Derivative re-labelling of other sets.
- UK relevance: low
- Our use: **(d)** Use the upstream Gretel set instead.

### 19. piimb/pii-masking-benchmark

- URL: https://huggingface.co/datasets/piimb/pii-masking-benchmark  |  Group: 1 PII masking  |  Raw: D-15.md
- Size: 175,055 test rows (150,022 sentences / 25,033 full_text)
- Documents: mix of OpenPII 1M, Gretel en v1, Nemotron-PII, Privy, MAPA EUR-LEX  |  Language: multi
- PII: synthetic (+ relabelled legal text)
- Labels: unified piimb scheme
- Mapping to our 13 types: unified scheme close to ours (inference)
- Format: text + entities spans
- Licence (verbatim): 'This benchmark is licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).'
- Commercial: no  |  Redistribution: yes, non-commercial  |  Access: open
- Quality / known issues: Card: 'For specialised use cases, this benchmark does not provide the full picture.'
- UK relevance: low
- Our use: **(a)** Internal research eval only; prefer the permissive upstream sets.

### 20. piimb/mapa-eur-lex-pii

- URL: https://huggingface.co/datasets/piimb/mapa-eur-lex-pii  |  Group: 1 PII masking  |  Raw: D-16.md
- Size: 42 documents (2 legal opinions x 21 languages)
- Documents: EU legal opinions  |  Language: 21 EU languages incl. en
- PII: real public legal text
- Labels: fine-grained piimb PII scheme
- Mapping to our 13 types: partial
- Format: text + entities char spans
- Licence (verbatim): 'License: CC BY 4.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: English hand-annotated; other languages projected by an LLM ('claude-haiku-4-5').
- UK relevance: low
- Our use: **(a)** Tiny legal eval (2 English docs).

### 21. ScienceSoft/piibench

- URL: https://huggingface.co/datasets/ScienceSoft/piibench  |  Group: 1 PII masking  |  Raw: D-19.md
- Size: 3,500 test rows
- Documents: third-party gold sets transformed into 'carriers' (windowed to ~600 chars)  |  Language: en, de, es, ru, ar
- PII: per source
- Labels: per source set
- Mapping to our 13 types: per source
- Format: rows.jsonl with set, lang, carrier, text
- Licence (verbatim): 'rows.jsonl is a single file mixing text under four different licences (MIT, Apache-2.0, CC-BY-4.0, CC-BY-SA-4.0)'
- Commercial: yes per row (SA rows carry share-alike)  |  Redistribution: per row  |  Access: open
- Quality / known issues: Card: 'We generate no test content.'
- UK relevance: low
- Our use: **(a)** Eval harness ideas; check row licences.

### 22. Pritesh-2711/pii-bench (PIIBench)

- URL: https://huggingface.co/datasets/Pritesh-2711/pii-bench  |  Group: 1 PII masking  |  Raw: D-29.md
- Size: 999,940 rows (train 799,948 / val 99,990 / test 100,002)
- Documents: merge of ~10 sources incl. Gretel finance and finer-139  |  Language: en
- PII: mixed
- Labels: 82 entity types, 165 BIO labels
- Mapping to our 13 types: needs collapsing
- Format: tokens + BIO labels
- Licence (verbatim): 'This dataset is derived from multiple sources. Users must comply with the original dataset licenses of the constituent datasets.'
- Commercial: unclear  |  Redistribution: unclear  |  Access: open
- Quality / known issues: arXiv 2604.15776.
- UK relevance: low
- Our use: **(d)** Licence inheritance unclear; use sources directly.

### 23. mks-logic/SPY

- URL: https://huggingface.co/datasets/mks-logic/SPY  |  Group: 1 PII masking  |  Raw: D-77.md; D-121.md
- Size: 4,491 medical consultations + 4,197 legal questions
- Documents: informal legal questions, online medical consultation forms  |  Language: en
- PII: synthetic: Llama-3-70B text with placeholders, filled by Faker at load time
- Labels: 7: NAME, EMAIL, PHONE_NUM, ADDRESS, URL, USERNAME, ID_NUM
- Mapping to our 13 types: PERSON, EMAIL, PHONE, ADDRESS; ID_NUM mixes ssn/iban/credit card/bban (must re-split); drop URL, USERNAME
- Format: tokens + trailing_whitespace + BIO ent_tags (placeholder JSONL in repo)
- Licence (verbatim): HF tag 'license: cc-by-4.0'; loader script SPY.py has '_LICENSE = ""'
- Commercial: yes (tag); Llama output terms apply (inference)  |  Redistribution: yes  |  Access: open, but loader needs trust_remote_code
- Quality / known issues: Do not run the loader (executes repo code). Default Faker locale is en_US in SPY.py. NAACL SRW 2025.
- UK relevance: low
- Our use: **(c)** Take the placeholder texts and fill them with our UK generator; good legal/medical question templates.

### 24. srirxml/PANORAMA

- URL: https://huggingface.co/datasets/srirxml/PANORAMA  |  Group: 1 PII masking  |  Raw: D-122.md; D-112.md
- Size: 384,789 samples from 9,674 profiles (paper); cardData lists 384,794 train examples
- Documents: wiki-style bios, social posts, forum posts, reviews, comments, marketplace listings  |  Language: en, 8 locales incl. United Kingdom
- PII: synthetic (OpenAI o3-mini + Faker)
- Labels: no span labels (id, content-type, text); profiles in PANORAMA-Plus
- Mapping to our 13 types: labels must be derived by matching profile values (inference)
- Format: text only
- Licence (verbatim): 'Creative Commons Attribution 4.0 International (CC BY 4.0)'
- Commercial: yes (check OpenAI output terms, inference)  |  Redistribution: yes  |  Access: gated 'auto' (accept terms)
- Quality / known issues: Paper limitation: 'the model occasionally generated social handles that were not present in the input.'
- UK relevance: medium (UK locale share ~1/8 per paper)
- Our use: **(c)** Source of informal UK-locale text with embedded PII for chat-style chunks; needs our own labelling.

### 25. Kaggle PII Data Detection (PIILO) / CRAPII

- URL: https://www.kaggle.com/datasets/lburleigh/piilo-dataset  |  Group: 1 PII masking  |  Raw: D-123.md; D-31.md; D-121.md
- Size: ~22,000 essays (PIILO); 22,688 essays (CRAPII); HF mirror metaboulie/Tidied-PII-Detection-Kaggle-7k has 6,807 rows
- Documents: student essays (one design-thinking prompt)  |  Language: en
- PII: real essays; CRAPII states identifiers 'replaced with surrogate identifiers'
- Labels: 7: NAME_STUDENT, EMAIL, USERNAME, ID_NUM, PHONE_NUM, URL_PERSONAL, STREET_ADDRESS
- Mapping to our 13 types: PERSON<-NAME_STUDENT, EMAIL, PHONE, ADDRESS, CUSTOM<-ID_NUM; drop URL/USERNAME
- Format: spaCy tokens + trailing_whitespace + BIO labels
- Licence (verbatim): PIILO: 'PIILO © 2024 by The Learning Agency Lab is licensed under CC BY 4.0.' CRAPII: 'Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)'
- Commercial: PIILO yes / CRAPII no  |  Redistribution: yes (attribution)  |  Access: Kaggle download
- Quality / known issues: SPY paper: 'only 24% of all essays contain any personal data, and six of the seven entity types have fewer than 110 samples'. Kaggle competition pages blocked our fetch (rate limit).
- UK relevance: low
- Our use: **(a)** Real-person-derived text: local eval of PERSON recall only, never through Mubit.

### 26. beki/privy

- URL: https://huggingface.co/datasets/beki/privy  |  Group: 1 PII masking  |  Raw: D-14.md
- Size: not stated on the fetched card (no viewer)
- Documents: protocol traces from OpenAPI specs: JSON, SQL, HTML, XML  |  Language: en
- PII: synthetic
- Labels: 60+ types; Presidio set incl. PERSON, LOCATION, NRP, DATE_TIME, CREDIT_CARD, IBAN_CODE, US_BANK_NUMBER, PHONE_NUMBER, US_SSN, US_PASSPORT, US_DRIVER_LICENSE, EMAIL_ADDRESS...
- Mapping to our 13 types: coarse, US-centric
- Format: spans + tokens (Presidio format)
- Licence (verbatim): 'license: mit'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: API payloads, not documents.
- UK relevance: low
- Our use: **(d)** Wrong domain for Veil.

### 27. NHSEDataScience/synthetic_clinical_notes

- URL: https://huggingface.co/datasets/NHSEDataScience/synthetic_clinical_notes  |  Group: 1 PII masking  |  Raw: D-33.md
- Size: HF tag 1K<n<10K (viewer did not report rows)
- Documents: synthetic NHS admissions and clinical notes (ward, bed, trust)  |  Language: en-GB
- PII: synthetic ('All data found in this repository is entirely synthetic.')
- Labels: structured fields: patient_name, first_name, surname, date_of_birth (DD/MM/YYYY), nhs_number, admission_timestamp, site_name, ward
- Mapping to our 13 types: PERSON, DOB, NHS number -> CUSTOM (our decision); notes need span labels by value matching (inference)
- Format: tabular fields + notes (Gold/Silver/Bronze tiers)
- Licence (verbatim): 'license: mit'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card: 'Synthetic data does have limitations.' Gold tier checked by clinicians.
- UK relevance: high (NHS England)
- Our use: **(c)+(b)** UK medical letter templates with DOB and NHS numbers; synthetic and MIT, so usable as traffic after labelling.

### 28. hyunjunian/RedacBench

- URL: https://huggingface.co/datasets/hyunjunian/RedacBench  |  Group: 1 PII masking  |  Raw: D-114.md
- Size: 514 texts, 187 policies, 8,053 propositions (3,591 sensitive)
- Documents: public research texts incl. PIILO essays  |  Language: en
- PII: real public research text
- Labels: policy violations per proposition (not spans)
- Mapping to our 13 types: none (not span-level)
- Format: single JSON (policies, texts, propositions)
- Licence (verbatim): 'license: cc-by-4.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: arXiv 2603.20208; policy-conditioned.
- UK relevance: low
- Our use: **(d)** Different task (policy redaction).

### 29. guneeshv/REDACT-PII-Benchmark

- URL: https://huggingface.co/datasets/guneeshv/REDACT-PII-Benchmark  |  Group: 1 PII masking  |  Raw: D-127.md; D-115.md
- Size: 13,427 records, 324,078 entities; locked eval split 1,000
- Documents: generated records across domains and formats  |  Language: 25 languages incl. en
- PII: synthetic
- Labels: 51 canonical entity types + disclosed / disclosure_form / sensitivity_tier
- Mapping to our 13 types: likely broad (label list in GitHub schema, not read)
- Format: text + entities {entity_type, entity_string, start, end}
- Licence (verbatim): HF tag 'license: other'; page section 'REDACT Dataset Terms' (not readable without accepting)
- Commercial: unknown  |  Redistribution: unknown  |  Access: gated 'auto'
- Quality / known issues: Card: GPT-4.1 exact micro-F1 0.558, Claude Sonnet 4.6 0.602 on the locked split. EMNLP 2026 Industry Track.
- UK relevance: low
- Our use: **(a)** Hard eval set, only after a human reads the terms.

### 30. PII-Bench (Shen et al., arXiv 2502.18545)

- URL: https://arxiv.org/abs/2502.18545  |  Group: 1 PII masking  |  Raw: D-126.md
- Size: 2,842 test samples, 55 PII categories (abstract)
- Documents: query + context, single and multi-party  |  Language: not stated in abstract
- PII: crafted
- Labels: 55 categories + query relevance
- Mapping to our 13 types: n/a
- Format: not checked
- Licence (verbatim): not found
- Commercial: unknown  |  Redistribution: unknown  |  Access: data location not found (no HF link)
- Quality / known issues: Query-aware masking task.
- UK relevance: low
- Our use: **(d)** Not obtainable today.

### 31. microsoft/presidio-research (data generator)

- URL: https://github.com/microsoft/presidio-research  |  Group: 1 PII masking  |  Raw: D-88.md; D-89.md
- Size: code + templates (no fixed dataset)
- Documents: template sentences ('My name is {{name}}')  |  Language: en
- PII: synthetic (Faker / Fake Name Generator)
- Labels: Presidio entity types
- Mapping to our 13 types: we choose
- Format: InputSample spans
- Licence (verbatim): 'MIT License' (LICENSE); 'Fake Name Generator identities ... are licensed under a Creative Commons Attribution-Share Alike 3.0 United States License'
- Commercial: yes  |  Redistribution: yes (SA for identities)  |  Access: open
- Quality / known issues: Includes pattern-aware train/test split notebook (avoid template leakage).
- UK relevance: low (we would use Faker en_GB)
- Our use: **(c)** Copy the template-split idea; do not ship its CC BY-SA identity file.

### 32. AIxBlock/92k-real-world-call-center-scripts-english

- URL: https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english  |  Group: 1 PII masking  |  Raw: D-117.md; D-125.md
- Size: 91,706 transcripts (~10,500 hours audio, audio not included)
- Documents: real inbound/outbound call-centre transcripts  |  Language: en (Indian, American, Filipino accents)
- PII: real, redacted for PII
- Labels: redaction list incl. person_name, phone_number, account_number, credit_card_number, date_of_birth, email_address, location...
- Mapping to our 13 types: placeholders only
- Format: JSON transcripts with timestamps
- Licence (verbatim): 'Provided strictly for research and AI model development. Commercial use, resale, or redistribution is prohibited.' (HF tag cc-by-nc-4.0)
- Commercial: no  |  Redistribution: no  |  Access: open download
- Quality / known issues: ASR by AssemblyAI; WER-based QA.
- UK relevance: low
- Our use: **(d)** Non-commercial and real-person-derived.

### 33. AIxBlock/stimulated-chatbot-conversations-PII-detection-7languages

- URL: https://huggingface.co/datasets/AIxBlock/stimulated-chatbot-conversations-PII-detection-7languages  |  Group: 1 PII masking  |  Raw: D-38.md
- Size: n<1K (tag)
- Documents: human-written support chats with PII  |  Language: en, fr, de, es + others
- PII: human-generated synthetic
- Labels: names, addresses, phone numbers, ID numbers (card)
- Mapping to our 13 types: partial
- Format: not checked
- Licence (verbatim): 'license: cc-by-nc-4.0'
- Commercial: no  |  Redistribution: non-commercial  |  Access: open
- Quality / known issues: Card: 'created entirely by humans, prior to the advent of ChatGPT'.
- UK relevance: low
- Our use: **(d)** Non-commercial.

### 34. RobinSta/SynthPAI

- URL: https://huggingface.co/datasets/RobinSta/SynthPAI  |  Group: 1 PII masking  |  Raw: D-79.md
- Size: 7,823 comments in 103 threads
- Documents: synthetic forum comments (GPT-4 agents)  |  Language: en
- PII: synthetic personal attributes
- Labels: inferable attributes per profile (not spans)
- Mapping to our 13 types: none
- Format: comments + profile + guesses
- Licence (verbatim): 'License: CC-BY-NC-SA-4.0'
- Commercial: no  |  Redistribution: share-alike, non-commercial  |  Access: open
- Quality / known issues: Attribute inference task.
- UK relevance: low
- Our use: **(d)** Wrong task, non-commercial.

### 35. bigcode/bigcode-pii-dataset

- URL: https://huggingface.co/datasets/bigcode/bigcode-pii-dataset  |  Group: 1 PII masking  |  Raw: D-70.md
- Size: tag 10K<n<100K
- Documents: source code  |  Language: code
- PII: real code with PII
- Labels: not readable (gated)
- Mapping to our 13 types: n/a
- Format: token-classification
- Licence (verbatim): gated 'manual'; README not readable without approval
- Commercial: unknown  |  Redistribution: unknown  |  Access: gated manual
- Quality / known issues: Code domain.
- UK relevance: none
- Our use: **(d)** Code, gated.

### 36. Other screened, not useful (scanpatch Ukrainian/Russian NER, hivetrace Russian bench, vkatg streaming PHI, paperboy desktop screenshots, capitaletech resume images, AdamLucek en-us-30k, MedOtter/PANORAMA)

- URL: https://huggingface.co/datasets  |  Group: 1 PII masking  |  Raw: D-32.md; D-18.md; D-34.md; D-30.md; D-37.md; D-27.md; D-26.md
- Size: 5,318 / 1,810 / 328 / 500 / 2,875 / 29,595 / 2,238 rows
- Documents: various  |  Language: uk+ru / ru / en / images / images / en / medical imaging
- PII: synthetic or n/a
- Labels: various
- Mapping to our 13 types: n/a
- Format: various
- Licence (verbatim): MIT / Apache-2.0 / MIT / other / none / 'cc' (no version) / CC BY-NC 4.0
- Commercial: various  |  Redistribution: various  |  Access: open
- Quality / known issues: MedOtter/PANORAMA is a pancreatic imaging set (name clash with PII PANORAMA).
- UK relevance: none
- Our use: **(d)** Wrong language, modality or task, or unclear licence.

### 37. Text Anonymization Benchmark (TAB)

- URL: https://github.com/NorskRegnesentral/text-anonymization-benchmark  |  Group: 2 Anonymisation  |  Raw: D-35.md; D-36.md; D-86.md; D-113.md
- Size: 1,268 ECHR cases (card); HF ildpil/text-anonymization-benchmark 2,208 annotation rows (1,112 / 541 / 555)
- Documents: European Court of Human Rights judgments  |  Language: en
- PII: real (public court judgments)
- Labels: PERSON, CODE, LOC, ORG, DEM, DATETIME, QUANTITY + identifier type DIRECT / QUASI / NO_MASK, confidential attributes, coreference
- Mapping to our 13 types: PERSON<-PERSON; CUSTOM<-CODE (application numbers); ADDRESS partial from LOC; most others are keep-classes for us
- Format: text + entity_mentions with start_offset/end_offset (char), per annotator
- Licence (verbatim): 'TAB is released under an MIT License.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Multiple annotators per document; quality_checked flag.
- UK relevance: medium (European legal English)
- Our use: **(a)** Gold legal eval for PERSON and case codes; real names, so never through Mubit.

### 38. i2b2 / n2c2 de-identification (2006, 2014)

- URL: https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/  |  Group: 2 Anonymisation  |  Raw: D-102.md
- Size: not checked
- Documents: US clinical notes (Partners Healthcare)  |  Language: en
- PII: real (de-identified with surrogates)
- Labels: HIPAA PHI types
- Mapping to our 13 types: partial
- Format: XML
- Licence (verbatim): 'Registration is not open for Unstructured notes from the Research Patient Data Registry at Partners Healthcare ... at this time.'
- Commercial: no  |  Redistribution: no  |  Access: restricted, registration closed
- Quality / known issues: Standard clinical de-id benchmark.
- UK relevance: low
- Our use: **(d)** Not obtainable now; real patient data.

### 39. MIMIC-IV-Note (PhysioNet)

- URL: https://physionet.org/content/mimic-iv-note/2.2/  |  Group: 2 Anonymisation  |  Raw: D-103.md
- Size: not checked
- Documents: de-identified US clinical notes  |  Language: en
- PII: real (de-identified)
- Labels: none for PII
- Mapping to our 13 types: n/a
- Format: CSV
- Licence (verbatim): 'Credentialed Access'
- Commercial: no  |  Redistribution: no  |  Access: credentialed
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(d)** Credentialed real patient data.

### 40. PhysioNet deid (software + gold standard)

- URL: https://physionet.org/content/deid/1.1/  |  Group: 2 Anonymisation  |  Raw: D-101.md
- Size: not checked
- Documents: nursing notes and discharge summaries (de-id software)  |  Language: en
- PII: real (surrogates)
- Labels: PHI
- Mapping to our 13 types: n/a
- Format: perl + text
- Licence (verbatim): 'COPYING - GNU General Public License, version 2'
- Commercial: yes (GPL terms)  |  Redistribution: GPL  |  Access: open (corpus access not verified)
- Quality / known issues: Rule lists (name lists, common words) could inspire regex checks.
- UK relevance: low
- Our use: **(d)** US clinical; software, not a training set.

### 41. joelniklaus/mapa (MAPA anonymisation corpus)

- URL: https://huggingface.co/datasets/joelniklaus/mapa  |  Group: 2 Anonymisation  |  Raw: D-72.md; D-16.md
- Size: 41,767 rows (27,823 / 3,354 / 10,590)
- Documents: EUR-Lex legal documents  |  Language: 24 EU languages incl. en
- PII: real public legal text
- Labels: coarse and fine levels incl. PERSON, ADDRESS, AMOUNT, DATE, ORGANISATION, license plate
- Mapping to our 13 types: PERSON, ADDRESS; drop AMOUNT, DATE, ORGANISATION
- Format: tokens + coarse/fine BIO tags
- Licence (verbatim): 'Attribution 4.0 International (CC BY 4.0)'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: piimb says the source MAPA labels 'are unsuitable for PII-masking evaluation' and relabelled 2 docs.
- UK relevance: low
- Our use: **(a)** Legal-domain sanity eval only.

### 42. CoNLL-2003 (eriktks/conll2003)

- URL: https://huggingface.co/datasets/eriktks/conll2003  |  Group: 3 NER  |  Raw: D-39.md
- Size: 14,041 / 3,250 / 3,453 sentences
- Documents: Reuters news  |  Language: en
- PII: real (public figures)
- Labels: PER, LOC, ORG, MISC
- Mapping to our 13 types: PERSON<-PER only
- Format: tokens + BIO
- Licence (verbatim): 'Because of copyright reasons we only make available the annotations. In order to build the complete data sets you will need access to the Reuters Corpus. It can be obtained for research purposes without any charge from NIST.'
- Commercial: no (inference from research-only Reuters terms)  |  Redistribution: no  |  Access: HF mirror; Reuters terms
- Quality / known issues: News, not documents.
- UK relevance: low
- Our use: **(d)** Research-only text; PER of public figures is not our PERSON.

### 43. OntoNotes 5.0 (LDC2013T19)

- URL: https://catalog.ldc.upenn.edu/LDC2013T19  |  Group: 3 NER  |  Raw: D-119.md; D-40.md; D-41.md
- Size: tner/ontonotes5: 76,714 rows (59,924 / 8,528 / 8,262)
- Documents: news, conversation, web  |  Language: en, zh, ar
- PII: real
- Labels: 18 OntoNotes NER types
- Mapping to our 13 types: PERSON only
- Format: tokens + tags
- Licence (verbatim): LDC: 'LDC User Agreement for Non-Members' (fee shown after login); HF ontonotes/conll2012_ontonotesv5 tag 'cc-by-nc-nd-4.0'
- Commercial: no without LDC licence  |  Redistribution: no  |  Access: LDC
- Quality / known issues: HF mirrors of LDC data are a licence risk.
- UK relevance: low
- Our use: **(d)** LDC-licensed.

### 44. DFKI-SLT/few-nerd

- URL: https://huggingface.co/datasets/DFKI-SLT/few-nerd  |  Group: 3 NER  |  Raw: D-42.md
- Size: supervised: 131,767 / 18,824 / 37,648 sentences
- Documents: Wikipedia  |  Language: en
- PII: real (public entities)
- Labels: coarse + fine types (person-*, location-*, organization-*...)
- Mapping to our 13 types: PERSON<-person-*; useful as KEEP negatives for organisations and places
- Format: tokens + ner_tags + fine_ner_tags
- Licence (verbatim): 'CC BY-SA 4.0 license'
- Commercial: yes (share-alike)  |  Redistribution: share-alike  |  Access: open
- Quality / known issues: Encyclopedic text.
- UK relevance: low
- Our use: **(c)** Negative examples of public org/place names; ShareAlike if redistributed.

### 45. Babelscape/multinerd

- URL: https://huggingface.co/datasets/Babelscape/multinerd  |  Group: 3 NER  |  Raw: D-43.md
- Size: 3,349,186 rows
- Documents: Wikipedia + WikiNews  |  Language: 10 languages
- PII: real (public)
- Labels: 15 NER types
- Mapping to our 13 types: PERSON only
- Format: tokens + ner_tags
- Licence (verbatim): 'Contents of this repository are restricted to only non-commercial research purposes under the ... (CC BY-NC-SA 4.0)'
- Commercial: no  |  Redistribution: non-commercial SA  |  Access: open
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(d)** Non-commercial.

### 46. WikiNER / Babelscape/wikineural

- URL: https://huggingface.co/datasets/Babelscape/wikineural  |  Group: 3 NER  |  Raw: D-44.md
- Size: WikiNEuRal: 1,027,506 rows
- Documents: Wikipedia  |  Language: 9 languages
- PII: real (public)
- Labels: PER, ORG, LOC, MISC
- Mapping to our 13 types: PERSON only
- Format: tokens + ner_tags
- Licence (verbatim): WikiNEuRal: 'restricted to only non-commercial research purposes under the ... (CC BY-NC-SA 4.0)'. Original WikiNER: licence not verified (no authoritative HF copy found).
- Commercial: no  |  Redistribution: no  |  Access: open
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(d)** Non-commercial; WikiNER licence not found.

### 47. WNUT-17 (leondz/wnut_17)

- URL: https://huggingface.co/datasets/leondz/wnut_17  |  Group: 3 NER  |  Raw: D-45.md
- Size: 3,394 / 1,009 / 1,287 sentences
- Documents: social media (emerging entities)  |  Language: en
- PII: real (social media)
- Labels: emerging entity types (not extracted here)
- Mapping to our 13 types: PERSON only
- Format: tokens + ner_tags
- Licence (verbatim): HF tag 'cc-by-4.0'; licensing section 'More Information Needed'
- Commercial: likely yes (tag only)  |  Redistribution: likely yes  |  Access: open
- Quality / known issues: Noisy text, few persons.
- UK relevance: low
- Our use: **(a)** PERSON recall in noisy chat-like text, local only.

### 48. Broad Twitter Corpus (tner/btc)

- URL: https://huggingface.co/datasets/tner/btc  |  Group: 3 NER  |  Raw: D-46.md
- Size: 9,339 (6,338 / 1,001 / 2,000)
- Documents: tweets  |  Language: en
- PII: real
- Labels: PER, LOC, ORG
- Mapping to our 13 types: PERSON only
- Format: tokens + tags
- Licence (verbatim): HF tag 'license: other'; GitHub API licence 'NOASSERTION'
- Commercial: unclear  |  Redistribution: unclear  |  Access: open
- Quality / known issues: n/a
- UK relevance: not verified
- Our use: **(d)** Licence unclear.

### 49. Enron personal-name NER (Minkov et al., CMU)

- URL: https://www.cs.cmu.edu/~einat/datasets.html  |  Group: 3 NER  |  Raw: D-98.md
- Size: Enron-Meetings + Enron-Random subsets (counts in paper, not extracted)
- Documents: real emails  |  Language: en
- PII: real
- Labels: personal name spans
- Mapping to our 13 types: PERSON
- Format: Minorthird format / XML tags
- Licence (verbatim): 'made available for research purposes'
- Commercial: no (inference)  |  Redistribution: no  |  Access: open download
- Quality / known issues: Only names annotated.
- UK relevance: low
- Our use: **(a)** Local PERSON-in-email eval only; never through Mubit.

### 50. CUAD (theatticusproject/cuad, cuad-qa)

- URL: https://huggingface.co/datasets/theatticusproject/cuad-qa  |  Group: 4 Documents  |  Raw: D-47.md; D-84.md
- Size: 510 contracts, 13,000+ labels, 41 clause categories; cuad-qa 22,450 / 4,182 QA rows
- Documents: commercial contracts from SEC EDGAR  |  Language: en
- PII: real (company names, some signatories)
- Labels: clause categories (no PII labels)
- Mapping to our 13 types: none; source of contract text and company-name negatives
- Format: text / SQuAD-style QA
- Licence (verbatim): 'CUAD is licensed under the Creative Commons Attribution 4.0 (CC BY 4.0) license and free to the public for commercial and non-commercial use.' / 'The creators make no representations or warranties regarding the license status of the underlying contracts'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: US contracts.
- UK relevance: low-medium
- Our use: **(c)** Contract templates: swap parties and signatories for synthetic UK people/addresses, keep company boilerplate as negatives.

### 51. ContractNLI

- URL: https://stanfordnlp.github.io/contract-nli/  |  Group: 4 Documents  |  Raw: D-106.md; D-50.md
- Size: 607 NDAs, 17 hypotheses
- Documents: non-disclosure agreements  |  Language: en
- PII: real (parties)
- Labels: NLI + evidence spans
- Mapping to our 13 types: none
- Format: JSON
- Licence (verbatim): 'The Dataset is being made available to you pursuant to ... the Creative Commons Attribution 4.0 International Public License.' (Hitachi America terms). HF mirror kiddothe2b/contract-nli is tagged 'cc-by-nc-sa-4.0'.
- Commercial: yes (official)  |  Redistribution: yes  |  Access: click-through terms
- Quality / known issues: Licence conflict with HF mirror: use the official download.
- UK relevance: low-medium
- Our use: **(c)** NDA templates.

### 52. LEDGAR (coastalcph/lex_glue, config ledgar)

- URL: https://huggingface.co/datasets/coastalcph/lex_glue  |  Group: 4 Documents  |  Raw: D-49.md
- Size: 60,000 / 10,000 / 10,000 provisions
- Documents: contract provisions from EDGAR  |  Language: en
- PII: real (rare)
- Labels: 100 provision types
- Mapping to our 13 types: none
- Format: text + label
- Licence (verbatim): HF tag 'cc-by-4.0'; licensing section 'More Information Needed'
- Commercial: likely yes  |  Redistribution: likely yes  |  Access: open
- Quality / known issues: Clause snippets only.
- UK relevance: low
- Our use: **(c)** Clause text as no-PII negatives.

### 53. theatticusproject/maud

- URL: https://huggingface.co/datasets/theatticusproject/maud  |  Group: 4 Documents  |  Raw: D-48.md
- Size: 39,231 rows (25,827 / 6,753 / 6,651)
- Documents: merger agreements (Q&A)  |  Language: en
- PII: real (companies)
- Labels: deal-point answers
- Mapping to our 13 types: none
- Format: text + QA
- Licence (verbatim): 'license: cc-by-4.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(c)** Long legal text negatives.

### 54. SEC EDGAR / eloukas/edgar-corpus

- URL: https://huggingface.co/datasets/eloukas/edgar-corpus  |  Group: 4 Documents  |  Raw: D-51.md; D-120.md
- Size: yearly configs from 1993; e.g. 220,375 rows in one listed split
- Documents: 10-K annual report sections  |  Language: en
- PII: real (executives)
- Labels: none
- Mapping to our 13 types: none
- Format: JSONL by year
- Licence (verbatim): 'EDGAR data is publicly available.' (HF tag apache-2.0); sec.gov access page returned 403 to our fetch
- Commercial: likely yes (inference: US government public data)  |  Redistribution: likely yes  |  Access: open
- Quality / known issues: Financial reports, little personal data.
- UK relevance: low
- Our use: **(c)** Finance boilerplate negatives.

### 55. Kleister NDA + Kleister Charity (applicaai)

- URL: https://github.com/applicaai/kleister-charity  |  Group: 4 Documents  |  Raw: D-90.md; D-91.md; D-83.md
- Size: HF mirror orgrctera/kleister_charity_train: 1,729 rows
- Documents: Charity: annual reports of British charities (PDF); NDA: EDGAR NDAs  |  Language: en (UK for Charity)
- PII: real (trustees, addresses)
- Labels: key-value extraction (charity address, number, name, income...; NDA parties)
- Mapping to our 13 types: ADDRESS (charity address), CUSTOM (charity number) - org data, mostly keep
- Format: TSV + PDF
- Licence (verbatim): README: no licence statement found; GitHub API licence: none. Charity data 'downloaded from https://www.gov.uk/government/organisations/charity-commission'
- Commercial: unknown  |  Redistribution: unknown  |  Access: open download
- Quality / known issues: Scanned PDFs, OCR needed.
- UK relevance: high (Charity)
- Our use: **(c)** UK document layouts; local reference only until licence is clarified.

### 56. GOV.UK model agreement for a shorthold assured tenancy

- URL: https://www.gov.uk/government/publications/model-agreement-for-a-shorthold-assured-tenancy  |  Group: 4 Documents  |  Raw: D-107.md; D-108.md
- Size: 1 template
- Documents: tenancy agreement template  |  Language: en-GB
- PII: none (blank template)
- Labels: n/a
- Mapping to our 13 types: template slots -> PERSON, ADDRESS, POSTCODE, BANK_ACCOUNT, SORT_CODE, DOB (our fill)
- Format: PDF/DOCX
- Licence (verbatim): GOV.UK content API: document_type 'gone', public_updated_at 2026-08-05, alternative_path to the UK Government Web Archive. OGL v3: 'exploit the Information commercially and non-commercially' / does not cover 'personal data in the Information'
- Commercial: yes  |  Redistribution: yes, with attribution  |  Access: archived copy only
- Quality / known issues: Page withdrawn from GOV.UK; use the web-archive copy.
- UK relevance: high
- Our use: **(c)** Core UK tenancy template for the generator.

### 57. legislation.gov.uk (othertales/uklegislation)

- URL: https://huggingface.co/datasets/othertales/uklegislation  |  Group: 4 Documents  |  Raw: D-81.md; D-111.md
- Size: 43,070 items
- Documents: UK Acts and SIs  |  Language: en-GB
- PII: none
- Labels: none
- Mapping to our 13 types: none
- Format: text + XML
- Licence (verbatim): 'Legislative content is generally covered by the UK Open Government Licence v3.0, but confirm applicability to your downstream use-case.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Third-party scrape; check against legislation.gov.uk.
- UK relevance: high
- Our use: **(c)** No-PII UK legal text: negatives with dates, section numbers and amounts.

### 58. Find Case Law (The National Archives)

- URL: https://caselaw.nationalarchives.gov.uk/  |  Group: 4 Documents  |  Raw: D-99.md; D-109.md; D-110.md
- Size: not checked
- Documents: UK court judgments and tribunal decisions  |  Language: en-GB
- PII: real (parties, witnesses)
- Labels: none
- Mapping to our 13 types: none
- Format: XML/HTML/PDF
- Licence (verbatim): 'The Open Justice Licence does not permit computational analysis.' Computational analysis includes 'machine learning or AI training on judgment datasets' and 'natural language processing of judgment text'. 'There are no costs to apply for a licence'
- Commercial: yes for publishing; ML/NLP needs licence  |  Redistribution: yes under OJL  |  Access: open; licence application for ML
- Quality / known issues: Real names of parties.
- UK relevance: high
- Our use: **(d)** ML training or NLP over judgments needs a TNA licence; do not use tonight.

### 59. Companies House Free Company Data Product

- URL: https://download.companieshouse.gov.uk/en_output.html  |  Group: 4 Documents  |  Raw: D-100.md; D-124.md
- Size: monthly snapshot; BasicCompanyDataAsOneFile-2026-10-01.zip (471Mb)
- Documents: CSV of live companies (name, number, registered office address, SIC, status)  |  Language: en-GB
- PII: real (registered addresses; officer data in other products)
- Labels: none
- Mapping to our 13 types: company names = KEEP negatives; addresses = UK address/postcode shapes
- Format: CSV
- Licence (verbatim): 'We impose no rules or requirements on how the information on the public register is used' / 'You are responsible for complying with any applicable data protection, copyright and other legislation' / FOI 2014: 'CH does not make public information, including the Free Company Data Product, available under the Open Government Licence (OGL).'
- Commercial: yes (no CH restrictions; data protection applies)  |  Redistribution: yes, at own legal risk  |  Access: open download
- Quality / known issues: Real data: use locally only.
- UK relevance: high
- Our use: **(c)** Real UK company names for 'keep' negatives and real postcode shapes; never send to Mubit.

### 60. Enron email corpus (CMU; HF mirrors corbt/enron-emails, LLM-PBE/enron-email, Yale-LILY/aeslc)

- URL: https://www.cs.cmu.edu/~enron/  |  Group: 4 Documents  |  Raw: D-97.md; D-52.md; D-53.md; D-54.md
- Size: ~0.5M messages from ~150 users (CMU); corbt 517,401; LLM-PBE 490,408; AESLC 18,302
- Documents: corporate emails  |  Language: en (US)
- PII: real
- Labels: none (AESLC: subject lines)
- Mapping to our 13 types: none
- Format: maildir / text
- Licence (verbatim): CMU: 'I am distributing this dataset as a resource for researchers'. Mirrors: corbt no licence tag; LLM-PBE tag 'apache-2.0'; AESLC 'unknown'
- Commercial: unclear  |  Redistribution: unclear  |  Access: open
- Quality / known issues: Some messages deleted 'as part of a redaction effort due to requests from affected employees'.
- UK relevance: low
- Our use: **(a)** Email structure reference and local eval only; real people, never through Mubit.

### 61. SAMSum (knkarthick/samsum)

- URL: https://huggingface.co/datasets/knkarthick/samsum  |  Group: 4 Documents  |  Raw: D-80.md; D-55.md
- Size: 16,368 (14,731 / 818 / 819)
- Documents: messenger-style dialogues + summaries  |  Language: en
- PII: names only
- Labels: none
- Mapping to our 13 types: none
- Format: dialogue + summary
- Licence (verbatim): 'distributed for research purposes (non-commercial licence: CC BY-NC-ND 4.0)'
- Commercial: no  |  Redistribution: no derivatives  |  Access: open (original Samsung/samsum repo not found on HF)
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(d)** NC-ND.

### 62. DialogSum (knkarthick/dialogsum)

- URL: https://huggingface.co/datasets/knkarthick/dialogsum  |  Group: 4 Documents  |  Raw: D-56.md
- Size: 14,460 (12,460 / 500 / 1,500)
- Documents: spoken-style dialogues  |  Language: en
- PII: names
- Labels: none
- Mapping to our 13 types: none
- Format: dialogue + summary + topic
- Licence (verbatim): 'CC BY-NC-SA 4.0'
- Commercial: no  |  Redistribution: non-commercial SA  |  Access: open
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(d)** Non-commercial.

### 63. bitext/Bitext-retail-banking-llm-chatbot-training-dataset

- URL: https://huggingface.co/datasets/bitext/Bitext-retail-banking-llm-chatbot-training-dataset  |  Group: 4 Documents  |  Raw: D-58.md
- Size: 25,545 rows
- Documents: banking customer-support instructions and responses with {{placeholders}}  |  Language: en
- PII: none (placeholders)
- Labels: intent + category
- Mapping to our 13 types: placeholders -> CUSTOM / BANK_ACCOUNT / CARD after we fill them
- Format: instruction, response, intent, category, tags
- Licence (verbatim): 'released under the Community Data License Agreement (CDLA) Sharing 1.0' / 'Users must attribute the dataset and continue to share derivatives under the same license.'
- Commercial: yes  |  Redistribution: share derivatives under CDLA-Sharing  |  Access: open
- Quality / known issues: Placeholders like '{{Order Number}}' make span labels free.
- UK relevance: medium
- Our use: **(c)+(b)** Fill placeholders with UK fakes -> labelled chat traffic for banking questions.

### 64. bitext/Bitext-customer-support-llm-chatbot-training-dataset

- URL: https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset  |  Group: 4 Documents  |  Raw: D-57.md
- Size: 26,872 rows
- Documents: general customer-support chats with {{placeholders}}  |  Language: en
- PII: none (placeholders)
- Labels: intent + category
- Mapping to our 13 types: as banking set
- Format: instruction, response, intent, category, flags
- Licence (verbatim): HF tag 'cdla-sharing-1.0'
- Commercial: yes  |  Redistribution: share-alike  |  Access: open
- Quality / known issues: Seen: 'question about cancelling order {{Order Number}}'.
- UK relevance: medium
- Our use: **(c)+(b)** Same trick; CUSTOM references (order, account numbers).

### 65. MultiWOZ 2.1 / 2.2 (ConvLab/multiwoz21, pfb30/multi_woz_v22)

- URL: https://github.com/budzianowski/multiwoz  |  Group: 4 Documents  |  Raw: D-94.md; D-85.md; D-69.md
- Size: v2.2: 8,437 / 1,000 / 1,000 dialogues
- Documents: task dialogues in Cambridge UK (restaurants, hotels, trains, taxis)  |  Language: en-GB
- PII: business data; booking references
- Labels: dialogue acts and slots
- Mapping to our 13 types: booking references -> CUSTOM; venue phone/postcode are business (KEEP)
- Format: JSON dialogues + DB
- Licence (verbatim): GitHub: 'released by Paweł Budzianowski from Cambridge Dialogue Systems Group under the MIT License.' HF: 'Apache License 2.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Seen DB rows: postcode 'cb58nt', phone '01223902088' (lowercase, no space).
- UK relevance: high
- Our use: **(c)** UK chat templates and realistic UK phone/postcode shapes; add synthetic personal details to the user turns.

### 66. UCI SMS Spam Collection (ucirvine/sms_spam)

- URL: https://archive.ics.uci.edu/dataset/228/sms+spam+collection  |  Group: 4 Documents  |  Raw: D-104.md; D-68.md
- Size: 5,574 SMS
- Documents: SMS (425 spam from UK forum Grumbletext, 450 ham from a Birmingham PhD thesis, 3,375 NUS Singapore ham)  |  Language: en
- PII: real
- Labels: ham/spam
- Mapping to our 13 types: none
- Format: text + label
- Licence (verbatim): UCI: 'This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license.' HF card: licence 'More Information Needed'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Short, informal.
- UK relevance: medium
- Our use: **(c)** Style reference for UK SMS chunks; local only (real messages).

### 67. apptek-com/apptek_callcenter_dialogues

- URL: https://huggingface.co/datasets/apptek-com/apptek_callcenter_dialogues  |  Group: 4 Documents  |  Raw: D-82.md
- Size: 2,619 rows (1,746 + 873 diarization)
- Documents: call-centre dialogues (audio + text)  |  Language: en incl. en-GB, en-GB_SCT, en-GB_WLS accents
- PII: none ('No personally identifiable information is included.')
- Labels: none
- Mapping to our 13 types: none
- Format: audio + text
- Licence (verbatim): 'License: CC BY-SA 4.0'
- Commercial: yes  |  Redistribution: share-alike  |  Access: open
- Quality / known issues: n/a
- UK relevance: medium
- Our use: **(c)** Call-centre style text; share-alike.

### 68. SROIE (ICDAR 2019)

- URL: https://github.com/zzzDavid/ICDAR-2019-SROIE  |  Group: 4 Documents  |  Raw: D-93.md; D-61.md
- Size: 1,000 scanned receipts (600 trainval / 400 test); HF darentang/sroie 973 rows
- Documents: receipts  |  Language: en
- PII: real shops
- Labels: company, date, address, total
- Mapping to our 13 types: shop address = KEEP
- Format: images + boxes + fields
- Licence (verbatim): repo LICENSE is MIT (code); dataset licence not stated
- Commercial: unknown  |  Redistribution: unknown  |  Access: open
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(d)** Data licence unknown, receipts have little personal data.

### 69. CORD (naver-clova-ix/cord-v2)

- URL: https://github.com/clovaai/cord  |  Group: 4 Documents  |  Raw: D-92.md; D-59.md
- Size: 1,000 released (800 / 100 / 100) of 11,000+ collected
- Documents: Indonesian receipts  |  Language: id/en
- PII: minimal
- Labels: receipt fields
- Mapping to our 13 types: none
- Format: images + JSON
- Licence (verbatim): 'This work is licensed under a Creative Commons Attribution 4.0 International License.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Some fields removed 'due to Indonesian legal issues'.
- UK relevance: low
- Our use: **(d)** Not UK; little PII.

### 70. FUNSD (nielsr/funsd)

- URL: https://guillaumejaume.github.io/FUNSD/  |  Group: 4 Documents  |  Raw: D-105.md; D-60.md
- Size: 199 forms, 31,485 words, 9,707 semantic entities
- Documents: scanned forms  |  Language: en
- PII: real (old forms)
- Labels: question/answer/header
- Mapping to our 13 types: none
- Format: images + words + boxes
- Licence (verbatim): Official page has a 'License' menu item but no licence text was retrieved; HF mirror has no licence
- Commercial: unknown  |  Redistribution: unknown  |  Access: open
- Quality / known issues: n/a
- UK relevance: low
- Our use: **(d)** Licence not verified.

### 71. AgamiAI/Indian-Bank-Statements

- URL: https://huggingface.co/datasets/AgamiAI/Indian-Bank-Statements  |  Group: 4 Documents  |  Raw: D-62.md
- Size: tag 10K<n<100K (viewer did not report)
- Documents: synthetic Indian business current-account statements  |  Language: en, hi
- PII: synthetic
- Labels: structured fields: account_holder, account_holder_address, account_number, ifsc_code, micr_code, customer_id, transactions
- Mapping to our 13 types: field names -> BANK_ACCOUNT, ADDRESS, CUSTOM
- Format: JSON records
- Licence (verbatim): 'License: Apache 2.0'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card: 'Business-only - No personal/savings account patterns'.
- UK relevance: low
- Our use: **(c)** Statement structure idea only; swap IFSC for sort codes.

### 72. Bankstatemently/bank-statement-parsing-benchmark

- URL: https://huggingface.co/datasets/Bankstatemently/bank-statement-parsing-benchmark  |  Group: 4 Documents  |  Raw: D-63.md
- Size: 15 synthetic statements (card); viewer 5 rows
- Documents: bank and card statement PDFs  |  Language: en, fr, nl + others; 12 countries
- PII: synthetic
- Labels: parsing ground truth
- Mapping to our 13 types: account numbers -> BANK_ACCOUNT/IBAN
- Format: PDF + JSON
- Licence (verbatim): 'MIT. See LICENSE.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card notes reissues to fix invalid IBAN check digits and static account numbers. UK not confirmed.
- UK relevance: unknown
- Our use: **(c)** PDF layout references for statement generator.

### 73. buthaya/payslips

- URL: https://huggingface.co/datasets/buthaya/payslips  |  Group: 4 Documents  |  Raw: D-64.md
- Size: 611 pages (485 / 126)
- Documents: payslip OCR pages  |  Language: en
- PII: masked/synthetic values (seen 'MMM CCC')
- Labels: word-level labels (salary and personal fields)
- Mapping to our 13 types: field labels -> PERSON, CUSTOM (pay no.)
- Format: words + boxes + labels
- Licence (verbatim): 'This dataset is released under the MIT License.'
- Commercial: yes  |  Redistribution: yes  |  Access: open
- Quality / known issues: Card: entities 'relevant to the insurance domain'.
- UK relevance: unknown
- Our use: **(c)** Payslip layout reference.

### 74. Resume / CV sets (opensporks/resumes, datasetmaster/resumes, d4rk3r/resumes-raw-pdf)

- URL: https://huggingface.co/datasets/opensporks/resumes  |  Group: 4 Documents  |  Raw: D-65.md; D-66.md; D-67.md
- Size: 2,484 / 4,817 / 1,940 PDFs
- Documents: CVs  |  Language: en
- PII: real or mixed (opensporks: 'Resume Examples taken from livecareer.com'; datasetmaster: 'merged collection of real and synthetic resume data')
- Labels: category only
- Mapping to our 13 types: none
- Format: text/HTML, JSON, PDF
- Licence (verbatim): opensporks: 'The license for this dataset is cc0-1.0' (converted from Kaggle snehaanbhawal/resume-dataset); datasetmaster: 'License: MIT'; d4rk3r: tag 'mit', provenance not stated
- Commercial: tags say yes; provenance doubtful  |  Redistribution: doubtful  |  Access: open
- Quality / known issues: Scraped or real CVs under permissive tags: provenance risk.
- UK relevance: low
- Our use: **(c)** CV section structure only, local; never through Mubit.

### 75. Suspicious leaked-data repos on HF (PhisherJR/Truecaller, PhisherJR/phonebook, PhisherJR/850M-India-data)

- URL: https://huggingface.co/PhisherJR  |  Group: 4 Documents  |  Raw: D-128.md
- Size: not opened
- Documents: unknown (names suggest scraped phone/identity data)  |  Language: unknown
- PII: likely real (inference from names)
- Labels: n/a
- Mapping to our 13 types: n/a
- Format: n/a
- Licence (verbatim): not opened
- Commercial: no  |  Redistribution: no  |  Access: public
- Quality / known issues: Seen only in HF search results.
- UK relevance: n/a
- Our use: **(d)** Possible personal-data dumps; do not download.

## Top 10 for us

1. **ai4privacy/pii-masking-openpii-1m** (b)+(a). CC BY 4.0 with commercial use and redistribution stated on the card, 1.43M synthetic rows, 35,830 GB-region train rows. Biggest legal source of Mubit training traffic. Needs remap (merge GIVENNAME+SURNAME, BUILDINGNUM+STREET+CITY), drop DATE/AGE/GENDER, and a UK-format filter (GB rows have weak postcodes and phones). Rows are short, so pack several rows into one chunk (inference) to look like our 1,500-token chunks.
2. **nvidia/Nemotron-PII** (b)+(a). CC BY 4.0, "ready for commercial use", document-shaped texts across 50+ industries, char spans already in our `start/end/text/label` shape. Take care: the card says 100k rows, the viewer shows 200k.
3. **gretelai/synthetic_pii_finance_multilingual** (b)+(c). Apache-2.0, full financial documents (avg 1,357 chars), has iban, bban, credit cards, DOB, passport, driving licence. Closest to contracts and bank letters. Drop `company`/`date` labels (our keep rule).
4. **gretelai/gretel-pii-masking-en-v1** (b)+(a). Apache-2.0, 60k English rows with a ready test split and many identifier types (customer_id, account_number, postcode, national_id) that feed CUSTOM and BANK_ACCOUNT.
5. **QuantumAiuk/uk-pii-redaction-synthetic** (b)+(a)+(c). Apache-2.0 and the only open set found with SORT_CODE, NI_NUMBER, NHS numbers, Ofcom drama phone ranges and UK postcodes. Small (3,000 train, 90 templates) and in masked-text form, so convert to spans; its unseen-template test and two hand-written "wild" sets are a ready UK eval.
6. **RedactionBench** (a). CC BY 4.0, 200 manually annotated documents in our document types (bank_statement, card_statement, invoice, receipt, lease_agreement, offer_letter, discharge_summary). Untyped (mandatory / contextual) spans, US-centric, half real-web documents: local eval of recall only.
7. **Text Anonymization Benchmark (TAB)** (a). MIT, real ECHR judgments with char offsets, DIRECT/QUASI identifier marks, several annotators. Best legal gold for PERSON and case codes. Real names, so never through Mubit.
8. **perplexity-ai/PII-TRACE** (a). MIT, 500 multi-turn chats with per-turn spans; matches Veil's chat UI. Small and regular, use as a chat smoke test.
9. **Bitext retail banking + customer support** (c)+(b). CDLA-Sharing-1.0, 52k support turns with `{{placeholders}}`. Filling placeholders with our UK fakes gives labelled banking and support chat for free. Share-alike applies to anything we publish from it.
10. **CUAD + ContractNLI + GOV.UK model tenancy agreement** (c). CC BY 4.0 (CUAD, ContractNLI official), OGL v3 (tenancy template, now only in the UK Government Web Archive). Contract and tenancy templates for the generator; swap parties for synthetic UK people.

Runners-up: MultiWOZ (UK chat shapes, MIT/Apache), NHSEDataScience/synthetic_clinical_notes (UK medical, MIT, synthetic), mks-logic/SPY (legal and medical question templates; refill with UK fakes, do not run its loader), srirxml/PANORAMA (UK-locale informal text, no labels), DataikuNLP/kiji (Apache, IBAN + DOB).

## Coverage gaps vs our 13 types and UK formats

| Our type | Best open coverage | Gap |
|---|---|---|
| PERSON | everywhere | UK name mix (South Asian, Eastern European, Ukrainian names) not checked; ai4privacy GB samples show odd names ("Hyon Davran", "Alpar Bualong") and names labelled USERNAME. |
| ADDRESS | ai4privacy (split into STREET/BUILDINGNUM/CITY), Gretel, Nemotron | Needs span merging; GB samples are often partial ("Saint Mary's Road"). Business addresses (MultiWOZ, Companies House, receipts) must stay unlabelled. |
| POSTCODE | QuantumAiuk; ai4privacy ZIPCODE | ai4privacy GB rows show outward codes only ("RG23", "YO19", "YO60"); MultiWOZ uses "cb58nt" (lowercase, no space). Full "SW1A 1AA"-style postcodes must come from our generator. |
| EMAIL | everywhere | none. |
| PHONE | everywhere; QuantumAiuk uses Ofcom drama ranges | ai4privacy GB phones are malformed ("+4418568 5356", "7456.428.8083"). Generate 07..., 01..., 02..., +44 forms ourselves. |
| BANK_ACCOUNT | Gretel (account_number, bban), QuantumAiuk (ACCOUNT_NUMBER) | UK 8-digit account + sort code pairs only in QuantumAiuk. |
| SORT_CODE | QuantumAiuk only | No large set. Gretel's `bank_routing_number` is a US-style routing number (inference). Generator needed. |
| IBAN | Gretel finance, kiji | GB IBAN share not checked; Bankstatemently notes earlier invalid IBAN check digits. Generator should emit valid GB IBANs. |
| CARD | ai4privacy, Gretel, Nemotron | fine; add "card ending 1234" look-alikes as keep (QuantumAiuk idea). |
| NI_NUMBER | QuantumAiuk only | Gretel labels an NI-shaped value "ZZ287351T" as SSN; ai4privacy SOCIALNUM in GB rows is US-shaped ("318 667 0376"). Generator needed. |
| DOB | Gretel, Nemotron, kiji, QuantumAiuk, ai4privacy 400k | openpii-1m has only DATE (DOB not separable), which fights our "ordinary dates are kept" rule. |
| ID_DOC | ai4privacy PASSPORTNUM/DRIVERLICENSENUM, Gretel, kiji | No UK passport or DVLA licence formats verified in any set; generator needed (format rules to be confirmed from official guidance). |
| CUSTOM | Gretel customer_id/employee_id, Bitext placeholders, MultiWOZ booking refs, Kaggle ID_NUM | No matter numbers, policy numbers, client codes. Generator needed. NHS numbers (NHSE notes, QuantumAiuk) need a decision: CUSTOM or a new type. |

Document-type gaps: no open labelled UK bank statements, payslips, council tax or utility bills, UK tenancy agreements, UK solicitor letters or GP letters. Only templates exist (GOV.UK archive, Kleister Charity PDFs, payslip and statement layouts). These must come from our generator.

Keep-class conflicts: Gretel finance labels `company` and `date`; Nemotron has non-identifying classes; ai4privacy labels DATE, AGE, GENDER, CITY. If we train on them unchanged the model will over-redact (inference). Strip these before any Mubit traffic.

Length gap: ai4privacy 500k averages 17.37 words per row; our chunks are up to ~1,500 tokens. Only Gretel finance, Nemotron, RedactionBench, TAB and DocPII are document-length.

## Licence red flags

1. **ai4privacy 200k / 300k / 400k**: 300k and 400k are academic and non-commercial only, redistribution needs a written licence, and "This dataset is watermarked". 200k is free only for individuals or companies with up to 3 staff and bans distributing derivatives. 65k / 43k have no licence. Only openpii-1m and openpii-1.5m are clearly CC BY 4.0.
2. **ai4privacy open-pii-masking-500k**: `license_name: cc-by-4.0`, but the card says use and distribution are subject to the Llama 3.1/3.3 Community License and Acceptable Use Policy.
3. **Derived benchmarks inherit licences**: piimb/pii-masking-benchmark is CC BY-NC 4.0 although its sources are permissive; Pritesh-2711/pii-bench is tagged Apache-2.0 but says users must follow every source licence; ScienceSoft/piibench mixes MIT, Apache, CC BY and CC BY-SA rows in one file.
4. **Non-commercial or no-derivatives**: SAMSum (CC BY-NC-ND), DialogSum, MultiNERD, WikiNEuRal, SynthPAI (CC BY-NC-SA), CRAPII and both AIxBlock sets (CC BY-NC; the 92k call-centre card adds "Commercial use, resale, or redistribution is prohibited").
5. **Find Case Law (UK judgments)**: "The Open Justice Licence does not permit computational analysis", and computational analysis explicitly includes "machine learning or AI training on judgment datasets". Needs a TNA licence (free to apply). Do not bulk-process judgments tonight.
6. **Companies House**: not OGL (FOI answer, 2014). Companies House sets no reuse rules, but the data is real and "You are responsible for complying with any applicable data protection" law. Local use only.
7. **OGL v3 does not cover personal data** in government information. Templates are fine; any personal data inside them is not licensed.
8. **Restricted clinical and NER corpora**: i2b2/n2c2 (registration currently closed), MIMIC-IV-Note (credentialed), OntoNotes (LDC user agreement and fee), CoNLL-2003 (Reuters text for research, annotations only).
9. **HF mirror tags that disagree with the source**: kiddothe2b/contract-nli says CC BY-NC-SA 4.0 while the official ContractNLI terms are CC BY 4.0; metaboulie's Kaggle mirror says Apache-2.0 while PIILO is CC BY 4.0 and CRAPII CC BY-NC 4.0; opensporks/resumes says CC0 for CVs "taken from livecareer.com"; LLM-PBE tags Enron emails Apache-2.0. Use the original source's licence, not the mirror tag.
10. **Unknown licence**: FUNSD (no licence text found), SROIE (code MIT, data not stated), Kleister NDA / Charity (no licence in README or GitHub), Broad Twitter Corpus (NOASSERTION), WikiNER original (not found), REDACT (gated "other" terms not read), bigcode PII (gated).
11. **LLM-generated sets carry generator terms (inference)**: SPY and ai4privacy 500k (Llama), PANORAMA (OpenAI o3-mini), DocPII (GPT-4.1-nano), hivetrace (Claude Sonnet 4.5). Mubit trains an open base model on our traffic; check each provider's output terms before mass use.
12. **Security**: mks-logic/SPY needs `trust_remote_code` (runs Python from the repo). Use its placeholder JSONL files, never the loader.
13. **Possible leaked personal data on HF**: PhisherJR/Truecaller, PhisherJR/phonebook, PhisherJR/850M-India-data appear in PII searches. Not opened. Never download.
14. **Real personal data that must never reach Mubit**: TAB, Enron (and its NER subsets), Kaggle essays, SMS Spam, CVs, RedactionBench real-web half, CUAD/ContractNLI parties, Companies House, MAPA.

## Conflicts between sources

- Nemotron-PII size: card 100,000 records (50k/50k) vs dataset viewer 200,000 rows (100k/100k, half with locale "intl"). Inference: an international half was added after the card text.
- ContractNLI licence: official CC BY 4.0 vs HF mirror CC BY-NC-SA 4.0.
- ai4privacy 500k: `license_name: cc-by-4.0` vs Llama licence text in the card body.
- PANORAMA size: 384,789 samples (paper, card) vs 384,794 train examples in cardData (5-row difference, not explained).
- ai4privacy 400k GB rows: card 41,853 (whole set) vs 33,493 in the train split via filter. Consistent with the 80/20 split, so not a real conflict.

## Not found or blocked

- Kaggle competition pages (rate-limited for our fetcher); facts taken from the PIILO and CRAPII Kaggle dataset pages instead.
- sec.gov EDGAR access policy page (HTTP 403).
- FUNSD licence text; WikiNER original licence; Kleister licence.
- PII-Bench (Shen et al.) data location: no Hugging Face link, GitHub fetch timed out.
- REDACT terms, bigcode PII card, ai4privacy health-phi-400k card (all gated; we did not accept terms).
- Samsung/samsum original repo (404 on HF); used the knkarthick mirror card.
- A second UK-specific open PII dataset: a Hugging Face search for "uk pii" returned only QuantumAiuk.
