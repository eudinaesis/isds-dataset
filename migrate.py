#!/usr/bin/env python3
"""Idempotent migration: adds research_notes table to isds.db."""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "isds.db"

SQL = """
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
"""

if __name__ == "__main__":
    con = sqlite3.connect(DB)
    con.execute(SQL)
    con.commit()
    con.close()
    print("Migration complete — research_notes table ready.")
