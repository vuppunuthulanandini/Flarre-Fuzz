
"""LLM mechanism tests using a fake Gemini client.

These tests do not call a real Gemini API.
They test integration behaviour, not real-model performance.
"""

import json
import sys
import types
from pathlib import Path

import pytest

from flarre_fuzz import bully, fixer,llm, orchestrator, referee, sandbox
from flarre_fuzz.bugs import GOOD_CODE, bug_variants


SPEC = (
    Path(__file__).parent.parent
    / "flarre_fuzz"
    / "data"
    / "spec.txt"
).read_text(encoding="utf-8")


def fake_llm(monkeypatch, reply=None, error=None):
    class Models:
        def generate_content(self, **kwargs):
            if error:
                raise error

            return types.SimpleNamespace(text=reply)

    class Client:
        def __init__(self, **kwargs):
            self.models = Models()

    google = types.ModuleType("google")
    genai = types.ModuleType("google.genai")
    genai.Client = Client
    google.genai = genai

    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.genai", genai)

    monkeypatch.delenv("FLARRE_NO_LLM", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")


def test_bully_parses_fenced_json_and_drops_invalid(monkeypatch):
    good = dict(
        age=29,
        claims=2,
        safe_driver=False,
        multi_policy=False
    )

    bad = dict(
        age=3,
        claims=2,
        safe_driver=False,
        multi_policy=False
    )

    fake_llm(
        monkeypatch,
        "Here you go:\n```json\n"
        + json.dumps([good, bad, "junk"])
        + "\n```"
    )

    notes = []

    assert bully.llm_profiles(SPEC, notes=notes) == [good]
    assert "1 of 3" in notes[-1]


def test_llm_layer_catches_age29_bug_when_it_probes_threshold(monkeypatch):
    code = bug_variants()["mid_range_boundary"]

    boundary_profiles = bully.generate(SPEC, ("boundary",))

    assert referee.check(
        boundary_profiles,
        sandbox.run(code, boundary_profiles)
    ) == []

    fake_llm(
        monkeypatch,
        json.dumps([
            dict(
                age=29,
                claims=2,
                safe_driver=False,
                multi_policy=False
            )
        ])
    )

    profiles = bully.generate(SPEC, ("boundary", "llm"))

    assert len(
        referee.check(profiles, sandbox.run(code, profiles))
    ) == 1


def test_bully_reports_llm_errors(monkeypatch):
    fake_llm(
        monkeypatch,
        error=RuntimeError("API authentication failed")
    )

    notes = []

    assert bully.llm_profiles(SPEC, notes=notes) == []
    assert "unavailable" in notes[0]
    assert "authentication" in notes[0]


def test_fixer_accepts_good_llm_patch_and_reverifies(monkeypatch):
    fake_llm(
        monkeypatch,
        "```python\n"
        + GOOD_CODE
        + "\n```\nFixed rules 2, 4, 5, 6 and 7."
    )

    data = Path(__file__).parent.parent / "flarre_fuzz" / "data"

    result = orchestrator.run_scan(
        (data / "target.py").read_text(encoding="utf-8"),
        SPEC
    )

    assert result["patch_source"] == "llm"
    assert result["remaining_failures"] == []
    assert "Fixed rules" in result["explanation"]


def test_fixer_rejects_broken_llm_patch(monkeypatch):
    fake_llm(
        monkeypatch,
        "```python\ndef premium(:\n```"
    )

    notes = []

    proposal = fixer.propose(
        "x",
        SPEC,
        [{
            "rule": "matches_reference",
            "input": {},
            "actual": 1,
            "expected": 2
        }],
        notes=notes
    )

    assert proposal.source == "fallback"
    assert "unusable" in notes[0]
