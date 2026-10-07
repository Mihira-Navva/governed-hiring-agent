#!/usr/bin/env python3
"""Validate the structure of a job specification before it goes to the guardian's criteria gate.

Usage:
    python validate_job_spec.py job-spec.json [--audit-log audit-log.jsonl]

Checks the things a hiring specialist would: weights add to 100; each hard requirement is a
checkable fact with a stated legal, operational or safety basis; each scored criterion uses a known
evidence type and says why it matters for the job; thresholds are sensible. This checks form. Whether
a criterion is fair is the guardian's gate, deliberately run by a different agent.
Exit code 0 if valid, 1 if not.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, load_json  # noqa: E402

HARD_EVIDENCE = {"resume_keywords", "application_answer"}
SCORED_EVIDENCE = {"application_field", "resume_experience_months", "resume_skills"}
BASES = {"regulatory", "operational", "safety"}


def validate(spec):
    errors, warnings = [], []
    for key in ("requisition_id", "role", "locations", "hard_requirements", "scored_criteria", "thresholds"):
        if not spec.get(key):
            errors.append(f"missing '{key}'")
    if not (spec.get("job_analysis") or {}).get("reference"):
        errors.append("no job analysis reference: every criterion must trace to one")

    for h in spec.get("hard_requirements", []):
        hid = h.get("id", "?")
        if h.get("basis") not in BASES:
            errors.append(f"{hid}: basis must be one of {sorted(BASES)} (a preference is not a hard requirement)")
        if not h.get("why"):
            errors.append(f"{hid}: say why this is required")
        if h.get("evidence") not in HARD_EVIDENCE:
            errors.append(f"{hid}: hard requirements must be checkable facts ({sorted(HARD_EVIDENCE)})")
        if h.get("evidence") == "resume_keywords" and not h.get("match_any"):
            errors.append(f"{hid}: needs 'match_any' phrases")
        if h.get("evidence") == "resume_keywords" and not h.get("ambiguous_if_any"):
            warnings.append(f"{hid}: no 'ambiguous_if_any' phrases; candidates 'pursuing' the requirement could be auto-rejected")
        if h.get("evidence") == "application_answer" and not (h.get("field") and h.get("pass_values")):
            errors.append(f"{hid}: needs 'field' and 'pass_values'")

    total = 0
    for c in spec.get("scored_criteria", []):
        cid = c.get("id", "?")
        total += c.get("weight", 0)
        if c.get("evidence") not in SCORED_EVIDENCE:
            errors.append(f"{cid}: unknown evidence type '{c.get('evidence')}'")
        if not c.get("why"):
            errors.append(f"{cid}: say how this predicts performance in the role")
        if c.get("evidence") == "resume_experience_months" and not (c.get("counts_if_any") and c.get("cap_months")):
            errors.append(f"{cid}: needs 'counts_if_any' and 'cap_months'")
        if c.get("evidence") == "resume_skills" and not (c.get("skills") and c.get("full_marks_at")):
            errors.append(f"{cid}: needs 'skills' and 'full_marks_at'")
        if c.get("evidence") == "application_field" and not c.get("field"):
            errors.append(f"{cid}: needs 'field'")
    if total != 100:
        errors.append(f"scored criterion weights add to {total}, not 100")

    t = spec.get("thresholds") or {}
    if not (0 < t.get("human_review_floor", 0) < t.get("advance", 0) <= 100):
        errors.append("thresholds must satisfy 0 < human_review_floor < advance <= 100")
    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--audit-log")
    args = ap.parse_args()
    spec = load_json(args.spec)
    errors, warnings = validate(spec)
    audit(args.audit_log, "validate_job_spec.py", [args.spec], [], {"valid": not errors, "errors": len(errors)})
    for e in errors:
        print(f"  ERROR    {e}")
    for w in warnings:
        print(f"  WARNING  {w}")
    print(f"Job spec {spec.get('requisition_id')}: {'VALID' if not errors else 'INVALID'} "
          f"({len(spec.get('hard_requirements', []))} hard requirements, {len(spec.get('scored_criteria', []))} scored criteria)")
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
