import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def no_real_llm(monkeypatch):
    """Tests never call a real LLM (and never spend money), even if a key is configured."""
    monkeypatch.setenv("FLARRE_NO_LLM", "1")

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("FLARRE_DB", str(tmp_path / "test.db"))
    from flarre_fuzz.api import app
    return TestClient(app)
