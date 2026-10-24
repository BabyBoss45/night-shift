# Hard cases to plant in synthetic data (Veil, task T1)

Agent: R (methods). Date: 24 Oct 2026. Every value below is fake: names are invented; phones are Ofcom drama numbers (R-31); NHS numbers start 999 (R-70); cards are Stripe test numbers (R-73); sort code/account pairs are Vocalink test cases (R-49); IBANs are computed from those (uk-formats.md).
`\n` = line break in the extracted text. Labels use the 13 Veil types. "keep" = must NOT be labelled.

## Labelling conventions (decide once, use in generator, T1 prompt and eval)
1. PERSON spans exclude honorifics (Mr, Mrs, Ms, Dr) and the possessive `'s`; include particles (de, dos, Ní) and hyphens.
2. ADDRESS and POSTCODE are separate adjacent spans: `12 Oak Road, Leeds` = ADDRESS, `LS6 2AB` = POSTCODE.
3. No nested spans: an email containing a name is one EMAIL span.
4. A value is labelled at **every** mention (TAB counts an entity as protected only if all mentions are masked, R-37).
5. Context beats checksum for high-risk types: a number after "card number" or "account" is labelled even if Luhn or length fails.
6. Open policy decisions (marked **[decision]**): NHS number and UTR have no own type (proposal: ID_DOC); last-4 card or account fragments (proposal: label with the parent type); card expiry and CVV (proposal: CARD); sole-trader VAT numbers (proposal: CUSTOM).

Why each class is hard, in short: context-free values lose recall (OpenAI Privacy Filter recall 0.584 without a clue word vs 0.863 with one, R-12); common words and organisations cause false names (R-1, R-10); non-standard forms raise re-identification risk from 44% to 69% across tools (R-39); long inputs and layout artefacts shift spans (R-10, R-46).

## A. PERSON (1-24)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 1 | First name = common noun | `Please ask Will to sign the will by Friday.` | PERSON `Will`; `will` keep | same token, case is the only cue; models over-predict names from common nouns (R-1) |
| 2 | Name = virtue word | `Grace Okafor confirmed the grace period of 14 days.` | PERSON `Grace Okafor`; `grace period` keep | over-redaction of common nouns (R-10) |
| 3 | Name = month | `April Nwosu signed on 3 April 2026.` | PERSON `April Nwosu`; date keep | same word as a date part |
| 4 | Name = city | `Florence Adeyemi is moving to Florence in May.` | PERSON `Florence Adeyemi`; `Florence`, `May` keep | location vs person ambiguity |
| 5 | Name only in sign-off | `Kind regards,\nJo` | PERSON `Jo` | two letters, no clue word, often at chunk end |
| 6 | Title + surname only | `Dear Mr Patel,` | PERSON `Patel` | "honorific-heavy references" are under-detected (R-10) |
| 7 | Initial + surname | `Signed: O. Kovalenko` | PERSON `O. Kovalenko` | initials (R-10) |
| 8 | Initials only, in minutes | `Attendees: O.K., R.S.\nAction: O.K. to chase the deposit.` | PERSON `O.K.` (x2), `R.S.` | looks like "OK"; no surname |
| 9 | Possessive | `Kovalenko's deposit was returned in full.` | PERSON `Kovalenko` | span boundary; restore must keep `'s` |
| 10 | Same person three ways | `Oleksandra Kovalenko (the "Tenant") ... Ms Kovalenko agreed ... Sasha will call.` | PERSON x3, same placeholder | coreference; all-mentions recall (R-37, R-46) |
| 11 | Nickname that is a noun | `William Hart (Bill) ... Bill paid the gas bill.` | PERSON `William Hart`, `Bill` (x2); `bill` keep | diminutive + common noun |
| 12 | Transliteration variants | `Oleksandr Shevchenko (Aleksandr Shevchenko in his passport, Alexander on the lease)` | PERSON x3 (one person) | regional naming conventions (R-10); consistency |
| 13 | Diacritics + particle | `Siobhán Ní Bhriain, flat 2` | PERSON `Siobhán Ní Bhriain` | non-ASCII; particle looks like a word; NFKD stripping changes offsets |
| 14 | Name particles | `Jan de Vries and Ana dos Santos are joint tenants.` | PERSON `Jan de Vries`, `Ana dos Santos` | lowercase particles split spans |
| 15 | Double-barrelled | `Harriet Lucas-Okafor` | PERSON (one span) | hyphen splits tokens |
| 16 | Surname-first caps in a form | `TENANT: KOVALENKO, OLEKSANDRA` | PERSON `KOVALENKO, OLEKSANDRA` | all caps, comma order |
| 17 | Lowercase chat | `spoke to mark yesterday, he'll mark it as paid` | PERSON first `mark`; second keep | no casing cue |
| 18 | Third party in a personal message | `my sister Olena will collect the keys` | PERSON `Olena` | SPY labels only the author as PII (R-12), so models trained that way skip third parties |
| 19 | Professional name | `Dr Amir Haddad (GP) wrote the fit note.` | PERSON `Amir Haddad` | some detectors treat professionals as public |
| 20 | Name broken by PDF hyphenation | `Oleksandra Kova-\nlenko` | PERSON (whole, or `Oleksandra Kovalenko` after de-hyphenation) | span crosses a line break (R-10 layout artefacts) |
| 21 | Name inside email | `o.kovalenko@example.com` | EMAIL only | nested span rule |
| 22 | Sole trader vs company | `Mark Ellison trading as Ellison Plumbing` / `Patel & Sons Ltd` | PERSON `Mark Ellison`; trading name keep; company keep | spec rule: hide a sole trader's personal name only; residual risk in the trading name |
| 23 | Name = street name | `Victoria Hughes lives at 8 Victoria Road, Hull` | PERSON `Victoria Hughes`; ADDRESS `8 Victoria Road, Hull` | same word in two types |
| 24 | Apostrophes in names | `Liam O'Connor and Priya D'Souza` | PERSON x2 | tokenisers split at `'`; looks like a possessive |

