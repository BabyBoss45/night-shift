# External PII datasets converted to the Veil canonical format

Date: Sat 24 Oct 2026. Code: `/Users/dima/Projects/night-shift/dataconv` (uv project, `uv run dataconv build`, `uv run dataconv combine`, `uv run pytest`). Data (gitignored): `/Users/dima/Projects/night-shift/data/external/`. Licences and attribution lines: `data/external/ATTRIBUTION.md`.

## Summary

| Pool | File | Docs | Sources |
|---|---|---:|---|
| A: synthetic, Mubit OK (`meta.mubit_ok = true`) | `pool_mubit_ok.jsonl` (647 MB) | 387,965 | openpii-1m, Nemotron-PII, Gretel finance, Gretel en-v1, QuantumAiuk train+valid, Bitext banking, Bitext support |
| B: real or mixed, local eval only (`meta.mubit_ok = false`) | `eval_local_only.jsonl` (23 MB) | 1,968 | TAB, RedactionBench, PII-TRACE |
| UK eval (synthetic, eval only) | `uk_eval.jsonl` | 260 | QuantumAiuk test (200, unseen templates) + wild (30) + wild2 (30) |

Entity totals after mapping:

| Type | Pool A | Pool B | UK eval |
|---|---:|---:|---:|
| PERSON | 276,258 | 13,662 | 227 |
| CUSTOM | 198,915 | 3,165 | 0 |
| EMAIL | 145,695 | 392 | 58 |
| PHONE | 107,421 | 218 | 52 |
| ADDRESS | 86,933 | 222 | 70 |
| ID_DOC | 74,043 | 0 | 17 |
| DOB | 67,385 | 1,198 | 49 |
| CARD | 40,143 | 0 | 0 |
| POSTCODE | 28,927 | 0 | 76 |
| BANK_ACCOUNT | 6,476 | 5 | 20 |
| IBAN | 822 | 0 | 0 |
| SORT_CODE | 319 | 0 | 21 |
| NI_NUMBER | 201 | 0 | 21 |
| UNTYPED (RedactionBench) | - | 53,286 | - |

Strict-clean subset of pool A (no out-of-scope sensitive values left unlabelled, no format quality flag): 243,495 docs. This is the recommended slice for Mubit traffic (filter: `meta.out_of_scope == []` and no `quality_flags` other than the provenance flags `offsets_recovered_*` / `placeholders_filled_*`).

Skipped or gated datasets: none. All nine sources were open (no gating, no terms to accept). No `trust_remote_code`, no repo code run (QuantumAiuk `build_dataset.py` / `build_wild_test.py` were not downloaded).

Tests: `uv run pytest` in `dataconv`: 21 passed (span validity, no overlaps, allowed types, chunk offsets and no span cut, unique doc ids and texts, licence per dataset, `mubit_ok` per pool, no pool B text and no uk_eval text in pool A, pool A sources only from list A, plus helper unit tests).

## Format and shared rules

- Canonical record per CONTEXT.md: `doc_id, source, doc_type, language, license, text, entities[{start,end,text,type}], split, meta`. `meta` always has `mubit_ok`, `pool` (A, B, uk_eval), `locale`, `revision`, `orig_labels` (original spans or entity list), `dropped_labels` (keep classes removed, counts), `out_of_scope` (spans of sensitive values outside our 13 types, left unlabelled; use them as ignore zones in eval and as a filter for training), `quality_flags`, `norm_hash`.
- `split`: source train/validation -> `train`; source test -> `eval`; everything in pool B and uk_eval -> `eval`. `meta.source_split` keeps the original.
- Spans trimmed of whitespace; PERSON spans drop titles (Mr, Dr, Ms...) and possessive `'s` (datagen contract); phone extensions (`ext 123`, `x50087`) trimmed from PHONE.
- Overlaps: keep the longer span, log the drop (`stats.json`: `overlap_dropped_*`).
- Sanity check per span (`common.span_ok`): an EMAIL without `@`, a PHONE with fewer than 7 digits, a PERSON with digits, a multi-line ID and similar mean a broken source label; the whole row is skipped (`broken_span_*`).
- DOB vs ordinary date (`common.is_dob_context`): a date becomes DOB only when a birth word (birth, born, DOB, birthday, birthdate) precedes it within 50 characters with no digit or newline in between, or follows it closely. Other dates are dropped (keep class).
- Social security / national ID numbers: NI_NUMBER if the value has the UK NI shape, else ID_DOC (government identity number). Account numbers: BANK_ACCOUNT when banking words are within 60 characters (bank, checking, savings, sort code, IBAN, routing, transfer...), else CUSTOM. Certificate / licence numbers: ID_DOC after "driver's/driving licence", else CUSTOM.
- Dedupe by `norm_hash` (lower case, collapsed whitespace, same as datagen) within each dataset and across pool A; pool A rows whose text is in pool B or uk_eval are removed (none found).
- Chunks: `data/external/<dataset>/chunks.jsonl`, max 6,000 characters, cut at a paragraph break first, then line, sentence, whitespace; never inside a span; `meta.char_start/char_end` into the document. Datagen has no chunker yet, so this is the rule from the brief; check it matches when datagen adds one.
- Per-dataset outputs: `data/external/<dataset>/docs.jsonl`, `chunks.jsonl`, `stats.json` (all kept/skip counters). Raw downloads: `data/external/raw/<dataset>/` with `download_manifest.json`.

