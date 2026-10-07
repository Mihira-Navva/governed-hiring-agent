# Enterprise AI Policy: extracts relevant to hiring

*Illustrative policy of the deploying organisation, approved by the Board. This is the
"enterprise context" layer of the skill library: the organisation's own rules, which sit on
top of the law.*

| ID | Policy | Effect in this library |
|---|---|---|
| POL-AI-01 | Every AI use case that affects people is approved by the AI Approval Committee before use, and re-approved on material change. | The agent exists to support this process. |
| POL-AI-02 | Approval is proportionate to risk, using the committee's tiering rubric. | `risk-tiering` |
| POL-AI-03 | No consequential decision about a person is made without meaningful human review. "Meaningful" means the reviewer sees the case, has time to consider it and can override without friction. | Red line RL-02 |
| POL-AI-04 | AI systems must not use protected characteristics or their close proxies, and must be tested for adverse impact by group before and during use. | Red lines RL-03, RL-05; `fairness-bias-review` |
| POL-AI-05 | Third-party AI must be open to independent audit, documented, and subject to change control. | Red line RL-04; conditions C-VE-* |
| POL-AI-06 | Every AI system has a tested manual fallback and can be switched off within one working day. | Condition C-MO-KILL |
| POL-AI-07 | The organisation does not use AI to infer emotions, personality or protected traits from faces, voices or bodies, in any country. | Red lines RL-01, RL-06; prohibited purpose PR-01 |
| POL-DATA-02 | Unsuccessful applicants' data is erased within 180 days unless they opt into a talent pool. | Obligation IN-DPDP-RETENTION |

## AI Approval Committee

Chair: Chief Risk Officer. Members: Chief Human Resources Officer, General Counsel (or delegate),
Data Protection Officer, Chief Information Security Officer, Head of AI Governance, and an
employee representative. Quorum: four, including Legal and the DPO for High-tier proposals.
Dissent is recorded in the minutes.

## Decision outcomes

| Outcome | Meaning |
|---|---|
| **Approve** | Use as proposed. Only for T1 and T2 with no open mandatory obligations. |
| **Approve with conditions** | Use permitted once conditions precedent are evidenced; conditions subsequent apply while live; time-limited. The normal ceiling for High-tier hiring AI. |
| **Pilot only** | Shadow-mode or tightly limited pilot to generate evidence; no candidate is affected by AI output; returns to committee with results. |
| **Redesign and resubmit** | Purpose is legitimate but the design crosses a red line. Not approvable until redesigned; the memo lists what the resubmission must show. |
| **Reject** | The purpose itself is not acceptable under policy or law. |
| **Return for information** | The committee cannot assess the proposal; specific questions go back to the proposer. Not a judgment on merit. |
