"""Flarre-Fuzz: adversarial safety layer for AI-written insurance code."""
import os
from pathlib import Path

__version__ = "0.3.0"

def _load_env() -> None:
    """Load KEY=VALUE pairs from a .env file (project root or current dir). Never overrides real env vars."""
    for base in (Path.cwd(), Path(__file__).resolve().parent.parent):
        f = base / ".env"
        if f.is_file():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return

_load_env()