## Pool A

### 1. ai4privacy/pii-masking-openpii-1m

- Revision ecfdc547f4a0955600cfe6ab98ba2a162207fcc0. File: `data/train.jsonl` (3.69 GB). The file is sorted by (language, region), so we bisected byte offsets with HTTP range requests and downloaded only the whole en-GB block (112 MB) plus 12 evenly spaced 4 MB slices of en-CA, en-IN and en-US (byte ranges in `download_manifest.json`). Validation file not used.
- Licence (card): "License: CC-BY-4.0. Copyright © 2026 Ai Suisse SA." / "Permitted Use: Research, commercial use, redistribution, and modification - subject to attribution requirements under CC-BY-4.0." Obligation: credit "Ai4Privacy / Ai Suisse SA", link, licence, note changes. Card YAML says `license: other`, `license_name: cc-by-4.0`.
- Rows: 50,174 English read (GB 35,830; CA 4,781; IN 4,832; US 4,731; 259 es/el rows in the slices ignored). Kept 44,974 (GB 31,977; US 4,361; IN 4,336; CA 4,300), under the 60,000 cap. Skipped: 2,735 STREET and 974 BUILDINGNUM (+2 BUILDINGNUM+CITY) that could not be assembled into an address (ambiguous; includes mislabels such as "365 feet" tagged BUILDINGNUM), 1,121 broken POSTCODE, 213 broken EMAIL, 155 broken ID_DOC. doc_type `short_message` (median 283 characters).

| Theirs | Ours |
|---|---|
| GIVENNAME, SURNAME (adjacent, space-separated: merged) | PERSON |
| BUILDINGNUM + STREET + CITY run (separators: space, comma, newline, `#`, `No.`, `number`, ` in `) containing STREET and a number or city | ADDRESS |
| STREET or BUILDINGNUM that cannot form such a run | row skipped |
| CITY alone | dropped (keep) |
| ZIPCODE | POSTCODE (own span) |
| EMAIL / TELEPHONENUM / CREDITCARDNUMBER | EMAIL / PHONE / CARD |
| PASSPORTNUM, DRIVERLICENSENUM, IDCARDNUM | ID_DOC |
| SOCIALNUM | NI_NUMBER if NI-shaped (none were), else ID_DOC |
| TAXNUM | CUSTOM (UTR-like tax reference, datagen puts HMRC UTR in CUSTOM) |
| DATE | DOB with birth context (6,700), else dropped (33,718) |
| TITLE, AGE, GENDER, SEX | dropped (keep) |

