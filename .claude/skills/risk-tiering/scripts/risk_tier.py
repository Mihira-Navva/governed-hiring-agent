#!/usr/bin/env python3
"""Assign a risk tier to an AI hiring use case from its intake record.

Usage:
    python risk_tier.py intake.json --out risk.json [--audit-log audit-log.jsonl]

Scores seven dimensions (0-3 each, max 21), applies the evaluative-system floor (any system that
screens, ranks or scores candidates is at least T3), and checks prohibitions and red lines.
Unknown values (null) are scored as the riskier answer: the burden of proof is on the proposer.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, get, load_json, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CRITERIA = os.path.join(HERE, "..", "references", "risk-criteria.json")


def not_true(v):
    """Treat 'no' and 'unknown' alike: an unevidenced safeguard is not a safeguard."""
    return v is not True


def score_dimensions(r, c):
    dims = {}

    func, stage = get(r, "system.primary_function"), get(r, "system.decision_stage")
    if func in c["evaluative_functions"] or stage in c["evaluative_stages"]:
        dims["consequence"] = (3, f"Evaluates candidates ({func or '?'} at {stage or '?'} stage): outcome affects access to employment")
    elif stage == "sourcing":
        dims["consequence"] = (2, "Sourcing: decides who is invited to apply")
    else:
        dims["consequence"] = (1, f"Supports hiring logistics ({func or stage}); does not judge candidates")

    level = get(r, "system.automation_level")
    a = c["automation_scores"].get(level, 3)
    reason = f"Automation level '{level}'"
    if level in ("assistive_ranking", "auto_shortlist") and \
            get(r, "human_oversight.human_reviews_every_rejection") is not True:
        a, reason = 3, reason + ", but no human reviews every rejection: treated as automated rejection in practice"
    if level == "auto_reject_hard_requirements":
        if get(r, "human_oversight.human_reviews_every_judgment_rejection") is not True:
            a, reason = 3, reason + ", and judgment-based rejections are not confirmed to be reviewed by a person"
        else:
            reason += " (verifiable requirements only; a person reviews every judgment-based rejection)"
    dims["automation"] = (a, reason)

    n = get(r, "use_case.annual_applications")
    if n is None:
        s, sreason = 3, "Volume unknown (scored as high)"
    else:
        s = c["scale_top_score"]
        for limit, score in c["scale_bands"]:
            if n < limit:
                s = score
                break
        sreason = f"{n:,} applications a year"
    dims["scale"] = (s, sreason)

    t = get(r, "system.techniques", {}) or {}
    sens, why = 1, ["CV and contact data are personal data"]
    if t.get("emotion_or_affect_inference") or t.get("biometric_categorisation"):
        sens, why = 3, ["Biometric or affect inference"]
    else:
        if get(r, "data.trained_on_historical_hiring_outcomes") is not False:
            sens += 1
            why.append("trained on (or unclear whether trained on) past hiring decisions")
        if any(t.get(k) for k in ("video_or_facial_analysis", "voice_analysis", "social_media_screening", "generative_llm_scoring")):
            sens += 1
            why.append("video, voice, social-media or LLM processing")
    dims["data_sensitivity"] = (min(sens, 3), "; ".join(why))

    o, why = 0, []
    if not_true(get(r, "transparency.individual_explanations_available")):
        o += 1; why.append("no individual explanations")
    if not_true(get(r, "transparency.model_documentation_available")):
        o += 1; why.append("no model documentation")
    if get(r, "system.build_type") in ("third_party", "hybrid", None):
        o += 1; why.append("third-party or unclear provenance")
    dims["opacity"] = (o, "; ".join(why) or "explainable, documented, in-house")

    ct, why = 0, []
    for field, label in (("contestability.appeal_channel", "no appeal channel"),
                         ("contestability.human_alternative_on_request", "no human alternative on request"),
                         ("contestability.grievance_officer_named", "no named grievance officer")):
        if not_true(get(r, field)):
            ct += 1; why.append(label)
    dims["contestability_gap"] = (ct, "; ".join(why) or "appeal, alternative and grievance routes in place")

    ov, why = 0, []
    if not_true(get(r, "human_oversight.reviewers_trained")):
        ov += 1; why.append("reviewers not trained")
    if not_true(get(r, "human_oversight.overrides_logged")):
        ov += 1; why.append("overrides not logged")
    if get(r, "human_oversight.ai_score_visible_before_independent_review") is not False:
        ov += 1; why.append("AI score seen before reviewer forms own view (anchoring)")
    dims["oversight_weakness"] = (ov, "; ".join(why) or "trained, logged, blind-first review")

    return dims


def check_red_lines(r, c):
    hits = []
    t = get(r, "system.techniques", {}) or {}
    rl = c["red_lines"]
    if t.get("emotion_or_affect_inference"):
        hits.append({"id": "RL-01", **rl["RL-01"]})
    level = get(r, "system.automation_level")
    if level == "auto_reject_hard_requirements":
        rl02 = get(r, "human_oversight.human_reviews_every_judgment_rejection") is not True
    else:
        rl02 = level in ("auto_archive", "auto_reject", "fully_automated") or \
            get(r, "human_oversight.human_reviews_every_rejection") is False
    if rl02:
        hits.append({"id": "RL-02", **rl["RL-02"]})
    if get(r, "vendor_governance.allows_independent_audit") is False:
        hits.append({"id": "RL-04", **rl["RL-04"]})
    if t.get("biometric_categorisation"):
        hits.append({"id": "RL-06", **rl["RL-06"]})
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("intake")
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    r = load_json(args.intake)
    c = load_json(CRITERIA)

    dims = score_dimensions(r, c)
    total = sum(v[0] for v in dims.values())
    tier = next(t for t in c["tiers"] if total <= t["max_score"])
    tier_id, label, floor_applied = tier["tier"], tier["label"], False

    order = [t["tier"] for t in c["tiers"]]
    if dims["consequence"][0] == 3 and order.index(tier_id) < order.index(c["evaluative_floor"]):
        floor_applied = True
        tier_id = c["evaluative_floor"]
        label = next(t["label"] for t in c["tiers"] if t["tier"] == tier_id)

    prohibited = []
    func = get(r, "system.primary_function")
    if func in c["prohibited_primary_functions"]:
        prohibited.append({"function": func, **c["prohibited_primary_functions"][func]})
        tier_id, label = "PROHIBITED", "Prohibited purpose"

    red_lines = check_red_lines(r, c)

    result = {
        "proposal_id": r.get("proposal_id"),
        "tier": tier_id,
        "tier_label": label,
        "score": total,
        "max_score": 21,
        "evaluative_floor_applied": floor_applied,
        "dimensions": {k: {"score": v[0], "reason": v[1]} for k, v in dims.items()},
        "prohibited_purpose": prohibited,
        "red_lines": red_lines,
        "review_requirements": c["review_requirements"][tier_id],
        "regulatory_classification": {
            "eu_ai_act": "High-risk (Annex III, point 4: employment, recruitment and selection)" if dims["consequence"][0] == 3
                         else "Not Annex III employment use (check other categories)",
            "eu_ai_act_note": "Annex III high-risk obligations apply from 2 Dec 2027 (Digital Omnibus on AI, in force 27 Jul 2026). Art. 5 prohibitions already apply. Relevant only where EU candidates are in scope; used here as a benchmark.",
        },
    }
    write_json(args.out, result)
    audit(args.audit_log, "risk_tier.py", [args.intake], [args.out],
          {"tier": tier_id, "score": total, "red_lines": [h["id"] for h in red_lines],
           "prohibited": [p["id"] for p in prohibited]})

    rl = ", ".join(h["id"] for h in red_lines) or "none"
    print(f"Tier {tier_id} ({label}), score {total}/21{' (evaluative floor applied)' if floor_applied else ''}; red lines: {rl}")


if __name__ == "__main__":
    main()
