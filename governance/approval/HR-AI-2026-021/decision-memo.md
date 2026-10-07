# AI Use Case Approval: Decision Memo

**Proposal:** HR-AI-2026-021 · Governed hiring agent for branch roles (in-house, skill-based)  
**Organisation:** Deccan Ledger Finance Ltd (fictional NBFC)  
**Submitted by:** Rohan Kulkarni (Head of Talent Acquisition), 2026-10-05  
**Prepared by:** AI Use Case Approval Agent, 2026-10-07  
**Status:** RECOMMENDATION. Awaiting decision of the AI Approval Committee.

## 1. Recommendation

> ### Approve with conditions
> Rule D5 · Risk tier T3 (High) · Approver: AI Approval Committee (quorum)
>
> Approve the governed hiring agent with conditions, at autonomy level L2 at most, for six months. The design keeps the line the committee drew for TalentSort: no candidate is rejected on a judgment of ability without a recruiter confirming it. It allows automation only where a decision is a checkable fact (a regulatory certificate, a stated inability to work at the branch), with evidence quoted, an appeal route and a 10% blind re-check. Scores come from published rules, not a learned model, so the past-decision bias that sank TalentSort v1 has no route in. The independent runtime guardian, which can withdraw autonomy on its own, is the main reason to accept automated hard-requirement rejections at all. Two conditions must be evidenced before the agent may act alone: the job analysis behind each input, and the controls around hard-requirement rejection.

## 2. Key findings

1. **No red lines; tier T3 (score 10/21, evaluative floor).** Automation is scored 2, not 3: rejection without a person is limited to verifiable hard requirements, and every judgment-based rejection is reviewed by a recruiter. Evidence: risk.json, intake human_oversight.
2. **No learned model, no historical labels.** Scoring is deterministic from the job analysis; the language model reads and writes notes but does not set scores. This removes the label-bias route and makes every score reproducible. Evidence: intake data.training_data.
3. **Shadow-pilot fairness: CONCERN, not FAIL.** No group shows significant adverse impact; two signals remain: a 10.8-point equal-opportunity gap for qualified 21–29 year-olds (p = 0.25), and groups too small to test. Evidence: fairness.json.
4. **All 16 applicable legal obligations met on the evidence given**, including a disclosed cross-border transfer to the model provider. Two claims still need documents on file. Evidence: legal.json; intake claims_needing_evidence.
5. **Runtime governance is designed in, not bolted on.** Criteria gate on every requisition, per-decision checks, group monitoring with an automatic circuit breaker, blind audit sampling and a hash-chained ledger. Evidence: hiring-guardrails skill; condition C-HO-GUARDIAN.

## 3. What the system does to a candidate

| Aspect | As submitted |
|---|---|
| Primary function | cv screening ranking |
| Stage of hiring | initial screening |
| Automation level | auto reject hard requirements |
| AI output | Proposed action per candidate with quoted evidence: advance, reject on failed hard requirement, hold for a person, human-only |
| Human reviews every rejection | no |
| Recruiter sees AI score first | yes |
| Applications per year | 60,000 |
| Roles | Relationship Manager (Investments & Insurance), Branch sales, Collections |
| Vendor | In-house agent on a general-purpose model, with a governed skill library |

An applicant applies online, is told AI assists, and can choose a human-only route. Their resume is blinded and scored against four job-related criteria. If they lack the NISM-Series-V-A certificate the regulator requires, they receive a letter naming the requirement and the evidence checked, with a 14-day human review route. If they score well, they are invited to interview. If they are borderline, unclear, flagged or low-scoring, a recruiter decides. Before any of this takes effect, the guardian checks it.

## 4. Risk profile

Score **10/21**, tier **T3 (High)** (evaluative-system floor applied). EU AI Act benchmark: High-risk (Annex III, point 4: employment, recruitment and selection).

