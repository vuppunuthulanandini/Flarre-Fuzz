"""Single-bug variants of the correct code, used by tests and the ablation study."""
from pathlib import Path

DATA = Path(__file__).parent / "data"
GOOD_CODE = (DATA / "fallback_patch.py").read_text()

_MUTATIONS = {
    "age_boundary":       ("if age < 25:", "if age <= 25:"),
    "surcharge_cap":      ("min(0.10 * claims, 0.50)", "0.10 * claims"),
    "discount_cap":       ("min(discount, 0.20)", "discount"),
    "truncation":         ("round(base, 2)", "int(base)"),
    "mid_range_boundary": ("25 <= age <= 29", "25 <= age < 29"),
}

def bug_variants() -> dict[str, str]:
    out = {}
    for name, (old, new) in _MUTATIONS.items():
        assert GOOD_CODE.count(old) == 1, f"mutation anchor for {name} not unique"
        out[name] = GOOD_CODE.replace(old, new)
    return out
