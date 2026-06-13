# ISDS Navigator — Data Guide

A tool for exploring the UNCTAD Investor-State Dispute Settlement dataset with a focus on Spain's ECT solar energy arbitration wave.

---

## Source Data

**UNCTAD ISDS Navigator** (31 December 2023 release). 1,332 cases covering investor-state arbitrations filed from the 1980s through 2023. Original source: `UNCTAD-ISDS-Navigator-data-set-31December2023.xlsx` (headers on row 12, data from row 13).

---

## Database Tables

### `cases` — Core UNCTAD data (1,332 rows)

| Column | Description |
|---|---|
| `no` | Case number (PK). Matches UNCTAD's numbering. |
| `year` | Year the arbitration was filed. |
| `short_name` | Short case name, e.g. "NextEra v. Spain". |
| `full_name` | Full formal case name with all parties. |
| `applicable_iia` | Treaty under which the claim was brought (e.g. "Energy Charter Treaty"). |
| `arbitral_rules` | Rules governing the arbitration: ICSID, SCC, UNCITRAL, ICC, etc. |
| `institution` | Administering institution, if any. |
| `status` | UNCTAD outcome: "Decided in favour of investor", "Decided in favour of State", "Pending", "Discontinued for unknown reasons", "Settled". |
| `respondent_state` | State being sued. |
| `home_state` | Home country of the investor (may be semicolon-separated for multiple claimants). |
| `sector` | Economic sector. |
| `subsector` | Economic subsector. |
| `summary` | Short UNCTAD summary of the dispute. |
| `investment_details` | Description of the investment at issue. |
| `arbitrators` | Named arbitrators. |
| `decisions` | List of decisions and awards issued. |
| `individual_opinions` | Separate or dissenting opinions. |
| `amount_claimed_m` | Amount claimed, in millions. Format: `"256.00 EUR (279.50 USD)"` or `"Data not available"`. |
| `amount_awarded_m` | Amount awarded, same format. NULL if no award yet. |
| `breaches_alleged` | Treaty provisions alleged to have been breached. |
| `breaches_found` | Breaches actually found by the tribunal. |
| `followon_type` | Type of follow-on proceeding (annulment, recognition, etc.). |
| `followon_status` | Status of follow-on proceeding. |
| `followon_decisions` | Decisions in follow-on proceedings. |
| `followon_opinions` | Opinions in follow-on proceedings. |
| `annulment_committee` | Members of an ICSID annulment committee, if applicable. |
| `italaw_link` | URL(s) to the case page on italaw.com. |
| `background_sources` | Additional source URLs. |

**Full-text search index:** `cases_fts` (FTS5) covers `short_name`, `full_name`, `applicable_iia`, `respondent_state`, `home_state`, `sector`, `status`, `summary`.

---

### `research_notes` — Spain ECT case annotations (56 rows)

Manually researched annotations for all 56 Spain cases. Keyed by `case_no`.

| Column | Description |
|---|---|
| `case_no` | FK → `cases.no` |
| `enforcement_status` | Rolled-up enforcement status (see values below). |
| `enforcement_detail` | Narrative summary of enforcement activity. |
| `amount_paid_usd_m` | USD millions actually paid, if any. NULL if unpaid. |
| `context` | 2–4 sentences on the investment and why the dispute arose. |
| `claim_basis` | Legal theory: FET, expropriation, umbrella clause, etc. |
| `significance` | Why this case matters (precedent, amount, novel issue). |
| `updated_at` | ISO datetime of last update. |

**`enforcement_status` values:**

| Value | Meaning |
|---|---|
| `paid` | Award fully satisfied by Spain. |
| `enforced` | Court judgment granting enforcement exists; Spain has not yet paid. |
| `not_paid` | Investor won, no enforcement judgment yet. |
| `blocked` | Enforcement blocked (set-aside by seat court, or EU state aid obstacle). |
| `state_won` | Spain prevailed; no award against it. |
| `discontinued` | Case discontinued. |
| `pending` | Arbitration still ongoing. |

**Distribution across the 56 Spain cases (as of mid-2026):**
- `paid`: 1 (Maffezini)
- `enforced`: 5 (NextEra, RREEF, 9REN, Watkins, JGC — court judgments exist; Spain has not paid)
- `not_paid`: 20 (investor wins, no enforcement judgment)
- `blocked`: 2 (Novenergia — Swedish courts; Antin — EC state aid)
- `state_won`: 9
- `discontinued`: 4
- `pending`: 15

**Full-text search index:** `research_notes_fts` (FTS5, non-content-backed) covers `enforcement_keywords` (synonym expansion per status), `enforcement_detail`, `context`, `claim_basis`, `significance`.

---

### `enforcement_proceedings` — Per-forum enforcement events

Structured records of individual enforcement proceedings, one row per forum event.

| Column | Description |
|---|---|
| `id` | Row PK. |
| `case_no` | FK → `cases.no` |
| `forum` | Court or body: "US DC Circuit", "Australian Federal Court", "ICSID Annulment Committee", etc. |
| `result` | Outcome of this proceeding (see values below). |
| `date_text` | Approximate date, e.g. "Aug 2025", "Dec 2022". |
| `notes` | Narrative on this specific proceeding. |
| `updated_at` | ISO datetime of last update. |

**`result` values:**

| Value | Meaning |
|---|---|
| `enforced` | Court granted enforcement or issued judgment in investor's favour. |
| `dismissed` | Court rejected enforcement attempt. |
| `pending` | Proceeding ongoing. |
| `set_aside` | Award set aside by seat court (applies to non-ICSID awards). |
| `annulled` | ICSID annulment committee annulled the award. |
| `blocked` | Enforcement blocked on non-jurisdictional grounds (e.g. EU state aid). |
| `appeal_pending` | A prior ruling is under appeal. |