## B. ADDRESS and POSTCODE (25-38)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 25 | Multi-line letter header | `Ms O. Kovalenko\nFlat 3\n12 Oak Road\nLeeds\nLS6 2AB` | PERSON `O. Kovalenko`; ADDRESS `Flat 3\n12 Oak Road\nLeeds`; POSTCODE `LS6 2AB` | no clue words; spans across lines |
| 26 | Address in table cells | `\| Property \| Flat 3, 12 Oak Road \| Town \| Leeds \| Postcode \| LS6 2AB \|` | ADDRESS `Flat 3, 12 Oak Road`, ADDRESS `Leeds`; POSTCODE | split across cells; bare values (R-12) |
| 27 | Flat letter, house suffix | `Flat 3B, 12a Oak Road` | ADDRESS | letters mixed into numbers |
| 28 | c/o | `c/o Mrs Joan Price, 4 Mill Lane, York YO1 7HH` | PERSON `Joan Price`; ADDRESS `4 Mill Lane, York`; POSTCODE `YO1 7HH` | two types interleaved |
| 29 | Postcode no space, lowercase | `postcode ls62ab` | POSTCODE `ls62ab` | case and spacing normalisation |
| 30 | No-break space from PDF | `LS6 2AB` | POSTCODE | literal-space regexes miss it |
| 31 | Address in narrative | `I moved from 27 Kingsley Avenue to my mum's place in Hull.` | ADDRESS `27 Kingsley Avenue`; `Hull` keep **[decision]** | no address layout; town of a relative is a quasi-identifier |
| 32 | Named house, no number | `Rose Cottage, Church Lane, Little Snoring NR21 0AA` | ADDRESS `Rose Cottage, Church Lane, Little Snoring`; POSTCODE | no digits; `Rose` looks like a name |
| 33 | Outward code only | `We let flats across the LS6 area.` | keep | partial postcode is a generic area |
| 34 | Address cut by chunk edge | chunk 1 ends `...12 Oak`, chunk 2 starts `Road, Leeds LS6 2AB` | ADDRESS in both chunks; POSTCODE | needs overlap and document-level merge |
| 35 | Street in a clause | `The Landlord is not liable for road works on Oak Road.` | keep | same string as the tenant's street |
| 36 | Previous address field | `Previous address (if less than 3 years): 9 Elm Close, Bath BA2 3QT` | ADDRESS `9 Elm Close, Bath`; POSTCODE | second address of the same person |
| 37 | Forces address | `Cpl R. Singh, BFPO 801` | PERSON `R. Singh`; ADDRESS `BFPO 801` | non-standard postal format (R-26) |
| 38 | Company registered office | `Registered office: Units 4-6, Riverside Park, Leeds LS10 1AB` (a Ltd company) | keep | address shape, but not a person's address |

