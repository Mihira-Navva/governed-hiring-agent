#!/usr/bin/env python3
"""Render the committee decision memo from the review folder.

Usage:
    python render_memo.py --review-dir reviews/<id> [--audit-log reviews/<id>/audit-log.jsonl]

Combines the structured findings (decision.json and the files behind it) with the reviewer's
judgment (reviewer-notes.json, written by the agent) into decision-memo.md. Numbers and
conditions come only from the structured files, so the memo cannot drift from the evidence;
judgment comes only from the notes, so it is clearly the reviewer's.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, get, load_json, now_iso  # noqa: E402

TODO = "_[Reviewer to complete]_"


def opt(folder, name):
    p = os.path.join(folder, name)
    return load_json(p) if os.path.exists(p) else None


def bullets(items, empty="None."):
    return "\n".join(f"- {i}" for i in items) if items else empty


def journey_table(intake):
    rows = [
        ("Primary function", get(intake, "system.primary_function")),
        ("Stage of hiring", get(intake, "system.decision_stage")),
        ("Automation level", get(intake, "system.automation_level")),
        ("AI output", get(intake, "system.ai_output")),
        ("Human reviews every rejection", get(intake, "human_oversight.human_reviews_every_rejection")),
        ("Recruiter sees AI score first", get(intake, "human_oversight.ai_score_visible_before_independent_review")),
        ("Applications per year", f"{get(intake, 'use_case.annual_applications'):,}" if get(intake, "use_case.annual_applications") else None),
        ("Roles", ", ".join(get(intake, "use_case.roles_in_scope") or []) or None),
        ("Vendor", get(intake, "system.vendor_name")),
    ]
    fmt = lambda v: "unknown" if v is None else ("yes" if v is True else "no" if v is False else str(v).replace("_", " "))  # noqa: E731
    return "| Aspect | As submitted |\n|---|---|\n" + "\n".join(f"| {k} | {fmt(v)} |" for k, v in rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review-dir", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()
    f = args.review_dir

    intake = opt(f, "intake.json") or {}
    dec = load_json(os.path.join(f, "decision.json"))
    risk, proxy, fair, legal = opt(f, "risk.json"), opt(f, "proxy-screen.json"), opt(f, "fairness.json"), opt(f, "legal.json")
    comp = opt(f, "completeness.json") or {}
    notes = opt(f, "reviewer-notes.json") or {}
    lib = opt(f, "library-check.json")

    L = []
    L.append("# AI Use Case Approval: Decision Memo\n")
    L.append(f"**Proposal:** {intake.get('proposal_id')} · {intake.get('title') or ''}  ")
    L.append(f"**Organisation:** {get(intake, 'organisation.name') or 'unknown'}  ")
    L.append(f"**Submitted by:** {get(intake, 'submitted_by.name') or 'unknown'} ({get(intake, 'submitted_by.role') or 'role unknown'}), "
             f"{intake.get('submission_date') or 'date unknown'}  ")
    L.append(f"**Prepared by:** AI Use Case Approval Agent, {now_iso()[:10]}  ")
    L.append("**Status:** RECOMMENDATION. Awaiting decision of the AI Approval Committee.\n")

    L.append("## 1. Recommendation\n")
    L.append(f"> ### {dec['outcome_label']}\n> Rule {dec['rule_fired']} · Risk tier {dec.get('risk_tier')} "
             f"({(risk or {}).get('tier_label', 'n/a')}) · Approver: {dec.get('approver') or 'n/a'}\n>")
    L.append(f"> {notes.get('summary', TODO)}\n")

    L.append("## 2. Key findings\n")
    kf = notes.get("key_findings") or [f"{r['finding']} ({r['source']})" for r in dec["rationale"]]
    L.append("\n".join(f"{i}. {k}" for i, k in enumerate(kf, 1)) + "\n")

    L.append("## 3. What the system does to a candidate\n")
    L.append(journey_table(intake) + "\n")
    if notes.get("candidate_journey"):
        L.append(notes["candidate_journey"] + "\n")

    if risk:
        L.append("## 4. Risk profile\n")
        L.append(f"Score **{risk['score']}/21**, tier **{risk['tier']} ({risk['tier_label']})**"
                 f"{' (evaluative-system floor applied)' if risk.get('evaluative_floor_applied') else ''}. "
                 f"EU AI Act benchmark: {risk['regulatory_classification']['eu_ai_act']}.\n")
        L.append("| Dimension | Score | Reason |\n|---|---:|---|")
        for k, v in risk["dimensions"].items():
            L.append(f"| {k.replace('_', ' ').capitalize()} | {v['score']} | {v['reason']} |")
        L.append("")
        all_rl = [r for r in risk.get("red_lines", [])] + (proxy or {}).get("red_lines", []) + (fair or {}).get("red_lines", [])
        if all_rl:
            L.append("**Red lines crossed**\n")
            L.append("| ID | Red line | Basis | Remedy |\n|---|---|---|---|")
            for r in all_rl:
                L.append(f"| {r['id']} | {r['title']} | {r['basis']} | {r.get('remedy', '')} |")
            L.append("")
        for p in risk.get("prohibited_purpose", []):
            L.append(f"**Prohibited purpose {p['id']}:** {p['title']}. {p['basis']}\n")

    L.append("## 5. Fairness evidence\n")
    if proxy:
        L.append(f"**Input screen: {proxy['verdict']}.** {proxy['feature_count']} inputs: " +
                 ", ".join(f"{v} {k.replace('_', ' ').lower()}" for k, v in proxy["counts"].items() if v) + ".\n")
        L.append("| Input | Category | Linked to | Action |\n|---|---|---|---|")
        for x in proxy["features"]:
            L.append(f"| {x['feature']} | {x['category'].replace('_', ' ').title()} | {', '.join(x['linked_attributes']) or '–'} | {x['action'].split('.')[0]}. |")
        L.append("")
    if fair and fair.get("records"):
        L.append(f"**Outcome test: {fair['overall_verdict']}** on {fair['records']:,} shadow-mode records "
                 f"(four-fifths benchmark with Fisher exact test, α = {fair['method']['alpha']}; equal-opportunity gap threshold "
                 f"{fair['method']['equal_opportunity_gap_threshold_pp']} pp).\n")
        tables = os.path.join(f, "fairness-tables.md")
        if os.path.exists(tables):
            with open(tables, encoding="utf-8") as fh:
                L.append(fh.read())
    else:
        L.append("**Outcome test: not possible.** No shadow-mode or pilot data was supplied. Absence of evidence of bias "
                 "is not evidence of fairness.\n")
    if notes.get("fairness_interpretation"):
        L.append("**Interpretation.** " + notes["fairness_interpretation"] + "\n")

    if legal:
        s = legal["summary"]
        L.append("## 6. Legal and policy obligations\n")
        L.append(f"{len(legal['obligations'])} obligations apply: {s['MET']} met, {s['GAP']} gaps, {s['UNKNOWN']} unknown; "
                 f"**{legal['mandatory_open']} mandatory items open.** {legal['disclaimer']}\n")
        L.append("| ID | Instrument and provision | Force | Status | Owner |\n|---|---|---|---|---|")
        for o in legal["obligations"]:
            L.append(f"| {o['id']} | {o['instrument']}, {o['provision']} | {o['legal_status'].replace('_', ' ')} | "
                     f"**{o['status']}** | {o['owner']} |")
        L.append("")
        if notes.get("issues_for_counsel"):
            L.append("**Issues for counsel**\n\n" + bullets(notes["issues_for_counsel"]) + "\n")

    L.append(f"## 7. {dec['condition_framing']}\n")
    if dec["outcome"] == "REJECT":
        L.append("None. The purpose is not approvable; no conditions could make it so.\n")
    else:
        for label, items in (("Before go-live / resubmission", dec["conditions_precedent"]),
                             ("While the system operates", dec["conditions_subsequent"])):
            if not items:
                continue
            L.append(f"**{label}**\n")
            L.append("| # | Condition | Owner | Evidence | Deadline | Principle |\n|---|---|---|---|---|---|")
            for c in items:
                L.append(f"| {c['id']} | **{c['title']}.** {c['text']} | {c['owner']} | {c['evidence']} | {c['deadline']} | {c['principle']} |")
            L.append("")

    L.append("## 8. Escalations\n")
    L.append(bullets(dec["escalations"]) + "\n")

    L.append("## 9. Benefits and trade-offs\n")
    L.append((notes.get("benefits_and_tradeoffs") or TODO) + "\n")

    L.append("## 10. Reviewer judgment\n")
    L.append((notes.get("reviewer_judgment") or TODO) + "\n")
    if notes.get("hidden_risks"):
        L.append("**Risks the scripts cannot see**\n\n" + bullets(notes["hidden_risks"]) + "\n")

    L.append("## 11. What would change this recommendation\n")
    L.append(bullets(notes.get("what_would_change"), TODO) + "\n")

    L.append("## 12. Integrity observations\n")
    io = get(intake, "intake_notes.integrity_observations") or []
    L.append(bullets(io, "None. No text in the submission attempted to direct the reviewer.") + "\n")

    L.append("## 13. Assumptions, unknowns and limits of this review\n")
    assumptions = (get(intake, "intake_notes.assumptions") or []) + (notes.get("assumptions") or [])
    L.append("**Assumptions made at intake**\n\n" + bullets(assumptions) + "\n")
    L.append(f"**Unanswered questions for the proposer ({len(dec['open_questions'])})**\n\n" +
             bullets(dec["open_questions"]) + "\n")
    L.append("**Limits.** This review relies on the submission and on the approved skill library. The keyword screen "
             "cannot see proxies inside composite scores; outcome tests reflect the pilot population only; legal findings "
             "identify obligations and are not legal advice; and the decision rules encode policy, not truth. "
             "The committee's judgment is required.\n")

    L.append("## 14. Committee decision\n")
    L.append("*To be completed by the AI Approval Committee. The agent does not complete this section.*\n")
    L.append("| | |\n|---|---|")
    L.append("| Decision | ☐ Approve ☐ Approve with conditions ☐ Pilot only ☐ Redesign and resubmit ☐ Reject ☐ Return for information |")
    L.append("| Conditions accepted / amended | |")
    L.append("| Departure from recommendation, with reasons | |")
    L.append("| Dissent recorded | |")
    L.append("| Accountable executive | |")
    L.append("| Re-review date | |")
    L.append("| Chair signature and date | |\n")

    L.append("---\n## Appendix A. Audit trail\n")
    if lib:
        L.append(f"Skill library check: **{lib.get('status')}** ({lib.get('checked_at', '')}). "
                 + ", ".join(f"{s['name']} v{s['version']}" for s in lib.get("skills", [])) + "\n")
    log = os.path.join(f, "audit-log.jsonl")
    if os.path.exists(log):
        L.append("| Time (UTC) | Skill | Version | Script | Inputs (SHA-256, first 12) | Result |\n|---|---|---|---|---|---|")
        with open(log, encoding="utf-8") as fh:
            for line in fh:
                e = json.loads(line)
                ins = "; ".join(f"{k} {v[:12]}" for k, v in e["inputs"].items())
                res = ", ".join(f"{k}={v}" for k, v in e["summary"].items() if not isinstance(v, (dict, list)) or v)
                L.append(f"| {e['ts'][11:19]} | {e['skill']} | {e['version']} | {e['script']} | {ins} | {res} |")
        L.append("")
    L.append("**Finding codes:** " + ", ".join(f"`{c}`" for c in dec["finding_codes"]) + "\n")

    out = os.path.join(f, "decision-memo.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    audit(args.audit_log, "render_memo.py", [os.path.join(f, "decision.json"), os.path.join(f, "reviewer-notes.json")],
          [out], {"outcome": dec["outcome"]})
    print(f"Memo written: {out}")


if __name__ == "__main__":
    main()
