# Job analysis method: turning a request into fair criteria

A hiring manager's request mixes three things: what the job truly requires, what predicts doing it
well, and personal preferences. The specification must keep the first two and leave out the third.

## 1. Sort every ask into one of four bins

| Bin | Test | Goes to | Example |
|---|---|---|---|
| **Hard requirement** | A law, regulator or the physical job makes it non-negotiable, **and** it can be checked as a fact | `hard_requirements` | NISM-Series-V-A certificate to distribute mutual funds; able to work at the branch |
| **Scored criterion** | It predicts performance in this role, shown by the job analysis | `scored_criteria`, with a weight | Score on a work-sample exercise; months of customer-facing sales |
| **Proxy** | It correlates with a protected characteristic more than with performance | Declined and recorded | College tier; "no career gaps"; graduation year; "presentable" |
| **Protected** | It is a protected characteristic | Declined and recorded; escalate if the manager insists | Age range; gender; marital status |

## 2. Questions to ask the manager

- "If someone has X but not Y, could they do the job in month three?" A "no" means Y may be required;
  a "yes" means it is at most a scored criterion.
- "How would we measure that the same way for every applicant?" If it can't be measured the same way,
  it can't be used.
- "Which of your current top performers would fail this requirement?" This often reveals a
  preference posing as a requirement.

## 3. Prefer direct measures

Measure the skill itself rather than a sign of it. A 20-minute work sample (a mock customer call, a
loan-eligibility case) predicts performance better than college name, and is fairer. Language for a
branch is tested in the assessment, not inferred from mother tongue or accent.

## 4. Experience: minimums, not maximums

Count relevant experience up to a cap (for example 24 months). Beyond the cap, more years add nothing,
otherwise experience becomes an age proxy. Never penalise gaps: the parser does not compute them.

## 5. Record what you declined

Every declined ask goes into `requests_declined` with the reason. The guardian and the committee see
them. If a manager insists on a proxy, write it into the spec as they asked and let the guardian's gate
decide. That way the disagreement is visible and settled by governance, not quietly by you.