| Dimension | Score | Reason |
|---|---:|---|
| Consequence | 3 | Evaluates candidates (cv_screening_ranking at initial_screening stage): outcome affects access to employment |
| Automation | 2 | Automation level 'auto_reject_hard_requirements' (verifiable requirements only; a person reviews every judgment-based rejection) |
| Scale | 3 | 60,000 applications a year |
| Data sensitivity | 1 | CV and contact data are personal data |
| Opacity | 0 | explainable, documented, in-house |
| Contestability gap | 0 | appeal, alternative and grievance routes in place |
| Oversight weakness | 1 | AI score seen before reviewer forms own view (anchoring) |

## 5. Fairness evidence

**Input screen: JUSTIFY.** 6 inputs: 4 job related, 2 unclassified.

| Input | Category | Linked to | Action |
|---|---|---|---|
| Work-sample assessment score | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Relevant sales experience with customers (months, capped at 24) | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Product and compliance skills listed | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Branch language test result | Unclassified | – | Proposer must justify its relevance to the job before it can be used. |
| NISM-Series-V-A certificate (hard requirement) | Job Related | – | Acceptable in principle; confirm it is measured the same way for every candidate and is validated for this role. |
| Able to work at branch (hard requirement) | Unclassified | – | Proposer must justify its relevance to the job before it can be used. |

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

**Interpretation.** The pilot used the same skills-first method as TalentSort v2, so the same signals carry over: no significant adverse impact, a non-significant age-related equal-opportunity gap, and small groups. Automated hard-requirement rejections add a new question the pilot cannot answer: whether the certification requirement itself falls unequally on groups. That is not a reason to drop a regulatory requirement, but the committee should see it, so the guardian reports hard-requirement rejection rates by group monthly.

## 6. Legal and policy obligations

16 obligations apply: 16 met, 0 gaps, 0 unknown; **0 mandatory items open.** Identifies obligations and evidence gaps for the committee. Not legal advice; Legal Counsel confirms applicability before go-live.

| ID | Instrument and provision | Force | Status | Owner |
|---|---|---|---|---|
| IN-DPDP-NOTICE | Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025, s. 5; Rule 3 | in force phased | **MET** | Data Protection Officer |
| IN-DPDP-BASIS | Digital Personal Data Protection Act, 2023, ss. 4, 6, 7 | in force phased | **MET** | Legal Counsel |
| IN-DPDP-PURPOSE | Digital Personal Data Protection Act, 2023, s. 6(1) (consent specific and limited to necessary data) | in force phased | **MET** | Data Protection Officer |
| IN-DPDP-ACCURACY | Digital Personal Data Protection Act, 2023, s. 8(3) | in force phased | **MET** | HR Technology Lead |
| IN-DPDP-SECURITY | Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025, s. 8(5); Rule 6 | in force phased | **MET** | Chief Information Security Officer |
| IN-DPDP-RETENTION | DPDP Act, 2023 and internal policy, s. 8(7); POL-DATA-02 (180-day cap) | internal policy | **MET** | Data Protection Officer |
| IN-DPDP-GRIEVANCE | Digital Personal Data Protection Act, 2023, ss. 8(10), 11-13 | in force phased | **MET** | Data Protection Officer |
| IN-DPDP-TRANSFER | Digital Personal Data Protection Act, 2023, s. 16 | in force phased | **MET** | Data Protection Officer |
| IN-WAGES-GENDER | Code on Wages, 2019, s. 3 | in force | **MET** | Chief Human Resources Officer |
| IN-TG-EMPLOYMENT | Transgender Persons (Protection of Rights) Act, 2019, ss. 3, 9 | in force | **MET** | Chief Human Resources Officer |
| IN-RPWD | Rights of Persons with Disabilities Act, 2016, ss. 2(y), 3, 20, 21 | in force | **MET** | Chief Human Resources Officer |
| IN-AIGG-ACCOUNTABILITY | India AI Governance Guidelines (MeitY, November 2025), Sutra: Accountability | guidance | **MET** | AI Approval Committee |
| IN-AIGG-UNDERSTANDABLE | India AI Governance Guidelines (MeitY, November 2025), Sutras: Understandable by Design; People First | guidance | **MET** | HR Technology Lead |
| BM-ISO42001 | ISO/IEC 42001:2023 AI management system, Cl. 6.1.4 (AI system impact assessment) | benchmark | **MET** | AI Governance Office |
| BM-NIST-MANAGE | NIST AI Risk Management Framework 1.0 (2023), MANAGE and MEASURE functions | benchmark | **MET** | AI Governance Office |
| POL-AI-06-KILL | Internal policy POL-AI-06 (operational resilience), Fallback and kill switch | internal policy | **MET** | HR Operations |

