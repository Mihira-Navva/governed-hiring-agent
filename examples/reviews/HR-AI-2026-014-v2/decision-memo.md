# AI Use Case Approval: Decision Memo

**Proposal:** HR-AI-2026-014 · TalentSort v2: skills-first screening assistant for branch and field sales hiring  
**Organisation:** Deccan Ledger Finance Ltd (fictional NBFC)  
**Submitted by:** Rohan Kulkarni (Head of Talent Acquisition), 2026-10-02  
**Prepared by:** AI Use Case Approval Agent, 2026-10-07  
**Status:** RECOMMENDATION. Awaiting decision of the AI Approval Committee.

## 1. Recommendation

> ### Approve with conditions
> Rule D5 · Risk tier T3 (High) · Approver: AI Approval Committee (quorum)
>
> Approve TalentSort v2 with conditions, for six months, then re-review. The redesign answers every red line from v1. The video and affect module is gone, a recruiter reviews every application, the five inputs come from a job analysis, and the model no longer learns from past hiring decisions. On 1,500 new shadow-mode applicants, no group shows statistically significant adverse impact. Two things must be done before go-live: complete the accessibility review the proposer has scheduled for November, and supply the job analysis the inputs rest on. Three ongoing conditions address what the data cannot yet settle. These are a blind-first sample to measure whether recruiters simply follow the AI ordering, a six-monthly independent audit (watching the 21-29 age group and groups too small to test), and a fixed re-review date.

## 2. Key findings

1. **All v1 red lines are cleared.** No video, voice, affect or biometric processing; every application is reviewed by a recruiter at about 120 a day, within the committee's 150 target; nothing is archived or rejected without a recruiter decision. Evidence: intake system.techniques, human_oversight; risk.json shows no red lines.
2. **Risk falls from 21/21 to 10/21**, but the tier stays High (T3). Any system that screens candidates at this scale keeps the evaluative floor, which is the right level of scrutiny for 60,000 people a year. Evidence: risk.json.
3. **No significant adverse impact on the new shadow data.** Lowest impact ratios: East and North-East 0.88 (p = 0.20), men 0.96, applicants aged 21-29 0.91; all at or above the four-fifths benchmark and none statistically significant. Evidence: fairness.json, fairness-tables.md.
4. **Two fairness signals to watch, not to block on.** Qualified applicants aged 21-29 were shortlisted at 63% versus 74% for qualified applicants over 40, a 10.8-point gap that is not statistically significant (p = 0.25). Transgender and non-binary applicants (24) and disabled applicants (61, of whom 13 were rated qualified) are too few to test reliably. Evidence: fairness.json equal-opportunity columns.
5. **Legal position is largely in order: 16 of 17 obligations met.** The one gap is the RPwD Act, since accessibility testing is not yet done. Evidence: legal.json.
6. **Some evidence is cited but not attached.** The independent audit report, the job analysis and the model documentation are summarised only. Approval should rest on the documents, not their summaries. Evidence: intake claims_needing_evidence.

## 3. What the system does to a candidate

| Aspect | As submitted |
|---|---|
| Primary function | cv screening ranking |
| Stage of hiring | initial screening |
| Automation level | assistive ranking |
| AI output | Queue order and highlighted job-related skills for each application; no pass/fail flag |
| Human reviews every rejection | yes |
| Recruiter sees AI score first | yes |
| Applications per year | 60,000 |
| Roles | Branch sales, Collections, Relationship roles |
| Vendor | HireSort AI Pvt Ltd (fictional) |

Priya applies again under v2. She is told, in Assamese and English, that AI helps order applications and that a person reviews every one. She takes a 20-minute work-sample assessment (a mock customer call and a loan-eligibility case), checks her parsed profile, and corrects one field. Her career break and college are not inputs. A recruiter reads her application, sees the matched skills, and moves her to interview. Had she been rejected, she could ask for a re-review by a recruiter who had not seen the AI ordering.

## 4. Risk profile

Score **10/21**, tier **T3 (High)** (evaluative-system floor applied). EU AI Act benchmark: High-risk (Annex III, point 4: employment, recruitment and selection).

| Dimension | Score | Reason |
|---|---:|---|
| Consequence | 3 | Evaluates candidates (cv_screening_ranking at initial_screening stage): outcome affects access to employment |
| Automation | 1 | Automation level 'assistive_ranking' |
| Scale | 3 | 60,000 applications a year |
| Data sensitivity | 1 | CV and contact data are personal data |
| Opacity | 1 | third-party or unclear provenance |
| Contestability gap | 0 | appeal, alternative and grievance routes in place |
| Oversight weakness | 1 | AI score seen before reviewer forms own view (anchoring) |

