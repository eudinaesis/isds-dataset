# Spain ECT Story — Timeline Visualization Roadmap

Goal: a set of visualizations that tell the whole "Spain ECT cases" story — connecting Spain's solar PV build-out, the policy/legal reversals, the wave of arbitration cases, and the enforcement/collection fight.

Status legend: [ ] todo · [~] in progress · [x] done

---

## Task 0 — External data (no DB; static JSON)  [x]

DONE: `timeline_data.json` written by research subagent — 19 capacity entries (2006-2024,
REE grid-connected PV-only) + 14 dated events (9 subsidy decrees, Achmea, Komstroy,
EC Antin state aid decision, Spain ECT exit notice, Spain ECT withdrawal effective).

## Task 1 — Case Lifecycle Flow (Sankey)  [x]

56 filed → decided / pending / discontinued → investor wins → enforcement split
(paid / enforced / not_paid / blocked). Pure `research_notes` data, no external dependency.
DONE: added `chartjs-chart-sankey` plugin + full-width "Spain ECT Case Lifecycle" card,
`buildLifecycleData()` / `renderLifecycle()` in index.html. JS syntax-checked.

## Task 2 — Master Timeline combo chart  [x]

Dual-axis, 2005–2026. DONE: mixed bar+line chart with custom `timelineEvents` plugin
for dashed colored vertical markers (incentive/cut/eu_law/ect). Left y: cases filed.
Right y: solar PV capacity (GW). Tooltip shows event labels for the hovered year.
`timelineData` fetched in parallel with DB on init. JS syntax-checked.

## Task 3 — Per-case Enforcement Timeline (Gantt-style)  [x]

DONE: scatter chart, x=parsed decimal year, y=case index (reversed). One dataset per
result type (enforced/set_aside/annulled/pending/appeal_pending/blocked). `parseEnfDate()`
handles "Aug 2025", "Sept 2024", "2020" TEXT dates. Hover tooltip shows case + forum +
date + result. JS syntax-checked.

---

## Sequencing

All tasks complete. `index.html` and `timeline_data.json` ready to commit.
