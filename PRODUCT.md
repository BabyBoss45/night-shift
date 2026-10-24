# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
React + Vite + TypeScript + Tailwind frontend (chosen by the team in the build request); FastAPI backend in `backend/` that calls models through Mubit.

## Users
Both, on one page with no separate modes:
- staff at firms that handle other people's documents (solicitors, letting agents, accountants, HR, insurers) who want to ask ChatGPT or Claude about a client's contract, bill or email without sending the client's personal data to the model provider;
- individuals who want an AI's help with their own tenancy agreement, bank letter or payslip without handing over their name, address or account numbers.

## Product Purpose
Veil hides personal data in any document before it reaches a frontier model. Drop or paste a document; Veil finds names, addresses, account and card numbers, NI numbers, dates of birth and organisation-specific references, shows them on the page, returns the same file with the values truly removed, and lets the user ask Claude or GPT about the document. The model only ever sees placeholders such as [PERSON_1]; the answer comes back with the real values put back locally. Success: zero personal values in what the provider receives, with answers as useful as on the original.

## Positioning
The redaction model is trained and hosted through Mubit and learns from each reviewer correction: a missed client code or an over-hidden word becomes a model update, so the model learns each firm's own identifiers. Rule-based redactors cannot learn from corrections, and a plain prompt to a frontier model sends the personal data to that provider first.

## Terminology
- Personal value types: PERSON, ADDRESS, POSTCODE, EMAIL, PHONE, BANK_ACCOUNT, SORT_CODE, IBAN, CARD, NI_NUMBER, DOB, ID_DOC, CUSTOM.
- Placeholder: `[PERSON_1]`; one placeholder per distinct value per document.
- "Pseudonymised", never "anonymised" or "compliant" (ICO: pseudonymised data is still personal data).

## Constraints
- Demo documents are synthetic (fake people); no real personal data in the demo.
- UI copy has no em dashes.
- Hackathon demo: must run live on a laptop, clear in under three minutes.