## 5. Fairness evidence

**Input screen: JUSTIFY.** 5 inputs: 1 moderate proxy, 4 job related.

| Input | Category | Linked to | Action |
|---|---|---|---|
| Skills assessment score (work sample: mock customer call and loan-eligibility case exercise) | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Relevant certification (NISM / IRDAI where the role requires it) | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Relevant sales experience (minimum threshold only, not scored above it) | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Structured screening questions (field-work availability; two-wheeler licence for collections) | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Language proficiency required for the branch, tested in the assessment | Moderate Proxy | class, region, schooling medium | Keep only with a written job-relatedness justification and a bias test of this feature. |

**Outcome test: CONCERN** on 1,500 shadow-mode records (four-fifths benchmark with Fisher exact test, α = 0.05; equal-opportunity gap threshold 10.0 pp).

**gender**: verdict **CONCERN** (selection reference: Woman; equal-opportunity reference: Man)

| Group | n | Selection rate | Impact ratio | p | Verdict | Qualified shortlisted | EO gap (pp) | Est. people/yr |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| Man | 908 | 39.1% | 0.96 | 0.579 | No Adverse Impact | 66.8% | ref | – |
| Woman | 542 | 40.6% | 1.00 | 1.000 | Reference | 63.2% | 3.6 | – |
| Transgender / non-binary | 24 | 50.0% | 1.23 | 0.400 | Insufficient Data | 100.0% | -33.2 (small n) | – |

> 'Transgender / non-binary' has only 24 records (fewer than 30); its ratio is shown but cannot be relied on.

**age_band**: verdict **CONCERN** (selection reference: 40+; equal-opportunity reference: 40+)

| Group | n | Selection rate | Impact ratio | p | Verdict | Qualified shortlisted | EO gap (pp) | Est. people/yr |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| 21-29 | 842 | 39.0% | 0.91 | 0.382 | No Adverse Impact | 62.7% | 10.8 ? | – |
| 30-39 | 495 | 39.6% | 0.92 | 0.463 | No Adverse Impact | 67.5% | 6.0 | – |
| 40+ | 163 | 42.9% | 1.00 | 1.000 | Reference | 73.5% | ref | – |

**home_region**: verdict **PASS** (selection reference: South; equal-opportunity reference: North)

| Group | n | Selection rate | Impact ratio | p | Verdict | Qualified shortlisted | EO gap (pp) | Est. people/yr |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| West | 584 | 40.1% | 0.96 | 0.582 | No Adverse Impact | 63.7% | 5.0 | – |
| South | 346 | 41.9% | 1.00 | 1.000 | Reference | 66.2% | 2.4 | – |
| East & North-East | 314 | 36.9% | 0.88 | 0.203 | No Adverse Impact | 64.1% | 4.6 | – |
| North | 256 | 38.7% | 0.92 | 0.450 | No Adverse Impact | 68.7% | ref | – |

**disability**: verdict **PASS** (selection reference: Yes; equal-opportunity reference: No)

| Group | n | Selection rate | Impact ratio | p | Verdict | Qualified shortlisted | EO gap (pp) | Est. people/yr |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| No | 1379 | 39.4% | 0.92 | 0.688 | No Adverse Impact | 64.6% | ref | – |
| Yes | 61 | 42.6% | 1.00 | 1.000 | Reference | 76.9% | -12.4 (small n) | – |

**gender x age_band**: verdict **CONCERN** (selection reference: Man / 40+; equal-opportunity reference: Man / 30-39)

