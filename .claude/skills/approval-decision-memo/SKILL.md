---
name: approval-decision-memo
description: Applies the AI Approval Committee's decision rules to the intake, risk, fairness and legal findings and writes the committee decision memo, with a recommended outcome, conditions with owners and deadlines, escalations, the reviewer's judgment, an unsigned committee sign-off block and a hash-linked audit trail. Use as the final step of an AI use case approval review.
---

# Approval Decision Memo

This skill turns findings into a decision the committee can take in one meeting. It keeps two
things strictly apart:

- **Rules and evidence**: the outcome, numbers and conditions come from `decide.py` and the
  structured files. They are consistent from one proposal to the next and reproducible.
- **Judgment**: what the numbers mean, how benefits weigh against risks, what the scripts
  cannot see. That comes from you, written in `reviewer-notes.json`, and is labelled as such.

## Inputs

All files in `reviews/<id>/` produced by earlier skills (any may be absent, e.g. when the
review stopped early), plus:

- `references/decision-rules.md`: the ordered rules D1-D6 and why they are ordered so.
- `references/conditions-library.json`: approved conditions and their triggers.
- `references/enterprise-ai-policy.md`: the organisation's AI policy and outcome definitions.
- `templates/reviewer-notes.json`: the structure for your judgment.

## Method

1. **Decide by rule:**
   ```bash
   python scripts/decide.py --review-dir reviews/<id> --audit-log reviews/<id>/audit-log.jsonl
   ```
2. **Read `decision.json` critically**, then write `reviews/<id>/reviewer-notes.json` from the
   template:
   - `summary`: what you would tell the chair in 30 seconds.
   - `key_findings`: three to six findings, each citing its evidence.
   - `benefits_and_tradeoffs`: take the proposal's benefits seriously. If the case for the
     system is strong, say so, and say what a safe version would look like.
   - `reviewer_judgment`: if you think the rule-based outcome is wrong, argue it here. Never
     edit `decision.json`.
   - `what_would_change`: concrete, checkable items. This is what makes a "no" constructive.
3. **Render the memo:**
   ```bash
   python scripts/render_memo.py --review-dir reviews/<id> --audit-log reviews/<id>/audit-log.jsonl
   ```
4. **Read the whole memo** as a committee member would. Check that every number matches its
   source file, every condition has an owner, evidence and deadline, and the sign-off block is
   blank.

5. **After the committee signs** (never before, and never by you), turn its decision into the runtime
   policy that the governed system must obey:
   ```bash
   python scripts/issue_runtime_policy.py --review-dir reviews/<id> \
       --committee reviews/<id>/committee-decision.json --out governance/runtime-policy.json
   ```
   The autonomy granted is capped by evidence: assist-only (L1) until every condition precedent is
   evidenced, at most L2 after that, and L3 only with a Board exception to POL-AI-03.

## Output

- `decision.json`: outcome, rule fired, rationale, conditions, escalations, open questions.
- `decision-memo.md`: the document for the committee.

## Tone

Plain, specific and fair to the proposer. The memo is read by HR leaders, lawyers and
engineers; avoid jargon, explain every acronym once, and write conditions so that someone could
check whether they were met.
