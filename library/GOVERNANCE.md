# Skill library governance

The skill library is treated as a product: owned, reviewed, versioned, tested and retired. This
file is the operating procedure. It implements the controls on the "Operating limits and
enterprise readiness" slide (trusted sources; review and permissions; testing and lifecycle).

## Scope

The library holds nine skills in three layers: **hiring** (`job-requisition`, `resume-screening`,
`hiring-decisions`), **runtime governance** (`hiring-guardrails`) and **approval governance** (the five
review skills). The same lifecycle applies to all of them. Version 1.1.0 of three approval skills
(intake, risk tiering, decision memo) went through it on 7 October 2026, to support governed autonomy.

## Roles

| Role | Responsibility |
|---|---|
| **Library owner:** AI Governance Office | Publishes the catalog, runs evaluations, schedules reviews, retires skills. |
| **Skill author** | Writes or changes a skill and its tests. Cannot approve their own change. |
| **Domain reviewers** (named per skill in `skill.json`) | Approve the method and reference content: HR for proxies, Legal for the register, the Risk Officer for the rubric. |
| **Information Security** | Reviews scripts against declared permissions. |
| **AI Approval Committee** | Approves releases of the library; owns decision rules and conditions. |
| **The agents** | Use only skills that verify; report failures; never edit skills. The hiring agent may not read the fairness audit data; the guardian may only lower autonomy. |

## Lifecycle

```
propose → author → domain review → security review → evaluate → approve → publish (hash) → use → monitor → re-review → retire
```

1. **Propose.** A gap is found (e.g. a new law, repeated reviewer disagreement with a rule, an eval failure).
2. **Author.** Change the skill and its tests together. Bump the version in `skill.json` and add a changelog line.
3. **Review.** Domain and security reviewers sign in `skill.json`.
4. **Evaluate.** `python evals/run_evals.py` must show release gate PASS; behaviour tests must have no open failures.
5. **Publish.** `python library/scripts/build_catalog.py --eval-results evals/results.json` records the content hash.
   From this moment, any edit to the skill, even one character, fails verification until re-approved.
6. **Use.** The agent runs `verify_library.py` before every review and records the result in the memo.
7. **Monitor.** Track reviewer disagreements with rule outcomes, committee departures from recommendations, and
   post-approval incidents. These are the library's quality signals.
8. **Re-review** every six months (`review_due`) or when a referenced law changes.
9. **Retire** a skill when it fails critical evaluations, misses its review date, or its legal references go stale
   for more than 30 days. Retired skills stay in version control for audit but leave the catalog.

## Controls and what they defend against

| Threat | Control | Where |
|---|---|---|
| Unreviewed or edited skill used in a decision | Content hash pinned at approval, checked before each review | `verify_library.py` integrity check |
| Skill doing more than it says (e.g. sending data out) | Declared permissions; static scan of imports and dangerous calls | `skill.json` permissions; `scan_scripts()` |
| Instructions hidden in submissions | Agent treats submissions as data; integrity observations surfaced | Agent §2; intake skill; eval E14, B1 |
| Stale law or policy | `as_of` date in register; `review_due` per skill; currency check | `obligations-register.json`; verify currency |
| Silent rubric weakening | Rubric is data under hash; eval I02 proves detection | `risk-criteria.json`; `run_evals.py` |
| Over-trust in automation | Agent recommends only; committee signs; reviewer judgment separated from rules | Agent §1; memo §10, §14 |
| Untraceable conclusions | Hash-linked audit log for every script run | `audit-log.jsonl`; memo appendix A |

## Known limits

- Hash verification proves a skill is unchanged, not that it is right. Correctness comes from review and evaluation.
- The static scan is a guardrail, not a sandbox. Production use should also run scripts with no network access at the
  operating-system level.
- In claude.ai, where the catalog is not available, verification falls back to the `status` and `review_due` fields in
  each `skill.json`. That checks approval, not integrity.
