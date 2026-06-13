#!/usr/bin/env python3
"""Seed enforcement_proceedings table with known Spain enforcement activity."""
import sqlite3
from pathlib import Path
import migrate

DB = Path(__file__).parent / "isds.db"

# (case_no, forum, result, date_text, notes)
# result enum: enforced | dismissed | pending | set_aside | annulled | blocked | appeal_pending
PROCEEDINGS = [
    # --- NextEra v. Spain (722) ---
    (
        722, "US DC Circuit", "enforced", "Aug 2024",
        "Confirmed US court jurisdiction to enforce ICSID awards against foreign sovereigns under FSIA. "
        "First major US enforcement win for an ECT-Spain claimant.",
    ),
    (
        722, "Australian Federal Court", "enforced", "Aug 2025",
        "Blasket Renewable Investments (assignee of NextEra award) obtained enforcement in Australia — "
        "part of Blasket [2025] FCA 1028 covering NextEra, RREEF, 9REN, Watkins (~€470M combined). "
        "Spain filed an appeal.",
    ),
    (
        722, "Australian Federal Court (Full Court)", "appeal_pending", "2025",
        "Spain appealing the Aug 2025 enforcement judgment.",
    ),

    # --- RREEF v. Spain (794) ---
    (
        794, "Australian Federal Court", "enforced", "Aug 2025",
        "Blasket [2025] FCA 1028 — enforcement granted for RREEF award as part of the group action. "
        "Spain filed an appeal.",
    ),
    (
        794, "Australian Federal Court (Full Court)", "appeal_pending", "2025",
        "Spain appealing the Aug 2025 enforcement judgment.",
    ),

    # --- 9REN Holding v. Spain (597) ---
    (
        597, "Australian Federal Court", "enforced", "Aug 2025",
        "Blasket [2025] FCA 1028 — enforcement granted as part of the group action. Spain filed an appeal.",
    ),
    (
        597, "Australian Federal Court (Full Court)", "appeal_pending", "2025",
        "Spain appealing the Aug 2025 enforcement judgment.",
    ),

    # --- Watkins and others v. Spain (678) ---
    (
        678, "Australian Federal Court", "enforced", "Aug 2025",
        "Blasket [2025] FCA 1028 — enforcement granted as part of the group action. Spain filed an appeal.",
    ),
    (
        678, "Australian Federal Court (Full Court)", "appeal_pending", "2025",
        "Spain appealing the Aug 2025 enforcement judgment.",
    ),

    # --- JGC v. Spain (639) ---
    (
        639, "US DC Circuit", "enforced", "Sept 2024",
        "Japanese claimant (non-EU investor, no Achmea obstacle). US court enforced the ICSID award "
        "following the NextEra DC Circuit precedent from Aug 2024.",
    ),

    # --- Novenergia v. Spain (656) ---
    (
        656, "Svea Court of Appeal (Sweden)", "set_aside", "Dec 2022",
        "SCC award set aside on grounds that the intra-EU application of the ECT was incompatible "
        "with EU law (Achmea/Komstroy). Non-ICSID awards seated in Sweden are vulnerable to annulment.",
    ),
    (
        656, "Swedish Supreme Court", "set_aside", "Jul 2023",
        "Swedish Supreme Court confirmed the Svea Court of Appeal's set-aside ruling. Award permanently annulled.",
    ),

    # --- Eiser and Energía Solar v. Spain (763) ---
    (
        763, "ICSID Annulment Committee", "annulled", "2020",
        "Original 2017 award (€128M) annulled due to arbitrator misconduct — one arbitrator had undisclosed "
        "ties to a party. First ICSID ECT-Spain award to be annulled.",
    ),
    (
        763, "ICSID Resubmission Tribunal", "enforced", "Oct 2025",
        "New award of ~€262M issued on resubmission. Spain filed a fresh annulment application.",
    ),
    (
        763, "ICSID Annulment Committee (second)", "pending", "2025",
        "Spain commenced a second ICSID annulment proceeding against the Oct 2025 resubmission award.",
    ),

    # --- Infrastructure Services / Antin v. Spain (774) ---
    (
        774, "European Commission", "blocked", "Mar 2025",
        "EC ruled that paying the Antin ECT award would constitute illegal state aid under EU law. "
        "Spain uses this decision as a shield to refuse payment in all EU proceedings. "
        "Award remains unpaid.",
    ),

    # --- Maffezini v. Spain (1318) ---
    (
        1318, "Spain (voluntary compliance)", "enforced", "2000",
        "Spain paid the Maffezini award voluntarily — the only Spain ECT case where the award was fully satisfied. "
        "Amount: ~USD 1.1M (a small early case predating the solar energy wave).",
    ),
]


def run():
    con = sqlite3.connect(DB)
    migrate.run(con)

    con.execute("DELETE FROM enforcement_proceedings")
    con.executemany(
        "INSERT INTO enforcement_proceedings(case_no, forum, result, date_text, notes) VALUES (?,?,?,?,?)",
        PROCEEDINGS,
    )
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM enforcement_proceedings").fetchone()[0]
    con.close()
    print(f"Seeded {n} enforcement_proceedings rows.")


if __name__ == "__main__":
    run()
