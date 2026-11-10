"""SQLite persistence: scans, failures, audit trail."""
import json, os, sqlite3, time
from contextlib import contextmanager

def _path() -> str:
    return os.getenv("FLARRE_DB", "flarre_fuzz.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS scans(
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, layers TEXT, profiles INTEGER,
  initial_failures INTEGER, remaining_failures INTEGER, seconds REAL,
  original_code TEXT, patched_code TEXT, explanation TEXT, patch_source TEXT, coverage TEXT, repros TEXT, notes TEXT,
  status TEXT DEFAULT 'pending_review');
CREATE TABLE IF NOT EXISTS failures(
  id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, rule TEXT, input TEXT, actual TEXT, expected TEXT);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, scan_id INTEGER, event TEXT, detail TEXT);
CREATE INDEX IF NOT EXISTS idx_fail_scan ON failures(scan_id);
"""

@contextmanager
def conn():
    c = sqlite3.connect(_path())
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    try:
        yield c
        c.commit()
    finally:
        c.close()

def _now() -> str: return time.strftime("%Y-%m-%d %H:%M:%S")

def audit(c, scan_id, event, **detail):
    c.execute("INSERT INTO audit(ts,scan_id,event,detail) VALUES(?,?,?,?)",
              (_now(), scan_id, event, json.dumps(detail)))

def save_scan(layers, original_code, res: dict) -> int:
    with conn() as c:
        cur = c.execute(
            "INSERT INTO scans(created_at,layers,profiles,initial_failures,remaining_failures,seconds,"
            "original_code,patched_code,explanation,patch_source,coverage,repros,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (_now(), ",".join(layers), res["profiles"], len(res["initial_failures"]),
             len(res["remaining_failures"]), res["seconds"], original_code, res["patched_code"],
             res["explanation"], res["patch_source"], json.dumps(res["coverage"]), json.dumps(res["repros"]), json.dumps(res["notes"])))
        sid = cur.lastrowid
        c.executemany("INSERT INTO failures(scan_id,rule,input,actual,expected) VALUES(?,?,?,?,?)",
                      [(sid, f["rule"], json.dumps(f["input"]), json.dumps(f["actual"]),
                        json.dumps(f["expected"])) for f in res["initial_failures"]])
        audit(c, sid, "scan_completed", profiles=res["profiles"], failures=len(res["initial_failures"]),
              remaining_after_fix=len(res["remaining_failures"]), patch_source=res["patch_source"])
        return sid

def get_scan(sid: int, sample: int = 50):
    with conn() as c:
        s = c.execute("SELECT * FROM scans WHERE id=?", (sid,)).fetchone()
        if not s: return None
        by_rule = {r["rule"]: r["n"] for r in c.execute(
            "SELECT rule, COUNT(*) n FROM failures WHERE scan_id=? GROUP BY rule ORDER BY n DESC", (sid,))}
        rows = c.execute("SELECT * FROM failures WHERE scan_id=? LIMIT ?", (sid, sample)).fetchall()
        samples = [{"input": json.loads(r["input"]), "rule": r["rule"],
                    "actual": json.loads(r["actual"]), "expected": json.loads(r["expected"])} for r in rows]
        return dict(s), by_rule, samples

def decide(sid: int, decision: str, reviewer: str, reason: str) -> bool:
    with conn() as c:
        cur = c.execute("UPDATE scans SET status=? WHERE id=? AND status='pending_review'", (decision, sid))
        if cur.rowcount == 0: return False
        audit(c, sid, "human_decision", decision=decision, reviewer=reviewer, reason=reason)
        return True

def list_audit(limit: int = 100):
    with conn() as c:
        return [{**dict(r), "detail": json.loads(r["detail"])} for r in
                c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,))]
