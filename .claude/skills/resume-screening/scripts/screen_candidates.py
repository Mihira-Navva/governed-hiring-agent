#!/usr/bin/env python3
"""Screen candidates against a job specification, using only blind profiles and application answers.

Usage:
    python screen_candidates.py --spec job-spec.json --blind blind-profiles.json \
        --applications applications.csv --out screening.json [--audit-log audit-log.jsonl]

For every candidate it reports:
  * each hard requirement as PASS, FAIL or UNCLEAR, with the evidence (a quoted line, or the fact that
    nothing was found where it was looked for);
  * each scored criterion's sub-score 0-100 with the evidence behind it, and the weighted total;
  * the exact list of inputs used, so the guardian can verify nothing else was read.
Candidates who asked for a human-only assessment, or did not consent to AI screening, are not scored.
"""
import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, load_json, write_json  # noqa: E402


def blind_lines(p):
    lines = [("certifications", c) for c in p["certifications"]]
    lines += [("skills", ", ".join(p["skills"]))] if p["skills"] else []
    for e in p["experience"]:
        lines.append(("experience", e["title"]))
        lines += [("experience", d) for d in e["details"]]
    return lines


def check_hard(req, profile, app):
    if req["evidence"] == "application_answer":
        val = (app.get(req["field"]) or "").strip()
        if not val:
            return "UNCLEAR", f"Application question '{req['field']}' not answered"
        ok = val in req["pass_values"]
        return ("PASS" if ok else "FAIL"), f"Application answer {req['field']} = '{val}'"
    hits = []
    for section, line in blind_lines(profile):
        low = line.lower()
        if any(m in low for m in req["match_any"]):
            hits.append((section, line))
    if not hits:
        # also look for the requirement being in progress anywhere in kept text
        for section, line in blind_lines(profile):
            low = line.lower()
            stem = req["match_any"][0].split()[0]
            if stem in low and any(a in low for a in req.get("ambiguous_if_any", [])):
                return "UNCLEAR", f"In progress, not held: \"{line}\" ({section})"
        return "FAIL", "Not found in certifications, skills or experience"
    section, line = hits[0]
    if any(a in line.lower() for a in req.get("ambiguous_if_any", [])):
        return "UNCLEAR", f"\"{line}\" ({section})"
    return "PASS", f"\"{line}\" ({section})"


def score_criterion(c, profile, app):
    ev = c["evidence"]
    if ev == "application_field":
        raw = (app.get(c["field"]) or "").strip()
        if c.get("map"):
            if raw not in c["map"] or c["map"][raw] is None:
                return None, f"{c['field']} = '{raw or 'blank'}' (cannot score)"
            return c["map"][raw], f"{c['field']} = '{raw}'"
        if raw == "":
            return None, f"{c['field']} missing (cannot score)"
        return max(0, min(100, float(raw))), f"{c['field']} = {raw}"
    if ev == "resume_experience_months":
        words = [w.lower() for w in c["counts_if_any"]]
        counted, used = 0, []
        for e in profile["experience"]:
            text = (e["title"] + " " + " ".join(e["details"])).lower()
            if e["months"] and any(re.search(rf"\b{re.escape(w)}", text) for w in words):
                counted += e["months"]
                used.append(f"{e['title']} ({e['months']} months)")
        capped = min(counted, c["cap_months"])
        return round(100 * capped / c["cap_months"], 1), (f"{counted} relevant months, capped at {c['cap_months']}: " +
                                                        ("; ".join(used) if used else "no relevant roles found"))
    if ev == "resume_skills":
        text = " ".join(l for _, l in blind_lines(profile)).lower()
        found = [s for s in c["skills"] if s.lower() in text]
        return round(100 * min(len(found), c["full_marks_at"]) / c["full_marks_at"], 1), \
            f"{len(found)} of {len(c['skills'])} listed: {', '.join(found) if found else 'none'}"
    raise ValueError(ev)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--blind", required=True)
    ap.add_argument("--applications", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()

    spec = load_json(args.spec)
    profiles = {p["candidate_id"]: p for p in load_json(args.blind)["profiles"]}
    with open(args.applications, newline="", encoding="utf-8") as fh:
        apps = {r["candidate_id"]: r for r in csv.DictReader(fh)}

    app_fields = sorted({h["field"] for h in spec["hard_requirements"] if h["evidence"] == "application_answer"} |
                        {c["field"] for c in spec["scored_criteria"] if c["evidence"] == "application_field"})
    results = []
    for cid in sorted(apps):
        app, p = apps[cid], profiles.get(cid)
        base = {"candidate_id": cid, "accommodation_requested": app.get("accommodation_requested") == "Yes"}
        if app.get("human_only_requested") == "Yes" or app.get("consent_ai") != "Yes":
            results.append({**base, "status": "NOT_SCORED_HUMAN_ONLY",
                            "reason": "Candidate asked for a human-only assessment" if app.get("human_only_requested") == "Yes"
                            else "No consent to AI screening", "inputs_used": []})
            continue
        if p is None:
            results.append({**base, "status": "NOT_SCORED_NO_RESUME", "reason": "No resume file", "inputs_used": []})
            continue
        hard = []
        for h in spec["hard_requirements"]:
            res, ev = check_hard(h, p, app)
            hard.append({"id": h["id"], "requirement": h["requirement"], "result": res, "evidence": ev})
        crit, total, unscorable = [], 0.0, []
        for c in spec["scored_criteria"]:
            sub, ev = score_criterion(c, p, app)
            crit.append({"id": c["id"], "criterion": c["criterion"], "weight": c["weight"], "score": sub, "evidence": ev})
            if sub is None:
                unscorable.append(c["id"])
            else:
                total += c["weight"] * sub / 100
        results.append({**base, "status": "SCORED", "parse_confidence": p["parse_confidence"],
                        "integrity_flags": p["integrity_flags"], "hard_requirements": hard, "criteria": crit,
                        "total": None if unscorable else round(total, 1), "unscorable": unscorable,
                        "inputs_used": ["blind_profile.experience", "blind_profile.certifications", "blind_profile.skills"]
                                       + [f"application.{f}" for f in app_fields]})

    write_json(args.out, {"requisition_id": spec["requisition_id"], "candidates": results})
    scored = [r for r in results if r["status"] == "SCORED"]
    audit(args.audit_log, "screen_candidates.py", [args.spec, args.blind, args.applications], [args.out],
          {"candidates": len(results), "scored": len(scored)})
    print(f"Screened {len(results)} applications: {len(scored)} scored, {len(results) - len(scored)} not scored by AI")


if __name__ == "__main__":
    main()
