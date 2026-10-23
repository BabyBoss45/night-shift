# Gretel label mapping

Maps the PII labels of [gretelai/synthetic_pii_finance_multilingual](https://huggingface.co/datasets/gretelai/synthetic_pii_finance_multilingual) (Apache-2.0, by Gretel.ai) to our 13 entity types (design section 9.4, team pack 7.5).

`build_gretel.py` reads this table directly, so it is the only copy of the mapping. In the second column, `keep visible` means the label is dropped and the text stays as it is, and `drop document` means any document carrying the label is left out. A label that is missing from the table also drops its document, and the build reports it by name (`unmapped_label:<label>`), so the table can be extended.

The label list below is the 29 PII types named on the dataset card. It could not be checked against the data while this was written, because huggingface.co was blocked from the build session. The first real run confirms it: any label not listed here shows up in the drop reasons.

| Gretel label | Our type | Why |
|---|---|---|
| `name` | PERSON | Person name |
| `first_name` | PERSON | Part of a person name. Adjacent first and last name spans (only spaces between) are merged into one PERSON span |
| `last_name` | PERSON | As above |
| `street_address` | ADDRESS | Any UK postcode inside the span is split out as its own POSTCODE entity; the ADDRESS parts of the span share one entity_id |
| `local_latlng` | ADDRESS | Coordinates of a person's location; ADDRESS is the closest type |
| `email` | EMAIL | All email addresses are EMAIL |
| `phone_number` | PHONE | All phone numbers are PHONE |
| `iban` | IBAN | |
| `bban` | BANK_ACCOUNT | Domestic account number (in the UK, sort code plus account number); BANK_ACCOUNT is the closest single type |
| `bank_routing_number` | SORT_CODE | US routing number, the role a UK sort code plays |
| `credit_card_number` | CARD | |
| `credit_card_security_code` | CARD | Card data (CVV). Not a card number, but CARD is the closest type and it must be hidden |
| `ssn` | NI_NUMBER | National identity and insurance number; NI_NUMBER is the UK equivalent |
| `date_of_birth` | DOB | |
| `driver_license_number` | ID_DOC | |
| `passport_number` | ID_DOC | |
| `customer_id` | CUSTOM | Customer identifier (design 9.4) |
| `employee_id` | CUSTOM | Identifier tied to a specific person |
| `user_name` | CUSTOM | Usernames map to CUSTOM (design 9.4) |
| `ipv4` | CUSTOM | IP addresses map to CUSTOM (design 9.4) |
| `ipv6` | CUSTOM | As above |
| `account_pin` | CUSTOM | Secret tied to one account holder. The design drops documents only for passwords and API keys, so the PIN is mapped to the closest type and hidden |
| `company` | keep visible | Company names stay visible (team pack 7.5). A hidden span that overlaps a company span is ambiguous (for example a sole trader's own name), so that document is dropped |
| `date` | keep visible | Ordinary date |
| `date_time` | keep visible | Ordinary date and time |
| `time` | keep visible | Ordinary time |
| `swift_bic_code` | keep visible | Identifies a bank, not a person (design 9.4) |
| `password` | drop document | Design 9.4 |
| `api_key` | drop document | Design 9.4 |

## Other rules applied with the mapping

- **Span check:** a document is dropped if any span has invalid offsets, does not match the span's own value field (when the dataset gives one), starts or ends in the middle of a word, or is an `email` span without `@`. Surrounding whitespace and trailing `.,;:` are trimmed from spans first.
- **Overlaps:** a duplicate or nested span of the same type is removed. Any other overlap between hidden spans drops the document.
- **Regex sweep** for structured identifiers outside every span (email, IBAN with a valid checksum, Luhn-valid card number, NI number, UK phone, UK postcode, sort code `NN-NN-NN`, standalone 8-digit number). A match inside a kept-visible span (such as a date) is ignored. A match is added as an entity only when it is unambiguous:
  - email, valid IBAN, NI number and postcode are always added;
  - a phone number is added when it is written with separators or `+`, or follows "tel", "phone", "mobile", "call", "fax" or "contact";
  - a card number is added when "card" appears in the 40 characters before it;
  - a sort code is added when "sort" appears in the 25 characters before it;
  - an 8-digit number becomes BANK_ACCOUNT when "account", "acct" or "a/c" comes shortly before it on the same line.

  Any other match drops the document (`sweep_ambiguous:<kind>`), and so does a match that partly overlaps a span.
- **entity_id:** mentions with the same type and the same value (ignoring case and spacing) share an id. The ADDRESS parts of one street address share one id. A one-word PERSON mention joins the only longer PERSON name in the document that contains that word; when two longer names contain it, it keeps its own id.
