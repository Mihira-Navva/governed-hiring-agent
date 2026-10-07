#!/usr/bin/env python3
"""Runtime guardian: check a batch of proposed hiring decisions before any of them takes effect.

Usage:
    python guard_decisions.py --run <run_dir> --governance <governance_dir> [--today YYYY-MM-DD] \
        [--audit-log audit-log.jsonl]

Reads from <run_dir>: job-spec.json, spec-gate.json, screening.json, decisions.json, letters/.
Reads from <governance_dir>: runtime-policy.json, autonomy-state.json (if any),
audit-data/self-declarations.csv (voluntary; only the guardian reads it), decision-ledger.jsonl.

Per decision (independently of what the hiring agent claims):
  G1 the action is allowed at the effective autonomy level, recomputed here from policy and state;
  G2 an automated rejection rests on a cleanly failed hard requirement with a legal/operational basis;
  G3 scoring read only permitted inputs (blind profile + application fields named in the spec);
  G4 every outcome letter carries the AI notice and the 14-day appeal route;
  G5 integrity-flagged and human-only candidates are never handled autonomously;
  G6 the job spec used is byte-for-byte the one the criteria gate cleared.
Autonomous decisions that pass are RELEASED; everything else goes to the human queue with a reason.

Per batch:
  * fairness monitor: advancement rate by self-declared group over all AI-handled decisions so far
    (ledger history + this batch); impact ratio with Fisher exact test -> GREEN / AMBER / RED;
  * circuit breaker: RED lowers autonomy to the policy's fallback level (L1) in autonomy-state.json and
    routes every autonomous decision in this batch to a person;
  * blind audit sample of released decisions (policy rate), chosen reproducibly;
  * every decision appended to the hash-chained ledger.
"""
import argparse
import csv
import datetime as dt
import hashlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger  # noqa: E402
from skillkit import audit, load_json, now_iso, write_json  # noqa: E402

ORDER = ["L0", "L1", "L2", "L3"]
AUTONOMOUS_ALLOWED = {"L0": set(), "L1": set(), "L2": {"AUTO_ADVANCE", "AUTO_REJECT_HARD_REQUIREMENT"},
                      "L3": {"AUTO_ADVANCE", "AUTO_REJECT_HARD_REQUIREMENT", "AUTO_REJECT_LOW_SCORE"}}
FAVOURABLE = {"AUTO_ADVANCE", "PROPOSE_ADVANCE"}


def _lc(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def fisher(a, b, c, d):
    r1, n, c1 = a + b, a + b + c + d, a + c
    if n == 0 or r1 in (0, n) or c1 in (0, n):
        return 1.0
    den = _lc(n, r1)
    p = lambda x: math.exp(_lc(c1, x) + _lc(n - c1, r1 - x) - den)  # noqa: E731
    po = p(a)
    return min(1.0, sum(v for v in (p(x) for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1)) if v <= po * (1 + 1e-7)))


def effective_level(policy, state, today):
    sig = (policy or {}).get("committee_signature") or {}
    if not policy or not sig.get("signed_by") or not (policy["valid_from"] <= today <= policy["valid_until"]):
        return "L0"
    lvl = policy["autonomy_level"]
    s = (state or {}).get("autonomy_level")
    return s if s and ORDER.index(s) < ORDER.index(lvl) else lvl


