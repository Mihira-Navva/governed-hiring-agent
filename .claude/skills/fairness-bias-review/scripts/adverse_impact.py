#!/usr/bin/env python3
"""Measure adverse impact and equal opportunity by group from shadow-mode or pilot data.

Usage:
    python adverse_impact.py pilot.csv --outcome ai_shortlisted --qualified expert_qualified \
        --groups gender,age_band,region,disability --intersect gender:age_band \
        --annual 60000 --out fairness.json --md fairness-tables.md [--audit-log audit-log.jsonl]

For each protected attribute it reports, per group:
  * selection rate and impact ratio against the most-selected adequately sized group
    (four-fifths benchmark, threshold 0.80);
  * a two-sided Fisher exact test, so small differences in small groups are not over-read and
    large differences are not dismissed as noise;
  * equal opportunity: among candidates an expert panel judged qualified, the share the AI
    shortlisted (true positive rate), and the gap to the reference group;
  * an estimate of how many people a year the gap affects.

Verdicts per group: ADVERSE_IMPACT, POSSIBLE_ADVERSE_IMPACT, SIGNIFICANT_SMALL_DIFFERENCE,
INSUFFICIENT_DATA, NO_ADVERSE_IMPACT. Attribute and overall verdicts: FAIL, CONCERN, PASS.
Standard library only.
"""
import argparse
import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, write_json  # noqa: E402

RANK = {"PASS": 0, "CONCERN": 1, "FAIL": 2}


