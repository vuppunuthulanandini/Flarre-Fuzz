
"""Orchestrator: plain-Python controller: Bully -> Sandbox -> Referee -> Fixer -> re-verify."""
import time
from . import bully, fixer, minimize, referee, sandbox
from .clauses import ClauseIndex, query_for


def run_scan(code: str, spec: str, layers=("boundary", "random"), auto_fix=True, max_attempts=3) -> dict:
    t0 = time.time()
    notes: list[str] = []
    index = ClauseIndex(spec)
    profiles = bully.generate(spec, layers, notes)
    failures = referee.check(profiles, sandbox.run(code, profiles))
    initial, patched, explanation, source = failures, code, "", "none"

    # Minimal reproductions: first failure per rule, shrunk, with the spec clause it violates
    repros, seen, minimal_seen = [], set(), set()
    by_rule = {}
    for f in initial:
        by_rule.setdefault(f["rule"], []).append(f)

    for rule, fs in by_rule.items():
        seen.add(rule)
        sig = lambda p: (
            p["age"] < 25,
            25 <= p["age"] <= 29,
            p["age"] >= 70,
            p["claims"] >= 2,
            p["claims"] >= 6,
            p["safe_driver"],
            p["multi_policy"]
        )
        best = {}
        for f in fs:
            s = sig(f["input"])
            if s not in best or minimize._size(f["input"]) < minimize._size(best[s]["input"]):
                best[s] = f

        # OPTIMIZATION 1: Keep the 5 simplest examples per rule instead of 24
        pool = sorted(
            best.values(),
            key=lambda f: minimize._size(f["input"])
        )[:5]

        for f in pool:
            # OPTIMIZATION 2: Use 3 shrinking rounds instead of 8
            m = minimize.shrink(code, f, max_rounds=3)
            if not m:
                continue

            clause = (
                index.search(query_for({
                    "rule": rule,
                    "input": m["minimal"],
                    "actual": m["actual"],
                    "expected": m["expected"]
                })) or [""]
            )[0]

            if (rule, clause) in minimal_seen:
                continue

            minimal_seen.add((rule, clause))
            repros.append({
                "rule": rule,
                "original": f["input"],
                "clause": clause,
                **m
            })

    clauses = {
        r: (index.search(query_for(next(f for f in initial if f["rule"] == r))) or [""])[0]
        for r in seen
    }

    attempts = 0
    while auto_fix and failures and attempts < max_attempts:
        proposal = fixer.propose(patched, spec, failures, clauses, notes)
        patched, explanation, source = proposal.code, proposal.explanation, proposal.source

        # Full-suite re-verification is preserved
        failures = referee.check(profiles, sandbox.run(patched, profiles))
        attempts += 1

    coverage = {
        "tested": sorted({(p["age"], p["claims"]) for p in profiles}),
        "failed": sorted({
            (f["input"]["age"], f["input"]["claims"])
            for f in initial
        })
    }

    return {
        "profiles": len(profiles),
        "initial_failures": initial,
        "patched_code": patched,
        "explanation": explanation,
        "patch_source": source,
        "remaining_failures": failures,
        "repros": repros,
        "notes": notes,
        "clauses": clauses,
        "coverage": coverage,
        "seconds": round(time.time() - t0, 2)
    }
