#!/usr/bin/env python3
"""Run the deterministic part of a review: every skill script, in the agent's order.

Usage:
    python evals/harness.py <review_dir> [--pilot data.csv] [--fresh]

The agent itself does the reading and judgment (writing intake.json and reviewer-notes.json).
This harness replays the scripted steps so that evaluations and worked examples are
reproducible. It calls the skills exactly as their SKILL.md instructions do.
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SK = os.path.join(ROOT, ".claude", "skills")


def run(args, quiet=False):
    p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0 and "verify_library" not in args[0]:
        raise RuntimeError(f"{os.path.basename(args[0])} failed:\n{p.stdout}\n{p.stderr}")
    if not quiet:
        print("  " + p.stdout.strip().replace("\n", "\n  "))
    return p.returncode


def run_review(review_dir, pilot=None, fresh=True, quiet=False, verify=True):
    r = os.path.abspath(review_dir)
    log = os.path.join(r, "audit-log.jsonl")
    if fresh:
        for f in ("audit-log.jsonl", "completeness.json", "risk.json", "proxy-screen.json", "fairness.json",
                  "fairness-tables.md", "legal.json", "decision.json", "decision-memo.md", "library-check.json"):
            p = os.path.join(r, f)
            if os.path.exists(p):
                os.remove(p)
    intake = os.path.join(r, "intake.json")
    if verify:
        code = run([os.path.join(ROOT, "library", "scripts", "verify_library.py"), "--out", os.path.join(r, "library-check.json")], quiet)
        if code != 0:
            raise RuntimeError("Library verification failed: the agent must not proceed.")
    run([f"{SK}/use-case-intake/scripts/check_completeness.py", intake, "--out", f"{r}/completeness.json", "--audit-log", log], quiet)
    run([f"{SK}/risk-tiering/scripts/risk_tier.py", intake, "--out", f"{r}/risk.json", "--audit-log", log], quiet)
    run([f"{SK}/fairness-bias-review/scripts/proxy_screen.py", intake, "--out", f"{r}/proxy-screen.json", "--audit-log", log], quiet)
    if pilot:
        with open(intake, encoding="utf-8") as fh:
            annual = json.load(fh)["use_case"].get("annual_applications")
        cmd = [f"{SK}/fairness-bias-review/scripts/adverse_impact.py", pilot, "--outcome", "ai_shortlisted",
               "--qualified", "expert_qualified", "--groups", "gender,age_band,home_region,disability",
               "--intersect", "gender:age_band", "--out", f"{r}/fairness.json", "--md", f"{r}/fairness-tables.md",
               "--audit-log", log]
        if annual:
            cmd += ["--annual", str(annual)]
        run(cmd, quiet)
    legal = [f"{SK}/legal-privacy-review/scripts/obligations.py", intake, "--out", f"{r}/legal.json", "--audit-log", log]
    if pilot:
        legal += ["--fairness", f"{r}/fairness.json"]
    run(legal, quiet)
    run([f"{SK}/approval-decision-memo/scripts/decide.py", "--review-dir", r, "--audit-log", log], quiet)
    if os.path.exists(os.path.join(r, "reviewer-notes.json")):
        run([f"{SK}/approval-decision-memo/scripts/render_memo.py", "--review-dir", r, "--audit-log", log], quiet)
    with open(os.path.join(r, "decision.json"), encoding="utf-8") as fh:
        return json.load(fh)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("review_dir")
    ap.add_argument("--pilot")
    args = ap.parse_args()
    d = run_review(args.review_dir, args.pilot)
    print(f"Outcome: {d['outcome_label']} (rule {d['rule_fired']})")