## C. EMAIL and PHONE (39-48)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 39 | Obfuscated email | `o.kovalenko [at] example [dot] com` | EMAIL (whole) | regex fails; non-standard form (R-39) |
| 40 | Email wrapped by PDF | `oleksandra.kovalenko@exam-\nple.co.uk` | EMAIL | hyphen inserted by line wrap |
| 41 | Plus tag and subdomain | `olena+lettings@mail.example.co.uk` | EMAIL | narrow regexes stop at `+` |
| 42 | +44 (0) form | `+44 (0)7700 900123` | PHONE (include `+44 (0)`) | brackets and redundant 0 |
| 43 | Phone split in speech | `my number is 07700, then 900, then 123` | PHONE `07700, then 900, then 123` | NER fails on split numbers (R-39) |
| 44 | Phone in words | `oh seven seven double-oh, nine hundred, one two three` | PHONE (whole) | spelled out |
| 45 | Extension | `020 7946 0321 ext. 204` | PHONE (include ext.) | boundary |
| 46 | Non-UK number | `+380 44 123 4567` | PHONE | UK validator rejects; model must still catch |
| 47 | Organisation helpline | `Customer Services: 03069 990123 (Mon-Fri 8am-6pm)` on a bill header | keep | same shape as a personal number |
| 48 | Missing trunk 0 | `Mobile: 7700 900123` | PHONE | also matches the 10-digit NHS regex (local test) |

## D. BANK_ACCOUNT, SORT_CODE, IBAN, CARD (49-62)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 49 | Account next to amount and date | `Paid £1,250.00 from account 66374958 on 01/02/2026.` | BANK_ACCOUNT `66374958`; amount, date keep | number soup |
| 50 | Sort code vs date | `Sort code: 12-03-24` / `Signed 12-03-24` | SORT_CODE first; second keep | identical shape (local regex test) |
| 51 | Bare 6-digit sort code | `Sort code 089999, account 66374958` | SORT_CODE `089999`; BANK_ACCOUNT | no hyphens |
| 52 | Spaced account | `Account no. 6637 4958` | BANK_ACCOUNT | 4+4 grouping |
| 53 | 10-digit with hyphen | `a/c 01-66374958` | BANK_ACCOUNT (whole) | NatWest 10-digit style (R-49) |
| 54 | Statement payee line | `FPS TO 20-29-59 63748472 K KOVALENKO REF RENT OCT` | SORT_CODE, BANK_ACCOUNT, PERSON `K KOVALENKO`; `RENT OCT` keep | caps, no punctuation |
| 55 | Transaction reference | `FPS REF 48213377 £850.00` | keep | 8 digits like an account |
| 56 | Building society roll number | `Roll No. 1234/56789-0` | BANK_ACCOUNT **[decision]** | non-standard identifier |
| 57 | IBAN lowercase with spaces | `iban gb82 west 1234 5698 7654 32` | IBAN | case |
| 58 | IBAN across lines | `GB70 NWBK 0899\n9966 3749 58` | IBAN (whole) | line break inside |
| 59 | Partial card | `Visa ending 4242` / `**** **** **** 4242` | CARD `4242` **[decision]** | 4 digits, no Luhn |
| 60 | Amex grouping | `3782 822463 10005` | CARD | 4-6-5 grouping |
| 61 | Card typo after clue | `Card number: 4242 4242 4242 4241` | CARD | Luhn-gated regex leaks it |
| 62 | Expiry and CVV | `exp 08/29, CVV 123` | CARD x2 **[decision]** | look like a date and a small number |

