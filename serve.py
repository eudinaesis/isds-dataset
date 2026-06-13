#!/usr/bin/env python3
"""Minimal HTTP server for the ISDS SQLite database. No dependencies beyond stdlib."""

import json
import os
import re
import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DB = Path(__file__).parent / "isds.db"
HTML = Path(__file__).parent / "index.html"
PORT = int(os.environ.get("PORT", 8123))

SEARCHABLE_COLS = [
    "short_name", "full_name", "applicable_iia",
    "respondent_state", "home_state", "sector", "status", "summary",
]

FILTER_COLS = [
    "year", "respondent_state", "home_state", "sector", "status",
    "arbitral_rules", "institution",
]


def query(params: dict) -> dict:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    q = params.get("q", "").strip()
    page = max(1, int(params.get("page", 1)))
    per_page = 50
    offset = (page - 1) * per_page
    filters = {k: params[k] for k in FILTER_COLS if params.get(k)}

    where_clauses = []
    args = []

    # Always join research_notes; FTS handled via subquery so base never changes
    base = "FROM cases LEFT JOIN research_notes rn ON cases.no = rn.case_no"

    if q:
        where_clauses.append(
            "(cases.no IN (SELECT rowid FROM cases_fts WHERE cases_fts MATCH ?) "
            "OR cases.no IN (SELECT rowid FROM research_notes_fts WHERE research_notes_fts MATCH ?))"
        )
        args.extend([q, q])

    for col, val in filters.items():
        where_clauses.append(f"cases.{col} = ?")
        args.append(val)

    # Handle enforcement_status filter (lives in research_notes, not cases)
    enforcement_filter = params.get("enforcement_status", "").strip()
    if enforcement_filter:
        where_clauses.append("rn.enforcement_status = ?")
        args.append(enforcement_filter)

    where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    select = "SELECT cases.*, rn.enforcement_status, rn.context, rn.claim_basis"
    all_rows = params.get("all") == "1"

    if all_rows:
        rows_sql = f"{select} {base} {where} ORDER BY cases.year DESC, cases.no ASC"
        rows = [dict(r) for r in con.execute(rows_sql, args)]
        total = len(rows)
    else:
        count_sql = f"SELECT COUNT(*) {base} {where}"
        total = con.execute(count_sql, args).fetchone()[0]
        rows_sql = f"{select} {base} {where} ORDER BY cases.year DESC, cases.no ASC LIMIT ? OFFSET ?"
        rows = [dict(r) for r in con.execute(rows_sql, args + [per_page, offset])]
    con.close()

    return {"total": total, "page": page, "per_page": per_page, "rows": rows}


def facets() -> dict:
    con = sqlite3.connect(DB)
    result = {}
    for col in FILTER_COLS:
        rows = con.execute(
            f"SELECT {col}, COUNT(*) AS n FROM cases WHERE {col} IS NOT NULL AND {col} != '' "
            f"GROUP BY {col} ORDER BY n DESC LIMIT 100"
        ).fetchall()
        result[col] = [{"value": r[0], "count": r[1]} for r in rows]
    con.close()
    return result


def run_sql(sql: str) -> dict:
    sql = sql.strip()
    # Block anything that isn't a read
    first = sql.upper().split()[0] if sql.split() else ""
    if first not in ("SELECT", "WITH", "EXPLAIN", "PRAGMA"):
        return {"error": "Only SELECT / WITH / EXPLAIN queries are allowed"}
    try:
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row
        cur = con.execute(sql)
        rows = cur.fetchmany(2000)
        cols = [d[0] for d in cur.description] if cur.description else []
        con.close()
        return {"columns": cols, "rows": [list(r) for r in rows], "count": len(rows)}
    except sqlite3.Error as e:
        return {"error": str(e)}


def research_index() -> dict:
    """Return enforcement_status for every case that has research notes."""
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT case_no, enforcement_status FROM research_notes"
    ).fetchall()
    con.close()
    return {str(r[0]): r[1] for r in rows}


