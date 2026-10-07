# Risk method: what the dimensions mean

| Dimension | 0 | 3 | Why it matters |
|---|---|---|---|
| **Consequence** | — | Evaluates candidates (screening, assessment, interview, selection) | Decides access to employment and income. |
| **Automation** | Advisory only | Auto-archive, auto-reject or fully automated; or ranking where no one reviews every rejection | Whether a human really decides. |
| **Scale** | < 1,000 applications a year | 50,000 or more | Errors and bias multiply with volume. |
| **Data sensitivity** | (1 is the minimum: CVs are personal data) | Biometric or affect inference | Sensitive processing, consent scope, proxy risk. |
| **Opacity** | Explainable, documented, in-house | No explanations, no documentation, third party | The committee and candidates cannot see why. |
| **Contestability gap** | Appeal, human alternative and grievance officer all exist | None exist | Wrong decisions cannot be corrected. |
| **Oversight weakness** | Trained reviewers, logged overrides, blind-first review | None of these | "Human in the loop" that only rubber-stamps. |

## Tiers

| Score | Tier | Approver | Re-review |
|---|---|---|---|
| 0–5 | T1 Low | Business line head | 24 months |
| 6–10 | T2 Moderate | Committee chair | 12 months |
| 11–15 | T3 High | Full committee | 6 months |
| 16–21 | T4 Very high | Committee and Board Risk Committee, pilot first | 3 months |

Floor: any evaluative system is at least T3.

## Red lines

| ID | Red line | Basis |
|---|---|---|
| RL-01 | Emotion, affect or personality inferred from face, voice or behaviour | EU AI Act Art. 5(1)(f); policy POL-AI-07 |
| RL-02 | Automated rejection in practice | Policy POL-AI-03; India AI Governance Guidelines; GDPR Art. 22 where relevant |
| RL-03 | Protected attribute used as a model input *(checked by `fairness-bias-review`)* | Code on Wages s. 3; RPwD Act; Transgender Persons Act; policy POL-AI-04 |
| RL-04 | Vendor refuses independent audit | Policy POL-AI-05 |
| RL-05 | Statistically significant adverse impact *(checked by `fairness-bias-review`)* | Policy POL-AI-04; four-fifths benchmark |
| RL-06 | Biometric categorisation by protected traits | EU AI Act Art. 5(1)(g); policy POL-AI-07 |

## Known limits of this rubric

- An additive score can hide a single severe issue; that is why red lines sit outside the score.
- Weights are a policy judgment, not a scientific measurement. They are reviewed with the rest
  of the library every six months, and changes are recorded in `skill.json`.
- The rubric assesses the proposal as described. Post-launch monitoring is what tells you
  whether the description was true.
