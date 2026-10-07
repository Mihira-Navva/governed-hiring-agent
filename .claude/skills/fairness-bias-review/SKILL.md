---
name: fairness-bias-review
description: Tests an AI hiring system for unfair treatment of groups. Screens model inputs for protected attributes and proxies common in Indian hiring (name, PIN code, college, career gaps, accent), and measures adverse impact and equal opportunity by gender, age, region and disability from shadow-mode or pilot data, with significance tests and people-affected estimates. Use after risk tiering for any system that screens, ranks or scores candidates.
---

# Fairness and Bias Review

The proposal says the system "may disadvantage some groups, use irrelevant information or reject
qualified people without a clear explanation". This skill turns those three worries into three
tests the committee can see:

| Worry | Test | Script |
|---|---|---|
| Uses irrelevant information | Every input feature screened for protected attributes and proxies | `proxy_screen.py` |
| Disadvantages some groups | Selection rate and impact ratio by group, with significance | `adverse_impact.py` |
| Rejects qualified people | Among expert-judged qualified candidates, share the AI shortlisted, by group | `adverse_impact.py --qualified` |

## Inputs

- `reviews/<id>/intake.json` (for the feature list and annual volume).
- Shadow-mode or pilot data, if supplied: one row per candidate with the AI outcome (0/1),
  optional independent expert "qualified" label (0/1), and voluntarily self-declared group
  columns. Never request group data that candidates were not asked for with consent.
- `references/proxy-dictionary.json` and `references/fairness-methods.md`.

## Method

1. **Screen the inputs.**
   ```bash
   python scripts/proxy_screen.py reviews/<id>/intake.json \
       --out reviews/<id>/proxy-screen.json --audit-log reviews/<id>/audit-log.jsonl
   ```
   Then read the proposal for features that the keyword screen cannot see: composite scores
   ("fit score", "potential index"), LLM summaries of CVs, or free-text fields. List them as
   hidden-proxy risks in your notes for the memo.

2. **Measure outcomes**, if data exists:
   ```bash
   python scripts/adverse_impact.py <pilot.csv> --outcome ai_shortlisted \
       --qualified expert_qualified --groups gender,age_band,region,disability \
       --intersect gender:age_band --annual <annual_applications> \
       --out reviews/<id>/fairness.json --md reviews/<id>/fairness-tables.md \
       --audit-log reviews/<id>/audit-log.jsonl
   ```
   Always include at least one intersection. Bias against, for example, women over 40 can
   be invisible in gender-only and age-only tables.

3. **Interpret, don't just report.** For each FAIL or CONCERN, write one or two sentences on the
   most likely cause, linking it to the proxy screen where you can (e.g. "career-gap feature
   penalises women aged 30-39"). Check before relying on the numbers:
   - Who labelled candidates "qualified"? A panel that saw the AI score is not independent.
   - Was the pilot population like the real applicant pool (roles, regions, season)?
   - How many records were excluded as "prefer not to say"? Heavy exclusion can hide bias.

4. **If no data exists**, say so plainly. The absence of evidence of bias is not evidence of
   fairness; the decision skill will route the proposal to a shadow-mode pilot.

## Output

- `proxy-screen.json`: every feature classified, features to remove or justify, RL-03 if any
  protected attribute is a model input.
- `fairness.json` and `fairness-tables.md`: per-attribute and intersectional results, verdicts,
  people affected per year, RL-05 if adverse impact is statistically significant.

## Guardrails

- Group data is for auditing only. It must never become a model input, and the audit set must
  be kept separate with its own access controls and consent.
- Passing the four-fifths benchmark is necessary, not sufficient. Report equal-opportunity
  gaps and intersections even when the headline ratio passes.
- Report the numbers you have, with their uncertainty. Never round a FAIL into a CONCERN.
