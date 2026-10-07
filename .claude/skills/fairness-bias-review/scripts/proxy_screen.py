#!/usr/bin/env python3
"""Screen a model's input features for protected attributes and proxies.

Usage:
    python proxy_screen.py intake.json --out proxy-screen.json [--audit-log audit-log.jsonl]

Reads data.input_features from the intake record and classifies each feature with the rules in
references/proxy-dictionary.json. A PROTECTED feature used as a model input triggers red line
RL-03. Features that match no rule are UNCLASSIFIED and need justification.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, get, load_json, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DICTIONARY = os.path.join(HERE, "..", "references", "proxy-dictionary.json")


def classify(feature, rules, priority):
    text = feature.lower()
    matches = [r for r in rules if re.search(r["pattern"], text)]
    if not matches:
        return "UNCLASSIFIED", None, []
    matches.sort(key=lambda r: priority.index(r["category"]))
    return matches[0]["category"], matches[0], matches


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("intake")
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    record = load_json(args.intake)
    d = load_json(DICTIONARY)
    features = get(record, "data.input_features") or []

    results = []
    for f in features:
        cat, top, all_matches = classify(f, d["rules"], d["priority"])
        attrs = sorted({a for m in all_matches for a in m["attributes"]})
        results.append({
            "feature": f,
            "category": cat,
            "rule": top["id"] if top else None,
            "linked_attributes": attrs,
            "rationale": top["rationale"] if top else "No rule matched. Relevance to the job has not been shown.",
            "action": d["actions"][cat],
            "also_matched": [m["id"] for m in all_matches[1:]],
        })

    counts = {c: sum(1 for r in results if r["category"] == c) for c in d["priority"] + ["UNCLASSIFIED"]}
    protected = [r["feature"] for r in results if r["category"] == "PROTECTED"]
    strong = [r["feature"] for r in results if r["category"] == "STRONG_PROXY"]

    red_lines = []
    if protected:
        red_lines.append({
            "id": "RL-03",
            "title": "Protected attribute used as a model input",
            "features": protected,
            "basis": "Code on Wages, 2019 s. 3; RPwD Act, 2016; Transgender Persons Act, 2019; policy POL-AI-04.",
            "remediable": True,
            "remedy": "Remove these inputs and retrain; keep protected data only in a separate, voluntary audit dataset.",
        })

    if protected:
        verdict = "FAIL"
    elif strong:
        verdict = "CONCERN"
    elif counts["MODERATE_PROXY"] or counts["UNCLASSIFIED"]:
        verdict = "JUSTIFY"
    else:
        verdict = "PASS"

    out = {
        "proposal_id": record.get("proposal_id"),
        "verdict": verdict,
        "feature_count": len(features),
        "counts": counts,
        "features": results,
        "features_to_remove": protected + strong,
        "features_to_justify": [r["feature"] for r in results if r["category"] in ("MODERATE_PROXY", "UNCLASSIFIED")],
        "red_lines": red_lines,
        "limits": "Keyword screening finds proxies that are named. It cannot find proxies hidden inside composite scores "
                  "or learned from free text; only outcome testing by group (adverse_impact.py) can show those.",
    }
    write_json(args.out, out)
    audit(args.audit_log, "proxy_screen.py", [args.intake], [args.out],
          {"verdict": verdict, "counts": counts, "red_lines": [r["id"] for r in red_lines]})

    print(f"Proxy screen {verdict}: {len(features)} features -> " +
          ", ".join(f"{k} {v}" for k, v in counts.items() if v))


if __name__ == "__main__":
    main()
