"""FastAPI backend. Run: uvicorn flarre_fuzz.api:app --reload"""
from pathlib import Path
import json, os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from . import ablation, db, llm, orchestrator
from .schemas import DecisionIn, ScanOut, ScanRequest

DATA = Path(__file__).parent / "data"
SPEC = (DATA / "spec.txt").read_text()
app = FastAPI(title="Flarre-Fuzz API", version="0.2.0",
              description="Adversarial safety layer for AI-written insurance code. Local demo: "
                          "the sandbox is process isolation only; do not expose publicly.")

def _out(sid: int) -> ScanOut:
    got = db.get_scan(sid)
    if not got: raise HTTPException(404, "scan not found")
    s, by_rule, samples = got
    return ScanOut(id=s["id"], status=s["status"], layers=s["layers"].split(","), profiles=s["profiles"],
                   initial_failures=s["initial_failures"], remaining_failures=s["remaining_failures"],
                   seconds=s["seconds"], failures_by_rule=by_rule, sample_failures=samples,
                   patched_code=s["patched_code"], explanation=s["explanation"], patch_source=s["patch_source"],
                   coverage=json.loads(s["coverage"]), repros=json.loads(s["repros"]), notes=json.loads(s["notes"] or "[]"))

@app.get("/health")
def health(): return {"status": "ok", "llm_configured": llm.configured(), "model": llm.model()}

_ablation_cache: dict = {}

@app.get("/ablation")
def get_ablation():
    if not _ablation_cache: _ablation_cache.update(ablation.matrix())
    return _ablation_cache

@app.get("/", include_in_schema=False)
def index(): return FileResponse(Path(__file__).parent / "static" / "index.html")

@app.get("/target")
def target(): return {"code": (DATA / "target.py").read_text(), "spec": SPEC}

@app.post("/scans", response_model=ScanOut, status_code=201)
def create_scan(req: ScanRequest):
    code = req.code or (DATA / "target.py").read_text()
    res = orchestrator.run_scan(code, SPEC, layers=tuple(req.layers), auto_fix=req.auto_fix)
    return _out(db.save_scan(req.layers, code, res))

@app.get("/scans/{scan_id}", response_model=ScanOut)
def read_scan(scan_id: int): return _out(scan_id)

@app.post("/scans/{scan_id}/decision")
def decide(scan_id: int, body: DecisionIn):
    if not db.get_scan(scan_id, sample=0): raise HTTPException(404, "scan not found")
    if not db.decide(scan_id, body.decision, body.reviewer, body.reason):
        raise HTTPException(409, "scan already decided")
    return {"scan_id": scan_id, "status": body.decision}

@app.get("/audit")
def audit_log(limit: int = 100): return db.list_audit(limit)
