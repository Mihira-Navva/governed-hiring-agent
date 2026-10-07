---
name: job-requisition
description: Turns a hiring manager's request into a structured, job-related job specification with verifiable hard requirements, weighted scored criteria tied to a job analysis, and decision thresholds, recording any requests declined as proxies or protected characteristics. Use when a new role opens or a requisition changes, before any resume is screened.
---

# Job Requisition

Unfair screening usually starts before any resume is read, in the criteria. This skill turns a
manager's request into criteria that are job-related, measurable and the same for everyone.

## Inputs
- The hiring manager's request and the job analysis for the role.
- `templates/job-spec.json`: the structure and the allowed evidence types.
- `references/job-analysis-method.md`: how to sort each ask into hard requirement, scored criterion,
  proxy or protected.

## Method
1. Sort every ask using the four bins in the method notes. Write the spec to
   `<run>/job-spec.json` from the template.
2. **Hard requirements** must be legal, regulatory, safety or genuinely operational facts, checkable from
   the resume or an application answer. Give `ambiguous_if_any` phrases (e.g. "pursuing", "appearing")
   so that candidates on their way to a requirement go to a person instead of being rejected.
3. **Scored criteria** carry weights that add to 100, each with a sentence on why it predicts
   performance. Prefer direct measures (work samples, tested language) over signs of them.
4. Decline protected characteristics outright. For proxies, explain the concern to the manager. If
   they insist, include it as asked and record the disagreement in `requests_declined`: the guardian's
   gate settles it, so the disagreement is visible.
5. Validate the structure:
   ```bash
   python scripts/validate_job_spec.py <run>/job-spec.json --audit-log <run>/audit-log.jsonl
   ```
6. **Submit to the guardian.** The spec is not used until `hiring-guardrails/scripts/check_job_spec.py`
   returns PASS. A BLOCK goes back to the manager with the guardian's reasons.

## Output
`job-spec.json`, structurally valid and cleared by the guardian's criteria gate.
