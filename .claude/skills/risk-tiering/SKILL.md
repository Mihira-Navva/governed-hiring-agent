---
name: risk-tiering
description: Classifies an AI hiring use case into a risk tier (T1 Low to T4 Very high, or Prohibited), checks it against prohibited practices and organisational red lines, and states which reviewers and approvers the tier requires. Use after intake, whenever an AI system screens, ranks, scores or interacts with job candidates.
---

# Risk Tiering

Proportionate governance means scrutiny that matches the stakes. A scheduling chatbot and a
model that filters 60,000 applicants should not face the same review. This skill decides how
much scrutiny a proposal gets, and flags anything that cannot be approved in its current form.

## Inputs

- `reviews/<id>/intake.json` from the `use-case-intake` skill.
- `references/risk-criteria.json`: the rubric, prohibitions, red lines and review requirements.
  The rubric is versioned data; to change policy, change this file through the library's
  review process, never the script.
- `references/risk-method.md`: what each dimension means and how to read the result.

## Method

1. Run the scorer:
   ```bash
   python scripts/risk_tier.py reviews/<id>/intake.json \
       --out reviews/<id>/risk.json --audit-log reviews/<id>/audit-log.jsonl
   ```
2. Read `risk.json` and **test it against the proposal**. The script works from the intake
   fields; you have read the documents. Ask:
   - Does the automation score reflect what really happens to low-ranked candidates?
   - Are any red lines hidden in vague wording (e.g. a "communication confidence" score
     computed from video is affect inference, whatever it is called)?
   - Is any dimension unknown only because the proposal is silent? Unknowns score as risky on
     purpose; note which ones the proposer could clear with evidence.
3. If you believe the tier is wrong, **do not edit `risk.json`**. Record your reasoning for the
   decision memo's *Reviewer judgment* section. The committee sees both.
4. Gate:
   - `PROHIBITED`: the purpose itself cannot be approved. Skip to `approval-decision-memo`.
   - Any red line: continue the review (the committee needs the full picture for a redesign),
     but expect the outcome *Redesign and resubmit*.

## Output

`risk.json`: tier, score per dimension with reasons, floor applied, prohibitions, red lines
with their basis and remedy, the required reviewers and approver, re-review interval, and the
EU AI Act classification used as a benchmark.

## Principles behind the rubric

- **Floor for evaluative systems.** Anything that screens or scores candidates is at least
  T3 (High), because it affects access to livelihood. This mirrors the EU AI Act's Annex III
  listing of recruitment and the India AI Governance Guidelines' "People First" sutra.
- **Unknown counts as risky.** An unevidenced safeguard is not a safeguard. This gives the
  proposer a reason to supply evidence.
- **Red lines are design flaws, not scores.** No amount of benefit offsets them; they must
  be designed out.