**Issues for counsel**

- Confirm in writing that the model provider's enterprise terms prohibit training on, or retaining, candidate data, and that the US processing is not to a country restricted under DPDP Act s. 16.
- Confirm that an automated rejection for a missing statutory certificate, with a human review route on request, is acceptable under the company's equal opportunity policy and POL-AI-03 as amended by this approval.

## 7. Conditions of approval

**Before go-live / resubmission**

| # | Condition | Owner | Evidence | Deadline | Principle |
|---|---|---|---|---|---|
| C-HO-HARDREQ | **Automated rejection only for verifiable hard requirements.** The system may reject on its own only when a documented legal, operational or safety requirement is clearly not met. Ambiguous or in-progress evidence goes to a person. Every automated rejection letter names the requirement and the evidence checked and offers a 14-day human review. A random 10% are re-checked by a person, and rejection rates by group are reported monthly. | Head of Talent Acquisition | Job-spec gate records; letter template; monthly audit and fairness reports. | Before go-live | Human oversight |
| C-FA-JUSTIFY | **Show every input is job-related.** Provide a job analysis for each role in scope and show how each remaining input relates to performance in that role. | Head of Talent Acquisition | Job analysis document; validation summary. | Before go-live | Fairness |

**While the system operates**

| # | Condition | Owner | Evidence | Deadline | Principle |
|---|---|---|---|---|---|
| C-HO-GUARDIAN | **Runtime guardian with circuit breaker.** An independent runtime guardian checks every decision before it takes effect, monitors advancement by self-declared group, and withdraws autonomy automatically (to assist-only) on statistically significant adverse impact. Only the committee can restore autonomy. | AI Governance Office | Guardian reports per batch; ledger verification; breaker test record. | Every batch | Safety |
| C-HO-BLIND | **Blind-first review on a sample to measure anchoring.** For a random 10% of applications, the recruiter records a judgment before seeing the AI score. Agreement and disagreement rates are reported monthly; persistent near-100% agreement is treated as a sign of rubber-stamping. | Head of Talent Acquisition | Monthly blind-review report. | Monthly from go-live | Human oversight |
| C-FA-AUDIT | **Independent bias audit, repeated.** An auditor independent of the vendor repeats the adverse-impact and equal-opportunity tests (including intersections) every six months and after any material model change. Results go to the committee. | AI Governance Office | Audit reports. | Every 6 months | Fairness |
| C-MO-REREVIEW | **Time-limited approval and re-review.** Approval lapses at the re-review date set by the risk tier unless the committee renews it on the basis of monitoring and audit results. Any material change to roles, inputs, model or vendor requires fresh approval. | AI Approval Committee | Re-review on the committee calendar. | Per risk tier | Accountability |

## 8. Escalations

- Chief Human Resources Officer
- Data Protection Officer
- Independent fairness reviewer
- Legal Counsel

## 9. Benefits and trade-offs

Compared with TalentSort v2 (assist-only ordering), this design saves more recruiter time: recruiters no longer read applications that plainly cannot be hired because of a regulatory requirement, or that clearly qualify for interview. The cost is a small, bounded set of automated rejections. Because they are restricted to facts, explained, appealable and audited, the expected harm is low, and the circuit breaker limits how long an error could run. The design deliberately leaves the most consequential judgment, rejecting someone as not good enough, with people.