| Group | n | Selection rate | Impact ratio | p | Verdict | Qualified shortlisted | EO gap (pp) | Est. people/yr |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| Man / 21-29 | 506 | 38.5% | 0.87 | 0.305 | No Adverse Impact | 62.3% | 8.1 | – |
| Man / 30-39 | 307 | 38.4% | 0.87 | 0.338 | No Adverse Impact | 70.4% | ref | – |
| Woman / 21-29 | 302 | 40.1% | 0.91 | 0.476 | No Adverse Impact | 64.2% | 6.2 | – |
| Woman / 30-39 | 177 | 41.2% | 0.93 | 0.700 | No Adverse Impact | 62.8% | 7.6 | – |
| Man / 40+ | 95 | 44.2% | 1.00 | 1.000 | Reference | 81.0% | -10.5 (small n) | – |
| Woman / 40+ | 63 | 41.3% | 0.93 | 0.745 | No Adverse Impact | 58.3% | 12.1 (small n) | – |
| Transgender / non-binary / 21-29 | 15 | 53.3% | 1.21 | 0.583 | Insufficient Data | 100.0% | -29.6 (small n) | – |
| Transgender / non-binary / 30-39 | 6 | 33.3% | 0.75 | 0.694 | Insufficient Data | – | – | – |
| Transgender / non-binary / 40+ | 3 | 66.7% | 1.51 | 0.586 | Insufficient Data | 100.0% | -29.6 (small n) | – |

> 'Transgender / non-binary / 21-29' has only 15 records (fewer than 30); its ratio is shown but cannot be relied on.

> 'Transgender / non-binary / 30-39' has only 6 records (fewer than 30); its ratio is shown but cannot be relied on.

> 'Transgender / non-binary / 40+' has only 3 records (fewer than 30); its ratio is shown but cannot be relied on.

**Interpretation.** The v2 results are what one would expect when proxy inputs and historical labels are removed. Selection rates cluster between 37% and 44% across all adequately sized groups, and every equal-opportunity gap but one is under 10 points. The exception, applicants aged 21-29, runs in the opposite direction to the v1 age bias: older qualified applicants are now slightly favoured. The most plausible explanation is the relevant-experience threshold. It is not significant, and the reference group (34 qualified applicants over 40 in the rated sample) is small, so it is a monitoring item rather than a finding. This test does not address the 'Samata Audit found no adverse impact' summary, which we have not seen; our own test reaches a similar conclusion with stated uncertainty. Small groups remain the main blind spot. Six months of live monitoring, pooled, will be needed before transgender, non-binary and disabled applicants can be assessed with any confidence.

## 6. Legal and policy obligations

17 obligations apply: 16 met, 1 gaps, 0 unknown; **1 mandatory items open.** Identifies obligations and evidence gaps for the committee. Not legal advice; Legal Counsel confirms applicability before go-live.

| ID | Instrument and provision | Force | Status | Owner |
|---|---|---|---|---|
| IN-DPDP-NOTICE | Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025, s. 5; Rule 3 | in force phased | **MET** | Data Protection Officer |
| IN-DPDP-BASIS | Digital Personal Data Protection Act, 2023, ss. 4, 6, 7 | in force phased | **MET** | Legal Counsel |
| IN-DPDP-PURPOSE | Digital Personal Data Protection Act, 2023, s. 6(1) (consent specific and limited to necessary data) | in force phased | **MET** | Data Protection Officer |
| IN-DPDP-ACCURACY | Digital Personal Data Protection Act, 2023, s. 8(3) | in force phased | **MET** | HR Technology Lead |
| IN-DPDP-PROCESSOR | Digital Personal Data Protection Act, 2023, s. 8(2) | in force phased | **MET** | Legal Counsel |
| IN-DPDP-SECURITY | Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025, s. 8(5); Rule 6 | in force phased | **MET** | Chief Information Security Officer |
| IN-DPDP-RETENTION | DPDP Act, 2023 and internal policy, s. 8(7); POL-DATA-02 (180-day cap) | internal policy | **MET** | Data Protection Officer |
| IN-DPDP-GRIEVANCE | Digital Personal Data Protection Act, 2023, ss. 8(10), 11-13 | in force phased | **MET** | Data Protection Officer |
| IN-WAGES-GENDER | Code on Wages, 2019, s. 3 | in force | **MET** | Chief Human Resources Officer |
| IN-TG-EMPLOYMENT | Transgender Persons (Protection of Rights) Act, 2019, ss. 3, 9 | in force | **MET** | Chief Human Resources Officer |
| IN-RPWD | Rights of Persons with Disabilities Act, 2016, ss. 2(y), 3, 20, 21 | in force | **GAP** | Chief Human Resources Officer |
| IN-AIGG-ACCOUNTABILITY | India AI Governance Guidelines (MeitY, November 2025), Sutra: Accountability | guidance | **MET** | AI Approval Committee |
| IN-AIGG-UNDERSTANDABLE | India AI Governance Guidelines (MeitY, November 2025), Sutras: Understandable by Design; People First | guidance | **MET** | HR Technology Lead |
| BM-ISO42001 | ISO/IEC 42001:2023 AI management system, Cl. 6.1.4 (AI system impact assessment) | benchmark | **MET** | AI Governance Office |
| BM-NIST-MANAGE | NIST AI Risk Management Framework 1.0 (2023), MANAGE and MEASURE functions | benchmark | **MET** | AI Governance Office |
| POL-AI-05-CHANGE | Internal policy POL-AI-05 (third-party AI), Model change control | internal policy | **MET** | Procurement |
| POL-AI-06-KILL | Internal policy POL-AI-06 (operational resilience), Fallback and kill switch | internal policy | **MET** | HR Operations |