def fairness_monitor(records, groups_by_id, attrs, cfg):
    results, status = [], "GREEN"
    rank = {"GREEN": 0, "AMBER": 1, "RED": 2}
    for attr in attrs:
        g = {}
        for r in records:
            val = (groups_by_id.get(r["candidate_id"]) or {}).get(attr, "")
            if not val or val in ("Prefer not to say", "Not disclosed"):
                continue
            s = g.setdefault(val, [0, 0])
            s[0] += 1
            s[1] += r["action"] in FAVOURABLE
        sized = {k: v for k, v in g.items() if v[0] >= cfg["min_group_n"]}
        if len(sized) < 2:
            results.append({"attribute": attr, "status": "AMBER", "note": f"fewer than two groups with {cfg['min_group_n']}+ records yet",
                            "groups": {k: {"n": v[0], "advanced": v[1]} for k, v in g.items()}})
            status = max(status, "AMBER", key=rank.get)
            continue
        ref = max(sized, key=lambda k: sized[k][1] / sized[k][0])
        rn, rs = sized[ref]
        a_status, rows = "GREEN", {}
        for k, (n, s) in g.items():
            ratio = (s / n) / (rs / rn) if rs else 1.0
            p = 1.0 if k == ref else fisher(s, n - s, rs, rn - rs)
            v = "OK"
            if k != ref and n < cfg["min_group_n"]:
                v = "INSUFFICIENT"
                a_status = max(a_status, "AMBER", key=rank.get)
            elif k != ref and ratio < cfg["impact_ratio_threshold"] and p < cfg["alpha"]:
                v, a_status = "ADVERSE_IMPACT", "RED"
            elif k != ref and ratio < cfg["impact_ratio_threshold"]:
                v = "POSSIBLE"
                a_status = max(a_status, "AMBER", key=rank.get)
            rows[k] = {"n": n, "advanced": s, "rate": round(s / n, 3), "impact_ratio": round(ratio, 2), "p": round(p, 4), "verdict": v}
        results.append({"attribute": attr, "status": a_status, "reference": ref, "groups": rows})
        status = max(status, a_status, key=rank.get)
    return status, results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--governance", required=True)
    ap.add_argument("--today", default=dt.date.today().isoformat())
    ap.add_argument("--audit-log")
    args = ap.parse_args()
    R, G = args.run, args.governance
    j = lambda d, f: os.path.join(d, f)  # noqa: E731

    spec, gate = load_json(j(R, "job-spec.json")), load_json(j(R, "spec-gate.json"))
    screening, dec = load_json(j(R, "screening.json")), load_json(j(R, "decisions.json"))
    policy = load_json(j(G, "runtime-policy.json")) if os.path.exists(j(G, "runtime-policy.json")) else None
    state_path = j(G, "autonomy-state.json")
    state = load_json(state_path) if os.path.exists(state_path) else None
    level = effective_level(policy, state, args.today)
    with open(j(R, "job-spec.json"), "rb") as fh:
        spec_hash = hashlib.sha256(fh.read()).hexdigest()
    spec_ok = gate.get("result") == "PASS" and gate.get("spec_sha256") == spec_hash

    scr = {c["candidate_id"]: c for c in screening["candidates"]}
    hard = {h["id"]: h for h in spec["hard_requirements"]}
    allowed_inputs = {"blind_profile.experience", "blind_profile.certifications", "blind_profile.skills"} | \
        {f"application.{h['field']}" for h in spec["hard_requirements"] if h["evidence"] == "application_answer"} | \
        {f"application.{c['field']}" for c in spec["scored_criteria"] if c["evidence"] == "application_field"}

    checked = []
    for d in dec["decisions"]:
        cid, s, problems = d["candidate_id"], scr.get(d["candidate_id"], {}), []
        if d["autonomous"]:
            if not spec_ok:
                problems.append("G6 job spec differs from the one the criteria gate cleared")
            if d["action"] not in AUTONOMOUS_ALLOWED[level]:
                problems.append(f"G1 '{d['action']}' is not allowed to act alone at level {level}")
            if d["action"] == "AUTO_REJECT_HARD_REQUIREMENT":
                fails = [h for h in s.get("hard_requirements", []) if h["result"] == "FAIL"]
                if not fails or any(h["result"] == "UNCLEAR" for h in s.get("hard_requirements", [])):
                    problems.append("G2 no clean hard-requirement failure in the screening record")
                elif hard[fails[0]["id"]].get("basis") not in ("regulatory", "operational", "safety"):
                    problems.append("G2 failed requirement has no legal, operational or safety basis")
            extra = set(s.get("inputs_used", [])) - allowed_inputs
            if extra:
                problems.append(f"G3 scoring read inputs outside the blind profile and spec: {sorted(extra)}")
            if s.get("integrity_flags") or s.get("status") != "SCORED":
                problems.append("G5 integrity-flagged or human-only candidate handled autonomously")
            if d["action"].startswith("AUTO_REJECT"):
                txt = ""
                if d.get("letter") and os.path.exists(j(j(R, "letters"), d["letter"])):
                    with open(j(j(R, "letters"), d["letter"]), encoding="utf-8") as fh:
                        txt = fh.read().lower()
                if not ("ai system helped" in txt and "within 14 days" in txt and "review your application again" in txt):
                    problems.append("G4 rejection letter lacks the AI notice or the appeal route")
            status = "RELEASED" if not problems else "ROUTED_TO_HUMAN"
        else:
            status = "QUEUED_FOR_HUMAN"
        checked.append({**d, "guardian_status": status, "guardian_problems": problems})

    # fairness monitor over everything the AI has handled so far
    groups_by_id = {}
    audit_csv = j(j(G, "audit-data"), "self-declarations.csv")
    if os.path.exists(audit_csv):
        with open(audit_csv, newline="", encoding="utf-8") as fh:
            groups_by_id = {r["candidate_id"]: r for r in csv.DictReader(fh)}
    history = [e for e in ledger.read(j(G, "decision-ledger.jsonl")) if e.get("ai_handled")]
    current = [c for c in checked if c["action"] != "HUMAN_ONLY"]
    cfg = policy.get("fairness_monitor", {}) if policy else {}
    cfg = {"min_group_n": cfg.get("min_group_n", 30), "impact_ratio_threshold": cfg.get("impact_ratio_threshold", 0.8),
           "alpha": cfg.get("alpha", 0.05)}
    records = [{"candidate_id": e["candidate_id"], "action": e["action"]} for e in history] + \
              [{"candidate_id": c["candidate_id"], "action": c["action"]} for c in current]
    attrs = ["gender", "age_band", "home_region", "disability"]
    fstatus, fresults = fairness_monitor(records, groups_by_id, attrs, cfg)

    # informational: who is rejected by hard requirements (a lawful requirement can still fall unequally)
    hr_rates = {}
    for attr in attrs:
        g = {}
        for rec in records:
            val = (groups_by_id.get(rec["candidate_id"]) or {}).get(attr, "")
            if not val or val in ("Prefer not to say", "Not disclosed"):
                continue
            s = g.setdefault(val, [0, 0])
            s[0] += 1
            s[1] += rec["action"] == "AUTO_REJECT_HARD_REQUIREMENT"
        hr_rates[attr] = {k: {"n": n, "rejected_on_hard_requirement": x, "rate": round(x / n, 3)} for k, (n, x) in g.items()}

    breaker = None
    if fstatus == "RED":
        fallback = (policy or {}).get("circuit_breaker", {}).get("fallback_level", "L1")
        red = [r["attribute"] for r in fresults if r["status"] == "RED"]
        breaker = {"autonomy_level": fallback, "set_by": "hiring-guardian", "set_at": now_iso(),
                   "reason": f"Circuit breaker: significant adverse impact in advancement by {', '.join(red)}",
                   "restore": "Only the AI Approval Committee can restore autonomy, by issuing a new signed runtime policy after review."}
        write_json(state_path, breaker)
        for c in checked:
            if c["guardian_status"] == "RELEASED":
                c["guardian_status"] = "ROUTED_TO_HUMAN"
                c["guardian_problems"].append("Circuit breaker tripped: autonomy withdrawn for this batch")

    # blind audit sample of released decisions, chosen reproducibly from a hash
    rate = (policy or {}).get("audit_sample_rate", 0.10)
    released = [c for c in checked if c["guardian_status"] == "RELEASED"]
    k = math.ceil(rate * len(released)) if released else 0
    pick = sorted(released, key=lambda c: hashlib.sha256(f"{spec_hash}:{c['candidate_id']}".encode()).hexdigest())[:k]
    for c in checked:
        c["blind_audit_sample"] = c in pick

    entries = ledger.append(j(G, "decision-ledger.jsonl"), [{
        "ts": now_iso(), "requisition_id": dec["requisition_id"], "candidate_id": c["candidate_id"], "action": c["action"],
        "autonomous": c["autonomous"], "guardian_status": c["guardian_status"], "ai_handled": c["action"] != "HUMAN_ONLY",
        "policy_id": (policy or {}).get("policy_id"), "level": level, "spec_sha256": spec_hash,
        "reasons_sha256": hashlib.sha256(" ".join(c["reasons"]).encode()).hexdigest()} for c in checked])

    counts = {}
    for c in checked:
        counts[c["guardian_status"]] = counts.get(c["guardian_status"], 0) + 1
    report = {"requisition_id": dec["requisition_id"], "checked_at": now_iso(), "effective_level": level,
              "agent_claimed_level": dec["effective_level"], "spec_cleared_and_unchanged": spec_ok,
              "counts": counts, "fairness_status": fstatus, "fairness": fresults,
              "fairness_records": len(records), "hard_requirement_rejections_by_group": hr_rates,
              "circuit_breaker": breaker,
              "blind_audit_sample": [c["candidate_id"] for c in pick],
              "ledger": {"appended": len(entries), "last_hash": entries[-1]["hash"] if entries else None},
              "decisions": checked}
    write_json(j(R, "guardian-report.json"), report)

    q = [c for c in checked if c["guardian_status"] != "RELEASED"]
    lines = [f"# Human review queue: {dec['requisition_id']}", "",
             f"Effective autonomy: **{level}** · fairness monitor: **{fstatus}** · "
             f"{len(q)} candidates need a person · {len(pick)} released decisions sampled for blind audit", ""]
    if breaker:
        lines += [f"> **Circuit breaker tripped.** {breaker['reason']}. Autonomy lowered to {breaker['autonomy_level']}.", ""]
    lines += ["| Candidate | Proposed | Why a person is needed |", "|---|---|---|"]
    for c in q:
        why = "; ".join(c["guardian_problems"] + c["reasons"]).replace("|", "/")
        lines.append(f"| {c['candidate_id']} | {c['action'].replace('_', ' ').lower()} | {why} |")
    if pick:
        lines += ["", "## Blind audit sample", "",
                  "Re-decide these from the resume without seeing the AI's assessment; record agreement in the monthly report.", ""]
        lines += [f"- {c['candidate_id']} (released: {c['action'].replace('_', ' ').lower()})" for c in pick]
    with open(j(R, "human-queue.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    audit(args.audit_log, "guard_decisions.py", [j(R, "decisions.json"), j(R, "screening.json"), j(G, "runtime-policy.json")],
          [j(R, "guardian-report.json"), j(R, "human-queue.md")],
          {"level": level, **counts, "fairness": fstatus, "breaker": bool(breaker), "audit_sample": len(pick)})
    print(f"Guardian at {level}: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())) +
          f"; fairness {fstatus} over {len(records)} AI-handled decisions; audit sample {len(pick)}"
          + ("; CIRCUIT BREAKER TRIPPED -> " + breaker["autonomy_level"] if breaker else ""))


if __name__ == "__main__":
    main()
