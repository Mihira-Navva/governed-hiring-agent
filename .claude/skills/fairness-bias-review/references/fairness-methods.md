# Fairness methods: what the numbers mean and where they stop

## 1. Selection rate and impact ratio

*Selection rate* = shortlisted ÷ applicants in a group.
*Impact ratio* = a group's selection rate ÷ the selection rate of the most-selected group
(among groups with at least 30 records).

The **four-fifths benchmark** treats an impact ratio below 0.80 as evidence of adverse impact.
It comes from the US Uniform Guidelines on Employee Selection Procedures (1978,
29 CFR 1607.4(D)) and is also the reference point in New York City's Local Law 144 bias audits.
It is a rule of thumb, not Indian law; we use it because it is widely understood, simple to
explain to a committee, and easy to monitor.

## 2. Why a significance test as well

A ratio alone misleads in both directions. With 12 people in a group, one extra shortlisting can
move the ratio from 0.70 to 0.95. With 5,000 people, a ratio of 0.85 can still reflect a real,
systematic difference. The script therefore reports a two-sided **Fisher exact test** for each
group against the reference group and combines the two:

| Impact ratio | p < 0.05 | Verdict |
|---|---|---|
| < 0.80 | yes | ADVERSE IMPACT (fail) |
| < 0.80 | no | POSSIBLE ADVERSE IMPACT (concern: collect more data) |
| ≥ 0.80 | yes | SIGNIFICANT SMALL DIFFERENCE (monitor) |
| ≥ 0.80 | no | NO ADVERSE IMPACT |
| any, group n < 30 | — | INSUFFICIENT DATA (concern) |

## 3. Equal opportunity: "rejects qualified people"

If an independent panel has judged a sample of candidates *qualified* (ideally without seeing
the AI score), we can ask: of the qualified candidates in each group, what share did the AI
shortlist? This is the **true positive rate**. A gap of more than 10 percentage points to the
reference group, if statistically significant, fails. This test speaks directly to the case
study's worry that the system could "reject qualified people".

## 4. Intersectionality

Discrimination often lands on combinations: women over 40, or disabled candidates from a
particular region. Single-attribute tables average these effects away. Always run at least one
intersection; expect small groups and read them as signals, not proof.

## 5. The sensitive-data paradox

You cannot test for bias against a group without knowing who is in it. But collecting caste,
disability or gender data creates its own risk. The approach here:

- Self-declaration is **voluntary**, with a "prefer not to say" option, and requested under a
  separate consent and purpose (fairness auditing) under the DPDP Act.
- Audit data is **stored separately** from the hiring system, with restricted access, and
  **never used as a model input**.
- Caste is not collected by default; region, mother tongue and institution proxies are tested
  instead, and caste-related testing is only done with legal and ethics approval.

## 6. Label bias

If the model was trained on "who we hired before", a perfect score on held-out data means it has
learned to copy past decisions, including their bias. The best-known case is Amazon's
experimental recruiting tool, abandoned in 2018 after it learned to downgrade CVs mentioning
women's colleges and activities (reported by Reuters). Ask what the label is before you trust
accuracy figures.

## 7. Many tests, some false alarms

A typical review runs 15 to 25 group comparisons. At a 5% significance level, one or more
"significant" results can appear by chance even in a perfectly fair system. The library's own
evaluation suite hit exactly this: a randomly generated "fair" test dataset showed a significant
gender gap (p = 0.02) that was pure noise. So:

- One isolated, marginal result (p between 0.01 and 0.05, ratio close to 0.80) in an otherwise
  clean table is a reason to re-test on fresh data, not proof of bias. Say so in the memo.
- Consistent patterns (several related groups in the same direction, very small p-values, a
  plausible cause in the inputs) are not explained by chance. Version 1 of the worked example is
  this kind of case.
- The script does not apply a correction automatically, because in hiring a missed bias costs
  more than a false alarm. The reviewer's interpretation must weigh it instead.

## 8. What fairness metrics cannot do

- Different fairness definitions (equal selection rates, equal true positive rates, calibration)
  generally cannot all be satisfied at once when base rates differ between groups. Choosing
  which to prioritise is a value judgment for the committee, not a technical fact. This library
  uses selection-rate parity as the screening test and equal opportunity as the qualified-
  candidate test, and says so in every memo.
- Passing today says nothing about next quarter. Applicant pools, roles and vendor models change.
  Monitoring is part of approval, not an extra.