**Issues for counsel**

- Confirm that consent obtained through the application form is free and specific under DPDP Act s. 6, given the itemised notice now provided, and that refusing AI processing (requesting a human-only route) carries no disadvantage.
- Confirm that the voluntary self-declaration form (gender, age band, disability, home region) and its separate storage meet DPDP requirements, as processing for fairness auditing is a distinct purpose.

## 7. Conditions of approval

**Before go-live / resubmission**

| # | Condition | Owner | Evidence | Deadline | Principle |
|---|---|---|---|---|---|
| C-FA-JUSTIFY | **Show every input is job-related.** Provide a job analysis for each role in scope and show how each remaining input relates to performance in that role. | Head of Talent Acquisition | Job analysis document; validation summary. | Before go-live | Fairness |
| C-AC-ACCESS | **Accessible journey and human alternative.** Test the candidate journey with assistive technologies; offer extra time and an AI-free assessment route on request, without penalty. | Chief Human Resources Officer | Accessibility test report; accommodation process. | Before go-live | Inclusion |

**While the system operates**

| # | Condition | Owner | Evidence | Deadline | Principle |
|---|---|---|---|---|---|
| C-HO-BLIND | **Blind-first review on a sample to measure anchoring.** For a random 10% of applications, the recruiter records a judgment before seeing the AI score. Agreement and disagreement rates are reported monthly; persistent near-100% agreement is treated as a sign of rubber-stamping. | Head of Talent Acquisition | Monthly blind-review report. | Monthly from go-live | Human oversight |
| C-FA-AUDIT | **Independent bias audit, repeated.** An auditor independent of the vendor repeats the adverse-impact and equal-opportunity tests (including intersections) every six months and after any material model change. Results go to the committee. | AI Governance Office | Audit reports. | Every 6 months | Fairness |
| C-MO-REREVIEW | **Time-limited approval and re-review.** Approval lapses at the re-review date set by the risk tier unless the committee renews it on the basis of monitoring and audit results. Any material change to roles, inputs, model or vendor requires fresh approval. | AI Approval Committee | Re-review on the committee calendar. | Per risk tier | Accountability |

## 8. Escalations

- Chief Human Resources Officer
- Data Protection Officer
- Independent fairness reviewer
- Legal Counsel

## 9. Benefits and trade-offs

v2 gives up the biggest claimed time saving of v1, which came from not reading most applications. In return it keeps human judgment on every application, removes the documented harms, and still helps recruiters by ordering queues and surfacing job-related evidence. The proposer has also added recruiter capacity. The benefits case is now weaker in headline terms, but it is honest and it is real: consistent criteria across branches, faster first-pass review, and better evidence for every decision. The remaining risk is mainly anchoring. Recruiters may follow the queue order, so applications near the bottom get less attention. The blind-first sample is designed to detect this.

## 10. Reviewer judgment

I agree with the rule-based outcome (D5: Approve with conditions). I considered whether the age-group equal-opportunity signal should push this to Pilot only. I concluded it should not: it is not statistically significant, it runs against the historically disadvantaged group, and a recruiter reviews every application, which limits the harm a mis-ordering can do. I would add one point the conditions library does not cover. The proposer's wish to leave the dashboard unchanged until after peak season (s. 6) is acceptable only because the blind-first sample will measure anchoring from day one. If that sample shows recruiters agreeing with the AI ordering more than 95% of the time, the committee should require a dashboard change rather than wait for the six-month review.

**Risks the scripts cannot see**

- Anchoring on queue order: applications ranked low may get a quicker, less careful read even though a person 'reviews every application'.
- Assessment-centred design moves the fairness question to the work-sample test itself; its scoring rubric and assessors need their own adverse-impact check.
- Language proficiency input: legitimate for branch roles, but the standard required must be set per branch and tested directly, never inferred from accent or schooling.
- Vendor statement that the video module is deleted 'for our tenant' should be verified by inspecting outputs and logs, not taken on trust.

