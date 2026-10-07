# Resubmission to AI Approval Committee

**Ref:** HR-AI-2026-014 · **Version:** 2.0 · **Date:** 2 October 2026
**Organisation:** Deccan Ledger Finance Ltd *(fictional)*
**Submitted by:** Rohan Kulkarni, Head of Talent Acquisition
**Accountable executive:** Meera Iyer, Chief Human Resources Officer
**Title:** TalentSort v2: skills-first screening assistant for branch and field sales hiring

> Fictional teaching case. This version responds to the committee's "Redesign and resubmit"
> recommendation on version 1.

---

## 1. What changed

| v1 | v2 |
|---|---|
| Video "Communication Confidence Score" | **Removed.** HireSort has disabled and deleted the module for our tenant; no video is collected. |
| Top 20% shown; others auto-archived after 14 days | **Every application is reviewed by a recruiter.** The AI orders the queue and highlights matched skills. Nothing is archived or rejected without a recruiter decision. Two contract recruiters added for peak season (workload ~120 applications/recruiter/day). |
| Trained on past hire / not-hire decisions | **Retrained** on a skills-based label: performance on a validated work-sample assessment, plus job analysis for each role. No past hiring decisions used. |
| 11 inputs incl. PIN code, college tier, graduation year, gaps, CTC | **5 inputs**, all from the job analysis (below). |
| Singapore hosting; vendor reuses data | **India region hosting**; contract bars any reuse of our candidate data. |
| 2-year retention | **180 days** unless the candidate opts into our talent pool. |
| Vendor self-assessment | **Independent bias audit** by Samata Audit LLP *(fictional)*, plus a new 10-week shadow pilot. |

## 2. Inputs

- Skills assessment score (work-sample: mock customer call and loan-eligibility case exercise)
- Relevant certification (NISM / IRDAI where the role requires it)
- Relevant sales experience (minimum 0-12 months depending on role; not scored above the minimum)
- Structured screening questions (availability for field work, two-wheeler licence for collections roles)
- Language proficiency required for the branch, tested directly in the assessment

## 3. Safeguards

- **Notice:** job ads and the application form explain that AI helps order applications, that a
  person reviews every one, and how to request a human-only assessment. English, Hindi, Marathi,
  Kannada, Telugu, Bengali and Assamese.
- **Explanations:** recruiters see the top factors for each ranking; candidates can ask for an
  explanation.
- **Appeals:** any candidate can ask for re-review by a recruiter who has not seen the AI score
  (answered within 15 working days).
- **Grievance officer:** named in the privacy notice.
- **Lawful basis:** consent, through an itemised notice reviewed by the DPO.
- **Accuracy:** candidates see and can correct their parsed profile before it is ranked;
  parsing tested on 2,000 real CVs including regional-language formats (98.4% field accuracy).
- **Training:** all recruiters completed a 2-hour module on the tool's limits and automation
  bias; overrides are logged with reasons.
- **Fairness audit data:** voluntary self-declaration with inclusive gender options, stored
  separately from TalentSort, never used by the model.
- **Vendor contract:** DPDP processor terms, independent audit access, 30-day notice of model
  changes, breach notification, indemnity. Information Security assessment completed.
- **Monitoring:** monthly dashboard to the CHRO (selection rates by group, override rates,
  appeals, parsing errors), reviewed by the AI Governance Office; incident runbook agreed.
- **Kill switch:** the AI ordering can be switched off within hours; recruiters fall back to
  date order. Fallback tested on 15 September 2026.

## 4. Evidence attached

- `deccan-v2-shadow-pilot.csv`: new shadow pilot, 1,500 applicants (14 Aug - 25 Sep 2026),
  independent panel ratings for half.
- Samata Audit LLP report (summary): no adverse impact found at the four-fifths threshold for
  gender, age band, home region or disability on the v2 shadow data.
- Job analysis for six role families; vendor model documentation (v2.1).

## 5. Answers to the committee's questions on v1

- **Biometric categorisation:** none. No images or video are collected.
- **Social media screening:** none.
- **Large language models:** none are used to score or rank candidates. CV parsing uses
  HireSort's rules-and-entity-recognition parser (documented in model documentation v2.1).
- **Alternatives considered:** more recruiters only (cost roughly 3x the licence and still slow
  in peak season); structured screening questions alone (adopted as one of the five inputs).
- **Training data:** work-sample assessment results from 9,400 candidates assessed in
  2024-2026, scored by trained assessors against a published rubric.

## 6. Still open

- Recruiters currently see the AI ordering before they open a profile. We would prefer not to
  change the dashboard until after peak season.
- The accessibility review of the assessment platform is scheduled for November.
