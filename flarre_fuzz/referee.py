"""Referee: DETERMINISTIC judge (no LLM). Invariants + comparison with the reference."""
from .reference import premium as ref

MAX_PREMIUM = 500 * 1.5 * 1.3 * 1.5   # highest legal premium under the spec

def _k(p): return (p["age"], p["claims"], p["safe_driver"], p["multi_policy"])

def check(profiles: list[dict], results: list[dict]) -> list[dict]:
    lookup = {_k(p): r["value"] for p, r in zip(profiles, results) if r["ok"]}   # O(1) neighbour lookups
    failures: list[dict] = []
    def fail(p, rule, actual, expected=None):
        failures.append({"input": p, "rule": rule, "actual": actual, "expected": expected})
    for p, r in zip(profiles, results):
        if not r["ok"]:
            fail(p, "crash_or_timeout", r["error"]); continue
        v, exp = r["value"], ref(**p)
        if v <= 0:                   fail(p, "premium_positive", v)
        if v > MAX_PREMIUM + 0.01:   fail(p, "max_premium_cap", v, MAX_PREMIUM)
        if abs(v - exp) > 0.005:     fail(p, "matches_reference", v, exp)
        nxt = lookup.get((p["age"], p["claims"] + 1, p["safe_driver"], p["multi_policy"]))
        if nxt is not None and nxt < v - 0.005:
            fail(p, "more_claims_never_cheaper", nxt, v)
        if p["safe_driver"] and p["multi_policy"]:
            base = lookup.get((p["age"], p["claims"], False, False))
            if base is not None and v < base * 0.8 - 0.01:
                fail(p, "discount_cap_20pct", v, round(base * 0.8, 2))
    return failures
