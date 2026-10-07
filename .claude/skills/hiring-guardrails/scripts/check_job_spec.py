#!/usr/bin/env python3
"""Criteria gate: decide whether a job specification may be used for screening.

Usage:
    python check_job_spec.py job-spec.json --out spec-gate.json [--audit-log audit-log.jsonl]

Every hard requirement and scored criterion is screened against the governance proxy dictionary:
  PROTECTED or STRONG_PROXY        -> BLOCK (cannot be used, whatever the manager prefers)
  MODERATE_PROXY                   -> allowed only with a written job-related reason, else BLOCK
  JOB_RELATED                      -> PASS
  UNCLASSIFIED                     -> PASS with a note: relevance rests on the job analysis
Also blocked: experience caps above 60 months (an age proxy) and hard requirements without a legal,
operational or safety basis. A PASS records the spec's SHA-256, so the guardian can later prove that
decisions were made on exactly the cleared specification. Exit code 0 on PASS, 1 on BLOCK.
"""
import argparse
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, load_json, now_iso, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DICT = os.path.join(HERE, "..", "references", "proxy-dictionary.json")


def classify(text, d):
    low = text.lower()
    hits = [r for r in d["rules"] if re.search(r["pattern"], low)]
    if not hits:
        return "UNCLASSIFIED", None
    hits.sort(key=lambda r: d["priority"].index(r["category"]))
    return hits[0]["category"], hits[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()
    spec, d = load_json(args.spec), load_json(DICT)
    with open(args.spec, "rb") as fh:
        spec_hash = hashlib.sha256(fh.read()).hexdigest()

    items = [("hard_requirement", h["id"], h["requirement"], h.get("why", ""), h) for h in spec.get("hard_requirements", [])]
    items += [("scored_criterion", c["id"], c["criterion"], c.get("why", ""), c) for c in spec.get("scored_criteria", [])]
    findings, blocked = [], False
    for kind, iid, name, why, raw in items:
        cat, rule = classify(name, d)
        verdict, reason = "PASS", rule["rationale"] if rule else "No proxy rule matched; relevance rests on the job analysis."
        if cat in ("PROTECTED", "STRONG_PROXY"):
            verdict = "BLOCK"
        elif cat == "MODERATE_PROXY" and len(why.strip()) < 20:
            verdict, reason = "BLOCK", reason + " No job-related reason was given."
        if kind == "scored_criterion" and raw.get("evidence") == "resume_experience_months" and raw.get("cap_months", 0) > 60:
            verdict, reason = "BLOCK", f"Experience counted up to {raw['cap_months']} months becomes an age proxy; cap at 60 or less."
        if kind == "hard_requirement" and raw.get("basis") not in ("regulatory", "operational", "safety"):
            verdict, reason = "BLOCK", "A hard requirement needs a legal, operational or safety basis; otherwise score it."
        blocked |= verdict == "BLOCK"
        findings.append({"item": iid, "type": kind, "text": name, "category": cat, "rule": rule["id"] if rule else None,
                         "verdict": verdict, "reason": reason})

    out = {"requisition_id": spec.get("requisition_id"), "checked_at": now_iso(), "spec_sha256": spec_hash,
           "result": "BLOCK" if blocked else "PASS", "findings": findings,
           "declined_by_hiring_agent": spec.get("requests_declined", []),
           "next_step": "Remove or rewrite the blocked items and resubmit; escalate to the AI Approval Committee if the manager disputes."
                        if blocked else "Cleared for screening. Decisions are valid only on this exact specification (hash recorded)."}
    write_json(args.out, out)
    audit(args.audit_log, "check_job_spec.py", [args.spec], [args.out], {"result": out["result"],
          "blocked": [f["item"] for f in findings if f["verdict"] == "BLOCK"]})
    for f in findings:
        print(f"  {f['verdict']:5}  {f['item']}  {f['text']}  [{f['category']}]")
    print(f"Criteria gate: {out['result']}")
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