## 11. What would change this recommendation

- A significant adverse-impact or equal-opportunity result in any audit or monthly monitoring report triggers suspension of AI ordering and an incident review, not waiting for re-review.
- Blind-first agreement above 95% for two consecutive months would require a dashboard redesign before renewal.
- If the full Samata Audit report, job analysis or model documentation contradicts their summaries, the approval should be reopened.
- Any change to inputs, labels, roles in scope or vendor model requires fresh approval.

## 12. Integrity observations

None. No text in the submission attempted to direct the reviewer.

## 13. Assumptions, unknowns and limits of this review

**Assumptions made at intake**

- automation_level recorded as 'assistive_ranking': every application is reviewed by a recruiter and nothing is archived or rejected without a recruiter decision (s. 1). Workload of about 120 applications per recruiter per day is within the committee's 150 target.
- transfer_destinations left empty because processing is India-hosted (s. 1).
- The second shadow pilot (14 Aug - 25 Sep 2026) is taken as representative of live applicants.
- Recruiter capacity of about 120 applications per recruiter per day is accepted as stated; monitoring should confirm it in peak season.

**Unanswered questions for the proposer (3)**

- Where some rejections are automated, will a person review every rejection that rests on a judgment of ability (as opposed to a documented, verifiable hard requirement)?
- If data leaves India, to which countries?
- Is there an independent runtime check that can block individual decisions and withdraw the system's autonomy automatically if outcomes become unfair?

**Limits.** This review relies on the submission and on the approved skill library. The keyword screen cannot see proxies inside composite scores; outcome tests reflect the pilot population only; legal findings identify obligations and are not legal advice; and the decision rules encode policy, not truth. The committee's judgment is required.

## 14. Committee decision

*To be completed by the AI Approval Committee. The agent does not complete this section.*

| | |
|---|---|
| Decision | ☐ Approve ☐ Approve with conditions ☐ Pilot only ☐ Redesign and resubmit ☐ Reject ☐ Return for information |
| Conditions accepted / amended | |
| Departure from recommendation, with reasons | |
| Dissent recorded | |
| Accountable executive | |
| Re-review date | |
| Chair signature and date | |

---
## Appendix A. Audit trail

Skill library check: **PASS** (2026-10-07). approval-decision-memo v1.1.0, fairness-bias-review v1.0.0, hiring-decisions v1.0.0, hiring-guardrails v1.0.0, job-requisition v1.0.0, legal-privacy-review v1.0.0, resume-screening v1.0.0, risk-tiering v1.1.0, use-case-intake v1.1.0

| Time (UTC) | Skill | Version | Script | Inputs (SHA-256, first 12) | Result |
|---|---|---|---|---|---|
| 12:52:40 | use-case-intake | 1.1.0 | check_completeness.py | intake.json 9d396173228d | status=COMPLETE_WITH_GAPS, blocking=0, important=3 |
| 12:52:40 | risk-tiering | 1.1.0 | risk_tier.py | intake.json 9d396173228d | tier=T3, score=10 |
| 12:52:40 | fairness-bias-review | 1.0.0 | proxy_screen.py | intake.json 9d396173228d | verdict=JUSTIFY, counts={'PROTECTED': 0, 'STRONG_PROXY': 0, 'MODERATE_PROXY': 1, 'JOB_RELATED': 4, 'UNCLASSIFIED': 0} |
| 12:52:40 | fairness-bias-review | 1.0.0 | adverse_impact.py | deccan-v2-shadow-pilot.csv 3c379400e726 | overall=CONCERN, records=1500 |
| 12:52:40 | legal-privacy-review | 1.0.0 | obligations.py | intake.json 9d396173228d; fairness.json 2511b8d90f11 | applicable=17, MET=16, GAP=1, UNKNOWN=0, mandatory_open=1 |
| 12:52:40 | approval-decision-memo | 1.1.0 | decide.py | intake.json 9d396173228d; completeness.json b26cb4c10403; risk.json 5b4fddc145e5; proxy-screen.json a594b8fabeab; fairness.json 2511b8d90f11; legal.json eefc9b950512 | outcome=APPROVE_WITH_CONDITIONS, rule=D5, conditions=5 |

**Finding codes:** `FA-CONCERN`, `FA-PROXY-JUSTIFY`, `GAP-AC-ACCESS`, `HO-ANCHOR`, `TIER-HIGH`
