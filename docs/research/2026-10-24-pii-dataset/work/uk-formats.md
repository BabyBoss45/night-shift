# UK identifier formats: rules, regexes, validators, tests

Agent: R (methods). Date: 24 Oct 2026. Raw pages: `scratchpad/pii/raw/R-<n>.md` (first line of each file is the URL).
All regexes and validators below were run locally (`python3 -I`, Python 3, scratch folder) on 5+ valid and 5 invalid examples per type. Result: **13 of 13 groups pass** (full output at the end).

## How to use this in Veil
- **Two functions per type.** A *detection regex* finds candidates in running text (recall first). A *validator* says whether a candidate is well formed (checksum, allowed letters). Label high-risk types from the regex even when the validator fails if a context word is present ("sort code", "account", "NI number"): a typo in a real number is still personal data.
- **Checksums are weak filters.** Local test: 9.1% of random 10-digit strings pass the NHS modulus 11 check and 18.2% pass the UTR check (10,000 consecutive numbers). Luhn passes 1 in 10 random digit strings by construction. Use context words, not only checksums.
- **Collisions to plant in data** (all confirmed locally): a date `12-03-24` matches the sort code regex; a Companies House number `12674479` matches the 8-digit account regex; the digits of `07700 900123` without the 0 match the NHS number regex.
- **Synthetic values that cannot belong to real people:** Ofcom drama phone ranges (R-31), NHS numbers starting 999 (R-70, R-71), Stripe test card numbers (R-73), Vocalink modulus test sort code/account pairs (R-49). Prefer these in the generator.

## Summary table

| Type (Veil label) | Format | Check | Source | Risk note |
|---|---|---|---|---|
| UK postcode (`POSTCODE`) | outward `A9`, `A99`, `AA9`, `AA99`, `A9A`, `AA9A` + space + `9AA` | letter-position rules only; existence needs PAF / Code-Point Open | Wikipedia validation section (R-26), gov.uk BDT PDF regex (R-75) | Low alone; high with house number (identifies a household) |
| NI number (`NI_NUMBER`) | 2 letters, 6 digits, suffix A-D | prefix rules (no checksum) | HMRC NIM39110 (R-14) | High-risk (identity fraud). Not special category |
| Sort code (`SORT_CODE`) | `NN-NN-NN` (6 digits) | none public; Vocalink modulus applies to sort code + account | Wikipedia (R-35), Vocalink spec (R-49) | High-risk when with account |
| Bank account (`BANK_ACCOUNT`) | 8 digits standard; 6, 7, 9, 10 exist and are converted | Vocalink modulus (needs weight table) | Vocalink v9.10 s.2.1.2 (R-49) | High-risk (fraud) |
| IBAN GB (`IBAN`) | `GBkk BBBB SSSS SSAA AAAA AA`, 22 chars | ISO 7064 mod 97 = 1 | Wikipedia IBAN (R-28) | High-risk |
| Payment card (`CARD`) | 12-19 digits, IIN prefix by scheme | Luhn + IIN/length table | Wikipedia (R-29), Stripe test numbers (R-73) | High-risk (PCI) |
| UK phone (`PHONE`) | NSN 10 digits (01 also 9; 0800 also 9 or 7) | length by first digit | Wikipedia (R-32), Ofcom drama ranges (R-31) | Medium |
| NHS number (no own label: use `ID_DOC` or `CUSTOM`, decide) | 10 digits, shown `3 3 4` | modulus 11 (mandatory) | NHS Data Dictionary (R-27) | Implies health context; health data is special category (R-76) |
| UK passport (`ID_DOC`) | **9 digits** for every series in circulation | no public check digit on the number | HMPO Basic passport checks (R-24) | High-risk |
| GB driving licence (`ID_DOC`) | 16 chars (+2-digit issue number = 18) | structure + date; DVLA check chars not public | Wikipedia (R-30), Presidio code comment (R-19) | High-risk; encodes surname, DOB, initials, sex |
| VAT number (`CUSTOM` if a sole trader, keep if a company) | `GB` + 9 digits (or 12 branch, `GD`/`HA` + 3) | weighted mod 97, or mod 97 after +55 ("9755") | HMRC reference-checker code (R-72), Wikipedia (R-33) | Personal data only for sole traders |
| Companies House number (keep) | 8 chars: 8 digits, or 2-letter prefix + 6 digits | none documented | Companies House URI guide (R-77) | Public register; keep trap |
| UTR (`CUSTOM`) | 10 digits, optional `K` before or after | first digit = lookup[(weighted sum of digits 2-10) mod 11] | HMRC reference-checker code (R-72), Sage KB (R-68) | High-risk (tax identity) |

## Details per type

### 1. UK postcode
- **Rules (R-26):** Q, V, X never in position 1; I, J, Z never in position 2; in `A9A` the third character is one of A B C D E F G H J K P S T U W; in `AA9A` the fourth is one of A B E H M N P R V W X Y; the inward unit letters never use C, I, K, M, O, V. Special: `GIR 0AA`, BFPO `BF1` codes, overseas territories `BIQQ 1ZZ`, `FIQQ 1ZZ`.
- **Official gov.uk regex has defects (tested):** the version in the UKVI Bulk Data Transfer PDF (R-75) contains `[A Za-z]` (a space instead of a hyphen) and binds `^` and `$` to different alternatives. Local test: it **rejects `W1A 0AX`**, and `re.search` returns `SW1A 1AA` from `XX99 SW1A 1AA` and `GIR 0AA` from `GIR 0AA trailing junk`. Do not use it as is.
- Existence check needs Code-Point Open or PAF (R-26). A regex only checks shape.
- Valid tested: `CR2 6XH`, `DN55 1PT`, `M1 1AE`, `B33 8TH`, `W1A 0AX`, `EC1A 1BB`. Invalid tested: `QA1 1AA`, `AJ1 1AA`, `M1 1CA`, `W1Z 0AX`, `EC1Z 1BB`.

