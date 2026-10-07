"""Run the project's deterministic demo and test suite from the web.

The project's scripts write into the repository (demo/run, governance/, evals/). Serverless file
systems are read-only except /tmp, so each run works in a fresh temporary copy of the project,
then the copy is deleted. Nothing in the deployed code is ever modified.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_IGNORE = shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__", "node_modules", "public", "web", ".vercel", "*.pyc")


def make_workspace(prefix: str) -> Path:
    base = Path(tempfile.mkdtemp(prefix=prefix))
    ws = base / "project"
    shutil.copytree(ROOT, ws, ignore=_IGNORE)
    return ws


def _run(ws: Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run([sys.executable, *args], cwd=ws, capture_output=True, text=True, timeout=timeout, env=env)


def _read(path: Path, as_json: bool = False):
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return json.loads(text) if as_json else text


def run_demo() -> dict:
    ws = make_workspace("gha-demo-")
    try:
        p = _run(ws, "demo/run_demo.py")
        run = ws / "demo" / "run" / "REQ-2026-0457"
        drill = ws / "demo" / "fire-drill"
        letters_dir = run / "letters"
        letters = {f.stem: f.read_text(encoding="utf-8") for f in sorted(letters_dir.glob("*.md"))} if letters_dir.exists() else {}
        after = _read(drill / "batch-after-breaker" / "decisions.json", True) or {}
        return {
            "ok": p.returncode == 0,
            "stdout": p.stdout[-20000:],
            "stderr": p.stderr[-5000:],
            "dashboard_md": _read(run / "dashboard.md"),
            "human_queue_md": _read(run / "human-queue.md"),
            "guardian_report": _read(run / "guardian-report.json", True),
            "runtime_policy": _read(ws / "governance" / "runtime-policy.json", True),
            "spec_gate_v0": _read(run / "spec-attempt-v0" / "spec-gate.json", True),
            "spec_gate_v1": _read(run / "spec-gate.json", True),
            "manager_request_md": _read(ws / "demo" / "requisition" / "hiring-manager-request.md"),
            "drill_report": _read(drill / "replayed-batch" / "guardian-report.json", True),
            "after_breaker_autonomous": sum(1 for d in after.get("decisions", []) if d.get("autonomous")),
            "after_breaker_level": after.get("effective_level"),
            "approval_memo_md": _read(ws / "governance" / "approval" / "HR-AI-2026-021" / "decision-memo.md"),
            "letters": letters,
        }
    finally:
        shutil.rmtree(ws.parent, ignore_errors=True)


def run_tests() -> dict:
    ws = make_workspace("gha-tests-")
    try:
        p = _run(ws, "evals/run_evals.py", timeout=180)
        return {
            "ok": p.returncode == 0,
            "stdout": p.stdout[-30000:],
            "stderr": p.stderr[-5000:],
            "results_md": _read(ws / "evals" / "results.md"),
            "behaviour_evals_md": _read(ws / "evals" / "agent-behaviour-evals.md"),
        }
    finally:
        shutil.rmtree(ws.parent, ignore_errors=True)
