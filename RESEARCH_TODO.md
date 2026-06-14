# ISDS Navigator — Research & Feature Roadmap

## Completed

- [x] `research_notes` table with enforcement status for all 56 Spain cases (paid/enforced/not_paid/blocked/state_won/discontinued/pending)
- [x] `enforcement_proceedings` table — structured per-forum rows (forum, result, date, notes)
- [x] Full-text search across research notes fields (enforcement_detail, context, claim_basis, significance)
- [x] Enforcement badge column in Browse table; Enforcement facet in sidebar
- [x] Case detail panel shows research notes + enforcement proceedings timeline
- [x] Visualizations tab — 4 Chart.js charts; tracks current Browse result set; preset buttons
- [x] Scatter chart dots colored by enforcement_status (one dataset per status)
- [x] SQL tab — read-only queries, pre-populates with current Browse query (Cmd+Enter)
- [x] Guide tab — renders GUIDE.md via marked.js
- [x] SPAIN_ANALYSIS.md — 18-question statistical breakdown
- [x] Mobile-friendly view — off-canvas filter drawer, card list, responsive charts
- [x] Case Browser tab — Spain cases one at a time (by claim amount desc), read-only notes panel, arrow-key navigation
- [x] Rearchitected as pure static site using sql.js (SQLite WASM) — no server, no Railway
- [x] Deployed to GitHub Pages (eudinaesis.github.io/isds-dataset)

---

## Backlog

- Per-case `sources` URLs field (add column to research_notes, display in detail panel + case browser)
- `key_facts` field per case (freeform paragraph; schema migration + re-seed)
- Scatter/bar chart highlight for non-EU vs EU investors (Achmea exposure dimension)
