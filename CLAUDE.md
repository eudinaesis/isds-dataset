# ISDS Navigator — Claude Project Instructions

## What this project is

UNCTAD ISDS Navigator: a queryable UI over 1,332 investor-state dispute settlement cases (through Dec 2023), with a research focus on Spain's ECT solar energy arbitration wave (56 cases). Live at https://eudinaesis.github.io/isds-dataset/.

## Architecture

Pure static site — no server. `index.html` fetches `isds.db` (~3.4MB) as an ArrayBuffer on page load and creates an in-memory SQLite database via **sql.js** (SQLite compiled to WebAssembly, loaded from cdnjs CDN). All queries run client-side. FTS5 full-text search is included in sql.js.

**To run locally:** `python3 -m http.server 8123` → http://localhost:8123/
Must use a file server — `file://` is blocked by CORS on the DB fetch. `serve.py` has been deleted.

**Deployment:** GitHub Pages, auto-deploys on push to `main`.

## Key files

- `index.html` — single-page app (~1550 lines); JS starts around line 893
- `isds.db` — committed to git; regenerate with the pipeline below
- `GUIDE.md` — rendered in the Guide tab via marked.js
- `convert.py` — Excel → `isds.db` (run once; requires openpyxl)
- `migrate.py` — idempotent migrations: creates `research_notes` + `enforcement_proceedings` tables and their FTS5 virtual tables
- `seed_research.py` — seeds `research_notes` for all 56 Spain cases
- `seed_proceedings.py` — seeds `enforcement_proceedings` for Spain cases with court activity
- `SPAIN_ANALYSIS.md` — 18-question statistical breakdown (rendered via doc-viewer modal)
- `spain_cases_research.md` — case-by-case research notes (rendered via doc-viewer modal)
- `timeline_data.json` — external reference data (Spain solar PV capacity by year + dated policy/EU-law/ECT events) for the master timeline chart; NOT in `isds.db`, fetched separately
- `timeline-todo.md` — roadmap for the Spain-ECT-story timeline visualizations

**DB regeneration pipeline:**
```bash
python3 convert.py && python3 migrate.py && python3 seed_research.py && python3 seed_proceedings.py
```
After any schema change: run migrate.py + seed scripts, then commit `isds.db`.

## UI — 5 tabs

1. **Browse** — default view, pre-filtered to Spain. Sidebar facets (Enforcement at top). Table with Enforcement badge column. Click row → detail panel.
2. **SQL** — read-only queries (SELECT/WITH/EXPLAIN/PRAGMA). Pre-populates with current Browse query. Cmd+Enter runs.
3. **Visualizations** — 4 Chart.js charts. Scatter dots colored by enforcement_status. Tracks Browse or SQL result set.
4. **Guide** — renders GUIDE.md via marked.js. Local `.md` links open in a doc-viewer modal.
5. **Case Browser** — 56 Spain cases ordered by USD claim amount desc. Arrow-key navigation. Read-only.

## Database schema (key tables)

**`cases`** (1,332 rows): 28 columns from UNCTAD source. Amounts are TEXT like `"256.00 EUR (279.50 USD)"` or `"Data not available"`. FTS5 index on `cases_fts`.

**`research_notes`** (56 rows, Spain only): `case_no` PK/FK, `enforcement_status` (paid|enforced|not_paid|blocked|state_won|discontinued|pending), `enforcement_detail`, `amount_paid_usd_m`, `context`, `claim_basis`, `significance`, `updated_at`.

**`enforcement_proceedings`**: per-forum enforcement events. `case_no`, `forum`, `result` (enforced|dismissed|pending|set_aside|annulled|blocked|appeal_pending), `date_text`, `notes`.

## Key JS globals

- `db` — sql.js `SQL.Database` (null until DB loads)
- `state = { q, filters, page }` — browse state
- `dbAll(sql, params)` — parameterized query → array of objects
- `buildSearchSQL(q, filters)` — returns `{where, args}` for the standard WHERE clause
- `enforcementIndex` — `{case_no: enforcement_status}` from research_notes

## Rules

- **Do not touch `/scrape`** — it is a separate independent git project in the parent directory.
- The app is fully read-only — no POST endpoints, no write capability.
- `serve.py` is deleted. Never reference it.
- All monetary amounts in the DB are TEXT strings, not numbers. Parse USD with the `parseUSD()` helper in index.html.