def _log_comb(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def fisher_exact(a, b, c, d):
    """Two-sided Fisher exact p-value for the 2x2 table [[a, b], [c, d]]."""
    r1, n = a + b, a + b + c + d
    c1 = a + c
    if n == 0 or r1 == 0 or r1 == n or c1 == 0 or c1 == n:
        return 1.0
    denom = _log_comb(n, r1)

    def p(x):
        return math.exp(_log_comb(c1, x) + _log_comb(n - c1, r1 - x) - denom)

    lo, hi = max(0, r1 - (n - c1)), min(r1, c1)
    p_obs = p(a)
    total = sum(px for px in (p(x) for x in range(lo, hi + 1)) if px <= p_obs * (1 + 1e-7))
    return min(1.0, total)


def rate(sel, n):
    return sel / n if n else None


def analyse(rows, attr, outcome, qualified, args):
    groups = {}
    excluded = 0
    for row in rows:
        g = (row.get(attr) or "").strip()
        if not g or g in args.exclude:
            excluded += 1
            continue
        s = groups.setdefault(g, {"n": 0, "sel": 0, "q_n": 0, "q_sel": 0})
        y = int(row[outcome])
        s["n"] += 1
        s["sel"] += y
        if qualified and row.get(qualified, "") != "" and int(row[qualified]) == 1:
            s["q_n"] += 1
            s["q_sel"] += y

    sized = {g: s for g, s in groups.items() if s["n"] >= args.min_n} or groups
    ref = max(sized, key=lambda g: rate(sized[g]["sel"], sized[g]["n"]))
    R = groups[ref]
    ref_rate = rate(R["sel"], R["n"])
    total_n = sum(s["n"] for s in groups.values())

    # Equal-opportunity reference: the group whose qualified candidates the AI shortlists most often,
    # among groups with enough expert-rated qualified candidates to be meaningful.
    eo_ref, ref_tpr, Q = None, None, None
    if qualified:
        q_sized = {g: s for g, s in groups.items() if s["q_n"] >= args.min_n}
        if q_sized:
            eo_ref = max(q_sized, key=lambda g: rate(q_sized[g]["q_sel"], q_sized[g]["q_n"]))
            Q = groups[eo_ref]
            ref_tpr = rate(Q["q_sel"], Q["q_n"])

    out_groups, worst, notes = [], "PASS", []
    for g, s in sorted(groups.items(), key=lambda kv: -kv[1]["n"]):
        r = rate(s["sel"], s["n"])
        ir = (r / ref_rate) if ref_rate else None
        p = 1.0 if g == ref else fisher_exact(s["sel"], s["n"] - s["sel"], R["sel"], R["n"] - R["sel"])

        if g == ref:
            v = "REFERENCE"
        elif s["n"] < args.min_n:
            v = "INSUFFICIENT_DATA"
        elif ir < args.threshold and p < args.alpha:
            v = "ADVERSE_IMPACT"
        elif ir < args.threshold:
            v = "POSSIBLE_ADVERSE_IMPACT"
        elif p < args.alpha and ir < 1:
            v = "SIGNIFICANT_SMALL_DIFFERENCE"
        else:
            v = "NO_ADVERSE_IMPACT"

        entry = {"group": g, "n": s["n"], "selected": s["sel"], "selection_rate": round(r, 4),
                 "impact_ratio": round(ir, 3) if ir is not None else None,
                 "p_value": round(p, 4), "verdict": v}

        if qualified:
            tpr = rate(s["q_sel"], s["q_n"])
            entry.update({"qualified_n": s["q_n"], "qualified_shortlisted": s["q_sel"],
                          "true_positive_rate": round(tpr, 4) if tpr is not None else None,
                          "qualified_missed": s["q_n"] - s["q_sel"]})
            if g == eo_ref:
                entry["eo_verdict"] = "EO_REFERENCE"
            elif tpr is not None and ref_tpr is not None:
                gap = ref_tpr - tpr
                p_eo = fisher_exact(s["q_sel"], s["q_n"] - s["q_sel"], Q["q_sel"], Q["q_n"] - Q["q_sel"])
                entry["eo_gap_pp"] = round(100 * gap, 1)
                entry["eo_p_value"] = round(p_eo, 4)
                if s["q_n"] < args.min_n:
                    entry["eo_verdict"] = "INSUFFICIENT_DATA"
                elif gap > args.eo_threshold and p_eo < args.alpha:
                    entry["eo_verdict"] = "UNEQUAL_OPPORTUNITY"
                elif gap > args.eo_threshold:
                    entry["eo_verdict"] = "POSSIBLE_UNEQUAL_OPPORTUNITY"
                else:
                    entry["eo_verdict"] = "OK"

        if args.annual and v in ("ADVERSE_IMPACT", "POSSIBLE_ADVERSE_IMPACT"):
            share = s["n"] / total_n
            entry["est_annual_people_affected"] = int(round((ref_rate - r) * share * args.annual))

        level = "PASS"
        if v == "ADVERSE_IMPACT" or entry.get("eo_verdict") == "UNEQUAL_OPPORTUNITY":
            level = "FAIL"
        elif v in ("POSSIBLE_ADVERSE_IMPACT", "INSUFFICIENT_DATA") or \
                entry.get("eo_verdict") == "POSSIBLE_UNEQUAL_OPPORTUNITY":
            level = "CONCERN"
        if v == "INSUFFICIENT_DATA":
            notes.append(f"'{g}' has only {s['n']} record{'s' if s['n'] != 1 else ''} (fewer than {args.min_n}); "
                         "its ratio is shown but cannot be relied on.")
        if RANK[level] > RANK[worst]:
            worst = level
        out_groups.append(entry)

    return {"attribute": attr, "reference_group": ref, "reference_rate": round(ref_rate, 4),
            "eo_reference_group": eo_ref,
            "excluded_records": excluded, "verdict": worst, "groups": out_groups, "notes": notes}


def markdown(results, args):
    lines = []
    for a in results:
        eo = f"; equal-opportunity reference: {a['eo_reference_group']}" if a.get("eo_reference_group") else ""
        lines.append(f"\n**{a['attribute']}**: verdict **{a['verdict']}** (selection reference: {a['reference_group']}{eo})\n")
        head = "| Group | n | Selection rate | Impact ratio | p | Verdict |"
        sep = "|---|---:|---:|---:|---:|---|"
        if args.qualified:
            head += " Qualified shortlisted | EO gap (pp) |"
            sep += "---:|---:|"
        if args.annual:
            head += " Est. people/yr |"
            sep += "---:|"
        lines += [head, sep]
        for g in a["groups"]:
            row = (f"| {g['group']} | {g['n']} | {g['selection_rate']:.1%} | {g['impact_ratio']:.2f} | "
                   f"{g['p_value']:.3f} | {g['verdict'].replace('_', ' ').title()} |")
            if args.qualified:
                tpr = g.get("true_positive_rate")
                row += f" {tpr:.1%} |" if tpr is not None else " – |"
                if g.get("eo_verdict") == "EO_REFERENCE":
                    row += " ref |"
                elif "eo_gap_pp" in g:
                    flag = {"UNEQUAL_OPPORTUNITY": " ✗", "POSSIBLE_UNEQUAL_OPPORTUNITY": " ?",
                            "INSUFFICIENT_DATA": " (small n)"}.get(g.get("eo_verdict"), "")
                    row += f" {g['eo_gap_pp']}{flag} |"
                else:
                    row += " – |"
            if args.annual:
                row += f" {g['est_annual_people_affected']:,} |" if "est_annual_people_affected" in g else " – |"
            lines.append(row)
        for n in a["notes"]:
            lines.append(f"\n> {n}")
    return "\n".join(lines).strip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--outcome", required=True, help="0/1 column: did the AI shortlist the candidate")
    ap.add_argument("--qualified", help="optional 0/1 column: independent expert judged the candidate qualified")
    ap.add_argument("--groups", required=True, help="comma-separated protected-attribute columns")
    ap.add_argument("--intersect", action="append", default=[], help="e.g. gender:age_band (repeatable)")
    ap.add_argument("--min-n", type=int, default=30)
    ap.add_argument("--threshold", type=float, default=0.80)
    ap.add_argument("--eo-threshold", type=float, default=0.10, help="max tolerated gap in true positive rate")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--annual", type=int, help="annual applications, to estimate people affected")
    ap.add_argument("--exclude", default="Prefer not to say,Not disclosed",
                    help="comma-separated values treated as missing")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    ap.add_argument("--audit-log")
    args = ap.parse_args()
    args.exclude = {v.strip() for v in args.exclude.split(",") if v.strip()}

    with open(args.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    attrs = [g.strip() for g in args.groups.split(",") if g.strip()]
    for spec in args.intersect:
        a, b = spec.split(":")
        name = f"{a} x {b}"
        for row in rows:
            va, vb = (row.get(a) or "").strip(), (row.get(b) or "").strip()
            row[name] = "" if (not va or not vb or va in args.exclude or vb in args.exclude) else f"{va} / {vb}"
        attrs.append(name)

    results = [analyse(rows, a, args.outcome, args.qualified, args) for a in attrs]
    overall = max((r["verdict"] for r in results), key=lambda v: RANK[v])
    failing = [r["attribute"] for r in results if r["verdict"] == "FAIL"]

    out = {
        "dataset": os.path.basename(args.csv),
        "records": len(rows),
        "overall_selection_rate": round(sum(int(r[args.outcome]) for r in rows) / len(rows), 4) if rows else None,
        "method": {"benchmark": "four-fifths rule (impact ratio < 0.80) with two-sided Fisher exact test",
                   "threshold": args.threshold, "alpha": args.alpha, "min_group_n": args.min_n,
                   "equal_opportunity_gap_threshold_pp": round(100 * args.eo_threshold, 1),
                   "qualified_label": args.qualified or None},
        "overall_verdict": overall,
        "attributes_failing": failing,
        "attributes": results,
        "red_lines": ([{"id": "RL-05", "title": "Statistically significant adverse impact or unequal opportunity",
                        "attributes": failing,
                        "basis": "Policy POL-AI-04; four-fifths benchmark (US Uniform Guidelines, 29 CFR 1607.4(D)); "
                                 "Code on Wages, 2019 s. 3 for gender.",
                        "remediable": True,
                        "remedy": "Find and remove the cause (features, labels or thresholds), then re-test on fresh shadow data."}]
                      if failing else []),
    }
    write_json(args.out, out)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(markdown(results, args))
    audit(args.audit_log, "adverse_impact.py", [args.csv], [args.out, args.md],
          {"overall": overall, "failing": failing, "records": len(rows)})

    print(f"Adverse impact {overall}: {len(rows)} records; " +
          "; ".join(f"{r['attribute']} {r['verdict']}" for r in results))


if __name__ == "__main__":
    main()