### 2. National Insurance number
- **Rules (HMRC NIM39110, R-14):** "2 letters, 6 numbers and a final letter, which is always A, B, C, or D"; D, F, I, Q, U, V never first or second letter; O never second; prefixes BG, GB, KN, NK, NT, TN, ZZ not used. Administrative look-alikes: OO, FY, NC, PP999999P, PZ/PY, TN (not real NINOs). A Temporary Reference Number has format `11 a1 11 11` and is not a NINO.
- **HMRC's own example `QQ 12 34 56 A` fails the rules** (Q is excluded). Template text often contains it: a keep trap if it is clearly an example, a leak if a user typed a real-looking value.
- Valid tested: `AB 12 34 56 C`, `JG103759A`, `CE 11 22 33 D`, `OA123456B`, `ZY 98 76 54 A`. Invalid tested: `QQ 12 34 56 A`, `AO123456A`, `GB123456A`, `AB123456E`, `DA123456A`.
- Presidio's `UK_NINO` regex encodes the same rules (R-21).

### 3. Sort code
- Six digits, "usually formatted as three pairs of numbers, for example 12-34-56" (R-35). No public checksum on its own. Validity is checked against the EISCD directory; modulus checks apply to the sort code + account pair (R-49).
- Detection: `NN-NN-NN` or `NN NN NN` with the same separator; bare `NNNNNN` only after a context word ("sort code").
- Valid tested (Vocalink test cases, R-49): `08-99-99`, `10-79-99`, `20-29-59`, `87 14 27`, `938611`. Invalid: `12-34-5`, `123-45-6`, `12-34 56`, `AB-12-34`, `12.34.56`.

### 4. UK bank account number
- Vocalink: "The modulus check methods described in this specification are based on a standard account number of eight digits" (R-49). Conversion: 10-digit NatWest use last 8; Co-operative Bank and Leeds BS use first 8; 9-digit Santander moves the first digit into the sort code; 7 digits prefix one 0; 6 digits prefix 00 (R-49, s.2.1.2).
- Full modulus checking needs Vocalink's weight table and exception rules (R-49); not worth it for the demo. Use 8-digit regex + context words ("account", "a/c", "acc no").
- Valid tested (Vocalink test cases): `66374958`, `88837491`, `63748472`, `46238510`, `07806039`. Invalid: `1234567`, `123456789`, `12345A78`, `6637 495`, empty.

### 5. IBAN (GB)
- 22 characters: `GB`, 2 check digits, 4-letter bank code, 6-digit sort code, 8-digit account. Validation: move the first 4 characters to the end, replace letters by numbers (A=10 ... Z=35), the integer mod 97 must be 1 (R-28). Wikipedia's fictitious example `GB82 WEST 1234 5698 7654 32` passes.
- Valid tested: `GB82 WEST 1234 5698 7654 32` plus four generated from Vocalink test pairs (`GB70NWBK08999966374958`, `GB76BARC20295963748472`, `GB88MIDL10799988837491`, `GB73LOYD87142746238510`). Invalid: wrong check digits, 21 characters, digit in bank code, a valid German IBAN (not GB), last digit changed.

### 6. Payment card
- 8 to 19 digits overall; IIN/BIN prefix; Luhn check digit (R-29). Ranges used (R-29): Visa `4` (13, 16, 19); Mastercard `51-55` and `2221-2720` (16); Amex `34`, `37` (15); Maestro UK `6759`, `676770`, `676774` (12-19); Maestro `5018, 5020, 5038, 5893, 6304, 6759, 6761-6763` (12-19); Discover `6011, 644-649, 65` (16-19); JCB `3528-3589` (16-19); Diners `30, 36, 38, 39` (14-19); UnionPay `62` (16-19).
- Valid tested (Stripe published test numbers, R-73): `4242 4242 4242 4242`, `5555 5555 5555 4444`, `2223 0031 2200 3222`, `3782 822463 10005`, `6011 1111 1111 1117`. Invalid: Luhn fail, no scheme, Amex with 14 digits, Luhn fail, all-9s.
- Partial card numbers ("ending 4821", `**** 4821`) cannot be validated; decide a policy (see hard-cases.md).

### 7. UK phone numbers
- NSN = digits after the 0 trunk prefix or +44. "Geographic telephone numbers in the UK always have nine or ten digits after the 0 trunk code" (R-32); 0800 can be 10, 9 or 7 digits; mobiles 071xx-075xx, 07624, 077xx-079xx; 070 personal numbering; 076 pagers (R-32).
- Accept `+44`, `0044`, `+44 (0)`, brackets, spaces, hyphens. `+44 07700 ...` (a common mistake) is rejected by the strict validator; the detection regex still flags it when written with `(0)`.
- **Use Ofcom drama ranges in synthetic data (R-31):** mobile `07700 900000-900999`; London `020 7946 0000-0999`; Leeds `0113 496 0000-0999`, same `496` block for 0114, 0115, 0116, 0117, 0118, 0121, 0131, 0141, 0151, 0161; Tyneside `0191 498 0000-0999`; Northern Ireland `028 9649 6000-6999`; Cardiff `029 2018 0000-0999`; no area `01632 960000-960999`; freephone `08081 570000-570999`; premium `0909 8790000-8790999`; UK-wide `03069 990000-990999`.
- Valid tested: `07700 900123`, `+44 7700 900456`, `020 7946 0321`, `0113 496 0789`, `+44 (0)161 496 0123`, `028 9649 6123`, `01632 960456`. Invalid: `07700 90012`, `06123 456789`, `+1 415 555 0199`, `0800 123`, `07700 9001234`.

