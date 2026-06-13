#!/usr/bin/env python3
"""Minimal HTTP server for the ISDS SQLite database. No dependencies beyond stdlib."""

import json
import os
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

    if q:
        where_clauses.append("cases_fts MATCH ?")
        args.append(q)

    for col, val in filters.items():
        if q:
            where_clauses.append(f"cases.{col} = ?")
        else:
            where_clauses.append(f"{col} = ?")
        args.append(val)

    if q:
        base = "FROM cases_fts JOIN cases ON cases.no = cases_fts.rowid"
    else:
        base = "FROM cases"

    where = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    count_sql = f"SELECT COUNT(*) {base} {where}"
    total = con.execute(count_sql, args).fetchone()[0]

    select = "SELECT cases.*" if q else "SELECT *"
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
        elif path == "/api/case":
            case_no = params.get("no")
            if not case_no:
                self._error(400, "missing no")
                return
            con = sqlite3.connect(DB)
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM cases WHERE no = ?", [case_no]).fetchone()
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
