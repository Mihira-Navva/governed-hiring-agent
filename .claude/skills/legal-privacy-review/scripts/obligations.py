#!/usr/bin/env python3
"""Map an AI hiring proposal against the obligations register.

Usage:
    python obligations.py intake.json --out legal.json [--fairness fairness.json] \
        [--audit-log audit-log.jsonl]

For each obligation in references/obligations-register.json it decides whether it APPLIES and,
if so, whether the proposal shows it is MET, has a GAP, or is UNKNOWN (the evidence needed to
tell is missing). Conditions are declarative JSON evaluated with three-valued logic; there is no
eval() of strings.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, get, load_json, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HERE, "..", "references", "obligations-register.json")

UNKNOWN = None  # third truth value


def evaluate(cond, ctx):
    """Return True, False or None (unknown)."""
    if "all" in cond:
        vals = [evaluate(c, ctx) for c in cond["all"]]
        if any(v is False for v in vals):
            return False
        return None if any(v is None for v in vals) else True
    if "any" in cond:
        vals = [evaluate(c, ctx) for c in cond["any"]]
        if any(v is True for v in vals):
            return True
        return None if any(v is None for v in vals) else False

    value, op, target = get(ctx, cond["field"]), cond["op"], cond.get("value")
    if op == "truthy":
        return None if value is None else bool(value)
    if value is None:
        return UNKNOWN
    if op == "eq":
        return value == target
    if op == "ne":
        return value != target
    if op == "in":
        return value in target
    if op == "contains":
        return target in value if isinstance(value, (list, str)) else False
    if op == "lte":
        return value <= target
    if op == "gte":
        return value >= target
    raise ValueError(f"Unknown operator {op}")


def fairness_context(path):
    if not path or not os.path.exists(path):
        return None
    f = load_json(path)
    return {"overall": f.get("overall_verdict"),
            "by_attribute": {a["attribute"]: a["verdict"] for a in f.get("attributes", [])}}


SEVERITY = {"in_force": "mandatory", "in_force_phased": "mandatory", "applies_from": "mandatory",
            "internal_policy": "mandatory", "guidance": "recommended", "benchmark": "recommended"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("intake")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fairness")
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    intake = load_json(args.intake)
    reg = load_json(REGISTER)
    ctx = {"intake": intake, "fairness": fairness_context(args.fairness)}

    results = []
    for ob in reg["obligations"]:
        applies = evaluate(ob["applies_if"], ctx)
        if applies is not True:
            continue
        met = evaluate(ob["check"], ctx)
        status = "MET" if met is True else ("GAP" if met is False else "UNKNOWN")
        results.append({
            "id": ob["id"], "instrument": ob["instrument"], "provision": ob["provision"],
            "jurisdiction": ob["jurisdiction"], "legal_status": ob["legal_status"],
            "status_note": ob["status_note"], "severity": SEVERITY[ob["legal_status"]],
            "requirement": ob["requirement"], "status": status,
            "evidence_needed": ob["evidence"], "gap_code": ob["gap_code"], "owner": ob["owner"],
        })

    summary = {s: sum(1 for r in results if r["status"] == s) for s in ("MET", "GAP", "UNKNOWN")}
    mandatory_open = [r for r in results if r["severity"] == "mandatory" and r["status"] != "MET"]
    review_functions = {"Legal Counsel", "Data Protection Officer", "Chief Information Security Officer",
                        "Chief Human Resources Officer"}
    escalations = sorted({r["owner"] for r in mandatory_open} & review_functions)

    out = {
        "proposal_id": intake.get("proposal_id"),
        "register_as_of": reg["as_of"],
        "jurisdictions": get(intake, "use_case.jurisdictions"),
        "summary": summary,
        "mandatory_open": len(mandatory_open),
        "obligations": results,
        "escalate_to": escalations,
        "disclaimer": "Identifies obligations and evidence gaps for the committee. Not legal advice; "
                      "Legal Counsel confirms applicability before go-live.",
    }
    write_json(args.out, out)
    audit(args.audit_log, "obligations.py", [args.intake, args.fairness], [args.out],
          {"applicable": len(results), **summary, "mandatory_open": len(mandatory_open)})

    print(f"{len(results)} obligations apply: {summary['MET']} met, {summary['GAP']} gaps, "
          f"{summary['UNKNOWN']} unknown ({len(mandatory_open)} mandatory items open)")


if __name__ == "__main__":
    main()
