#!/usr/bin/env python3
"""Evaluation suite for the AI hiring approval skill library.

Usage:
    python evals/run_evals.py

Three layers, mirroring how the library is governed:
  1. Unit tests: the statistics, the proxy screen and the three-valued legal logic give
     known-correct answers.
  2. Scenario tests: complete reviews of 14 proposals (evals/cases.json), including
     adversarial ones, reach the expected outcome for the expected reasons.
  3. Library integrity: a tampered skill is detected and refused.

Writes evals/results.json and evals/results.md. Critical cases must all pass before release.
"""
import copy
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SK = os.path.join(ROOT, ".claude", "skills")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import run_review  # noqa: E402
import hiring_evals  # noqa: E402


def deep_merge(base, patch):
    out = copy.deepcopy(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def import_from(skill, module):
    path = os.path.join(SK, skill, "scripts")
    sys.path.insert(0, path)
    try:
        if module in sys.modules:
            del sys.modules[module]
        if "skillkit" in sys.modules:
            del sys.modules["skillkit"]
        return __import__(module)
    finally:
        sys.path.remove(path)


# ---------------------------------------------------------------- unit tests

def unit_tests():
    results = []

    def check(name, skill, ok, detail=""):
        results.append({"id": name, "skill": skill, "passed": bool(ok), "detail": detail})

    ai = import_from("fairness-bias-review", "adverse_impact")
    p1 = ai.fisher_exact(3, 1, 1, 3)
    check("U01 Fisher exact, classic tea-tasting table = 0.4857", "fairness-bias-review", abs(p1 - 0.4857) < 1e-4, f"{p1:.4f}")
    p2 = ai.fisher_exact(1, 9, 11, 3)
    check("U02 Fisher exact [[1,9],[11,3]] = 0.002759", "fairness-bias-review", abs(p2 - 0.002759) < 1e-5, f"{p2:.6f}")
    p3 = ai.fisher_exact(10, 10, 10, 10)
    check("U03 Fisher exact, identical groups = 1.0", "fairness-bias-review", abs(p3 - 1.0) < 1e-9, f"{p3:.4f}")

    ps = import_from("fairness-bias-review", "proxy_screen")
    d = json.load(open(os.path.join(SK, "fairness-bias-review", "references", "proxy-dictionary.json")))
    expected = {
        "Graduation year": "STRONG_PROXY", "Employment gaps (months)": "STRONG_PROXY",
        "Current location PIN code": "STRONG_PROXY", "College tier": "STRONG_PROXY",
        "Date of birth": "PROTECTED", "Marital status": "PROTECTED", "Candidate photo": "PROTECTED",
        "Aptitude test score": "JOB_RELATED", "Structured interview rating": "JOB_RELATED",
        "Current CTC": "MODERATE_PROXY", "Video communication confidence score": "STRONG_PROXY",
        "Hobbies and interests": "MODERATE_PROXY", "Typing speed": "UNCLASSIFIED",
        "Language used in messages": "UNCLASSIFIED",
    }
    for feat, want in expected.items():
        got = ps.classify(feat, d["rules"], d["priority"])[0]
        check(f"U04 Proxy screen: '{feat}' -> {want}", "fairness-bias-review", got == want, got)

    ob = import_from("legal-privacy-review", "obligations")
    ctx = {"a": {"t": True, "f": False, "n": None, "list": ["IN"]}}
    cases = [
        ({"field": "a.t", "op": "eq", "value": True}, True),
        ({"field": "a.n", "op": "eq", "value": True}, None),
        ({"all": [{"field": "a.t", "op": "eq", "value": True}, {"field": "a.n", "op": "eq", "value": True}]}, None),
        ({"all": [{"field": "a.f", "op": "eq", "value": True}, {"field": "a.n", "op": "eq", "value": True}]}, False),
        ({"any": [{"field": "a.n", "op": "eq", "value": True}, {"field": "a.t", "op": "eq", "value": True}]}, True),
        ({"field": "a.list", "op": "contains", "value": "EU"}, False),
    ]
    for i, (cond, want) in enumerate(cases, 1):
        got = ob.evaluate(cond, ctx)
        check(f"U05.{i} Three-valued logic returns {want}", "legal-privacy-review", got is want, str(got))
    return results


# ---------------------------------------------------------------- scenario tests

def make_small_group_csv(path):
    """600 records where every group has the same 40% selection rate except 20 disabled applicants (2/20).

    Built deterministically rather than randomly: a random version produced a 'significant' gender gap by
    chance, which is exactly the multiple-comparisons trap described in fairness-methods.md.
    """
    rows = []
    for i in range(600):
        disability = "Yes" if i < 20 else "No"
        shortlisted = (1 if i in (0, 1) else 0) if disability == "Yes" else (1 if i % 5 in (0, 1) else 0)
        rows.append({"candidate_id": f"S{i:04d}", "gender": ["Man", "Woman"][i % 2],
                     "age_band": ["21-29", "30-39", "40+"][(i // 2) % 3],
                     "home_region": ["West", "South", "North", "East & North-East"][(i // 6) % 4],
                     "disability": disability, "ai_shortlisted": shortlisted, "expert_qualified": ""})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def scenario_tests():
    spec = json.load(open(os.path.join(ROOT, "evals", "cases.json")))
    bases = {k: json.load(open(os.path.join(ROOT, v))) for k, v in spec["bases"].items()}
    make_small_group_csv(os.path.join(ROOT, "evals", "data", "small-group.csv"))
    results = []
    work = tempfile.mkdtemp(prefix="evals-")
    for case in spec["cases"]:
        folder = os.path.join(work, case["id"])
        os.makedirs(folder)
        intake = deep_merge(bases[case["base"]], case["patch"])
        intake["proposal_id"] = f"EVAL-{case['id']}"
        json.dump(intake, open(os.path.join(folder, "intake.json"), "w"), indent=2)
        pilot = os.path.join(ROOT, case["pilot"]) if case.get("pilot") else None
        dec = run_review(folder, pilot, quiet=True, verify=False)
        risk = json.load(open(os.path.join(folder, "risk.json")))
        comp = json.load(open(os.path.join(folder, "completeness.json")))
        legal = json.load(open(os.path.join(folder, "legal.json")))
        fair = json.load(open(os.path.join(folder, "fairness.json"))) if os.path.exists(os.path.join(folder, "fairness.json")) else {}

        exp, fails = case["expect"], []
        red = {c for c in dec["finding_codes"] if c.startswith("RL-")}
        conds = {c["id"] for c in dec["conditions_precedent"] + dec["conditions_subsequent"]}
        if "outcome" in exp and dec["outcome"] != exp["outcome"]:
            fails.append(f"outcome {dec['outcome']} != {exp['outcome']}")
        if "tier" in exp and risk["tier"] != exp["tier"]:
            fails.append(f"tier {risk['tier']} != {exp['tier']}")
        if "red_lines" in exp and red != set(exp["red_lines"]):
            fails.append(f"red lines {sorted(red)} != {exp['red_lines']}")
        for c in exp.get("conditions", []):
            if c not in conds:
                fails.append(f"missing condition {c}")
        if "conditions_count" in exp and len(conds) != exp["conditions_count"]:
            fails.append(f"{len(conds)} conditions, expected {exp['conditions_count']}")
        if "questions_include" in exp and not any(exp["questions_include"] in q for q in dec["open_questions"]):
            fails.append("expected question not asked")
        for w in exp.get("warnings", []):
            if w not in {x["code"] for x in comp["consistency_warnings"]}:
                fails.append(f"missing warning {w}")
        for o in exp.get("obligations", []):
            if o not in {x["id"] for x in legal["obligations"]}:
                fails.append(f"obligation {o} not applied")
        for e in exp.get("escalations", []):
            if e not in dec["escalations"]:
                fails.append(f"no escalation to {e}")
        if "fairness_overall" in exp and fair.get("overall_verdict") != exp["fairness_overall"]:
            fails.append(f"fairness {fair.get('overall_verdict')} != {exp['fairness_overall']}")

        results.append({"id": case["id"], "title": case["title"], "critical": case["critical"], "passed": not fails,
                        "outcome": dec["outcome_label"], "rule": dec["rule_fired"], "tier": risk["tier"],
                        "red_lines": sorted(red), "why": case["why"], "failures": fails})
    shutil.rmtree(work)
    return results


# ---------------------------------------------------------------- integrity test

def integrity_test():
    work = tempfile.mkdtemp(prefix="tamper-")
    try:
        copy_dir = os.path.join(work, "skills")
        shutil.copytree(SK, copy_dir, ignore=shutil.ignore_patterns("__pycache__"))
        verify = os.path.join(ROOT, "library", "scripts", "verify_library.py")
        clean = subprocess.run([sys.executable, verify, "--skills-dir", copy_dir], capture_output=True, text=True).returncode
        target = os.path.join(copy_dir, "risk-tiering", "references", "risk-criteria.json")
        crit = json.load(open(target))
        crit["evaluative_floor"] = "T1"  # quietly weaken the rubric
        json.dump(crit, open(target, "w"), indent=2)
        tampered = subprocess.run([sys.executable, verify, "--skills-dir", copy_dir], capture_output=True, text=True)
        net = os.path.join(copy_dir, "legal-privacy-review", "scripts", "obligations.py")
        with open(net, "a") as fh:
            fh.write("\nimport urllib.request  # exfiltration attempt\n")
        perm = subprocess.run([sys.executable, verify, "--skills-dir", copy_dir], capture_output=True, text=True)
        return [
            {"id": "I01 Untouched copy of the library verifies", "passed": clean == 0, "detail": f"exit {clean}"},
            {"id": "I02 Weakened risk rubric is detected (integrity)", "passed": tampered.returncode == 1 and "risk-tiering" in tampered.stdout
             and "content changed" in tampered.stdout, "detail": "risk-tiering FAIL: content changed"},
            {"id": "I03 Undeclared network import is detected (permissions)", "passed": perm.returncode == 1 and "urllib" in perm.stdout,
             "detail": "legal-privacy-review FAIL: imports 'urllib'"},
        ]
    finally:
        shutil.rmtree(work)


def main():
    units, scenarios, integrity = unit_tests(), scenario_tests(), integrity_test()
    hiring = hiring_evals.run()
    crit = [s for s in scenarios if s["critical"]]
    summary = {
        "unit": f"{sum(u['passed'] for u in units)}/{len(units)}",
        "scenarios": f"{sum(s['passed'] for s in scenarios)}/{len(scenarios)}",
        "critical_scenarios": f"{sum(s['passed'] for s in crit)}/{len(crit)}",
        "integrity": f"{sum(i['passed'] for i in integrity)}/{len(integrity)}",
        "hiring_and_guardian": f"{sum(h['passed'] for h in hiring)}/{len(hiring)}",
        "release_gate": "PASS" if all(u["passed"] for u in units) and all(s["passed"] for s in crit) and all(i["passed"] for i in integrity)
                        and all(h["passed"] for h in hiring) else "FAIL",
    }
    by_skill = {}
    for u in units:
        b = by_skill.setdefault(u["skill"], {"unit_passed": 0, "unit_total": 0})
        b["unit_passed"] += u["passed"]
        b["unit_total"] += 1
    for name in os.listdir(SK):
        by_skill.setdefault(name, {"unit_passed": 0, "unit_total": 0})["scenario_pass_rate"] = summary["scenarios"]

    for h in hiring:
        b = by_skill.setdefault(h["area"], {"unit_passed": 0, "unit_total": 0})
        b["unit_passed"] += h["passed"]
        b["unit_total"] += 1
    out = {"summary": summary, "by_skill": by_skill, "unit": units, "scenarios": scenarios, "integrity": integrity, "hiring": hiring}
    json.dump(out, open(os.path.join(ROOT, "evals", "results.json"), "w"), indent=2)

    md = ["# Evaluation results\n", f"**Release gate: {summary['release_gate']}** · unit {summary['unit']} · "
          f"scenarios {summary['scenarios']} (critical {summary['critical_scenarios']}) · integrity {summary['integrity']} · "
          f"hiring agent and guardian {summary['hiring_and_guardian']}\n",
          "## Scenario tests\n", "| ID | Scenario | Critical | Outcome | Rule | Tier | Red lines | Result | Why it matters |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s in scenarios:
        md.append(f"| {s['id']} | {s['title']} | {'yes' if s['critical'] else ''} | {s['outcome']} | {s['rule']} | {s['tier']} | "
                  f"{', '.join(s['red_lines']) or '–'} | {'PASS' if s['passed'] else 'FAIL: ' + '; '.join(s['failures'])} | {s['why']} |")
    md += ["\n## Unit tests\n", "| Test | Result | Detail |", "|---|---|---|"]
    md += [f"| {u['id']} | {'PASS' if u['passed'] else 'FAIL'} | {u['detail']} |" for u in units]
    md += ["\n## Hiring agent and guardian tests\n", "| Test | Area | Result | Detail |", "|---|---|---|---|"]
    md += [f"| {h['id']} | {h['area']} | {'PASS' if h['passed'] else 'FAIL'} | {h['detail']} |" for h in hiring]
    md += ["\n## Library integrity tests\n", "| Test | Result | Detail |", "|---|---|---|"]
    md += [f"| {i['id']} | {'PASS' if i['passed'] else 'FAIL'} | {i['detail']} |" for i in integrity]
    open(os.path.join(ROOT, "evals", "results.md"), "w").write("\n".join(md) + "\n")

    for s in scenarios:
        print(f"  {'PASS' if s['passed'] else 'FAIL'}  {s['id']} {s['title']}: {s['outcome']}" + (f"  {s['failures']}" if s["failures"] else ""))
    for u in units + integrity + hiring:
        if not u["passed"]:
            print(f"  FAIL  {u['id']}: {u['detail']}")
    print(f"Unit {summary['unit']} · scenarios {summary['scenarios']} (critical {summary['critical_scenarios']}) · "
          f"integrity {summary['integrity']} · hiring/guardian {summary['hiring_and_guardian']} · release gate {summary['release_gate']}")
    sys.exit(0 if summary["release_gate"] == "PASS" else 1)


if __name__ == "__main__":
    main()
