# Financial and insurance documents (dataset-finance)

Builds `data/docs/financial.jsonl` and `data/docs/insurance.jsonl` in the documents schema shared with the other dataset builders. Design: `docs/superpowers/specs/2026-10-23-pii-training-dataset-design.md` (branch `docs/dataset-design`), sections 3, 4, 5 and 9.

**Status (23 Oct 2026, night):** the code is complete and tested on local fixtures, but no documents have been built yet. The build session's network policy blocked all three sources (`huggingface.co`, `www.sec.gov`, `www.justice.gov.uk`; proxy answered 403 to CONNECT). The JSONL files and the two templates need a session that can reach those hosts. See `data/sources/financial_insurance/manifest.json`.

## Files

| File | What it does |
|---|---|
| `common.py` | Schema check, regex sweep for structured identifiers, valid fake UK numbers (GB IBAN with checksum, Luhn cards, NI, sort code, 8-digit account, DVLA licence), JSONL and manifest IO |
| `check.py` | Fails loudly (exit 1) unless every record passes the schema invariants: offsets match values, sorted, non-overlapping, allowed types, no slot markers or unfilled blanks, split rules, and no unlabelled structured identifier in a rendered template |
| `build_gretel.py` | Part A: streams the Gretel dataset at a pinned commit, keeps English UK documents, maps labels with `label_map.md`, validates, selects about 100 for variety, splits 50/30/20 by document (seeded) |
| `label_map.md` | Gretel label to our type, read by `build_gretel.py` |
| `fetch_real.py` | Part B: downloads INS1 and INS2 to `/tmp/raw/financial_insurance` (outside the repo) with a descriptive User-Agent and converts them to text |
| `tests/run.sh` | Self-test without network: renders `tests/fixture_templates/INS9.txt` (every slot form and block) and builds from `tests/gretel_rows.jsonl` (one row per drop reason) into a temp dir, then runs `check.py` |
| `build_real.py` | Part B: renders `data/templates/insurance/INS*.txt` 5 times each with Faker `en_GB`, recording every inserted value's offsets as it writes; fills 1-3 train, 4-5 fresh |

## Run

```bash
pip install -r scripts/sources/financial_insurance/requirements.txt
cd scripts/sources/financial_insurance
python3 build_gretel.py                 # Part A; prints file sizes, then streams
python3 fetch_real.py                   # Part B raw files to /tmp/raw/financial_insurance
# write data/templates/insurance/INS1.txt and INS2.txt from the raw text (syntax below)
python3 build_real.py --sweep           # leftover structured identifiers and blanks in the templates
python3 build_real.py                   # render 5 fills per template
python3 check.py                        # both JSONL files
```

Each builder replaces only its own records in the shared `insurance.jsonl` (Gretel: `source_id` starting `gretel-`; real: `INS1`, `INS2`), so they can run in any order, and re-running gives the same output.

## Template syntax (`data/templates/insurance/INS*.txt`)

A header of `# key: value` lines, a line `---`, then the body. Required header keys: `source_id`, `group` (insurance), `subtype`, `url`, `licence`, `kind` (`template` for a blank form such as INS1, `filled_real` for a filed document whose real values were replaced, such as INS2). Other `#` lines are comments.

Entity slots, `{{TYPE:key}}` or `{{TYPE:key|form|modifier}}`. The key names the real-world person or thing: every slot with the same key and type gets the same `entity_id` (`key.type`), whatever surface form it renders.

| Slot | Renders |
|---|---|
| `{{PERSON:k}}` forms: `full` (default), `formal` (Mr Raj Patel), `title_surname`, `initial_surname` (R. Patel), `first`, `surname`, `initials` (RP), `surname_first` (PATEL, Raj), `any` (a different form each mention), `signature` | A person. Modifier `poss` adds `'s` (or `'`) outside the entity |
| `{{ADDRESS:k}}` forms: `lines`, `oneline` (default: chosen per fill); modifiers `nopostcode`, `noco` | ADDRESS, then the postcode as a separate POSTCODE entity; sometimes a `c/o` line with its own PERSON |
| `{{POSTCODE:k}}`, `{{DOB:k}}` | The postcode of address `k`; the date of birth of person `k` |
| `{{EMAIL:k}}`, `{{PHONE:k}}` (form `mobile`) | Email built from person `k`'s name; a UK phone number |
| `{{SORT_CODE:k}}`, `{{BANK_ACCOUNT:k}}`, `{{IBAN:k}}`, `{{CARD:k}}`, `{{NI_NUMBER:k}}` | Valid fake UK values (the IBAN reuses `k`'s sort code and account). Forms `last4` ("ending 4821") and `masked` (`**** **** **** 4821`, only the digits are the entity) |
| `{{ID_DOC:k}}` forms: `licence` (default, DVLA format from `k`'s name and DOB), `passport` | Identity document number |
| `{{CUSTOM:k}}` | An organisation-specific reference. Keys with their own format, which recurs in every fill and source: `claim_ref` CLM·4471·KX, `insurer_ref` MTR/19/004417-k, `our_ref` PK.0412.017, `matter_ref` M/2024/118b, `policy_no` MV07-44173/T, `umr` B0509FN071234Z, `bond_no` FIB 07 3312 PZ, `broker_ref` BRK07x3312, `client_id` 4471 0412 17, `insured_ref` ~K412~07. Other keys use two letters and six digits |

Unlabelled slots, `{{keep:key|kind}}` (kind defaults to the key; the same key renders the same text): `date` (an ordinary date in the fill's date style), `amount` (`|amount|small` or `|amount|big`), `year`, `insurer` (a fictional insurer), `firm` (a firm named after people, kept visible), `wording` (a public Lloyd's clause code such as NMA 2915, an over-redaction trap), `place` (a place that looks like a name or address, such as "the Rose Garden car park").

Text variation blocks, which may nest: `[[alt: A || B || C]]` picks one; `[[opt: A]]` includes A in about half the fills; `[[shuffle: A || B || C]]` reorders paragraphs (joined by a blank line). Items are trimmed.

Per fill, the renderer also varies the date and DOB styles, the address layout, spacing in NI numbers, IBANs and cards, and initials with or without a dot. About a quarter of people get names that are common words (Will, Hope, Penny; Banks, Cash, Sterling, Bond, Lloyd) and about a sixth get transliterated or non-English names. Each record's `hard_cases` lists what was planted: `common_word_name`, `transliterated_name`, `initials`, `possessive`, `name_variants`, `signature_only_name`, `address_multiline`, `address_oneline`, `care_of_address`, `partial_number`, `company_person_name`, `custom_unusual_format`, `over_redaction_trap`.

Writing a template: replace every personal value in the source with a slot (fill-in fields in INS1; insured parties' identifying details, policy, claim and broker references in INS2), keep corporate names as text, then run `build_real.py --sweep` until it prints nothing.