### 8. NHS number
- "10 numeric digits ... The check digit is validated using the Modulus 11 algorithm and the use of this algorithm is mandatory" (R-27). Weights 10..2 on digits 1-9; check = 11 - (sum mod 11); 11 becomes 0; 10 means invalid.
- Test numbers: NHS England says synthetic records use NHS numbers that start 999, "from a range of numbers from which real NHS numbers will never be issued" (R-70); the PDS smoke-test patient is `9990548609` (NHS England PDS FHIR API test data page, R-78).
- **Finding (local test):** both documentation examples `999 123 4567` (NHS service manual "preferred example number", R-71) and `999 123 4566` (e-RS guidance, R-70) **fail** modulus 11 (the check computes to 10). A checksum-gated detector would skip them. Do not use them as "valid" examples in data; use generated ones.
- Valid tested: `999 054 8609`, `999 000 0018`, `999 000 0026`, `999 000 0034`, `999 000 0042`. Invalid: `999 054 8608`, `999 123 4567`, `999 123 4566`, `99912345678`, `999 12A 4566`.
- Scotland (CHI) and Northern Ireland (H&C) numbers are also 10 digits; not covered here.

### 9. UK passport number
- HM Passport Office: 9 digits for the 1988, 1998, 2006, 2010, 2015 series and "9 numerical digits" for the 2020 and 2025 series; the thin-film serial "3 alpha characters and 4 numeric followed by a check symbol ... should not be confused with the 9 digit passport number" (R-24).
- **Presidio's `UK_PASSPORT` recognizer uses `[A-Z]{2}\d{7}` (R-22), which matches no UK passport number;** an open issue documents this (R-25). If we report Presidio as a baseline, say so or patch it.
- No public check digit on the number (the MRZ line has its own check digits; out of scope). Detection must rely on context ("passport", "passport no").
- Valid tested: `123456789`, `925665416`, `533401372`, `107185703`, `000000001`. Invalid: `AB1234567`, `12345678`, `1234567890`, `12345678A`, `1234 56789`.

### 10. GB driving licence number
- 16 characters plus a 2-digit issue number (R-30): 1-5 surname (padded with 9), 6 decade digit of birth year, 7-8 month (+50 for female, so 51-62), 9-10 day, 11 year digit, 12-13 initials (9 if no middle initial), 14 arbitrary digit (usually 9), 15-16 two computer check characters (may be letters), 17-18 issue number. Presidio notes "the DVLA check digit algorithm is not public" (R-19). Northern Ireland licences use a different numeric format (not covered).
- It **encodes surname, date of birth, sex and initials**, so one leaked licence number leaks several attributes.
- Valid tested: `MORGA753116SM9IJ`, `SMITH801024J99AB`, `JONES862217SA9XY`, `LI999905302W99KZ`, `MORGA753116SM9IJ 35`. Invalid: month 13, 30 February, all-9 surname, 9 inside surname, 15 characters.

### 11. VAT registration number (GB)
- `GB` + 9 digits (3-4-2), or 12 digits for branch traders, `GD` + 000-499 (government departments), `HA` + 500-999 (health authorities) (R-33). The 2-digit block is a weighted modulus 97 check; since November 2009 a parallel "9755" series subtracts 55 (R-33).
- Implemented exactly as HMRC's open-source `VatReferenceChecker` (weights 8, 7, 6, 5, 4, 3, 2; accept 97-mod or 97-mod after +55) (R-72).
- Valid tested: `GB999 9999 73` (Wikipedia example), `GB123456782`, `GB100012318` (9755 series), `GBGD001`, `GBHA599`. Invalid: `GB999 9999 74`, `GB12345678`, `GBGD500`, `GBHA499`, `GB999 9999 7`.
- A company's VAT number is not personal data; a sole trader's is. Label by context.

### 12. Companies House company number
- 8 characters; E&W companies are 8 digits (leading zeros), others use a 2-letter prefix + 6 digits: SC, NI, OC (LLP E&W), SO, NC, LP, SL, NL, FC, R0 and others (R-77). No documented checksum.
- **Keep trap:** an 8-digit company number is indistinguishable from an 8-digit account number without context ("Registered in England and Wales no.", "Company number").
- Valid tested: `02050399`, `SC002180` (both from R-77), `OC301234`, `NI012345`, `12674479`. Invalid: `SC12345`, `XX123456`, `00000000`, `1234567A`, `SC1234567`.

### 13. Unique Taxpayer Reference (UTR)
- 10 digits; Self Assessment may show a `K` before or after. Check digit is the **first** digit: weights 6, 7, 8, 9, 10, 5, 4, 3, 2 on digits 2-10, remainder mod 11, lookup `2 1 9 8 7 6 5 4 3 2 1` (HMRC `UtrReferenceChecker`, R-72). Sage's worked example `3282497350` (R-68) passes. HMRC has not published this as a specification; the weights come from HMRC's own open-source checker (R-69, R-72).
- Valid tested: `3282497350`, `2234567890`, `1123456789`, `9987654321K`, `K7555000111`. Invalid: `3282497351`, `328249735`, `32824973500`, `K3282497350K`, `ABCDE12345`.

