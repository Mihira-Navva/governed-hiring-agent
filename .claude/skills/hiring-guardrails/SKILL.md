---
name: hiring-guardrails
description: Runtime governance for an AI hiring agent. Gates job specifications against protected characteristics and proxies, checks every proposed hiring decision against the committee's signed runtime policy before it takes effect, monitors advancement rates by self-declared group with significance tests, trips a circuit breaker that withdraws autonomy on adverse impact, samples autonomous decisions for blind human audit, and records everything in a tamper-evident ledger. Use when a job spec is submitted and whenever the hiring agent proposes a batch of decisions.
---

# Hiring Guardrails

Approval before deployment is not enough: an approved system can drift, be misconfigured, or be fed a
biased requisition next month. This skill is the committee's control **at the moment of each
decision**. It is used by the `hiring-guardian`, never by the hiring agent that it checks.

## Inputs
- `references/proxy-dictionary.json`: the same dictionary the approval review uses, so pre-deployment
  and runtime governance agree.
- `references/runtime-controls.md`: what each check defends against.
- `governance/runtime-policy.json` (committee-signed), `governance/autonomy-state.json`,
  `governance/audit-data/self-declarations.csv` (voluntary; guardian-only), `governance/decision-ledger.jsonl`.

## Method
1. **Criteria gate**, when a job spec is submitted:
   ```bash
   python scripts/check_job_spec.py <run>/job-spec.json --out <run>/spec-gate.json --audit-log <run>/audit-log.jsonl
   ```
   BLOCK goes back to the hiring manager with reasons. If the manager disputes it, escalate to the
   committee. Never edit the spec yourself.
2. **Decision check**, when the hiring agent proposes a batch:
   ```bash
   python scripts/guard_decisions.py --run <run> --governance governance --audit-log <run>/audit-log.jsonl
   ```
3. **Read the report as an auditor.** Look at `guardian-report.json` and `human-queue.md`. Write
   `guardian-notes.md`: anything the checks passed that still looks wrong (a quoted piece of evidence
   that does not support its decision; an AMBER group trending down across batches).
4. **Verify the ledger** whenever asked, and before every monthly report:
   ```bash
   python scripts/ledger.py verify governance/decision-ledger.jsonl
   ```

## Output
- `spec-gate.json`: PASS or BLOCK per criterion, with the spec's hash.
- `guardian-report.json`: per-decision status (RELEASED / ROUTED_TO_HUMAN / QUEUED_FOR_HUMAN) with
  reasons, fairness status, hard-requirement rejection rates by group (for the monthly report),
  circuit-breaker action, audit sample, ledger hash.
- `human-queue.md`: what recruiters must handle, and why.
- `governance/autonomy-state.json`: written only when the circuit breaker trips.

## Fairness status
| Status | Meaning | Effect |
|---|---|---|
| GREEN | Every group with enough records advances at 0.80 or more of the top group's rate | None |
| AMBER | Too few records to tell, or a gap that is not yet statistically significant | Reported to the committee; keep collecting |
| RED | A statistically significant gap below 0.80 | **Circuit breaker:** autonomy drops to L1 until the committee issues a new policy |
