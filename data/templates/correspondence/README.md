# Correspondence templates

One file per source (`R1.txt` to `R5.txt`, Enron email threads). Each file has a header
(`# key: value` lines ending with `# ---`) and the source text in which every personal
value is a typed slot such as `{{PERSON:usf_counsel|last_comma_first}}` or
`{{EMAIL:usf_counsel|<last><f>@usfilter.com}}`. Slot keys are roles, never real names.
`[[opt:...]]` and `[[alt:a||b]]` blocks are added text variations, not source text.

The full slot syntax is in the docstring of `scripts/sources/correspondence/build.py`,
which renders 5 fills per template into `data/docs/correspondence.jsonl` and writes the
answer key from the slots. Provenance and checksums of the raw messages are in
`data/sources/correspondence/manifest.json`.

Changes to the original text, applied to all five threads:
- headers reduced to Date, From, To, Subject, Cc; display names taken from X-From/X-To;
  Message-ID, Bcc and the other X- headers dropped;
- names, emails, phones, signature and contact addresses replaced by slots; registered
  company addresses and a hotel's listing address are public business data and stay as text;
- R3: the Lotus Notes column table is flattened into plain header lines;
- R5: "?" encoding artefacts replaced by spaces;
- dates are `{{DATE:...}}` slots so each fill can move them by a calendar-preserving
  number of years and print them in US or UK style.

R6 to R11 have no templates yet: their hosts were blocked from the build sandbox
(see the manifest). Adding `R<n>.txt` here is enough for `build.py` to render it.