## Special category and high-risk notes
- UK GDPR special category data: racial or ethnic origin, political opinions, religious or philosophical beliefs, trade union membership, genetic data, biometric data (for identification), health, sex life or sexual orientation (ICO, R-76). The ICO says financial data "does not constitute special category data" although it may be sensitive (R-76).
- So: none of the 13 identifiers is special category by itself. NHS numbers point to health records (inference: treat as high-risk). Card, account, sort code, IBAN, NI number, UTR, passport and driving licence are high-risk for fraud and identity theft (spec NFR-1 already targets zero leaks for account, card, NI, IBAN).

## Code (tested)
```python
"""UK identifier regexes (detection) and validators (strict checks).

Detection regexes are recall-oriented: they find candidate spans in running text.
Validators are precision-oriented: they say whether a candidate is a well-formed value.
Use both: regex -> validator -> (optional) context words -> label.
"""
import re

# ---------------------------------------------------------------- POSTCODE
# Rules from Wikipedia "Postcodes in the United Kingdom" > Validation (R-26):
# pos1 not Q,V,X; pos2 not I,J,Z; A9A third letter in ABCDEFGHJKPSTUW;
# AA9A fourth letter in ABEHMNPRVWXY; inward unit letters never C,I,K,M,O,V.
_OUTWARD = (
    r"(?:[A-PR-UWYZ][0-9]{1,2}"          # A9, A99
    r"|[A-PR-UWYZ][A-HK-Y][0-9]{1,2}"    # AA9, AA99
    r"|[A-PR-UWYZ][0-9][A-HJKPSTUW]"     # A9A
    r"|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY])"  # AA9A
)
_INWARD = r"[0-9][ABD-HJLNP-UW-Z]{2}"
POSTCODE_RE = re.compile(rf"\b(?:GIR ?0AA|{_OUTWARD} ?{_INWARD})\b", re.I)

def is_valid_postcode(s: str) -> bool:
    s = s.strip().upper()
    return re.fullmatch(rf"(?:GIR ?0AA|{_OUTWARD} ?{_INWARD})", s) is not None

# Official gov.uk regex, copied verbatim from the Bulk Data Transfer PDF (R-75), for comparison only.
GOVUK_POSTCODE_RE_VERBATIM = (r"^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})"
                              r"|(([A Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$")

# ---------------------------------------------------------------- NI NUMBER
# HMRC NIM39110 (R-14): D,F,I,Q,U,V never 1st or 2nd letter; O never 2nd;
# BG, GB, KN, NK, NT, TN, ZZ never used; suffix always A-D.
NINO_RE = re.compile(
    r"\b(?!BG|GB|KN|NK|NT|TN|ZZ)[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]"
    r"[ -]?\d{2}[ -]?\d{2}[ -]?\d{2}[ -]?[A-D]\b", re.I)
NINO_ADMIN_PREFIXES = {"OO", "FY", "NC", "PZ", "PY", "TN"}  # HMRC: look like NINOs, not real NINOs

def is_valid_nino(s: str) -> bool:
    s = re.sub(r"[ -]", "", s.upper())
    if not re.fullmatch(r"[A-Z]{2}\d{6}[A-D]", s):
        return False
    p1, p2 = s[0], s[1]
    if p1 in "DFIQUV" or p2 in "DFIQUVO":
        return False
    if s[:2] in {"BG", "GB", "KN", "NK", "NT", "TN", "ZZ"}:
        return False
    if s == "PP999999P":
        return False
    return True

# ---------------------------------------------------------------- SORT CODE / ACCOUNT
SORT_CODE_RE = re.compile(r"\b\d{2}([- ])\d{2}\1\d{2}\b")      # same separator twice
SORT_CODE_BARE_RE = re.compile(r"(?i)(?<=sort code)[:\s]*\b(\d{6})\b")
ACCOUNT_RE = re.compile(r"\b\d{8}\b")                          # needs context words to label

def is_valid_sort_code(s: str) -> bool:
    return re.fullmatch(r"\d{2}([- ]?)\d{2}\1\d{2}", s.strip()) is not None

def normalise_account(acc: str, sort_code: str = "") -> tuple[str, str] | None:
    """Vocalink rules for nonstandard lengths (R-49, section 2.1.2). Returns (sort, 8-digit account)."""
    d = re.sub(r"[ -]", "", acc)
    sc = re.sub(r"\D", "", sort_code)
    if not d.isdigit():
        return None
    if len(d) == 8:
        return sc, d
    if len(d) == 7:
        return sc, "0" + d
    if len(d) == 6:
        return sc, "00" + d
    if len(d) == 9 and len(sc) == 6:          # Santander: last sort digit := first account digit
        return sc[:5] + d[0], d[1:]
    if len(d) == 10:                          # NatWest: last 8; Co-op/Leeds BS: first 8 (bank-specific)
        return sc, d[-8:]
    return None

def is_valid_account_number(s: str) -> bool:
    return re.fullmatch(r"\d{8}", re.sub(r"[ -]", "", s.strip())) is not None

# ---------------------------------------------------------------- IBAN (GB)
IBAN_GB_RE = re.compile(r"\bGB\d{2} ?[A-Z]{4} ?\d{4} ?\d{4} ?\d{4} ?\d{2}\b", re.I)

def iban_mod97(iban: str) -> int:
    s = re.sub(r"\s", "", iban).upper()
    s = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in s)) % 97

def is_valid_iban_gb(s: str) -> bool:
    s = re.sub(r"\s", "", s).upper()
    return re.fullmatch(r"GB\d{2}[A-Z]{4}\d{14}", s) is not None and iban_mod97(s) == 1

def make_iban_gb(bank4: str, sort6: str, acc8: str) -> str:
    bban = bank4 + sort6 + acc8
    check = 98 - iban_mod97("GB00" + bban)
    return f"GB{check:02d}{bban}"

# ---------------------------------------------------------------- CARD
CARD_RE = re.compile(r"\b(?:\d[ -]?){11,18}\d\b")

def luhn_ok(d: str) -> bool:
    total, alt = 0, False
    for ch in reversed(d):
        n = int(ch)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0

def card_scheme(d: str) -> str | None:
    """IIN ranges and lengths from Wikipedia 'Payment card number' (R-29)."""
    n = len(d)
    p = lambda k: int(d[:k])
    if d[0] == "4" and n in (13, 16, 19):
        return "visa"
    if (51 <= p(2) <= 55 or 2221 <= p(4) <= 2720) and n == 16:
        return "mastercard"
    if p(2) in (34, 37) and n == 15:
        return "amex"
    if (p(4) in (6759,) or p(6) in (676770, 676774)) and 12 <= n <= 19:
        return "maestro_uk"
    if p(4) in (5018, 5020, 5038, 5893, 6304, 6759, 6761, 6762, 6763) and 12 <= n <= 19:
        return "maestro"
    if (p(4) == 6011 or 644 <= p(3) <= 649 or p(2) == 65) and 16 <= n <= 19:
        return "discover"
    if 3528 <= p(4) <= 3589 and 16 <= n <= 19:
        return "jcb"
    if p(2) in (30, 36, 38, 39) and 14 <= n <= 19:
        return "diners"
    if p(2) == 62 and 16 <= n <= 19:
        return "unionpay"
    return None

def is_valid_card(s: str) -> bool:
    d = re.sub(r"[ -]", "", s)
    return d.isdigit() and 12 <= len(d) <= 19 and luhn_ok(d) and card_scheme(d) is not None

# ---------------------------------------------------------------- PHONE (UK)
PHONE_RE = re.compile(
    r"(?<![\w+])(?:(?:\+|00)44[\s-]?(?:\(0\)[\s-]?)?|\(?0)"
    r"(?:\d[\s\-)]{0,2}){8,10}\d\b")

def phone_nsn(s: str) -> str | None:
    """National significant number: digits after +44 / 0044 / leading 0 (R-32)."""
    t = s.strip()
    t = re.sub(r"\(0\)", "", t)
    d = re.sub(r"[^\d+]", "", t)
    if d.startswith("+44"):
        d = d[3:]
    elif d.startswith("0044"):
        d = d[4:]
    elif d.startswith("0"):
        d = d[1:]
    else:
        return None
    return d if d.isdigit() else None

def is_valid_uk_phone(s: str) -> bool:
    nsn = phone_nsn(s)
    if not nsn or nsn[0] == "0":
        return False
    first, n = nsn[0], len(nsn)
    if first == "1":
        return n in (9, 10)            # 01: 10, rarely 9 (e.g. 016977 xxxx)
    if first in "23":
        return n == 10                 # 02 geographic, 03 UK-wide
    if first == "7":
        return n == 10                 # 07 mobile / personal / pager
    if first == "8":
        return n in (7, 9, 10)         # 0800 can be 10, 9 or 7; 0845 10 or 7
    if first == "9":
        return n == 10
    return False                       # 04, 06 unused; 05 only legacy

# ---------------------------------------------------------------- NHS NUMBER
NHS_RE = re.compile(r"\b\d{3}[ -]?\d{3}[ -]?\d{4}\b")

def is_valid_nhs(s: str) -> bool:
    """NHS Data Dictionary modulus 11 (R-27)."""
    d = re.sub(r"[ -]", "", s)
    if not re.fullmatch(r"\d{10}", d):
        return False
    total = sum(int(d[i]) * (10 - i) for i in range(9))
    check = 11 - total % 11
    if check == 11:
        check = 0
    if check == 10:
        return False
    return check == int(d[9])

def make_nhs(first9: str) -> str | None:
    total = sum(int(first9[i]) * (10 - i) for i in range(9))
    check = 11 - total % 11
    check = 0 if check == 11 else check
    return None if check == 10 else first9 + str(check)

# ---------------------------------------------------------------- PASSPORT (UK)
# HM Passport Office: every series uses 9 numerical digits (R-24). No public check digit on the number.
PASSPORT_RE = re.compile(r"(?i)\bpassport(?:\s+(?:no\.?|number|#))?[:\s]*\b(\d{9})\b")

def is_valid_uk_passport(s: str) -> bool:
    return re.fullmatch(r"\d{9}", s.strip()) is not None

# ---------------------------------------------------------------- DRIVING LICENCE (GB)
# Structure from Wikipedia 'Driving licence in the United Kingdom' (R-30); month/day classes as in Presidio (R-19).
DL_RE = re.compile(
    r"\b[A-Z9]{5}\d(?:0[1-9]|1[0-2]|5[1-9]|6[0-2])(?:0[1-9]|[12]\d|3[01])\d"
    r"[A-Z][A-Z9]\d[A-Z0-9]{2}(?:\s?\d{2})?\b")

def is_valid_gb_driving_licence(s: str) -> bool:
    t = re.sub(r"\s", "", s.upper())
    if len(t) == 18:
        if not t[16:].isdigit():
            return False
        t = t[:16]
    if not re.fullmatch(r"[A-Z9]{5}\d\d{2}\d{2}\d[A-Z][A-Z9]\d[A-Z0-9]{2}", t):
        return False
    if not re.fullmatch(r"[A-Z]+9*", t[:5]):      # letters, then 9-padding only at the end
        return False
    mm, dd = int(t[6:8]), int(t[8:10])
    if mm > 50:
        mm -= 50                                    # female: month + 50
    if not 1 <= mm <= 12:
        return False
    max_day = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mm - 1]
    return 1 <= dd <= max_day

# ---------------------------------------------------------------- VAT (GB)
VAT_RE = re.compile(r"\bGB ?(?:\d{3} ?\d{4} ?\d{2}(?: ?\d{3})?|GD[0-4]\d{2}|HA[5-9]\d{2})\b", re.I)

def is_valid_gb_vat(s: str) -> bool:
    """HMRC reference-checker VatReferenceChecker (R-72): weights 8..2 on 7 digits, 97-mod or 97-mod after +55."""
    t = re.sub(r"[\s-]", "", s.upper())
    if t.startswith("GB"):
        t = t[2:]
    m = re.fullmatch(r"GD([0-4]\d{2})|HA([5-9]\d{2})", t)
    if m:
        return True
    if not re.fullmatch(r"\d{9}(\d{3})?", t):
        return False
    t9 = t[:9]
    wsum = sum(int(t9[i]) * w for i, w in enumerate([8, 7, 6, 5, 4, 3, 2]))
    expected = int(t9[7:9])
    def check(total: int) -> bool:
        while total > 97:
            total -= 97
        return 97 - total == expected
    return check(wsum) or check(wsum + 55)

# ---------------------------------------------------------------- COMPANIES HOUSE
CH_PREFIXES = ("SC NI OC SO NC LP SL NL R0 FC SF NF GE GS GN SE ES EN AC SA NA ZC SZ NZ "
               "IP SP IC SI NP NV RC SR NR NO").split()      # Companies House URI guide list
CRN_RE = re.compile(rf"\b(?:\d{{8}}|(?:{'|'.join(CH_PREFIXES)})\d{{6}})\b")

def is_valid_crn(s: str) -> bool:
    t = re.sub(r"\s", "", s.upper())
    if t == "00000000":
        return False
    return re.fullmatch(r"\d{8}", t) is not None or (t[:2] in CH_PREFIXES and re.fullmatch(r"\d{6}", t[2:]) is not None and len(t) == 8)

# ---------------------------------------------------------------- UTR
UTR_RE = re.compile(r"\bK?\d{5} ?\d{5}K?\b")

def is_valid_utr(s: str) -> bool:
    """HMRC reference-checker UtrReferenceChecker (R-72): check digit is the FIRST digit."""
    t = re.sub(r"\s", "", s.upper())
    if t.startswith("K"):
        t = t[1:]
    elif t.endswith("K"):
        t = t[:-1]
    if not re.fullmatch(r"\d{10}", t):
        return False
    wsum = sum(int(t[i + 1]) * w for i, w in enumerate([6, 7, 8, 9, 10, 5, 4, 3, 2]))
    return "21987654321"[wsum % 11] == t[0]

def make_utr(last9: str) -> str:
    wsum = sum(int(last9[i]) * w for i, w in enumerate([6, 7, 8, 9, 10, 5, 4, 3, 2]))
    return "21987654321"[wsum % 11] + last9
```

