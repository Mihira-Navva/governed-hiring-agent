---
name: hiring-decisions
description: Converts screening results into proposed hiring actions (advance, reject on a failed hard requirement, hold for a person, human-only) strictly within the autonomy level granted by the committee's signed runtime policy and the guardian's current state, and drafts plain-language candidate letters with an AI notice and appeal route. Use after resume screening, before handing the batch to the hiring guardian.
---

# Hiring Decisions

This is where the agent acts, so this is where the limits are strictest. The skill never decides
**how much** it may do on its own: the committee's runtime policy and the guardian decide that.

## Inputs
- `job-spec.json` (thresholds), `screening.json`.
- `governance/runtime-policy.json` (signed by the committee) and `governance/autonomy-state.json`
  (written by the guardian). Read both; edit neither.
- `references/autonomy-levels.md`, `templates/letters.json`.

## Method
1. Run:
   ```bash
   python scripts/decide_candidates.py --spec <run>/job-spec.json --screening <run>/screening.json \
       --policy governance/runtime-policy.json --state governance/autonomy-state.json \
       --out <run>/decisions.json --letters <run>/letters --audit-log <run>/audit-log.jsonl
   ```
2. Read the effective level and its reason at the top of `decisions.json`. If it is L0, stop and tell
   the hiring team why.
3. Read every HOLD_FOR_HUMAN reason and make sure a recruiter could act on it without opening the
   scoring files. Improve the wording in `decision-notes.md` if needed.
4. Hand the batch to the `hiring-guardian`. **Nothing is sent, scheduled or rejected until the guardian
   releases it.** Letters stay drafts.

## Output
- `decisions.json`: per candidate, action, whether it is autonomous, reasons with evidence, letter.
- `letters/`: draft letters. Every outcome letter carries the AI notice and appeal route.

## Decision table (L2)

| Situation | Action |
|---|---|
| Asked for human-only, or no consent | HUMAN_ONLY |
| Integrity flag; parse confidence below policy; accommodation with assessment outstanding | HOLD_FOR_HUMAN |
| A hard requirement FAILs cleanly | AUTO_REJECT_HARD_REQUIREMENT (appealable) |
| A hard requirement is UNCLEAR, or an input is missing | HOLD_FOR_HUMAN |
| Score at or above the advance threshold | AUTO_ADVANCE |
| Score between the review floor and the advance threshold | HOLD_FOR_HUMAN |
| Score below the review floor | PROPOSE_REJECT (a recruiter confirms) |
