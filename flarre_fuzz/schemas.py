"""Pydantic models: every LLM output and API payload is validated before use."""
import ast
from typing import Any, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

Layer = Literal["boundary", "random", "llm"]

class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    age: int = Field(ge=16, le=100)
    claims: int = Field(ge=0, le=20)
    safe_driver: bool
    multi_policy: bool

class FixProposal(BaseModel):
    code: str
    explanation: str
    source: Literal["llm", "fallback", "none"]

    @field_validator("code")
    @classmethod
    def must_define_premium(cls, v: str) -> str:
        tree = ast.parse(v)  # SyntaxError surfaces as a validation failure
        fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "premium"]
        if not fn or [a.arg for a in fn[0].args.args] != ["age", "claims", "safe_driver", "multi_policy"]:
            raise ValueError("patch must define premium(age, claims, safe_driver, multi_policy)")
        return v

class ScanRequest(BaseModel):
    code: Optional[str] = Field(None, description="Code under test; defaults to the bundled buggy target")
    layers: list[Layer] = ["boundary", "random"]
    auto_fix: bool = True

class FailureOut(BaseModel):
    input: dict[str, Any]
    rule: str
    actual: Any
    expected: Any = None

class ReproOut(BaseModel):
    rule: str
    original: dict[str, Any]
    minimal: dict[str, Any]
    actual: Any
    expected: Any
    clause: str = ""

class ScanOut(BaseModel):
    id: int
    status: str
    layers: list[str]
    profiles: int
    initial_failures: int
    remaining_failures: int
    seconds: float
    failures_by_rule: dict[str, int]
    sample_failures: list[FailureOut]
    patched_code: str
    explanation: str
    patch_source: str
    coverage: dict[str, Any]
    repros: list[ReproOut]
    notes: list[str] = []

class DecisionIn(BaseModel):
    decision: Literal["approved", "rejected"]
    reviewer: str = "demo-reviewer"
    reason: str = ""
