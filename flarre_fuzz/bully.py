"""Bully: attack-input generator. Layers: boundary, random, llm (all validated by Pydantic)."""
import itertools, json, random, re
from pydantic import ValidationError
from . import llm
from .schemas import Profile

AGES = [16, 17, 24, 25, 26, 69, 70, 71, 100]      # hand-picked: deliberately NOT spec-derived
CLAIMS = [0, 1, 5, 6, 7, 20]

def boundary_profiles() -> list[dict]:
    return [dict(age=a, claims=c, safe_driver=s, multi_policy=m)
            for a, c, s, m in itertools.product(AGES, CLAIMS, [False, True], [False, True])]

def random_profiles(n: int = 1000, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    return [dict(age=rng.randint(16, 100), claims=rng.randint(0, 20),
                 safe_driver=rng.random() < 0.5, multi_policy=rng.random() < 0.5) for _ in range(n)]

def llm_profiles(spec: str, n: int = 40, notes: list | None = None) -> list[dict]:
    """LLM invents rare cases from the spec. Invalid items are dropped; problems are reported in `notes`."""
    note = (lambda m: notes.append(m)) if notes is not None else (lambda m: None)
    try:
        text = llm.complete(
            f"Business rules:\n{spec}\n\nInvent {n} customer profiles most likely to expose bugs in "
            "code implementing these rules: probe every threshold in the rules and the values just "
            "inside and outside them, and unusual combinations. Reply ONLY with a JSON list of "
            "objects with keys age (int), claims (int), safe_driver (bool), multi_policy (bool).")
    except Exception as e:
        note(f"LLM Bully unavailable ({llm.describe(e)}); boundary and random layers still ran.")
        return []
    m = re.search(r"\[.*\]", text, re.S)
    try:
        items = json.loads(m.group(0)) if m else []
    except json.JSONDecodeError:
        items = []
    out = []
    for item in items:
        try:
            out.append(Profile.model_validate(item).model_dump())
        except ValidationError:
            continue
    note(f"LLM Bully: {len(out)} of {len(items)} proposed profiles were valid." if items
         else "LLM Bully returned no parseable JSON list.")
    return out

def generate(spec: str, layers=("boundary", "random"), notes: list | None = None) -> list[dict]:
    profiles: list[dict] = []
    if "boundary" in layers: profiles += boundary_profiles()
    if "random" in layers:   profiles += random_profiles()
    if "llm" in layers:      profiles += llm_profiles(spec, notes=notes)
    seen, unique = set(), []
    for p in profiles:
        k = tuple(p.values())
        if k not in seen:
            seen.add(k); unique.append(p)
    return unique
