---
name: legal-privacy-review
description: Maps an AI hiring proposal against Indian law (DPDP Act and Rules, Code on Wages, RPwD Act, Transgender Persons Act, Constitution for public employers), India's AI Governance Guidelines, internal policy, and global benchmarks (EU AI Act, GDPR, NYC Local Law 144, ISO/IEC 42001, NIST AI RMF), and reports each applicable obligation as met, gap or unknown with the evidence needed. Use after the fairness review for any AI system that processes candidate data.
---

# Legal and Privacy Review

The committee needs to know three things: which rules apply, whether the proposal meets them,
and who must act if it does not. This skill answers those from a maintained obligations
register. It identifies obligations; it does not give legal advice. Legal Counsel confirms.

## Inputs

- `reviews/<id>/intake.json`.
- `reviews/<id>/fairness.json` if the fairness review produced one (equality obligations are
  tested against it).
- `references/obligations-register.json`: each obligation, when it applies, how to test it,
  its legal status and its owner.
- `references/legal-landscape.md`: plain-language notes on each instrument and its timing.

## Method

1. Run the mapper:
   ```bash
   python scripts/obligations.py reviews/<id>/intake.json --fairness reviews/<id>/fairness.json \
       --out reviews/<id>/legal.json --audit-log reviews/<id>/audit-log.jsonl
   ```
2. Review every `GAP` and `UNKNOWN`. For each, confirm from the documents that the gap is real
   (and not something the intake missed). If the intake missed it, correct `intake.json`
   and rerun from the intake stage, so the audit log shows the correction.
3. **Be precise about timing and force.** Distinguish what binds now, what is phased in, what
   applies from a future date, what is guidance, and what is a benchmark. Do not describe a
   benchmark as a legal requirement, and do not dismiss a phased obligation because it is not
   yet in force: a hiring system approved today will still be running when it is.
4. Note any issue the register does not cover (e.g. sector-specific regulators, collective
   agreements, a jurisdiction not in the register) under *Issues for counsel*.

## Output

`legal.json`: applicable obligations, each with status, legal force, evidence needed, gap code
and owner; a count of open mandatory items; the list of functions to escalate to.

## Keeping the register current

The register carries an `as_of` date. Laws here are moving: the DPDP regime phases in through
2027, the Labour Codes took effect in November 2025, and EU AI Act high-risk dates were moved by
the 2026 Digital Omnibus. The library owner reviews the register every six months and whenever
a listed instrument changes. A stale register is a reason to stop and ask, not to proceed.
