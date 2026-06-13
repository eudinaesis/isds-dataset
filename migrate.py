#!/usr/bin/env python3
"""Idempotent migration: adds research_notes + research_notes_fts tables to isds.db."""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "isds.db"

# Human-readable keywords added per status so FTS matches natural-language queries
# e.g. "unpaid" → matches "not_paid" rows; "blocked" → matches "blocked" rows
ENF_KEYWORDS = {
    "paid":         "paid settled resolved",
    "enforced":     "enforced court judgment enforcement",
    "not_paid":     "not paid award unpaid outstanding",
    "blocked":      "blocked set aside refused annulled state aid",
    "state_won":    "state won prevailed dismissed rejected",
    "discontinued": "discontinued withdrawn abandoned",
    "pending":      "pending ongoing arbitration",
}


def run(con: sqlite3.Connection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS research_notes (
            case_no            INTEGER PRIMARY KEY REFERENCES cases(no),
            enforcement_status TEXT,
            enforcement_detail TEXT,
            amount_paid_usd_m  REAL,
            context            TEXT,
            claim_basis        TEXT,
            significance       TEXT,
            updated_at         TEXT
        )
    """)
    # Non-content-backed FTS so we can inject keyword synonyms per status
    con.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS research_notes_fts USING fts5(
            enforcement_keywords,
            enforcement_detail,
            context,
            claim_basis,
            significance
        )
    """)
    con.commit()


def rebuild_fts(con: sqlite3.Connection) -> int:
    """Re-populate research_notes_fts from current research_notes rows."""
    rows = con.execute(
        "SELECT case_no, enforcement_status, enforcement_detail, context, claim_basis, significance "
        "FROM research_notes"
    ).fetchall()
    con.execute("DELETE FROM research_notes_fts")
    con.executemany(
        "INSERT INTO research_notes_fts(rowid, enforcement_keywords, enforcement_detail, context, claim_basis, significance) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                r[0],
                ENF_KEYWORDS.get(r[1] or "", r[1] or ""),
                r[2] or "",
                r[3] or "",
                r[4] or "",
                r[5] or "",
            )
            for r in rows
        ],
    )
    con.commit()
    return len(rows)


if __name__ == "__main__":
    con = sqlite3.connect(DB)
    run(con)
    n = rebuild_fts(con)
    con.close()
    print(f"Migration complete — research_notes + FTS ready ({n} rows indexed).")