**Cases with proceedings seeded (as of mid-2026):**

| Case | Forum | Result |
|---|---|---|
| NextEra v. Spain | US DC Circuit | enforced (Aug 2024) |
| NextEra v. Spain | Australian Federal Court | enforced (Aug 2025), appeal pending |
| RREEF v. Spain | Australian Federal Court | enforced (Aug 2025), appeal pending |
| 9REN v. Spain | Australian Federal Court | enforced (Aug 2025), appeal pending |
| Watkins v. Spain | Australian Federal Court | enforced (Aug 2025), appeal pending |
| JGC v. Spain | US DC Circuit | enforced (Sept 2024) |
| Novenergia v. Spain | Svea Court of Appeal (Sweden) | set aside (Dec 2022) |
| Novenergia v. Spain | Swedish Supreme Court | set aside confirmed (Jul 2023) |
| Eiser v. Spain | ICSID Annulment Committee | annulled (2020) |
| Eiser v. Spain | ICSID Resubmission Tribunal | enforced (Oct 2025) |
| Eiser v. Spain | ICSID Annulment Committee (second) | pending (2025) |
| Antin v. Spain | European Commission | blocked — state aid (Mar 2025) |
| Maffezini v. Spain | Spain (voluntary compliance) | enforced (2000) |

---

## Using the App

### Browse tab

The default view, pre-filtered to Spain cases.

- **Search bar** — full-text search across case names, parties, treaties, sector, summary, and all research note fields.
- **Sidebar facets** — click any value to filter. Active filters are highlighted. Click again to clear. Enforcement status facet is at the top; UNCTAD facets (Year, Status, Respondent State, etc.) follow.
- **Table** — one row per case. Click any row to open the detail panel.
- **Detail panel** — shows all UNCTAD fields, a structured enforcement proceedings table (where available), and full research notes.

### SQL tab

Runs read-only SQL directly against the database (SELECT, WITH, EXPLAIN, PRAGMA only). Returns up to 2,000 rows.

The textarea pre-populates with the SQL equivalent of your current Browse view when you switch to this tab — use it as a starting point for custom queries.

**Useful tables to query:** `cases`, `research_notes`, `enforcement_proceedings`

**Example queries:**

```sql
-- Spain cases with investor wins, sorted by award size
SELECT c.no, c.short_name, c.year, c.amount_awarded_m, rn.enforcement_status
FROM cases c
LEFT JOIN research_notes rn ON c.no = rn.case_no
WHERE c.respondent_state = 'Spain'
  AND c.status = 'Decided in favour of investor'
ORDER BY c.amount_awarded_m DESC NULLS LAST;
```

```sql
-- All enforcement proceedings by forum
SELECT ep.forum, ep.result, ep.date_text, c.short_name
FROM enforcement_proceedings ep
JOIN cases c ON ep.case_no = c.no
ORDER BY ep.case_no, ep.id;
```

```sql
-- Summary of Spain enforcement status distribution
SELECT rn.enforcement_status, COUNT(*) AS n
FROM research_notes rn
JOIN cases c ON rn.case_no = c.no
WHERE c.respondent_state = 'Spain'
GROUP BY rn.enforcement_status
ORDER BY n DESC;
```

### Visualizations tab

Four charts driven by the current Browse filter set (or a named preset):

- **Case Outcomes** — doughnut of status distribution.
- **Investors' Countries of Origin** — horizontal bar of home states.
- **Cases Filed per Year** — stacked bar by outcome.
- **Compensation Claimed vs. Awarded** — scatter of USD claimed vs. awarded; hover for case name.

**Preset buttons:** *Current Browse* (mirrors active Browse filters), *Spain* (all 56 Spain cases), *All Cases* (all 1,332 cases).

Running a SQL query whose columns include `status` and `year` automatically updates the visualization data from the SQL result.

---

## Key Spain ECT Research Findings

Spain is the world's most-sued state under the Energy Charter Treaty. 50 of its 56 cases relate to the 2011–2022 solar and wind energy policy reversal, which removed subsidies that investors had relied on.

**Why Spain doesn't pay:**
- **Intra-EU enforcement:** EU courts refuse to enforce ECT awards against EU member states following *Achmea* (2018) and *Komstroy* (2021), citing incompatibility with EU law.
- **EC state aid shield (Antin, Mar 2025):** The European Commission ruled that paying the Antin award would constitute illegal state aid. Spain uses this as a systemic shield in all EU enforcement proceedings.

**Where enforcement has succeeded:**
- **Non-EU jurisdictions:** US courts (DC Circuit) and Australian courts have enforced ICSID awards. Non-EU investors (Japan: JGC; Switzerland: EBL/Schwab) face no Achmea obstacle.
- **Blasket strategy (Aug 2025):** Blasket Renewable Investments purchased the awards from NextEra, RREEF, 9REN, and Watkins and obtained Australian Federal Court enforcement (~€470M combined). Spain is appealing.
- **English High Court (Nov 2025):** Ruled ICSID awards are not assignable to third parties — contradicts the Australian approach. Creates legal uncertainty for Blasket-style transactions.

**Spain's ECT withdrawal:** Spain withdrew from the ECT effective 28 June 2025. A 20-year sunset clause protects investments existing before that date.

---

## Running Locally

```bash
# Start the server (default port 8123)
python3 serve.py

# Regenerate DB from Excel source
python3 convert.py && python3 migrate.py && python3 seed_research.py && python3 seed_proceedings.py

# Re-run migration + re-seed only (after schema changes)
python3 migrate.py && python3 seed_research.py && python3 seed_proceedings.py
```
