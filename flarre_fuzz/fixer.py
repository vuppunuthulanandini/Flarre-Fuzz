"""Fixer: LLM proposes a patch; output validated; clearly labelled fallback if the LLM is unavailable."""
import collections, os, re
from . import llm
from .schemas import FixProposal
from .bugs import GOOD_CODE

def propose(code: str, spec: str, failures: list[dict], clauses: dict | None = None,
            notes: list | None = None) -> FixProposal:
    note = (lambda m: notes.append(m)) if notes is not None else (lambda m: None)
    by_rule = collections.defaultdict(list)
    for f in failures: by_rule[f["rule"]].append(f)
    summary = "\n".join(f"- {r}: {len(fs)} failures, e.g. {fs[0]}\n  relevant spec clause: {(clauses or {}).get(r, 'n/a')}"
                        for r, fs in by_rule.items())
    try:
        text = llm.complete(
            f"Business rules:\n{spec}\n\nCode:\n{code}\n\nTest failures:\n{summary}\n\n"
            "Return the corrected full Python code in one ```python block, keeping the same "
            "function signature, then a short plain-English explanation of each bug, citing the "
            "rule number from the spec.")
        m = re.search(r"```python\s*(.*?)```", text, re.S)
        if not m: raise ValueError("no ```python block in the reply")
        return FixProposal(code=m.group(1).strip(), explanation=text[m.end():].strip() or "(no explanation returned)", source="llm")
    except Exception as e:   # includes pydantic ValidationError for malformed patches
        note(f"LLM Fixer unusable ({llm.describe(e)}).")
        if os.getenv("FLARRE_NO_FALLBACK"):
            return FixProposal(code=code, explanation=f"No patch available ({type(e).__name__}).", source="none")
        return FixProposal(code=GOOD_CODE, source="fallback",
                           explanation=f"LLM unavailable or unusable ({type(e).__name__}); stored reference patch used for demo.")
