"""Failure minimization (delta-debugging style): shrink a failing profile to the simplest one that
still breaks the same rule, so a reviewer sees 'age 25, no claims' instead of a messy case."""
from . import referee, sandbox
from .reference import premium as ref

PER_PROFILE = {"matches_reference", "max_premium_cap", "premium_positive", "crash_or_timeout"}

def _size(p): return (p["claims"] + p["safe_driver"] + p["multi_policy"], abs(p["age"] - 30))

def _neighbours(p: dict) -> list[dict]:
    out = []
    def add(**kw):
        q = {**p, **kw}
        if q != p and 16 <= q["age"] <= 100 and q["claims"] >= 0: out.append(q)
    add(claims=p["claims"] - 1); add(claims=0)
    add(safe_driver=False); add(multi_policy=False)
    for a in {(p["age"] + 30) // 2, p["age"] - 1, p["age"] + 1, 30}:
        add(age=a)
    return out

def _fails(code: str, cands: list[dict], rule: str) -> list[bool]:
    res = sandbox.run(code, cands)
    return [any(f["rule"] == rule for f in referee.check([c], [r])) for c, r in zip(cands, res)]

def shrink(code: str, failure: dict, max_rounds: int = 10) -> dict | None:
    rule, p = failure["rule"], dict(failure["input"])
    if rule not in PER_PROFILE: return None
    for _ in range(max_rounds):
        cands = _neighbours(p)
        better = [c for c, bad in zip(cands, _fails(code, cands, rule)) if bad and _size(c) < _size(p)]
        if not better: break
        p = min(better, key=_size)
    r = sandbox.run(code, [p])[0]
    return {"minimal": p, "actual": r.get("value", r.get("error")), "expected": ref(**p)}