## Test script
```python
import re, sys
sys.path.insert(0, sys.argv[1])
from uk_formats import *

def make_vat(first7: str, series9755: bool = False) -> str:
    wsum = sum(int(first7[i]) * w for i, w in enumerate([8, 7, 6, 5, 4, 3, 2]))
    if series9755:
        wsum += 55
    while wsum > 97:
        wsum -= 97
    return first7 + f"{97 - wsum:02d}"

nhs_gen = [make_nhs(x) for x in ("999000001", "999000002", "999000003", "999000004")]

CASES = {
 "POSTCODE": (is_valid_postcode, POSTCODE_RE,
    ["CR2 6XH", "DN55 1PT", "M1 1AE", "B33 8TH", "W1A 0AX", "EC1A 1BB"],
    ["QA1 1AA", "AJ1 1AA", "M1 1CA", "W1Z 0AX", "EC1Z 1BB"]),
 "NI_NUMBER": (is_valid_nino, NINO_RE,
    ["AB 12 34 56 C", "JG103759A", "CE 11 22 33 D", "OA123456B", "ZY 98 76 54 A"],
    ["QQ 12 34 56 A", "AO123456A", "GB123456A", "AB123456E", "DA123456A"]),
 "SORT_CODE": (is_valid_sort_code, SORT_CODE_RE,
    ["08-99-99", "10-79-99", "20-29-59", "87 14 27", "938611"],
    ["12-34-5", "123-45-6", "12-34 56", "AB-12-34", "12.34.56"]),
 "BANK_ACCOUNT": (is_valid_account_number, ACCOUNT_RE,
    ["66374958", "88837491", "63748472", "46238510", "07806039"],
    ["1234567", "123456789", "12345A78", "6637 495", ""]),
 "IBAN": (is_valid_iban_gb, IBAN_GB_RE,
    ["GB82 WEST 1234 5698 7654 32", make_iban_gb("NWBK", "089999", "66374958"),
     make_iban_gb("BARC", "202959", "63748472"), make_iban_gb("MIDL", "107999", "88837491"),
     make_iban_gb("LOYD", "871427", "46238510")],
    ["GB83 WEST 1234 5698 7654 32", "GB82WEST1234569876543", "GB82 W3ST 1234 5698 7654 32",
     "DE89370400440532013000", "GB82 WEST 1234 5698 7654 33"]),
 "CARD": (is_valid_card, CARD_RE,
    ["4242 4242 4242 4242", "5555 5555 5555 4444", "2223 0031 2200 3222", "3782 822463 10005", "6011 1111 1111 1117"],
    ["4242 4242 4242 4241", "1234 5678 1234 5678", "3782 822463 1000", "5555 5555 5555 4440", "9999 9999 9999 9995"]),
 "PHONE": (is_valid_uk_phone, PHONE_RE,
    ["07700 900123", "+44 7700 900456", "020 7946 0321", "0113 496 0789", "+44 (0)161 496 0123", "028 9649 6123", "01632 960456"],
    ["07700 90012", "06123 456789", "+1 415 555 0199", "0800 123", "07700 9001234"]),
 "NHS_NUMBER": (is_valid_nhs, NHS_RE,
    ["999 054 8609"] + [f"{x[:3]} {x[3:6]} {x[6:]}" for x in nhs_gen if x],
    ["999 054 8608", "999 123 4567", "999 123 4566", "99912345678", "999 12A 4566"]),
 "PASSPORT": (is_valid_uk_passport, None,
    ["123456789", "925665416", "533401372", "107185703", "000000001"],
    ["AB1234567", "12345678", "1234567890", "12345678A", "1234 56789"]),
 "DRIVING_LICENCE": (is_valid_gb_driving_licence, DL_RE,
    ["MORGA753116SM9IJ", "SMITH801024J99AB", "JONES862217SA9XY", "LI999905302W99KZ", "MORGA753116SM9IJ 35"],
    ["SMITH813024J99AB", "SMITH802304J99AB", "99999801024J99AB", "SM9TH801024J99AB", "SMITH80102J99AB"]),
 "VAT": (is_valid_gb_vat, VAT_RE,
    ["GB999 9999 73", "GB" + make_vat("1234567"), "GB" + make_vat("1000123", True), "GBGD001", "GBHA599"],
    ["GB999 9999 74", "GB12345678", "GBGD500", "GBHA499", "GB999 9999 7"]),
 "COMPANY_NUMBER": (is_valid_crn, CRN_RE,
    ["02050399", "SC002180", "OC301234", "NI012345", "12674479"],
    ["SC12345", "XX123456", "00000000", "1234567A", "SC1234567"]),
 "UTR": (is_valid_utr, UTR_RE,
    ["3282497350", "2234567890", make_utr("123456789"), make_utr("987654321") + "K", "K" + make_utr("555000111")],
    ["3282497351", "328249735", "32824973500", "K3282497350K", "ABCDE12345"]),
}

fails = 0
for name, (fn, rx, valid, invalid) in CASES.items():
    v = [(x, fn(x)) for x in valid]
    iv = [(x, fn(x)) for x in invalid]
    ok = all(r for _, r in v) and not any(r for _, r in iv)
    fails += 0 if ok else 1
    det = ""
    if rx is not None:
        found = [bool(rx.search(f"Ref: {x}.")) for x in valid]
        det = f"  detect-regex finds {sum(found)}/{len(found)} valid in context"
    print(f"{name:16s} {'PASS' if ok else 'FAIL'}{det}")
    print("   valid  :", "; ".join(f"{x} -> {r}" for x, r in v))
    print("   invalid:", "; ".join(f"{x} -> {r}" for x, r in iv))

# Context tests for the passport and sort-code-without-dashes regexes
print("PASSPORT ctx:", PASSPORT_RE.search("Passport number: 533401372 issued 2021").group(1))
print("SORT bare ctx:", SORT_CODE_BARE_RE.search("Sort code 938611, account 07806039").group(1))
print("normalise 9-digit Santander:", normalise_account("123456789", "09-01-26"))

# Official gov.uk postcode regex: show its defects
gov = re.compile(GOVUK_POSTCODE_RE_VERBATIM)
for pc in ["W1A 0AX", "EC1A 1BB", "M1 1AE", "SW1A 1AA"]:
    print(f"gov.uk verbatim fullmatch {pc!r}: {bool(gov.fullmatch(pc))}")
print("gov.uk verbatim search inside 'XX99 SW1A 1AA':", gov.search("XX99 SW1A 1AA").group(0))
print("gov.uk verbatim search 'GIR 0AA trailing junk':", gov.search("GIR 0AA trailing junk").group(0))

# Keep-trap collisions
print("date 12-03-24 matches SORT_CODE_RE:", bool(SORT_CODE_RE.search("Signed 12-03-24")))
print("company 12674479 matches ACCOUNT_RE:", bool(ACCOUNT_RE.search("Company no. 12674479")))
print("amount 1,250.00 matches ACCOUNT_RE:", bool(ACCOUNT_RE.search("Total 1,250.00")))
print("NHS_RE also matches 10-digit phone body 7700900123:", bool(NHS_RE.search("7700900123")))
print("random 10-digit passes NHS mod11 share:",
      round(sum(is_valid_nhs(f"{n:010d}") for n in range(1234500000, 1234510000)) / 10000, 3))
print("random 10-digit passes UTR check share:",
      round(sum(is_valid_utr(f"{n:010d}") for n in range(1234500000, 1234510000)) / 10000, 3))
print("FAILED GROUPS:", fails)
```

