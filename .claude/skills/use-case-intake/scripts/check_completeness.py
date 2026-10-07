#!/usr/bin/env python3
"""Check an intake record for missing, invalid and internally inconsistent information.

Usage:
    python check_completeness.py intake.json --out completeness.json [--audit-log audit-log.jsonl]

Status:
    INCOMPLETE           a blocking field is missing or invalid -> review cannot proceed
    COMPLETE_WITH_GAPS   only non-blocking fields are missing -> review proceeds, gaps become questions
    COMPLETE             nothing missing
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, get, is_missing, load_json, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIELD_GUIDE = os.path.join(HERE, "..", "references", "field-guide.json")
TEMPLATE = os.path.join(HERE, "..", "templates", "intake-record.json")


def check_enums(record, enums):
    errors = []
    for path, allowed in enums.items():
        value = get(record, path)
        if is_missing(value):
            continue
        values = value if isinstance(value, list) else [value]
        bad = [v for v in values if v not in allowed]
        if bad:
            errors.append({"field": path, "value": bad, "allowed": [a for a in allowed if a is not None]})
    return errors


def consistency_checks(r):
    """Contradictions a careful reviewer would notice. Each one becomes a question."""
    warnings = []
    level = get(r, "system.automation_level")
    reviews_all = get(r, "human_oversight.human_reviews_every_rejection")
    if level in ("advisory_only", "assistive_ranking", "auto_shortlist") and reviews_all is False:
        warnings.append({
            "code": "W-DEFACTO-AUTO",
            "message": f"Automation level is stated as '{level}', but no human reviews every rejection. "
                       "Applicants the AI ranks low may never be seen: this may be automated rejection in practice.",
        })
    if level == "auto_reject_hard_requirements" and \
            get(r, "human_oversight.human_reviews_every_judgment_rejection") is not True:
        warnings.append({
            "code": "W-DEFACTO-AUTO-JUDGMENT",
            "message": "Some rejections are automated, but it is not confirmed that a person reviews every rejection "
                       "based on judgment rather than a verifiable hard requirement.",
        })
    if get(r, "system.primary_function") == "video_interview_affect_analysis" and \
            get(r, "system.techniques.emotion_or_affect_inference") is False:
        warnings.append({"code": "W-AFFECT-CONTRADICTION",
                         "message": "Primary function is affect analysis but emotion/affect inference is marked false."})
    if get(r, "system.techniques.emotion_or_affect_inference") and \
            not get(r, "system.techniques.video_or_facial_analysis") and \
            not get(r, "system.techniques.voice_analysis"):
        warnings.append({"code": "W-AFFECT-SOURCE",
                         "message": "Affect inference is declared but neither video nor voice analysis is: ask what it is inferred from."})
    if get(r, "testing.bias_audit_independent") and not get(r, "testing.bias_audit_completed"):
        warnings.append({"code": "W-AUDIT-CONTRADICTION",
                         "message": "An independent bias audit is claimed but no audit is marked as completed."})
    if get(r, "data.cross_border_transfer") and is_missing(get(r, "data.transfer_destinations")):
        warnings.append({"code": "W-TRANSFER-DEST",
                         "message": "Data leaves India but the destination countries are not stated."})
    if get(r, "data.trained_on_historical_hiring_outcomes") and get(r, "testing.bias_audit_completed") is not True:
        warnings.append({"code": "W-HISTORICAL-LABELS",
                         "message": "Model learns from past hiring decisions and has no completed bias audit: past bias may be reproduced."})
    return warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("intake")
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    record = load_json(args.intake)
    guide = load_json(FIELD_GUIDE)["fields"]
    enums = load_json(TEMPLATE)["_enums"]

    blocking, important = [], []
    for path, meta in guide.items():
        if is_missing(get(record, path)):
            item = {"field": path, "question": meta["question"], "why": meta["why"]}
            (blocking if meta["tier"] == "blocking" else important).append(item)

    enum_errors = check_enums(record, enums)
    warnings = consistency_checks(record)

    if blocking or enum_errors:
        status = "INCOMPLETE"
    elif important:
        status = "COMPLETE_WITH_GAPS"
    else:
        status = "COMPLETE"

    total = len(guide)
    provided = total - len(blocking) - len(important)
    result = {
        "proposal_id": record.get("proposal_id"),
        "status": status,
        "fields_provided": provided,
        "fields_total": total,
        "completeness_pct": round(100 * provided / total, 1),
        "blocking_missing": blocking,
        "important_missing": important,
        "invalid_values": enum_errors,
        "consistency_warnings": warnings,
        "claims_needing_evidence": get(record, "intake_notes.claims_needing_evidence", []),
        "integrity_observations": get(record, "intake_notes.integrity_observations", []),
    }
    write_json(args.out, result)
    audit(args.audit_log, "check_completeness.py", [args.intake], [args.out],
          {"status": status, "blocking": len(blocking), "important": len(important),
           "warnings": [w["code"] for w in warnings]})

    print(f"{status}: {provided}/{total} fields provided ({result['completeness_pct']}%), "
          f"{len(blocking)} blocking gaps, {len(important)} other gaps, {len(warnings)} consistency warnings")


if __name__ == "__main__":
    main()
