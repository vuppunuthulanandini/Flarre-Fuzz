"""Spec-clause retrieval: TF-IDF cosine search over the rulebook, linking each failure to the
clause it violates. (Pure Python; swap in embeddings + a vector DB for large rulebooks.)"""
import math, re
from collections import Counter

def _tok(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower())

class ClauseIndex:
    def __init__(self, spec: str):
        self.clauses = [l.strip() for l in spec.splitlines() if re.match(r"\d+\.", l.strip())]
        docs = [Counter(_tok(c)) for c in self.clauses]
        df = Counter(t for d in docs for t in d)
        n = len(docs)
        self.idf = {t: math.log((1 + n) / (1 + df[t])) + 1 for t in df}
        self.vecs = [self._vec(d) for d in docs]

    def _vec(self, counts: Counter) -> dict:
        v = {t: c * self.idf.get(t, 0) for t, c in counts.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def search(self, query: str, k: int = 1) -> list[str]:
        q = self._vec(Counter(_tok(query)))
        scored = sorted(((sum(w * v.get(t, 0) for t, w in q.items()), c)
                         for v, c in zip(self.vecs, self.clauses)), reverse=True)
        return [c for s, c in scored[:k] if s > 0]

def query_for(f: dict) -> str:
    """Describe a failure in the spec's vocabulary so retrieval can find the clause."""
    p, rule = f["input"], f["rule"]
    if rule == "max_premium_cap":     return "each claim adds 10% capped at 50% in total"
    if rule == "discount_cap_20pct":  return "total discount is capped at 20%"
    if rule == "more_claims_never_cheaper": return "each claim adds 10% premium"
    try:   # a sub-1.00 gap is a rounding problem, whatever the inputs
        if abs(float(f["actual"]) - float(f["expected"])) < 1: return "final premium rounded to 2 decimal places"
    except (TypeError, ValueError):
        pass
    try:   # the size of the discrepancy often names the violated multiplier
        ratio = float(f["actual"]) / float(f["expected"])
        for m, hint in ((1.5, "driver age under 25 multiply by 1.5"), (1.3, "driver age 70 or over multiply by 1.3"),
                        (1.1, "drivers aged 25 to 29 inclusive with 2 or more claims surcharge"),
                        (1 / 1.1, "drivers aged 25 to 29 inclusive with 2 or more claims surcharge"),
                        (1 / 1.5, "driver age under 25 multiply by 1.5")):
            if abs(ratio - m) < 0.02: return hint
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    q = []
    if p["age"] < 25: q.append("driver age under 25 multiply")
    if p["age"] >= 70: q.append("driver age 70 or over multiply")
    if 25 <= p["age"] <= 29 and p["claims"] >= 2: q.append("drivers aged 25 to 29 inclusive with 2 or more claims surcharge")
    if p["claims"] > 0: q.append("each claim adds premium capped")
    if p["safe_driver"] or p["multi_policy"]: q.append("discount safe-driver multi-policy")
    try:
        if abs(float(f["actual"]) - float(f["expected"])) < 1: q.append("final premium rounded to 2 decimal places")
    except (TypeError, ValueError):
        pass
    return " ".join(q) or "base premium"