## 10. Reviewer judgment

I agree with D5, Approve with conditions, and with capping autonomy at L2. I would not support L3 (automated low-score rejection) on this evidence, and the policy file records that L3 needs a Board exception. One point the rules do not capture: this proposal comes from the same organisation that built the governance library, and the same agent architecture reviewed it. That is a structural conflict of interest. The committee should ask the independent fairness reviewer to repeat the shadow-pilot analysis, and have Internal Audit check the guardian's first three monthly reports.

**Risks the scripts cannot see**

- Language-model variability: the agent's notes could differ run to run. Scores do not, because they come from scripts, but recruiters may read the notes. Notes must stay labelled as non-binding.
- Requirement creep: a manager could relabel a preference as an 'operational' hard requirement to automate rejections. The criteria gate checks basis and proxies, but a person should review every new hard requirement.
- Parser limits: unusual CV formats lower parse confidence and add recruiter work rather than errors. That is the right failure mode, but it should be measured.
- Automation complacency: as recruiters see fewer applications, borderline reviews may become cursory. The blind-first sample measures this.

## 11. What would change this recommendation

- A RED fairness status in any monthly report (the breaker already drops autonomy to L1 automatically).
- Blind-audit disagreement above 5% on automated decisions, or appeals upheld above 5%.
- Any new hard requirement without a documented legal, operational or safety basis.
- A change of model provider or model version without re-running the evaluation suite.

## 12. Integrity observations

None. No text in the submission attempted to direct the reviewer.

## 13. Assumptions, unknowns and limits of this review

**Assumptions made at intake**

- automation_level 'auto_reject_hard_requirements': the agent may reject alone only on a cleanly failed, documented hard requirement; all judgment-based rejections are confirmed by a recruiter.
- generative_llm_scoring recorded false: the language model does not set scores; scores come from deterministic scripts. The model's notes are labelled as judgment.
- vendor_reuses_data_for_training recorded false on the basis of the enterprise terms with the model provider; Legal to confirm in writing.
- Candidate data is processed by the model provider outside India; recorded as a cross-border transfer.
- The shadow pilot (synthetic, 1,500 applicants) is taken as representative of live applicants for the role family.

**Unanswered questions for the proposer (0)**

None.

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
| 12:57:39 | use-case-intake | 1.1.0 | check_completeness.py | intake.json 210ad601fbb9 | status=COMPLETE, blocking=0, important=0 |
| 12:57:39 | risk-tiering | 1.1.0 | risk_tier.py | intake.json 210ad601fbb9 | tier=T3, score=10 |
| 12:57:39 | fairness-bias-review | 1.0.0 | proxy_screen.py | intake.json 210ad601fbb9 | verdict=JUSTIFY, counts={'PROTECTED': 0, 'STRONG_PROXY': 0, 'MODERATE_PROXY': 0, 'JOB_RELATED': 4, 'UNCLASSIFIED': 2} |
| 12:57:39 | fairness-bias-review | 1.0.0 | adverse_impact.py | deccan-v2-shadow-pilot.csv 3c379400e726 | overall=CONCERN, records=1500 |
| 12:57:39 | legal-privacy-review | 1.0.0 | obligations.py | intake.json 210ad601fbb9; fairness.json 2511b8d90f11 | applicable=16, MET=16, GAP=0, UNKNOWN=0, mandatory_open=0 |
| 12:57:39 | approval-decision-memo | 1.1.0 | decide.py | intake.json 210ad601fbb9; completeness.json ff674fe88ed6; risk.json aaa898a79edb; proxy-screen.json 5a582903bc20; fairness.json 2511b8d90f11; legal.json 25649457a575 | outcome=APPROVE_WITH_CONDITIONS, rule=D5, conditions=6 |

**Finding codes:** `FA-CONCERN`, `FA-PROXY-JUSTIFY`, `HO-ANCHOR`, `HO-HARDREQ-AUTO`, `TIER-HIGH`
