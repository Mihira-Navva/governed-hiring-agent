# Legal landscape for AI in hiring (India-first), as of October 2026

Plain-language notes for reviewers. They help identify obligations; they are not legal advice.

## India: binding law

**Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025.** The Rules were notified in
November 2025 and the regime phases in over 18 months: the Data Protection Board and some
provisions started at once; most substantive duties (notice, consent, security, breach
reporting, data principal rights) commence in May 2027. Until then the SPDI Rules, 2011 under
the IT Act continue. For hiring AI the key duties are:
- notice and a lawful basis for processing (ss. 5-7); consent must be specific to the purpose;
- data used to make decisions about a person must be complete, accurate and consistent (s. 8(3));
- processors (vendors) only under a valid contract (s. 8(2));
- reasonable security safeguards (s. 8(5)), erasure when the purpose is served (s. 8(7));
- grievance redressal and rights to access, correct and erase (ss. 8(10), 11-13);
- cross-border transfer allowed except to restricted countries (s. 16).
India has no GDPR-style right against automated decisions; the organisation's own policy
(POL-AI-03) fills that gap.

**Code on Wages, 2019.** In force with the other three Labour Codes from 21 November 2025.
Section 3 prohibits gender discrimination, including against transgender persons, in
recruitment for the same or similar work. An AI that shortlists women at a lower rate without
job-related justification is a compliance problem, not only an ethical one.

**Rights of Persons with Disabilities Act, 2016.** Equal opportunity policies for every
establishment (s. 21), non-discrimination in government employment (s. 20), and reasonable
accommodation (s. 2(y), s. 3). Timed online tests, video interviews and CV parsers that
mis-read accessible formats can all exclude disabled candidates.

**Transgender Persons (Protection of Rights) Act, 2019.** Prohibits unfair treatment in
recruitment (ss. 3, 9).

**Constitution of India.** Arts. 14-16 bind the State; public sector employers must not select
arbitrarily or discriminatorily.

## India: guidance

**India AI Governance Guidelines (MeitY, November 2025).** Seven principles ("sutras") including
Trust, People First, Fairness and Equity, Accountability, and Understandable by Design, with
recommendations across six pillars. Non-binding; the Government's stated approach is to apply
existing laws rather than enact a new AI law now. Useful as the Indian vocabulary for the
committee's principles.

## Benchmarks used for good practice

**EU AI Act.** AI used to recruit, filter applications and evaluate candidates is high-risk
(Annex III, point 4). Prohibitions, including emotion recognition in the workplace
(Art. 5(1)(f)), apply since 2 February 2025. The Digital Omnibus on AI, in force since
27 July 2026, moved Annex III high-risk obligations to 2 December 2027. Deployers then must
ensure trained human oversight, monitoring, log retention and information to affected persons
(Art. 26), and people get a right to an explanation (Art. 86). Binding only where EU candidates
are in scope; elsewhere it is the most developed benchmark available.

**GDPR Art. 22.** No solely automated decisions with significant effects without safeguards.

**NYC Local Law 144.** Independent annual bias audit, public summary and 10 business days' notice
for automated employment decision tools used on New York City candidates. Its audit method
(selection rates and impact ratios by sex, race/ethnicity and their intersections) is the model
for `adverse_impact.py`.

**ISO/IEC 42001:2023.** Certifiable AI management system standard; requires AI system impact
assessments. **NIST AI RMF 1.0.** Govern, Map, Measure, Manage functions; voluntary.

## How the library maps to these

| Library element | Main legal or standard anchor |
|---|---|
| Completeness gate, claims needing evidence | DPDP s. 8(3); ISO/IEC 42001 documentation |
| Risk tiering with evaluative floor | EU AI Act Annex III; NIST MAP |
| Red lines RL-01, RL-06 | EU AI Act Art. 5(1)(f), (g) |
| Red line RL-02 | Policy POL-AI-03; GDPR Art. 22; India AIGG People First |
| Proxy screen, adverse impact | Code on Wages s. 3; RPwD Act; Transgender Persons Act; NYC LL144 method |
| Conditions, monitoring, re-review | NIST MANAGE; EU AI Act Art. 26; ISO/IEC 42001 |
| Skill catalog, hashes, permissions | ISO/IEC 42001 operational control; NIST GOVERN |
