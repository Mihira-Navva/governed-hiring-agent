# Reading an AI hiring proposal: reviewer's notes

These notes capture what experienced reviewers look for. They are the "domain method" layer of
this skill: the questions a specialist asks that a general model would not think to ask.

## 1. Follow the candidate, not the product description

Trace one ordinary applicant from the moment they press *Apply* to the moment they are hired or
rejected. At each step ask: who or what decides, what do they see, and what happens if nobody
acts? Most hidden automation is found here.

| Phrase in the proposal | What to check |
|---|---|
| "AI assists recruiters" | Does a person see *every* applicant, or only the top of the ranking? |
| "Low-fit profiles are de-prioritised" | Are they ever looked at? What is the recruiter's daily volume? |
| "Auto-archived after N days" | Archive followed by a templated rejection is an automated rejection. |
| "Recruiters can override" | Is overriding easy, logged, and actually done? Ask for override rates. |
| "Bias-free / fair by design" | There is no such thing. Ask for audit results by group. |
| "Validated model" | Validated for what, on whose data, and by whom? |
| "Trained on our top performers" | Who became a "top performer" was itself shaped by past hiring and promotion. |
| "Communication / confidence / culture-fit score" | Often inferred from voice, face or style: possible affect inference and proxy bias. |
| "Vendor is certified / compliant" | Certified against what standard? Ask for the certificate and its scope. |

## 2. Look for the label

A model learns to predict its training label. If the label is "was hired by us in 2019-2024",
the model learns to reproduce 2019-2024 hiring, including its biases. Prefer labels tied to job
performance measured fairly, and even then check how performance was rated.

## 3. Count the people

Scale changes the ethics. A 2% error rate on 60,000 applications is 1,200 people. Write the
number of affected people into the record, not just the percentage.

## 4. Ask what the alternative is

A good proposal says what problem exists today (e.g. recruiters spend 70% of their time on
first-pass CV reading) and why lower-risk options (structured screening questions, skills tests,
more recruiters at peak) were not enough.

## 5. Indian context reminders

- Name, surname, home town, PIN code, mother tongue, college and even hobbies can reveal caste,
  religion, region or class. Treat them as proxies, not neutral facts.
- Career gaps are common for women (marriage, maternity, caregiving) and for people with
  disabilities or long illnesses.
- English fluency and "polish" correlate with schooling medium and class more than with ability
  in many field roles.
- Candidates may apply on mobile networks with poor video quality; video-based scores can
  penalise connectivity rather than competence.
