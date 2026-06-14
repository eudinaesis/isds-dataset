# ISDS Navigator — Research & Feature Roadmap

## Completed

- [x] `research_notes` table with enforcement status for all 56 Spain cases (paid/enforced/not_paid/blocked/state_won/discontinued/pending)
- [x] `enforcement_proceedings` table — structured per-forum rows (forum, result, date, notes)
- [x] Full-text search across research notes fields (enforcement_detail, context, claim_basis, significance)
- [x] Enforcement badge column in Browse table
- [x] Case detail panel shows research notes fields
- [x] Visualizations tab tracks current Browse result set; preset buttons (Current Browse, Spain, All Cases)
- [x] SQL tab pre-populates with current Browse query
- [x] Guide tab with rendered GUIDE.md
- [x] SPAIN_ANALYSIS.md — 18-question statistical breakdown

---

## Next: Mobile-Friendly View (iPhone mini target)

iPhone SE / mini viewport: 375×667px. Current layout is desktop-only (sidebar + table, fixed header, multi-column grids).

### Changes needed

1. **Responsive layout** — sidebar collapses to a drawer (toggle button in header); table scrolls horizontally or switches to card list below ~600px
2. **Header** — stack title + search vertically on small screens; tab bar wraps or scrolls horizontally
3. **Browse tab** — card-per-row list instead of wide table on mobile; show short_name, year, status, enforcement badge
4. **Detail panel** — full-screen overlay on mobile (currently a right-side split panel)
5. **Visualizations tab** — charts resize to single-column stack; touch-friendly tap targets on chart elements
6. **SQL tab** — textarea stays full width; result table scrolls horizontally
7. **Facet sidebar** — off-canvas drawer triggered by a "Filters" button; overlay closes on tap-outside

### Implementation notes

- Add `@media (max-width: 600px)` breakpoints to the `<style>` block in `index.html`
- No JS framework needed — CSS flex/grid restructuring only, plus a small JS toggle for the filter drawer
- Test at 375px width (iPhone mini/SE) and 390px (iPhone 14)

---

## Backlog

- Per-case `sources` URLs field (currently not tracked in research_notes)
- Research workflow view: Spain cases one at a time for annotation/review
- Scatter/bar chart dots colored by enforcement_status
- `key_facts` field per case (planned in original schema but not yet added)
