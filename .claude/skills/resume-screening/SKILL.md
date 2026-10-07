---
name: resume-screening
description: Reads plain-text resumes and application answers, removes identifying and protected information before anything is scored, detects text aimed at manipulating an AI screener, and scores each candidate against a cleared job specification with quoted evidence for every requirement and criterion. Use after a job specification has passed the guardian's criteria gate and applications have arrived.
---

# Resume Screening

Two principles govern this skill. **What is not seen cannot bias the score.** **Every score must
show its evidence.**

## Inputs
- A job specification that has passed the guardian's criteria gate.
- A folder of resumes (`<candidate_id>.txt`) and `applications.csv` (screening answers, assessment
  results, consent, human-only and accommodation requests).
- `references/blinding-rules.json`: what is removed, why, and the patterns that flag manipulation.
- `references/screening-method.md`: how to read the results.

## Method
1. **Parse and blind:**
   ```bash
   python scripts/parse_resumes.py <run>/resumes --out-full <run>/profiles.json \
       --out-blind <run>/blind-profiles.json --audit-log <run>/audit-log.jsonl
   ```
   `profiles.json` is restricted to contacting candidates. From here on, read only `blind-profiles.json`.
2. **Screen:**
   ```bash
   python scripts/screen_candidates.py --spec <run>/job-spec.json --blind <run>/blind-profiles.json \
       --applications <run>/applications.csv --out <run>/screening.json --audit-log <run>/audit-log.jsonl
   ```
3. **Read what the scripts cannot judge.** For any candidate with an UNCLEAR requirement, low parse
   confidence or an integrity flag, write one line in `screening-notes.md` saying what a person should
   look at. Do not rescore anyone by hand. If you think the scoring is wrong for someone, say so in the
   notes so a person can check.

## Output
- `blind-profiles.json`: scoring input, with `removed_before_scoring` and `integrity_flags` per candidate.
- `screening.json`: per candidate, hard requirements (PASS / FAIL / UNCLEAR + evidence), criteria
  sub-scores with evidence, total, and `inputs_used`.

## Guardrails
- Candidates who asked for a human-only assessment, or did not consent, are **not scored at all**.
- An integrity flag is not a penalty. The flagged text is removed, the rest is scored, and a person decides.
- Experience is counted in months up to the cap; employment gaps are never computed.
