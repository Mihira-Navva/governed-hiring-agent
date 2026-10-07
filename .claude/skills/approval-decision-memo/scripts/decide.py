#!/usr/bin/env python3
"""Apply the committee's decision rules to the review findings.

Usage:
    python decide.py --review-dir reviews/<id> [--audit-log reviews/<id>/audit-log.jsonl]

Reads from the review folder whichever of these exist: intake.json, completeness.json, risk.json,
proxy-screen.json, fairness.json, legal.json. Writes decision.json with the outcome, the rule
that fired, the findings behind it, the conditions attached, escalations and open questions.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, get, load_json, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CONDITIONS = os.path.join(HERE, "..", "references", "conditions-library.json")

LABELS = {
    "REJECT": "Reject",
    "RETURN_FOR_INFORMATION": "Return for information",
    "REDESIGN_AND_RESUBMIT": "Redesign and resubmit",
    "PILOT_ONLY": "Pilot only (shadow mode)",
    "APPROVE_WITH_CONDITIONS": "Approve with conditions",
    "APPROVE": "Approve",
}
FILES = ["intake", "completeness", "risk", "proxy-screen", "fairness", "legal"]


def load_review(folder):
    data = {}
    for name in FILES:
        path = os.path.join(folder, f"{name}.json")
        data[name] = load_json(path) if os.path.exists(path) else None
    return data


def collect_codes(d):
    """Translate every finding into a code that the conditions library understands."""
    codes, findings = set(), []
    intake, risk = d["intake"] or {}, d["risk"] or {}
    proxy, fair, legal, comp = d["proxy-screen"], d["fairness"], d["legal"], d["completeness"]

    red_lines = []
    for src_name, src in (("risk.json", risk), ("proxy-screen.json", proxy), ("fairness.json", fair)):
        for rl in (src or {}).get("red_lines", []):
            red_lines.append({**rl, "source": src_name})
            codes.add(rl["id"])

    if risk.get("tier") in ("T3", "T4"):
        codes.add("TIER-HIGH")

    t = lambda path: get(intake, path)  # noqa: E731
    if t("system.automation_level") == "auto_reject_hard_requirements":
        codes.add("HO-HARDREQ-AUTO")
    if t("human_oversight.reviewers_trained") is not True:
        codes.add("HO-TRAIN")
    if t("human_oversight.overrides_logged") is not True:
        codes.add("HO-LOG")
    if t("human_oversight.ai_score_visible_before_independent_review") is not False:
        codes.add("HO-ANCHOR")
    if t("contestability.appeal_channel") is not True:
        codes.add("CO-APPEAL")
    if t("transparency.candidate_notified_of_ai_use") is not True:
        codes.add("TR-NOTICE")
    if t("transparency.model_documentation_available") is not True:
        codes.add("TR-DOCS")
    if t("data.trained_on_historical_hiring_outcomes") is not False:
        codes.add("FA-LABELS")
    if t("testing.job_relatedness_validated") is not True:
        codes.add("FA-JOBREL")

    if proxy:
        if proxy["counts"].get("STRONG_PROXY"):
            codes.add("FA-PROXY-STRONG")
        if proxy["counts"].get("MODERATE_PROXY") or proxy["counts"].get("UNCLASSIFIED"):
            codes.add("FA-PROXY-JUSTIFY")
    has_outcome_data = bool(fair and fair.get("records"))
    if not has_outcome_data:
        codes.add("FA-NO-DATA")
    elif fair["overall_verdict"] == "CONCERN":
        codes.add("FA-CONCERN")

    if legal:
        for ob in legal["obligations"]:
            if ob["status"] != "MET":
                codes.add(ob["gap_code"])

    for w in (comp or {}).get("consistency_warnings", []):
        codes.add(w["code"])
    if get(intake, "intake_notes.integrity_observations"):
        codes.add("INT-INJECTION")

    return codes, red_lines, has_outcome_data


def pick_conditions(codes, library):
    chosen = []
    for c in library["conditions"]:
        hit = sorted(set(c["triggers"]) & codes)
        if hit:
            chosen.append({**{k: c[k] for k in ("id", "title", "text", "type", "owner", "evidence", "deadline", "principle")},
                           "triggered_by": hit})
    return chosen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review-dir", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    d = load_review(args.review_dir)
    intake, comp, risk, fair, legal = d["intake"] or {}, d["completeness"] or {}, d["risk"] or {}, d["fairness"], d["legal"]
    library = load_json(CONDITIONS)
    codes, red_lines, has_outcome_data = collect_codes(d)

    tier = risk.get("tier")
    mandatory_open = (legal or {}).get("mandatory_open", 0)
    rationale = []

    if tier == "PROHIBITED":
        outcome, rule = "REJECT", "D1"
        for p in risk.get("prohibited_purpose", []):
            rationale.append({"finding": f"{p['id']}: {p['title']}", "basis": p["basis"], "source": "risk.json"})
    elif red_lines:
        outcome, rule = "REDESIGN_AND_RESUBMIT", "D2"
        for rl in red_lines:
            detail = f" ({', '.join(rl.get('features') or rl.get('attributes') or [])})" if (rl.get("features") or rl.get("attributes")) else ""
            rationale.append({"finding": f"{rl['id']}: {rl['title']}{detail}", "basis": rl["basis"],
                              "remedy": rl.get("remedy"), "source": rl["source"]})
        if comp.get("status") == "INCOMPLETE":
            rationale.append({"finding": f"Also incomplete: {len(comp['blocking_missing'])} blocking fields missing; "
                                         "the resubmission must answer them.", "basis": "Completeness gate", "source": "completeness.json"})
    elif comp.get("status") == "INCOMPLETE":
        outcome, rule = "RETURN_FOR_INFORMATION", "D3"
        rationale.append({"finding": f"{len(comp['blocking_missing'])} blocking fields missing; the committee cannot assess the proposal.",
                          "basis": "Completeness gate", "source": "completeness.json"})
    elif not has_outcome_data and get(intake, "testing.bias_audit_completed") is not True:
        outcome, rule = "PILOT_ONLY", "D4"
        rationale.append({"finding": "No outcome evidence: no shadow or pilot data analysed and no completed bias audit.",
                          "basis": "Decision rule D4; policy POL-AI-04", "source": "fairness.json / intake.json"})
    elif tier in ("T3", "T4") or mandatory_open or (fair and fair.get("overall_verdict") == "CONCERN"):
        outcome, rule = "APPROVE_WITH_CONDITIONS", "D5"
        rationale.append({"finding": f"Risk tier {tier} ({risk.get('tier_label')}); {mandatory_open} mandatory obligations open; "
                                     f"fairness {fair['overall_verdict'] if fair else 'n/a'}.",
                          "basis": "Decision rule D5", "source": "risk.json, legal.json, fairness.json"})
    else:
        outcome, rule = "APPROVE", "D6"
        rationale.append({"finding": f"Risk tier {tier}; all mandatory obligations met.", "basis": "Decision rule D6",
                          "source": "risk.json, legal.json"})

    conditions = [] if outcome == "REJECT" else pick_conditions(codes, library)
    precedent = [c for c in conditions if c["type"] == "precedent"]
    subsequent = [c for c in conditions if c["type"] == "subsequent"]

    escalations = set((risk.get("review_requirements") or {}).get("reviewers", []))
    escalations |= set((legal or {}).get("escalate_to", []))
    if {"RL-01", "RL-06"} & codes or tier == "PROHIBITED":
        escalations.add("Ethics Board")
    if fair and fair.get("overall_verdict") == "FAIL":
        escalations |= {"Chief Human Resources Officer", "Legal Counsel"}
    if "INT-INJECTION" in codes:
        escalations |= {"Procurement", "Internal Audit"}

    questions = [q["question"] for q in comp.get("blocking_missing", []) + comp.get("important_missing", [])]
    questions += [f"Consistency check: {w['message']}" for w in comp.get("consistency_warnings", [])]

    out = {
        "proposal_id": intake.get("proposal_id"),
        "outcome": outcome,
        "outcome_label": LABELS[outcome],
        "rule_fired": rule,
        "risk_tier": tier,
        "rationale": rationale,
        "finding_codes": sorted(codes),
        "conditions_precedent": precedent,
        "conditions_subsequent": subsequent,
        "condition_framing": "Requirements for resubmission" if outcome == "REDESIGN_AND_RESUBMIT" else
                             ("Conditions for the pilot and for any later approval" if outcome == "PILOT_ONLY" else "Conditions of approval"),
        "escalations": sorted(escalations),
        "open_questions": questions,
        "re_review_months": (risk.get("review_requirements") or {}).get("re_review_months"),
        "approver": (risk.get("review_requirements") or {}).get("approver"),
        "decision_authority": "Recommendation only. The AI Approval Committee decides.",
    }
    write_json(os.path.join(args.review_dir, "decision.json"), out)
    inputs = [os.path.join(args.review_dir, f"{n}.json") for n in FILES]
    audit(args.audit_log, "decide.py", inputs, [os.path.join(args.review_dir, "decision.json")],
          {"outcome": outcome, "rule": rule, "conditions": len(conditions)})

    print(f"Recommendation: {LABELS[outcome]} (rule {rule}); {len(precedent)} conditions precedent, "
          f"{len(subsequent)} subsequent; escalate to {len(escalations)} functions")


if __name__ == "__main__":
    main()
