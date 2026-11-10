"""Runs code under test in an isolated subprocess with a timeout.
NOTE: process isolation only. Do not expose to untrusted users; production needs containers."""
import json, subprocess, sys, tempfile
from pathlib import Path

_RUNNER = '''
import json, sys
sys.path.insert(0, ".")
from target_mod import premium
out = []
for p in json.load(sys.stdin):
    try:
        out.append({"ok": True, "value": premium(**p)})
    except Exception as e:
        out.append({"ok": False, "error": repr(e)})
print(json.dumps(out))
'''

def run(code: str, profiles: list[dict], timeout: int = 15) -> list[dict]:
    with tempfile.TemporaryDirectory() as d:
        Path(d, "target_mod.py").write_text(code)
        Path(d, "runner.py").write_text(_RUNNER)
        try:
            r = subprocess.run([sys.executable, "runner.py"], input=json.dumps(profiles),
                               capture_output=True, text=True, timeout=timeout, cwd=d)
        except subprocess.TimeoutExpired:
            return [{"ok": False, "error": "timeout"} for _ in profiles]
        if r.returncode != 0:
            return [{"ok": False, "error": r.stderr[-300:]} for _ in profiles]
        return json.loads(r.stdout)