## Test output (24 Oct 2026, local run)
```
POSTCODE         PASS  detect-regex finds 6/6 valid in context
   valid  : CR2 6XH -> True; DN55 1PT -> True; M1 1AE -> True; B33 8TH -> True; W1A 0AX -> True; EC1A 1BB -> True
   invalid: QA1 1AA -> False; AJ1 1AA -> False; M1 1CA -> False; W1Z 0AX -> False; EC1Z 1BB -> False
NI_NUMBER        PASS  detect-regex finds 5/5 valid in context
   valid  : AB 12 34 56 C -> True; JG103759A -> True; CE 11 22 33 D -> True; OA123456B -> True; ZY 98 76 54 A -> True
   invalid: QQ 12 34 56 A -> False; AO123456A -> False; GB123456A -> False; AB123456E -> False; DA123456A -> False
SORT_CODE        PASS  detect-regex finds 4/5 valid in context
   valid  : 08-99-99 -> True; 10-79-99 -> True; 20-29-59 -> True; 87 14 27 -> True; 938611 -> True
   invalid: 12-34-5 -> False; 123-45-6 -> False; 12-34 56 -> False; AB-12-34 -> False; 12.34.56 -> False
BANK_ACCOUNT     PASS  detect-regex finds 5/5 valid in context
   valid  : 66374958 -> True; 88837491 -> True; 63748472 -> True; 46238510 -> True; 07806039 -> True
   invalid: 1234567 -> False; 123456789 -> False; 12345A78 -> False; 6637 495 -> False;  -> False
IBAN             PASS  detect-regex finds 5/5 valid in context
   valid  : GB82 WEST 1234 5698 7654 32 -> True; GB70NWBK08999966374958 -> True; GB76BARC20295963748472 -> True; GB88MIDL10799988837491 -> True; GB73LOYD87142746238510 -> True
   invalid: GB83 WEST 1234 5698 7654 32 -> False; GB82WEST1234569876543 -> False; GB82 W3ST 1234 5698 7654 32 -> False; DE89370400440532013000 -> False; GB82 WEST 1234 5698 7654 33 -> False
CARD             PASS  detect-regex finds 5/5 valid in context
   valid  : 4242 4242 4242 4242 -> True; 5555 5555 5555 4444 -> True; 2223 0031 2200 3222 -> True; 3782 822463 10005 -> True; 6011 1111 1111 1117 -> True
   invalid: 4242 4242 4242 4241 -> False; 1234 5678 1234 5678 -> False; 3782 822463 1000 -> False; 5555 5555 5555 4440 -> False; 9999 9999 9999 9995 -> False
PHONE            PASS  detect-regex finds 7/7 valid in context
   valid  : 07700 900123 -> True; +44 7700 900456 -> True; 020 7946 0321 -> True; 0113 496 0789 -> True; +44 (0)161 496 0123 -> True; 028 9649 6123 -> True; 01632 960456 -> True
   invalid: 07700 90012 -> False; 06123 456789 -> False; +1 415 555 0199 -> False; 0800 123 -> False; 07700 9001234 -> False
NHS_NUMBER       PASS  detect-regex finds 5/5 valid in context
   valid  : 999 054 8609 -> True; 999 000 0018 -> True; 999 000 0026 -> True; 999 000 0034 -> True; 999 000 0042 -> True
   invalid: 999 054 8608 -> False; 999 123 4567 -> False; 999 123 4566 -> False; 99912345678 -> False; 999 12A 4566 -> False
PASSPORT         PASS
   valid  : 123456789 -> True; 925665416 -> True; 533401372 -> True; 107185703 -> True; 000000001 -> True
   invalid: AB1234567 -> False; 12345678 -> False; 1234567890 -> False; 12345678A -> False; 1234 56789 -> False
DRIVING_LICENCE  PASS  detect-regex finds 5/5 valid in context
   valid  : MORGA753116SM9IJ -> True; SMITH801024J99AB -> True; JONES862217SA9XY -> True; LI999905302W99KZ -> True; MORGA753116SM9IJ 35 -> True
   invalid: SMITH813024J99AB -> False; SMITH802304J99AB -> False; 99999801024J99AB -> False; SM9TH801024J99AB -> False; SMITH80102J99AB -> False
VAT              PASS  detect-regex finds 5/5 valid in context
   valid  : GB999 9999 73 -> True; GB123456782 -> True; GB100012318 -> True; GBGD001 -> True; GBHA599 -> True
   invalid: GB999 9999 74 -> False; GB12345678 -> False; GBGD500 -> False; GBHA499 -> False; GB999 9999 7 -> False
COMPANY_NUMBER   PASS  detect-regex finds 5/5 valid in context
   valid  : 02050399 -> True; SC002180 -> True; OC301234 -> True; NI012345 -> True; 12674479 -> True
   invalid: SC12345 -> False; XX123456 -> False; 00000000 -> False; 1234567A -> False; SC1234567 -> False
UTR              PASS  detect-regex finds 5/5 valid in context
   valid  : 3282497350 -> True; 2234567890 -> True; 1123456789 -> True; 9987654321K -> True; K7555000111 -> True
   invalid: 3282497351 -> False; 328249735 -> False; 32824973500 -> False; K3282497350K -> False; ABCDE12345 -> False
PASSPORT ctx: 533401372
SORT bare ctx: 938611
normalise 9-digit Santander: ('090121', '23456789')
gov.uk verbatim fullmatch 'W1A 0AX': False
gov.uk verbatim fullmatch 'EC1A 1BB': True
gov.uk verbatim fullmatch 'M1 1AE': True
gov.uk verbatim fullmatch 'SW1A 1AA': True
gov.uk verbatim search inside 'XX99 SW1A 1AA': SW1A 1AA
gov.uk verbatim search 'GIR 0AA trailing junk': GIR 0AA
date 12-03-24 matches SORT_CODE_RE: True
company 12674479 matches ACCOUNT_RE: True
amount 1,250.00 matches ACCOUNT_RE: False
NHS_RE also matches 10-digit phone body 7700900123: True
random 10-digit passes NHS mod11 share: 0.091
random 10-digit passes UTR check share: 0.182
FAILED GROUPS: 0
```
