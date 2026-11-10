import pytest
from flarre_fuzz import bully, referee, sandbox
from flarre_fuzz.bugs import GOOD_CODE, bug_variants
from flarre_fuzz.reference import premium
from flarre_fuzz.schemas import FixProposal, Profile
from pydantic import ValidationError
from pathlib import Path

SPEC = (Path(__file__).parent.parent / "flarre_fuzz/data/spec.txt").read_text()

def scan(code, layers=("boundary", "random")):
    P = bully.generate(SPEC, layers)
    return referee.check(P, sandbox.run(code, P))

def test_reference_known_values():
    assert premium(30, 0, False, False) == 500.0
    assert premium(20, 0, False, False) == 750.0              # under 25
    assert premium(75, 0, False, False) == 650.0              # 70+
    assert premium(27, 2, False, False) == 660.0              # 500*1.10*1.2
    assert premium(40, 9, True, True) == round(500 * 1.5 * 0.8, 2)  # both caps

def test_correct_code_has_no_false_alarms():
    assert scan(GOOD_CODE) == []

@pytest.mark.parametrize("bug", list(bug_variants()))
def test_each_planted_bug_is_detected(bug):
    assert len(scan(bug_variants()[bug])) > 0

def test_boundary_layer_alone_misses_mid_range_bug():
    """Documents a real weakness: hand-picked boundaries never probe age 29."""
    assert scan(bug_variants()["mid_range_boundary"], ("boundary",)) == []

def test_random_layer_catches_mid_range_bug():
    assert len(scan(bug_variants()["mid_range_boundary"], ("random",))) > 0

def test_sandbox_timeout_and_crash_are_reported():
    loop = "def premium(age, claims, safe_driver, multi_policy):\n    while True: pass\n"
    crash = "def premium(age, claims, safe_driver, multi_policy):\n    return 1/0\n"
    P = [dict(age=30, claims=0, safe_driver=False, multi_policy=False)]
    assert sandbox.run(loop, P, timeout=2)[0]["error"] == "timeout"
    assert not sandbox.run(crash, P)[0]["ok"]
    assert {f["rule"] for f in referee.check(P, sandbox.run(crash, P))} == {"crash_or_timeout"}

def test_profile_validation_rejects_bad_llm_output():
    for bad in [dict(age=5, claims=0, safe_driver=True, multi_policy=True),
                dict(age=30, claims=0, safe_driver="yes", multi_policy=True),
                dict(age=30, claims=0, safe_driver=True),
                dict(age=30, claims=0, safe_driver=True, multi_policy=True, extra=1)]:
        with pytest.raises(ValidationError):
            Profile.model_validate(bad)

def test_fix_proposal_rejects_broken_or_wrong_signature_code():
    for bad in ["def premium(:", "def other(x): return 1",
                "def premium(age, claims): return 1"]:
        with pytest.raises((ValidationError, SyntaxError)):
            FixProposal(code=bad, explanation="x", source="llm")

def test_minimizer_and_clause_retrieval_find_all_root_causes():
    from flarre_fuzz import orchestrator
    d = Path(__file__).parent.parent / "flarre_fuzz/data"
    r = orchestrator.run_scan((d / "target.py").read_text(), SPEC)
    clauses = {x["clause"].split(".")[0] for x in r["repros"]}
    assert clauses >= {"2", "4", "5", "6", "7"}          # every planted bug traced to its spec clause
    assert any(x["minimal"] == dict(age=25, claims=0, safe_driver=False, multi_policy=False) for x in r["repros"])
    assert r["remaining_failures"] == [] and r["coverage"]["failed"]

def test_clause_index_search():
    from flarre_fuzz.clauses import ClauseIndex
    idx = ClauseIndex(SPEC)
    assert idx.search("total discount capped at 20%")[0].startswith("6.")