## E. NI_NUMBER, DOB, ID_DOC (63-77)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 63 | NINO spaced lowercase | `ni no: ab 12 34 56 c` | NI_NUMBER | case and spaces |
| 64 | NINO without suffix | `NINO AB123456` | NI_NUMBER | strict validator fails (suffix A-D required, R-14) |
| 65 | NINO across lines | `AB 12 34\n56 C` | NI_NUMBER | line break |
| 66 | HMRC example in a template | `Enter your NI number, for example QQ 12 34 56 A.` | keep (example) | HMRC's own example; Q prefix is invalid (R-14); but a user-typed value is always labelled |
| 67 | DOB vs other dates | `Date of birth: 14/03/1988. Tenancy start: 14/03/2026.` | DOB `14/03/1988`; start keep | same format |
| 68 | DOB in words | `born on the fourteenth of March 1988` | DOB `the fourteenth of March 1988` | spelled out |
| 69 | DOB short year, dots | `DOB 14.03.88` | DOB | short format |
| 70 | Age | `aged 37` | keep (no type; quasi-identifier) | spec has no AGE type |
| 71 | Birthday without year | `her birthday is 14 March` | DOB **[decision]** | partial DOB |
| 72 | Passport near dates | `Passport no. 533401372, issued 02/05/2021, expires 02/05/2031` | ID_DOC `533401372`; dates keep | 9 digits, needs context (R-24) |
| 73 | Presidio-style fake passport | `Booking ref AB1234567` | keep | Presidio flags `[A-Z]{2}\d{7}` as UK_PASSPORT (R-22), but no UK passport has letters (R-24) |
| 74 | Driving licence + issue number | `Licence: SMITH801024J99AB 35` | ID_DOC (include `35`) | 18 characters; encodes DOB and initials (R-30) |
| 75 | Driving licence printed with spaces | `SMITH 801024 J99AB` | ID_DOC | spaced form breaks the 16-char regex (inference) |
| 76 | NHS number | `NHS No: 999 000 0018` | ID_DOC **[decision]** | 3-3-4 like a phone; checksum passes for ~1 in 11 random numbers (local test) |
| 77 | UTR with K | `UTR: 32824 97350K` | ID_DOC **[decision]** | 10 digits like a phone body |