def spain_data() -> dict:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT no, short_name, year, status, home_state, amount_claimed_m, amount_awarded_m "
        "FROM cases WHERE respondent_state LIKE '%Spain%'"
    ).fetchall()]
    con.close()

    outcome_counts: dict[str, int] = {}
    for r in rows:
        s = r["status"] or "Unknown"
        outcome_counts[s] = outcome_counts.get(s, 0) + 1
    outcomes = [{"label": k, "count": v}
                for k, v in sorted(outcome_counts.items(), key=lambda x: -x[1])]

    state_counts: dict[str, int] = {}
    for r in rows:
        parts = [p.strip() for p in re.split(r"[;\n]+", r["home_state"] or "") if p.strip()]
        for p in parts:
            state_counts[p] = state_counts.get(p, 0) + 1
    home_states = sorted(
        [{"country": k, "count": v} for k, v in state_counts.items()],
        key=lambda x: -x["count"],
    )

    OUTCOME_KEY = {
        "Decided in favour of investor": "investor",
        "Decided in favour of State": "state",
        "Pending": "pending",
        "Discontinued for unknown reasons": "discontinued",
    }
    years_map: dict[int, dict] = {}
    for r in rows:
        yr = r["year"]
        if yr not in years_map:
            years_map[yr] = {"year": yr, "investor": 0, "state": 0, "pending": 0, "discontinued": 0}
        key = OUTCOME_KEY.get(r["status"] or "", "investor")
        years_map[yr][key] += 1
    by_year = sorted(years_map.values(), key=lambda x: x["year"])

    def parse_usd(s: str | None) -> float | None:
        if not s or "Data not available" in s:
            return None
        m = re.search(r'\((\d+(?:\.\d+)?)\s+USD\)', s)
        if m:
            return float(m.group(1))
        m = re.search(r'(\d+(?:\.\d+)?)\s+USD', s)
        if m:
            return float(m.group(1))
        return None

    amounts = []
    for r in rows:
        claimed = parse_usd(r["amount_claimed_m"])
        if claimed is None:
            continue
        amounts.append({
            "no": r["no"],
            "name": r["short_name"],
            "claimed_usd": claimed,
            "awarded_usd": parse_usd(r["amount_awarded_m"]),
            "status": r["status"],
            "year": r["year"],
        })
    amounts.sort(key=lambda x: -(x["claimed_usd"] or 0))

    return {
        "total": len(rows),
        "outcomes": outcomes,
        "home_states": home_states,
        "by_year": by_year,
        "amounts": amounts,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/sql":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            self._json(run_sql(body.get("sql", "")))
        else:
            self._error(404, "not found")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = dict(urllib.parse.parse_qsl(parsed.query))

        if path == "/" or path == "/index.html":
            self._serve_file(HTML, "text/html")
        elif path == "/api/search":
            self._json(query(params))
        elif path == "/api/facets":
            self._json(facets())
        elif path == "/api/spain":
            self._json(spain_data())
        elif path == "/api/research":
            self._json(research_index())
        elif path == "/api/case":
            case_no = params.get("no")
            if not case_no:
                self._error(400, "missing no")
                return
            con = sqlite3.connect(DB)
            con.row_factory = sqlite3.Row
            row = con.execute(
                """SELECT cases.*,
                          rn.enforcement_status, rn.enforcement_detail,
                          rn.amount_paid_usd_m, rn.context,
                          rn.claim_basis, rn.significance, rn.updated_at AS research_updated_at
                   FROM cases
                   LEFT JOIN research_notes rn ON cases.no = rn.case_no
                   WHERE cases.no = ?""",
                [case_no],
            ).fetchone()
            con.close()
            if row:
                self._json(dict(row))
            else:
                self._error(404, "not found")
        else:
            self._error(404, "not found")

    def _serve_file(self, path: Path, content_type: str):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj):
        data = json.dumps(obj, default=str).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def _error(self, code: int, msg: str):
        data = json.dumps({"error": msg}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    if not DB.exists():
        print("isds.db not found — run convert.py first")
        raise SystemExit(1)
    print(f"Serving at http://localhost:{PORT}/")
    HTTPServer(("", PORT), Handler).serve_forever()
