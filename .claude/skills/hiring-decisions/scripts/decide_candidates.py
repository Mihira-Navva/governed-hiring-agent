#!/usr/bin/env python3
"""Turn screening results into proposed actions, strictly within the autonomy level governance allows.

Usage:
    python decide_candidates.py --spec job-spec.json --screening screening.json \
        --policy governance/runtime-policy.json --state governance/autonomy-state.json \
        --out decisions.json --letters <run>/letters [--today YYYY-MM-DD] [--audit-log audit-log.jsonl]

The effective autonomy level is the LOWER of the committee's signed policy and the guardian's current
state. An invalid policy (missing, unsigned or expired) means L0: nothing is decided.

Actions (each marked autonomous or needing a person):
  AUTO_ADVANCE                 score >= advance threshold (L2+)
  AUTO_REJECT_HARD_REQUIREMENT a hard requirement FAILs cleanly (L2+); appealable
  AUTO_REJECT_LOW_SCORE        score below the policy's L3 floor (L3 only); appealable
  PROPOSE_ADVANCE / PROPOSE_REJECT   the same outcomes when the level does not allow acting alone
  HOLD_FOR_HUMAN               borderline score, unclear requirement, missing input, low parse
                               confidence, integrity flag, accommodation pending
  HUMAN_ONLY                   candidate asked for a person, or did not consent to AI
Nothing here is sent or actioned: the guardian releases or routes every decision.
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, load_json, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LETTERS = os.path.join(HERE, "..", "templates", "letters.json")
ORDER = ["L0", "L1", "L2", "L3"]


def effective_level(policy, state, today):
    if not policy:
        return "L0", "No runtime policy issued"
    sig = policy.get("committee_signature") or {}
    if not sig.get("signed_by") or not sig.get("date"):
        return "L0", "Runtime policy is not signed by the committee"
    if not (policy.get("valid_from", "") <= today <= policy.get("valid_until", "")):
        return "L0", f"Runtime policy not valid on {today} (valid {policy.get('valid_from')} to {policy.get('valid_until')})"
    level = policy.get("autonomy_level", "L0")
    reason = f"Committee policy {policy.get('policy_id')} sets {level}"
    s = (state or {}).get("autonomy_level")
    if s and ORDER.index(s) < ORDER.index(level):
        level, reason = s, f"Guardian lowered autonomy to {s}: {state.get('reason')}"
    return level, reason


def letter(templates, kind, **kw):
    kw.setdefault("ai_notice", templates["ai_notice"])
    kw["appeal"] = templates["appeal"].format(grievance_contact=kw.get("grievance_contact", ""))
    return templates[kind].format(**kw)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--screening", required=True)
    ap.add_argument("--policy", required=True)
    ap.add_argument("--state")
    ap.add_argument("--out", required=True)
    ap.add_argument("--letters", required=True)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    spec = load_json(args.spec)
    screening = load_json(args.screening)
    policy = load_json(args.policy) if os.path.exists(args.policy) else None
    state = load_json(args.state) if args.state and os.path.exists(args.state) else None
    tmpl = load_json(LETTERS)
    level, level_reason = effective_level(policy, state, args.today)
    n = ORDER.index(level)
    th = spec["thresholds"]
    min_conf = (policy or {}).get("min_parse_confidence", 0.7)
    l3_floor = (policy or {}).get("l3_low_score_floor")
    contact = (policy or {}).get("grievance_contact", "the hiring grievance officer")
    hard_meta = {h["id"]: h for h in spec["hard_requirements"]}
    os.makedirs(args.letters, exist_ok=True)

    decisions = []
    for c in screening["candidates"]:
        cid, reasons, action, kind = c["candidate_id"], [], None, None
        if c["status"] != "SCORED":
            action, reasons = "HUMAN_ONLY", [c["reason"]]
        elif n == 0:
            action, reasons = "HOLD_FOR_HUMAN", [f"Agent not authorised to act: {level_reason}"]
        else:
            fails = [h for h in c["hard_requirements"] if h["result"] == "FAIL"]
            unclear = [h for h in c["hard_requirements"] if h["result"] == "UNCLEAR"]
            if c["integrity_flags"]:
                action = "HOLD_FOR_HUMAN"
                reasons.append("Resume contains text addressed to an AI screener (removed before scoring); a person should read the original")
            elif c["parse_confidence"] < min_conf:
                action = "HOLD_FOR_HUMAN"
                reasons.append(f"Resume could not be read reliably (parse confidence {c['parse_confidence']})")
            elif c["accommodation_requested"] and c["unscorable"]:
                action = "HOLD_FOR_HUMAN"
                reasons.append("Accommodation requested and an assessment is outstanding: arrange an accessible assessment")
            elif fails:
                h = fails[0]
                action = "AUTO_REJECT_HARD_REQUIREMENT" if n >= 2 else "PROPOSE_REJECT"
                kind = "reject_hard_requirement"
                reasons.append(f"{h['id']} not met: {h['requirement']}. Evidence: {h['evidence']}")
            elif unclear:
                action = "HOLD_FOR_HUMAN"
                reasons += [f"{h['id']} unclear: {h['evidence']}" for h in unclear]
            elif c["total"] is None:
                action = "HOLD_FOR_HUMAN"
                reasons.append("Cannot score: missing " + ", ".join(c["unscorable"]) + " (missing is not treated as zero)")
            elif c["total"] >= th["advance"]:
                action = "AUTO_ADVANCE" if n >= 2 else "PROPOSE_ADVANCE"
                kind = "advance"
                top = sorted([x for x in c["criteria"] if x["score"] is not None], key=lambda x: -x["weight"] * x["score"])[:2]
                reasons.append(f"Score {c['total']} (advance at {th['advance']}). Strongest: " +
                               "; ".join(f"{x['criterion']} ({x['evidence']})" for x in top))
            elif c["total"] >= th["human_review_floor"]:
                action = "HOLD_FOR_HUMAN"
                reasons.append(f"Borderline score {c['total']} (between {th['human_review_floor']} and {th['advance']}): a recruiter decides")
            else:
                if n >= 3 and l3_floor is not None and c["total"] < l3_floor:
                    action, kind = "AUTO_REJECT_LOW_SCORE", "reject_low_score_auto"
                else:
                    action, kind = "PROPOSE_REJECT", "reject_judgment"
                weak = sorted([x for x in c["criteria"] if x["score"] is not None], key=lambda x: x["score"])[:2]
                reasons.append(f"Score {c['total']} (below {th['human_review_floor']}). Weakest: " +
                               "; ".join(f"{x['criterion']} ({x['evidence']})" for x in weak))
            if c["accommodation_requested"] and action not in ("HOLD_FOR_HUMAN",):
                reasons.append("Accommodation requested: recruiter to confirm interview arrangements")

        autonomous = action in ("AUTO_ADVANCE", "AUTO_REJECT_HARD_REQUIREMENT", "AUTO_REJECT_LOW_SCORE")
        lpath = None
        if kind or action in ("HOLD_FOR_HUMAN", "HUMAN_ONLY"):
            k = kind or "acknowledge"
            fields = {"role": spec["role"], "grievance_contact": contact, "reasons": " ".join(reasons)}
            if k == "reject_hard_requirement":
                h = hard_meta[fails[0]["id"]]
                fields.update(requirement=h["requirement"], why=h["why"], evidence=fails[0]["evidence"])
            lpath = os.path.join(args.letters, f"{cid}.md")
            with open(lpath, "w", encoding="utf-8") as fh:
                fh.write(f"<!-- DRAFT: not sent until released by the guardian{' and confirmed by a recruiter' if not autonomous and kind else ''} -->\n")
                fh.write(letter(tmpl, k, **fields))
        decisions.append({"candidate_id": cid, "action": action, "autonomous": autonomous,
                          "needs_person": not autonomous, "score": c.get("total"), "reasons": reasons,
                          "letter": os.path.basename(lpath) if lpath else None, "letter_kind": kind or "acknowledge"})

    out = {"requisition_id": spec["requisition_id"], "effective_level": level, "level_reason": level_reason,
           "decided_on": args.today, "decisions": decisions}
    write_json(args.out, out)
    counts = {}
    for d in decisions:
        counts[d["action"]] = counts.get(d["action"], 0) + 1
    audit(args.audit_log, "decide_candidates.py", [args.spec, args.screening, args.policy], [args.out],
          {"level": level, **counts})
    print(f"Autonomy {level} ({level_reason}). " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