- Entities: PERSON 43,577; ID_DOC 33,848; EMAIL 24,595; PHONE 17,704; ADDRESS 14,252; POSTCODE 13,062; CARD 9,897; CUSTOM 8,217; DOB 6,700. Chunks 44,974.
- Quality issues: GB postcodes often outward-only ("RG2", "YO19", "ZIP OX9"): 6,798 GB rows flagged `postcode_not_full_uk` (labelled POSTCODE because they are used as the person's postcode, but our datagen rule leaves bare outward codes unlabelled). GB phones malformed ("7456.428.8083", "+321.69 984-9693", "(80).3822.4998"): 8,833 GB rows flagged `phone_not_uk_format`. Odd names ("Hyon Davran"), US-shaped SOCIALNUM in GB rows, IDCARDNUM in GB rows although the UK has no ID cards, trailing spaces inside spans (trimmed). Only 19,126 GB rows carry no flag.
- Recommended use: short-message Mubit traffic from the 32,123 strict-clean rows (GB rows without flags first); do not use it to teach UK postcode or phone formats. Pack several rows per request only if the trainer accepts multi-message chunks.

### 2. nvidia/Nemotron-PII

- Revision b70ffaf5ff39e079776134c5bf4381f00a9fd1ed. Files: `data/train-00000-of-00001.parquet`, `data/test-00000-of-00001.parquet`.
- Licence (card): "This dataset is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0)" / "This dataset is ready for commercial use." Obligation: attribution to NVIDIA, link, licence, note changes.
- Size conflict resolved: the card says "100,000 records (50k train / 50k test)"; the files hold 100,000 train + 100,000 test rows. Each `uid` appears exactly twice per split, once with locale `us` and once `intl` (different texts), so the card counts 50k personas per split and the files hold 200k texts.
- Rows: 200,000 read, kept 199,378. Skipped: 621 rows with broken spans (574 email labels on text such as "her email", "[Email Address]", "researchgate.net"; 82 postcode; 47 address; 41 card; 41 CUSTOM...), 1 duplicate text. In 12,965 spans the `text` field is lower-cased while offsets are right; we use the text slice.

| Theirs | Ours |
|---|---|
| first_name, last_name (merged when adjacent) | PERSON |
| street_address (+ adjacent city, state, county) | ADDRESS |
| city, state, county alone; country | dropped (keep) |
| postcode | POSTCODE |
| email; phone_number, fax_number | EMAIL; PHONE |
| date_of_birth | DOB |
| credit_debit_card | CARD |
| ssn, national_id | NI_NUMBER if NI-shaped (10), else ID_DOC |
| account_number | BANK_ACCOUNT with banking context (4,962), else CUSTOM |
| certificate_license_number | ID_DOC after driver/driving licence, else CUSTOM |
| customer_id, employee_id, medical_record_number, health_plan_beneficiary_number, tax_id | CUSTOM |
| company_name, date, time, date_time, occupation, employment_status, education_level, race_ethnicity, religious_belief, blood_type, gender, age, political_view, sexuality, language, url, swift_bic | dropped (keep / non-identifying) |
| password, pin, cvv, api_key, http_cookie, ipv4, ipv6, mac_address, device_identifier, biometric_identifier, vehicle_identifier, license_plate, coordinate, user_name, bank_routing_number, unique_id | out of scope: unlabelled, listed in `meta.out_of_scope` |

- Entities: PERSON 164,384; CUSTOM 129,824; EMAIL 102,858; PHONE 62,490; ADDRESS 33,532; DOB 30,699; CARD 21,777; ID_DOC 16,969; POSTCODE 14,175; BANK_ACCOUNT 4,962; NI_NUMBER 10. Splits: train 99,678, eval 99,700. Chunks 199,423 (longest doc 14,608 characters).
- Quality issues: US formats dominate (SSNs, 5-digit ZIPs, 555-style phones); `intl` rows use non-UK formats. 103,608 docs contain out-of-scope sensitive values left unlabelled. 223 docs flagged `address_without_number` (e.g. "proceeding south along Elm Avenue" tagged street_address: a street used as a place, a keep trap for us). city/state not adjacent to the street were dropped, so some addresses are shorter than the source span set.
- Recommended use: document-shaped Mubit traffic from the 95,646 strict-clean docs; best source of CUSTOM and DOB variety. Use `split = eval` rows as a held-out US-format test.

### 3. gretelai/synthetic_pii_finance_multilingual (English only)

- Revision 7b844d16738527a04264f50214cb426a4cea0897. Files: `data/English_train-00000-of-00001.parquet`, `data/English_test-00000-of-00001.parquet`.
- Licence (card): "released under Apache 2.0" / "All data in this generated dataset is Apache 2.0 licensed and can be used for any purpose that is not harmful." Obligation: keep the Apache-2.0 notice, state changes.
- Rows: 28,910 read (26,019 train + 2,891 test; card says English 28,910), kept 28,284. Skipped: 596 rows with broken spans (template placeholders labelled as PII: "[Phone Number]", "Date of Birth", "MM/DD/YYYY", "[email protected]", names with digits "Gregory20"), 30 duplicate texts. `meta.locale` en-GB for the 4,352 kept rows described as "English language as spoken in the United Kingdom", else en-US/GB/CA (23,932).

| Theirs | Ours |
|---|---|
| name; first_name + last_name (merged) | PERSON (titles trimmed) |
| street_address | ADDRESS |
| email, phone_number | EMAIL, PHONE |
| iban | IBAN |
| bban | BANK_ACCOUNT (domestic account identifier; inference) |
| credit_card_number | CARD |
| date_of_birth | DOB |
| passport_number, driver_license_number | ID_DOC |
| ssn | NI_NUMBER if NI-shaped (none), else ID_DOC |
| customer_id, employee_id | CUSTOM |
| company, date, time, date_time, swift_bic_code | dropped (keep) |
| credit_card_security_code, account_pin, api_key, password, user_name, ipv4, ipv6, local_latlng, bank_routing_number | out of scope (unlabelled, `meta.out_of_scope`) |

- Entities: PERSON 36,753; ADDRESS 21,640; PHONE 4,946; EMAIL 2,649; ID_DOC 2,209; CUSTOM 1,936; DOB 1,304; BANK_ACCOUNT 857; IBAN 822; CARD 738. Splits: train 25,454, eval 2,830. Chunks 28,295.
- Quality issues: card: "A NER library labeled the PII, which may introduce false negatives (missed labels) or false positives". Seen: dummy values ("Jane Doe", "123-45-6789", "+44 123 456 7890"); nested duplicate name spans with and without title (435 PERSON overlaps dropped); `name` may also cover organisations (not fixable). Many docs are structured formats (FIX, MT940, FpML, CSV, EDI). 7,090 docs have no entity left after dropping company/date labels (useful negatives).
- Recommended use: finance-document traffic (IBAN, BANK_ACCOUNT, CARD) from 23,439 strict-clean docs; good negatives for the company/date keep rule.

### 4. gretelai/gretel-pii-masking-en-v1

- Revision e06eb1499ca8d54470f085021cd8e54f9efac7fd. Files: `data/{train,validation,test}-00000-of-00001.parquet`.
- Licence (card metadata): "license: apache-2.0" (no licence section in the body). Obligation: Apache-2.0 notice, state changes.
- Offsets: the source lists entity strings and types only. We label every whole-token occurrence of each string (`(?<!\w)value(?!\w)`), so `quality_flags` includes `offsets_recovered_by_string_search`. A row is skipped if an in-scope entity is not found (88 rows) or one string carries conflicting types (0). Kept 59,912 of 60,000.

| Theirs | Ours |
|---|---|
| name, first_name, last_name (adjacent first+last merged) | PERSON |
| street_address (+ adjacent city/state), address | ADDRESS |
| postcode | POSTCODE (split off an address that ends with it) |
| email, phone_number, credit_card_number | EMAIL, PHONE, CARD |
| date_of_birth | DOB |
| ssn, national_id | NI_NUMBER if NI-shaped (none; "ZZ287351T" is not, it ends in T), else ID_DOC |
| account_number | BANK_ACCOUNT with banking context (337), else CUSTOM |
| certificate_license_number | ID_DOC after driver/driving licence, else CUSTOM |
| customer_id, employee_id, medical_record_number, health_plan_beneficiary_number, tax_id | CUSTOM |
| date, time, date_time, company_name, city, state, country, url, swift_bic | dropped (keep) |
| ipv4, ipv6, license_plate, user_name, device_identifier, biometric_identifier, bank_routing_number, vehicle_identifier, coordinate, api_key, password, cvv, pin, unique_identifier | out of scope (unlabelled, `meta.out_of_scope`) |

- Entities: CUSTOM 58,938; DOB 28,293; PERSON 27,036; ID_DOC 20,767; ADDRESS 16,901; EMAIL 13,009; PHONE 10,310; CARD 7,731; POSTCODE 1,151; BANK_ACCOUNT 337. Splits: train 54,919 (train + validation), eval 4,993 (test). Chunks 59,912.
- Quality issues: all occurrences of a listed string are labelled, so a surname that also appears as a place name is labelled everywhere (inference: rare). 22,546 docs have out-of-scope values (IPs, licence plates, usernames, MRN-like `unique_identifier`). US addresses dominate. 605 docs flagged `address_without_number`.
- Recommended use: secondary traffic and the best CUSTOM source (medical record, employee, customer numbers); 36,870 strict-clean docs. Its test split is a ready held-out set.

### 5. QuantumAiuk/uk-pii-redaction-synthetic

- Revision 750398a543653ca8d26b0765430c563d8f52b1c0. Files: `train.jsonl`, `valid.jsonl`, `test.jsonl`, `test_meta.jsonl`, `wild_meta.jsonl`, `wild2_meta.jsonl` (the two builder scripts were not downloaded).
- Licence (card metadata): "license: apache-2.0"; card: "Every record is synthetic. No real person's data is included."
- Span recovery: the assistant message is the user text with values replaced by tags. We split it into literals and tags, enumerate every placement of the literals in the user text, and accept only a single alignment in which every value passes a format check for its tag (UK postcode, NI, sort code, 8-digit account, 10-digit NHS, phone, email, name, DOB). For the `*_meta` files the recovered values must also equal the listed `pii` values. Result: 0 failed and 0 ambiguous alignments out of 3,460; 2 duplicate texts dropped. `test_meta.jsonl` matches `test.jsonl` row for row (checked).

| Theirs | Ours |
|---|---|
| [NAME] | PERSON (titles stay outside, as in the source) |
| [ADDRESS], [POSTCODE] | ADDRESS, POSTCODE (separate spans, as in the source) |
| [PHONE], [EMAIL] | PHONE, EMAIL |
| [NI_NUMBER], [SORT_CODE] | NI_NUMBER, SORT_CODE |
| [ACCOUNT_NUMBER] | BANK_ACCOUNT |
| [DATE_OF_BIRTH] | DOB |
| [NHS_NUMBER] | ID_DOC (datagen README contract: NHS number is ID_DOC; datasets.md had suggested CUSTOM, the generator contract wins) |

- Pool A (train 3,000 + valid 198 = 3,198 docs; the 2 duplicate texts were in valid): PERSON 2,476; PHONE 746; ADDRESS 608; EMAIL 596; POSTCODE 539; DOB 389; SORT_CODE 319; BANK_ACCOUNT 319; ID_DOC 250; NI_NUMBER 191. 628 docs have no entities (look-alike negatives).
- UK eval (260 docs; test 200, wild 30, wild2 30): PERSON 227; POSTCODE 76; ADDRESS 70; EMAIL 58; PHONE 52; DOB 49; SORT_CODE 21; NI_NUMBER 21; BANK_ACCOUNT 20; ID_DOC 17.
- Quality issues: 90 templates only (train), short single sentences, same team wrote generator and tests (card). Conflict with our contract: "card ending 4421" is left unlabelled here, while datagen labels the visible digits of a partial card as CARD; do not mix the two without deciding. Valid shares templates with train.
- Recommended use: the only open source of SORT_CODE, NI_NUMBER, NHS numbers and full UK postcodes; use all 3,198 pool A docs as UK traffic, keep `uk_eval.jsonl` strictly for evaluation (wild sets are the closest thing to real user messages).

### 6. Bitext retail banking + customer support (two datasets)

- bitext/Bitext-retail-banking-llm-chatbot-training-dataset, revision 3e3621092fc6baaf7f53ceb6f091c60ae99acb67, file `bitext-retail-banking-llm-chatbot-training-dataset.parquet`.
- bitext/Bitext-customer-support-llm-chatbot-training-dataset, revision 430d1a89bd93bd1fa23c16f29dd53e73f0087443, file `Bitext_Sample_Customer_Support_Training_Dataset_27K_responses-v11.csv`.
- Licence: CDLA-Sharing-1.0. Banking card: "released under the Community Data License Agreement (CDLA) Sharing 1.0" / "Users must attribute the dataset and continue to share derivatives under the same license." Support card: metadata "license: cdla-sharing-1.0". Both "(c) Bitext Innovations, 2024". Obligation: share-alike for anything we publish that contains these rows (including `pool_mubit_ok.jsonl`), attribution, licence text. Not checked tonight: how the licence treats a trained model; read https://cdla.dev/sharing-1-0/ before publishing.
- Finding: most placeholders are field names, not values ("provide your {{Account Number}}", "fill in your {{Full Name}}"): 1,221 distinct placeholders in banking, 385 in support. Filling them with values would produce text where the agent states the customer's details. So:

| Placeholder | Fill | Label |
|---|---|---|
| Customer Support / Service Phone Number, Toll-Free Number, other "... Phone Number" value slots | fake UK number from Ofcom drama ranges (020 7946 0xxx, 0161 496 0xxx, 07700 900xxx, 0808 157 0xxx...) | PHONE (organisation numbers are PHONE in datagen too) |
| Customer Support / Service Email (Address) | support@<fake bank or shop>.co.uk | EMAIL |
| Person Name, Client (Full/First/Last) Name (support set) | Faker en_GB name | PERSON |
| Salutation | Mr / Mrs / Ms / Dr / Miss | none (title) |
| Bank Name, Company Name, website and URL slots, working hours, Account Type, Account Category, Delivery City / Country, amounts, Currency Symbol, Date Range | fake keep-class values | none (keep) |
| Order / Invoice / Tracking Number, Transaction ID | fake references | none (document/transaction refs are keep traps in datagen) |
| Any slot after a possessive ("your", "their", "recipient's") or in a list headed by one, or followed by "field / section / details"; every personal slot in banking responses (the agent never knows the customer's details); every Password / PIN / Username / key slot; all other UI slots ("Account Settings") | the slot name as plain text | none (no value present) |

- Rows: banking 25,545 read, 187 skipped (malformed braces), 25,358 kept; support 26,872 read, 11 skipped, 26,861 kept. Text: `Customer: <instruction>\n\nAgent: <response>`, doc_type `support_chat_banking` / `support_chat_retail`, offsets recorded while filling (never searched).
- Entities: banking PHONE 8,576, EMAIL 1,789. Support PHONE 2,649, PERSON 2,032, EMAIL 199, BANK_ACCOUNT 1. 39,850 of 52,219 docs have no entity.
- Quality issues: US-register English ("checking account"); near-duplicate templates (about 1,000 rows per intent); almost no customer PII; Faker en_GB names are mostly Anglo.
- Recommended use: chat-shaped traffic and hard negatives (bank names, URLs, hours, order numbers must stay unredacted); sample a few hundred per intent rather than all. Keep rows separable by `source` because of share-alike.

## Pool B (local evaluation only, never through Mubit)

### 7. Text Anonymization Benchmark (TAB)

- Source: GitHub NorskRegnesentral/text-anonymization-benchmark, commit 558e09e26d6b36f5f78440074e6a233946d98bd9, files `echr_train.json`, `echr_dev.json`, `echr_test.json`, `LICENSE.txt`, `guidelines.md` (the HF mirror ildpil/text-anonymization-benchmark, revision 1f22ce098996054689b5b331fb20b3a74a78e1c5, card read only).
- Licence: MIT. LICENSE.txt: "The MIT License (MIT) Copyright (C) 2021-2026 Norsk Regnesentral"; HF card: "TAB is released under an MIT License." Obligation: keep the notice.
- Rows: 1,268 documents read (1,014 / 127 / 127), all kept. One annotator per document (quality-checked annotator if listed, else the first id); 274 documents had 2 to 10 annotators, `meta.n_annotators` records it.

| Theirs (identifier_type) | Ours |
|---|---|
| PERSON DIRECT / QUASI | PERSON (titles trimmed), `meta.entity_tags[i].identifier_type` keeps DIRECT/QUASI and TAB entity_id |
| CODE DIRECT / QUASI (application numbers) | CUSTOM |
| DATETIME DIRECT / QUASI with birth context ("born in 1970") | DOB |
| other DATETIME, LOC, ORG, DEM, MISC, QUANTITY (DIRECT / QUASI) | `meta.out_of_scope` (ignore zone) |
| PERSON NO_MASK (judges, agents, officials) | `meta.out_of_scope` (ignore zone: our model will flag them) |
| other NO_MASK | unlabelled |

- Entities: PERSON 12,914; CUSTOM 2,735; DOB 1,198 (8 overlapping PERSON mentions dropped). Chunks 2,274 (longest document 29,673 characters).
- Quality issues: real names; ECHR legal English; LOC quasi-identifiers (cities, countries) are not ADDRESS in our scheme, so ADDRESS recall cannot be measured here; birth years only ("born in 1970") count as DOB.
- Recommended use: legal-document eval of PERSON and CUSTOM recall; score predictions inside `out_of_scope` spans as neither TP nor FP.

### 8. RedactionBench

- Revision d45e9cec89bc49c69355e252fec29cc0229982f6. Files: `data/test-00000-of-00001.parquet`, `croissant.json`.
- Licence (card): "License: CC BY 4.0"; "RedactionBench is an evaluation-only benchmark"; out of scope per card: "Training or fine-tuning production redaction systems". Obligation: attribution.
- Rows: 200 read, 200 kept; 53,286 spans kept as `type: "UNTYPED"` with `meta.span_tiers` aligned (mandatory 16,993, contextual 36,293); span text kept exactly (single-character "combinator" spans survive, no trimming). `meta.real_web_document` true for 101 documents; `original_document_url` kept.
- Chunks 568 (longest document 166,001 characters).
- Quality issues: US-centric genres (1040, I-9, DS-160); half the documents are transcribed real web documents; structured files, logs and terminal sessions are far from Veil traffic.
- Recommended use: recall-only eval: recall over `mandatory` spans, ignore predictions on `contextual` spans; report per category.

### 9. perplexity-ai/PII-TRACE

- Revision 1c3eb67bbd43e8571b4433a9d3d76271f9970eb9. Files: `data/train.parquet`, `LICENSE`.
- Licence: MIT. Card: "License: MIT."; LICENSE: "MIT License Copyright (c) 2026 Perplexity AI, Inc."; card: "This subset may be used for training, evaluation, and error analysis in PII span detection research." Synthetic per card; kept in pool B by project decision.
- Rows: 500 conversations, all kept (empty controls included, `meta.empty_control`). All gold spans are in user messages, so each document is the user turns joined by a blank line; `meta.turns` gives each turn's offsets.

| Theirs | Ours |
|---|---|
| private_person | PERSON |
| private_email (also "x @ y.com" and "x at y dot com" forms) | EMAIL |
| private_phone | PHONE (extensions trimmed, 168) |
| private_address | ADDRESS |
| account_number ("reference number") | CUSTOM, BANK_ACCOUNT with banking context (5) |
| other_pii ("ID") | CUSTOM |
| private_date | DOB with birth context (0), else ignore zone (221, future dates such as "2080-01-03") |
| private_url, secret | ignore zone (`meta.out_of_scope`) |

- Entities: PERSON 748; CUSTOM 430; EMAIL 392; ADDRESS 222; PHONE 218; BANK_ACCOUNT 5. Chunks 500.
- Quality issues (card): "identifier formats are more regular than production traffic". Invented names ("Kestia Ironvale"), example.com emails, US 202-555 phones.
- Recommended use: multi-turn chat smoke test for PERSON / EMAIL / PHONE / CUSTOM recall with cross-turn context.

## Notes and open decisions for the human

- Outward-only postcodes (openpii GB) are labelled POSTCODE and flagged; datagen leaves bare outward codes unlabelled. Decide one rule before mixing.
- Partial cards: QuantumAiuk keeps "card ending 4421" unlabelled; datagen labels the 4 digits as CARD.
- NHS numbers: mapped to ID_DOC per the datagen README (datasets.md suggested CUSTOM).
- Non-UK identifiers (US SSNs, routing numbers, ZIP codes) are in pool A with their nearest type or as out-of-scope ignore zones; filter by `meta.locale` and `meta.out_of_scope` when UK realism matters.
- Facts vs inference: counts above come from `stats.json` / `combined_stats.json`; mapping choices marked "inference" (BBAN as BANK_ACCOUNT, TAXNUM as CUSTOM) are our decisions, not statements from the cards.
