# Runtime controls and what each defends against

| Control | Failure it stops | Why it sits with the guardian, not the hiring agent |
|---|---|---|
| Criteria gate on every job spec | A manager's preference for "top colleges" or "no career gaps" turning into automated discrimination | The hiring agent works for the manager; the guardian works for the committee |
| Spec hash check (G6) | A spec edited after it was cleared | Proves which criteria every decision used |
| Level recomputed independently (G1) | An agent claiming more autonomy than granted, or ignoring a breaker | The guardian never trusts the agent's own claim about its permissions |
| Clean hard-requirement failure (G2) | A judgment rejection disguised as a requirement failure | Automated rejection is allowed only for checkable facts |
| Input check (G3) | Scoring that read names, addresses or other removed fields | Verifies blinding actually happened |
| Letter check (G4) | Rejections without explanation or appeal | Contestability is a condition of approval |
| Integrity and human-only check (G5) | A manipulated resume, or a candidate who opted out, being handled by AI | Their choice and the integrity process are honoured |
| Fairness monitor + circuit breaker | Drift: a system fair at approval becoming unfair in use | Uses self-declared group data the hiring agent must never see |
| Blind audit sample | Recruiters and the agent agreeing for the wrong reasons | A person re-decides without the AI's view, giving an unbiased error estimate |
| Hash-chained ledger | Records quietly altered after a complaint | Any edit breaks the chain |

## Why the breaker only lowers autonomy
Raising autonomy is a governance decision, made by people on evidence. Lowering it is a safety action,
which must be fast and automatic. An asymmetric switch (anyone can stop the line; only the committee can
restart it) is the standard pattern in safety-critical operations.

## What these controls cannot catch
- Bias inside a criterion that is legitimately required (e.g. a certification held less often by one
  group). The monitor shows its effect, and the committee decides whether the requirement stays.
- Small groups. With few records the monitor stays AMBER, and the committee must act on judgment and
  pooled data.
- A biased assessment instrument. The work-sample test itself needs its own validation.