## F. CUSTOM (78-85)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 78 | Client code | `Client code CL-20931` | CUSTOM | org-specific; not in any pretrained taxonomy (TAB: Presidio missed all case numbers, R-37) |
| 79 | Matter number with initials | `Our ref: M/2024/118/OK` | CUSTOM (whole) | slashes split tokens; contains initials |
| 80 | Policy number | `Policy number POL-77-4410-UK` | CUSTOM | mixed letters and digits |
| 81 | Reference built from surname | `Customer ref KOVA0042` | CUSTOM | leaks part of the surname |
| 82 | Reference in subject line | `RE: Matter M/2024/118 - Kovalenko deposit dispute` | CUSTOM, PERSON | headers are often skipped |
| 83 | ID shaped like a postcode | `Membership no. EH12 9QX` | CUSTOM (not POSTCODE) | valid postcode shape; context decides |
| 84 | Invoice vs account reference | `Invoice No. INV-2026-0457` / `Account ref ACC-55102` | invoice keep; CUSTOM second | boundary of "customer reference" |
| 85 | Sole-trader VAT | `VAT Reg No. GB 123 4567 82 (Mark Ellison t/a Ellison Plumbing)` | CUSTOM **[decision]**; PERSON | a company VAT number would be keep (#99) |

## G. Document level, chunking, PDF extraction (86-95)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 86 | Surname only in a later chunk | chunk 1: `Oleksandra Kovalenko (the Tenant)`; chunk 4: `Kovalenko must give notice` | PERSON in chunk 4 too | chunk has no context; fix with document-level propagation |
| 87 | Value cut by chunk edge | chunk 2 ends `Oleksandra Kova`, chunk 3 starts `lenko, of Flat 3` | PERSON fragments in both chunks | overlap needed; PII-TRACE: single-pass reading loses a third of gold characters on long dialogues (R-36) |
| 88 | Header/footer on every page | `Tenancy Agreement - O. Kovalenko - Page 2 of 9` (x9) | PERSON at every page | repeated text; dedupe changes offsets |
| 89 | Two-column interleaving | `Tenant: Oleksandra    Landlord: Graham\nKovalenko    Whitfield` | PERSON `Oleksandra`, `Kovalenko`, `Graham`, `Whitfield` | reading order mixes columns; parsers differ by layout (R-66) |
| 90 | Ligature in a name | `Griﬃths` (U+FB03) | PERSON | NFKC changes length, so offsets shift |
| 91 | Table row, no labels | `Kovalenko \| 14/03/1988 \| AB123456C \| 07700 900123` | PERSON, DOB, NI_NUMBER, PHONE | no clue words (R-12) |
| 92 | Quoted email thread | `> On 3 Oct, Graham Whitfield <g.whitfield@example.com> wrote:` (repeated in 3 quoted replies) | PERSON, EMAIL at every repeat | duplicates; quote markers |
| 93 | Same IBAN far apart | page 1 and page 28 of a 30-page contract | IBAN at both | long-range consistency |
| 94 | Already redacted input | `[PERSON_1] signed on behalf of [PERSON_2].` | keep | idempotency; must not re-label placeholders |
| 95 | Template fields | `[Tenant name] of [Property address]` | keep | look like placeholders, contain no data |

## H. Keep traps (96-108)

| # | Pattern | Example text | Correct labels | Why hard |
|---|---|---|---|---|
| 96 | Amounts, also in words | `Monthly rent £1,250.00 (one thousand two hundred and fifty pounds)` | keep | numbers near IDs |
| 97 | Ordinary dates and terms | `The tenancy starts on 1 March 2026 for a term of 12 months.` | keep | dates look like DOB |
| 98 | Clause and statute numbers | `Under clause 12.3.4 and section 21 of the Housing Act 1988` | keep | numeric references |
| 99 | Company VAT number | `Octavia Energy Ltd, VAT Reg GB 999 9999 73` | keep | valid VAT checksum; company, not person |
| 100 | Companies House number | `Registered in England and Wales no. 12674479` | keep | same shape as an 8-digit account (local test) |
| 101 | Company names with person names | `John Lewis Partnership`, `Marks and Spencer`, `Patel & Sons Ltd` | keep | look like people (R-10 over-redaction of organisations) |
| 102 | Product and tariff names | `Fixed Saver 12M tariff`, `iPhone 15 Pro` | keep | capitalised, mixed digits |
| 103 | Generic places | `Leeds City Council`, `London Underground`, `Royal Mail` | keep | contain location names |
| 104 | Role words | `the Landlord`, `the Tenant`, `the Guarantor` | keep | capitalised like names |
| 105 | Words that are names | `You may mark the invoice as paid at the Rose Garden office.` | keep (all) | May, Mark, Rose |
| 106 | 8-digit invoice number | `Invoice No. 00045678` | keep | account shape |
| 107 | Meter data | `Meter reading 04512 kWh, meter serial E12Z345678` | keep (spec has no type) | IDs with digits |
| 108 | Durations and counts | `24 months`, `3 bedrooms`, `2 parking spaces` | keep | numbers |

## Mix guidance (inference)
- About 30% of planted cases should be keep traps, so over-redaction is measured, not guessed.
- Plant each PERSON in at least two surface forms per document (#7, #9, #10) and at least one value per document without a clue word (#25, #91).
- Put a share of documents through a PDF render and extraction round trip, so #20, #40, #58, #88 to #90 occur naturally.
- Hold some hard-case patterns out of training entirely (eval only), so the demo can show the correction loop fixing a pattern it had not seen.
