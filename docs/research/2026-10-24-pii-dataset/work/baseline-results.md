# Baseline results (regex + validators)

Run on 2026-10-24 09:48 with `evalkit` (regex baseline from uk-formats.md). These are the numbers the model has to beat.

## Regex baseline: eval_synthetic

- Documents: 1459 (1540 records, 0 without a prediction)
- Leaks per 100 documents: **766.0** (11176 of 18164 values)
- Zero-leak documents: **10.7%**
- Values hidden (recall): 38.5%; precision: 100.0%; over-redacted spans: 0; keep-trap hit rate: 0.0%

| Type | Gold | Hidden | Strict | Partial | Right type | Leaked (fully) |
|---|---:|---:|---:|---:|---:|---:|
| PERSON | 6640 | 0.0% | 0.0% | 0.0% | 0.0% | 6640 (6640) |
| PHONE | 2401 | 98.8% | 98.5% | 98.8% | 100.0% | 28 (28) |
| ADDRESS | 1983 | 0.0% | 0.0% | 0.0% | 0.0% | 1983 (1983) |
| POSTCODE | 1923 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |
| CUSTOM | 1479 | 0.1% | 0.1% | 3.6% | 0.0% | 1477 (1425) |
| EMAIL | 1045 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |
| BANK_ACCOUNT | 815 | 61.6% | 60.0% | 61.6% | 100.0% | 313 (313) |
| SORT_CODE | 684 | 88.0% | 86.1% | 88.0% | 100.0% | 82 (82) |
| DOB | 368 | 0.0% | 0.0% | 0.0% | 0.0% | 368 (368) |
| CARD | 280 | 14.6% | 14.6% | 14.6% | 100.0% | 239 (239) |
| NI_NUMBER | 233 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |
| ID_DOC | 205 | 77.6% | 77.6% | 82.4% | 100.0% | 46 (36) |
| IBAN | 108 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |

## Regex baseline: eval_uk_external

- Documents: 260 (260 records, 0 without a prediction)
- Leaks per 100 documents: **135.38** (352 of 611 values)
- Zero-leak documents: **23.1%**
- Values hidden (recall): 42.4%; precision: 100.0%; over-redacted spans: 0; keep-trap hit rate: 0.0%

| Type | Gold | Hidden | Strict | Partial | Right type | Leaked (fully) |
|---|---:|---:|---:|---:|---:|---:|
| PERSON | 227 | 0.0% | 0.0% | 0.0% | 0.0% | 227 (227) |
| POSTCODE | 76 | 98.7% | 98.7% | 98.7% | 100.0% | 1 (1) |
| ADDRESS | 70 | 0.0% | 0.0% | 0.0% | 0.0% | 70 (70) |
| EMAIL | 58 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |
| PHONE | 52 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |
| DOB | 49 | 0.0% | 0.0% | 0.0% | 0.0% | 49 (49) |
| SORT_CODE | 21 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |
| NI_NUMBER | 21 | 100.0% | 100.0% | 100.0% | 100.0% | 0 (0) |
| BANK_ACCOUNT | 20 | 90.0% | 90.0% | 90.0% | 100.0% | 2 (2) |
| ID_DOC | 17 | 82.3% | 82.3% | 82.3% | 100.0% | 3 (3) |

