#!/usr/bin/env python3
"""Run the governed hiring demo end to end, exactly as the agents' skills instruct.

    python demo/run_demo.py

Act 1  Governance approves the hiring agent: approval review -> committee record (simulated) -> runtime policy.
Act 2  A hiring manager's request: spec v0 (with proxies) is BLOCKED by the guardian; spec v1 PASSES.
Act 3  The hiring agent screens 40 applications: parse and blind -> screen -> decide (within L2).
Act 4  The guardian checks the batch: per-decision checks, fairness monitor, audit sample, ledger.
Act 5  Fire drill: biased historical decisions trip the circuit breaker; the same batch re-runs at L1.
Writes a dashboard to demo/run/REQ-2026-0457/dashboard.md. Deterministic: --today is fixed.
"""
import csv
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SK = os.path.join(ROOT, ".claude", "skills")
GOV = os.path.join(ROOT, "governance")
RUN = os.path.join(ROOT, "demo", "run", "REQ-2026-0457")
DRILL = os.path.join(ROOT, "demo", "fire-drill")
TODAY = "2026-10-07"
sys.path.insert(0, os.path.join(ROOT, "evals"))
from harness import run_review  # noqa: E402


def sh(*args, ok=(0,)):
    p = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip()
    print("    " + out.replace("\n", "\n    "))
    if p.returncode not in ok:
        sys.exit(f"Step failed: {args[0]}")
    return p.returncode


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    for p in (os.path.join(GOV, "decision-ledger.jsonl"), os.path.join(GOV, "autonomy-state.json")):
        if os.path.exists(p):
            os.remove(p)
    shutil.rmtree(RUN, ignore_errors=True)
    shutil.rmtree(DRILL, ignore_errors=True)
    os.makedirs(RUN)
    log = os.path.join(RUN, "audit-log.jsonl")

    print("\nAct 0  Verify the skill library")
    sh("library/scripts/verify_library.py")

    print("\nAct 1  Governance approves the hiring agent (HR-AI-2026-021)")
    appr = os.path.join(GOV, "approval", "HR-AI-2026-021")
    d = run_review(appr, os.path.join(ROOT, "examples", "data", "deccan-v2-shadow-pilot.csv"), quiet=True)
    print(f"    Approval recommendation: {d['outcome_label']} (rule {d['rule_fired']}); memo at governance/approval/HR-AI-2026-021/decision-memo.md")
    sh(f"{SK}/approval-decision-memo/scripts/issue_runtime_policy.py", "--review-dir", appr,
       "--committee", os.path.join(appr, "committee-decision.json"), "--out", os.path.join(GOV, "runtime-policy.json"),
       "--audit-log", os.path.join(appr, "audit-log.jsonl"))

    print("\nAct 2  Job specification through the guardian's criteria gate")
    v0 = os.path.join(RUN, "spec-attempt-v0")
    os.makedirs(v0)
    shutil.copy(os.path.join(ROOT, "demo", "requisition", "job-spec-v0-as-requested.json"), os.path.join(v0, "job-spec.json"))
    sh(f"{SK}/job-requisition/scripts/validate_job_spec.py", os.path.join(v0, "job-spec.json"))
    sh(f"{SK}/hiring-guardrails/scripts/check_job_spec.py", os.path.join(v0, "job-spec.json"), "--out", os.path.join(v0, "spec-gate.json"),
       "--audit-log", log, ok=(1,))
    shutil.copy(os.path.join(ROOT, "demo", "requisition", "job-spec-v1.json"), os.path.join(RUN, "job-spec.json"))
    sh(f"{SK}/job-requisition/scripts/validate_job_spec.py", os.path.join(RUN, "job-spec.json"), "--audit-log", log)
    sh(f"{SK}/hiring-guardrails/scripts/check_job_spec.py", os.path.join(RUN, "job-spec.json"), "--out", os.path.join(RUN, "spec-gate.json"),
       "--audit-log", log)

    print("\nAct 3  Hiring agent screens 40 applications")
    shutil.copytree(os.path.join(ROOT, "demo", "applications", "resumes"), os.path.join(RUN, "resumes"))
    shutil.copy(os.path.join(ROOT, "demo", "applications", "applications.csv"), os.path.join(RUN, "applications.csv"))
    sh(f"{SK}/resume-screening/scripts/parse_resumes.py", os.path.join(RUN, "resumes"), "--out-full", os.path.join(RUN, "profiles.json"),
       "--out-blind", os.path.join(RUN, "blind-profiles.json"), "--audit-log", log)
    sh(f"{SK}/resume-screening/scripts/screen_candidates.py", "--spec", os.path.join(RUN, "job-spec.json"), "--blind",
       os.path.join(RUN, "blind-profiles.json"), "--applications", os.path.join(RUN, "applications.csv"),
       "--out", os.path.join(RUN, "screening.json"), "--audit-log", log)
    sh(f"{SK}/hiring-decisions/scripts/decide_candidates.py", "--spec", os.path.join(RUN, "job-spec.json"), "--screening",
       os.path.join(RUN, "screening.json"), "--policy", os.path.join(GOV, "runtime-policy.json"), "--state",
       os.path.join(GOV, "autonomy-state.json"), "--out", os.path.join(RUN, "decisions.json"), "--letters",
       os.path.join(RUN, "letters"), "--today", TODAY, "--audit-log", log)

    print("\nAct 4  Guardian checks the batch before anything takes effect")
    sh(f"{SK}/hiring-guardrails/scripts/guard_decisions.py", "--run", RUN, "--governance", GOV, "--today", TODAY, "--audit-log", log)
    sh(f"{SK}/hiring-guardrails/scripts/ledger.py", "verify", os.path.join(GOV, "decision-ledger.jsonl"))

    print("\nAct 5  Fire drill: does the circuit breaker work?")
    fire_drill()

    dashboard()
    print(f"\nDashboard: demo/run/REQ-2026-0457/dashboard.md")


