# Next Feature: Case-by-Case Research Notes for Spain Disputes

## Goal
Go through all 56 Spain cases one at a time, do external research on each
(news, ICSID documents, legal commentary, Italaw), and store structured notes
that the tool can display alongside the UNCTAD data.

## Workflow (per case)
1. Open the case detail panel in the app.
2. Follow the Italaw link (already in the DB) to read the case page.
3. Search for news coverage and legal commentary.
4. Write a short research note in the format below.
5. Commit after each batch of 5–10 cases.

## Data to collect per case
- `context`: 2–4 sentences on the investment and why the dispute arose
- `claim_basis`: what legal theory the investor relied on (FET, expropriation, etc.)
- `key_facts`: one-paragraph summary of key facts not in the UNCTAD summary
- `significance`: why this case matters (precedent, amount, novel issue)
- `sources`: list of URLs used for research

Priority order: cases with real award amounts first (42 cases already have USD
figures), then pending/unknown-amount cases.

## Implementation plan

### Step 1 — Add `research_notes` table to the DB
```sql
CREATE TABLE research_notes (
    case_no      INTEGER PRIMARY KEY REFERENCES cases(no),
    context      TEXT,
    claim_basis  TEXT,
    key_facts    TEXT,
    significance TEXT,
    sources      TEXT,   -- newline-separated URLs
    updated_at   TEXT    -- ISO datetime
);
```
Regenerate `isds.db` by running `convert.py` and then applying this migration,
OR add the table in a separate `migrate.py` that runs once and is idempotent.

### Step 2 — Seed script
Write `research.py` (or use the SQL tab) to INSERT notes one case at a time.
No UI needed for data entry — just SQL or a simple CLI.

### Step 3 — Expose notes in the API
- `GET /api/case?no=N` — extend existing response to include research notes
  fields if a row exists in `research_notes`.

### Step 4 — Display in case detail panel
- In `showDetail()`, render the research fields below the existing grid when
  they are non-empty.
- Add a subtle "Research" badge to the case row in the browse table when
  a note exists (requires a join or a pre-fetched set of annotated case IDs).

### Step 5 — Spain tab: highlight researched cases
- In the amounts scatter chart and by-year chart, mark dots/bars that have
  research notes with a darker outline or click handler that opens the detail.

## Cases to research (sorted by claimed amount, desc)
Run this query in the SQL tab to get the current list:

```sql
SELECT c.no, c.short_name, c.year, c.status,
       c.amount_claimed_m, c.amount_awarded_m,
       CASE WHEN r.case_no IS NOT NULL THEN 'done' ELSE '' END AS researched
FROM cases c
LEFT JOIN research_notes r ON c.no = r.case_no
WHERE c.respondent_state LIKE '%Spain%'
ORDER BY CAST(REPLACE(SUBSTR(c.amount_claimed_m, INSTR(c.amount_claimed_m,'(')+1),
              ' USD)', '') AS REAL) DESC NULLS LAST;
```
