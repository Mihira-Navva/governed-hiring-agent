#!/usr/bin/env python3
"""Issue the runtime policy that a governed AI system must obey, from the committee's signed decision.

Usage:
    python issue_runtime_policy.py --review-dir <approval review> --committee committee-decision.json \
        --out governance/runtime-policy.json [--audit-log audit-log.jsonl]

This is where the approval layer hands control to the runtime layer. The policy is issued only if a
named committee chair has signed an approving decision. The autonomy level granted is capped by
evidence, not by the request:
  * no conditions precedent evidenced yet          -> at most L1 (assist only)
  * all conditions precedent evidenced             -> up to L2
  * L3 additionally needs a recorded Board exception to policy POL-AI-03
  * PILOT_ONLY approval                            -> L1, shadow mode
The agent cannot sign; the committee record is written by people.
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, load_json, write_json  # noqa: E402

ORDER = ["L0", "L1", "L2", "L3"]


def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    return dt.date(d.year + y, mo + 1, min(d.day, 28))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review-dir", required=True)
    ap.add_argument("--committee", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    dec = load_json(os.path.join(args.review_dir, "decision.json"))
    com = load_json(args.committee)
    sig = com.get("signature") or {}
    if not sig.get("signed_by") or not sig.get("date"):
        sys.exit("Refused: the committee decision is not signed.")
    if com.get("decision") not in ("APPROVE", "APPROVE_WITH_CONDITIONS", "PILOT_ONLY"):
        sys.exit(f"Refused: committee decision is {com.get('decision')}; nothing to issue.")

    precedent = {c["id"] for c in dec["conditions_precedent"]}
    met = set(com.get("conditions_precedent_evidenced", []))
    outstanding = sorted(precedent - met)
    requested = com.get("autonomy_level_requested", "L1")
    cap, why = "L2", "all conditions precedent evidenced"
    if com["decision"] == "PILOT_ONLY":
        cap, why = "L1", "pilot approval: assist only, shadow mode"
    elif outstanding:
        cap, why = "L1", f"conditions precedent outstanding: {', '.join(outstanding)}"
    if requested == "L3":
        if com.get("board_exception_POL_AI_03") and cap == "L2":
            cap, why = "L3", "Board exception to POL-AI-03 recorded and all conditions evidenced"
        else:
            why += "; L3 needs a Board exception to POL-AI-03"
    level = requested if ORDER.index(requested) <= ORDER.index(cap) else cap

    start = dt.date.fromisoformat(sig["date"])
    months = dec.get("re_review_months") or 6
    policy = {
        "policy_id": f"RP-{dec['proposal_id']}-{start.isoformat()}",
        "system": com.get("system"),
        "approval_ref": dec["proposal_id"],
        "approval_outcome": com["decision"],
        "autonomy_level": level,
        "autonomy_requested": requested,
        "autonomy_cap_reason": why,
        "shadow_mode": com["decision"] == "PILOT_ONLY",
        "valid_from": start.isoformat(),
        "valid_until": add_months(start, months).isoformat(),
        "min_parse_confidence": com.get("min_parse_confidence", 0.7),
        "l3_low_score_floor": com.get("l3_low_score_floor") if level == "L3" else None,
        "audit_sample_rate": com.get("audit_sample_rate", 0.10),
        "fairness_monitor": {"min_group_n": 30, "impact_ratio_threshold": 0.8, "alpha": 0.05,
                             "attributes": ["gender", "age_band", "home_region", "disability"]},
        "circuit_breaker": {"trips_on": "RED", "fallback_level": "L1", "restored_by": "AI Approval Committee only"},
        "grievance_contact": com.get("grievance_contact"),
        "conditions_subsequent": [c["id"] for c in dec["conditions_subsequent"]],
        "conditions_precedent_outstanding": outstanding,
        "committee_signature": {"signed_by": sig["signed_by"], "role": sig.get("role"), "date": sig["date"]},
        "earned_autonomy_path": {
            "L3_requires": ["6 months at L2", "fairness GREEN in every monthly report", "blind-audit agreement >= 95%",
                            "appeals upheld < 5%", "Board exception to POL-AI-03"]},
    }
    write_json(args.out, policy)
    audit(args.audit_log, "issue_runtime_policy.py", [os.path.join(args.review_dir, "decision.json"), args.committee],
          [args.out], {"level": level, "requested": requested, "valid_until": policy["valid_until"]})
    print(f"Runtime policy {policy['policy_id']}: autonomy {level} (requested {requested}; {why}); "
          f"valid {policy['valid_from']} to {policy['valid_until']}")


if __name__ == "__main__":
    main()