def fire_drill():
    """Replay 1,200 historical decisions from the biased TalentSort v1 pilot through a copy of governance."""
    g, r = os.path.join(DRILL, "governance"), os.path.join(DRILL, "replayed-batch")
    os.makedirs(os.path.join(g, "audit-data"))
    os.makedirs(os.path.join(r, "letters"))
    shutil.copy(os.path.join(GOV, "runtime-policy.json"), g)
    shutil.copy(os.path.join(RUN, "job-spec.json"), r)
    shutil.copy(os.path.join(RUN, "spec-gate.json"), r)
    with open(os.path.join(ROOT, "examples", "data", "deccan-v1-shadow-pilot.csv"), newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(os.path.join(g, "audit-data", "self-declarations.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["candidate_id", "gender", "age_band", "home_region", "disability"])
        for x in rows:
            w.writerow([x["candidate_id"], x["gender"], x["age_band"], x["home_region"], x["disability"]])
    allowed = ["blind_profile.experience", "blind_profile.certifications", "blind_profile.skills",
               "application.can_work_at_branch", "application.assessment_score", "application.language_test"]
    json.dump({"requisition_id": "DRILL", "candidates": [{"candidate_id": x["candidate_id"], "status": "SCORED", "integrity_flags": [],
               "hard_requirements": [], "inputs_used": allowed} for x in rows]}, open(os.path.join(r, "screening.json"), "w"))
    json.dump({"requisition_id": "DRILL", "effective_level": "L2", "decisions": [
        {"candidate_id": x["candidate_id"], "action": "AUTO_ADVANCE" if x["ai_shortlisted"] == "1" else "PROPOSE_REJECT",
         "autonomous": x["ai_shortlisted"] == "1", "reasons": ["replayed historical decision"], "letter": None} for x in rows]},
        open(os.path.join(r, "decisions.json"), "w"))
    sh(f"{SK}/hiring-guardrails/scripts/guard_decisions.py", "--run", r, "--governance", g, "--today", TODAY)
    print("    Same 40-application batch, re-decided under the drill's autonomy state:")
    rr = os.path.join(DRILL, "batch-after-breaker")
    os.makedirs(rr)
    sh(f"{SK}/hiring-decisions/scripts/decide_candidates.py", "--spec", os.path.join(RUN, "job-spec.json"), "--screening",
       os.path.join(RUN, "screening.json"), "--policy", os.path.join(g, "runtime-policy.json"), "--state",
       os.path.join(g, "autonomy-state.json"), "--out", os.path.join(rr, "decisions.json"), "--letters", os.path.join(rr, "letters"),
       "--today", TODAY)


def dashboard():
    pol, gate0, gate = load(os.path.join(GOV, "runtime-policy.json")), load(os.path.join(RUN, "spec-attempt-v0", "spec-gate.json")), load(os.path.join(RUN, "spec-gate.json"))
    rep, blind = load(os.path.join(RUN, "guardian-report.json")), load(os.path.join(RUN, "blind-profiles.json"))
    drill = load(os.path.join(DRILL, "replayed-batch", "guardian-report.json"))
    after = load(os.path.join(DRILL, "batch-after-breaker", "decisions.json"))
    ds = rep["decisions"]
    act = {}
    for x in ds:
        act[x["action"]] = act.get(x["action"], 0) + 1
    st = rep["counts"]
    person = sum(1 for x in ds if x["guardian_status"] != "RELEASED")
    after_auto = sum(1 for x in after["decisions"] if x["autonomous"])
    L = ["# Governed hiring run: REQ-2026-0457", "",
         f"Relationship Manager (Investments & Insurance), Guwahati and Shillong · run date {TODAY} · all data synthetic", "",
         "## At a glance", "",
         "| Measure | Result |", "|---|---|",
         f"| Runtime policy | {pol['policy_id']}, signed by {pol['committee_signature']['signed_by']}, valid to {pol['valid_until']} |",
         f"| Autonomy | **{rep['effective_level']}** (granted {pol['autonomy_level']}; {pol['autonomy_cap_reason']}) |",
         f"| Job spec as the manager asked (v0) | **{gate0['result']}**: " + "; ".join(f"{f['item']} {f['text']}" for f in gate0['findings'] if f['verdict'] == 'BLOCK') + " |",
         f"| Job spec v1 | **{gate['result']}**, hash recorded ({gate['spec_sha256'][:12]}…) |",
         f"| Applications | {len(ds)} |",
         f"| Released to act autonomously | {st.get('RELEASED', 0)} ({act.get('AUTO_ADVANCE', 0)} invited to interview, {act.get('AUTO_REJECT_HARD_REQUIREMENT', 0)} rejected on a failed hard requirement) |",
         f"| Need a person | {person} (borderline, unclear, flagged, human-only, or judgment-based rejection proposals) |",
         f"| Blind audit sample | {len(rep['blind_audit_sample'])}: {', '.join(rep['blind_audit_sample'])} |",
         f"| Fairness monitor | **{rep['fairness_status']}** over {rep['fairness_records']} AI-handled decisions (too few per group yet; pooled monthly) |",
         f"| Integrity flags | " + ", ".join(b["candidate_id"] for b in blind["profiles"] if b["integrity_flags"]) + " (text aimed at the AI removed; a person reads it) |",
         f"| Ledger | {rep['ledger']['appended']} entries appended, chain verified |",
         f"| Fire drill | Replay of 1,200 biased historical decisions: fairness **{drill['fairness_status']}**, breaker set autonomy to **{drill['circuit_breaker']['autonomy_level']}**; the same 40-application batch then had **{after_auto}** autonomous actions (was {st.get('RELEASED', 0)}) |",
         "", "## Every candidate", "",
         "| Candidate | Proposed action | Guardian | Main reason |", "|---|---|---|---|"]
    for x in ds:
        reason = (x["reasons"][0] if x["reasons"] else "").replace("|", "/")
        if len(reason) > 150:
            reason = reason[:147] + "…"
        L.append(f"| {x['candidate_id']} | {x['action'].replace('_', ' ').lower()} | {x['guardian_status'].replace('_', ' ').lower()}"
                 f"{' · audit' if x['blind_audit_sample'] else ''} | {reason} |")
    L += ["", "Recruiters work from `human-queue.md`. Letters in `letters/` remain drafts until released by the guardian "
          "(autonomous outcomes) or confirmed by a recruiter (everything else)."]
    with open(os.path.join(RUN, "dashboard.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
