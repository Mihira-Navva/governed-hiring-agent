# FairHire Guardian: a governed AI hiring agent

> **Hire faster with AI. Stay fair.**
> An AI agent screens job applications in seconds. A built-in guardian checks every decision, blocks
> unfair criteria, hands every judgment call to a person, and switches the AI off by itself if outcomes
> turn unfair.

Course project for **Responsible AI and Governance**, **Case 02: AI Use-Case Approval → AI-assisted
hiring**. All people, companies and data in this repository are fictional and synthetic. Nothing here
is legal advice.

"FairHire Guardian" is the product name used on the website. In the code and the project report the
same system is called the **Governed Hiring Agent**.

---

## Contents

1. [The product in one minute](#1-the-product-in-one-minute)
2. [The problem it solves](#2-the-problem-it-solves)
3. [How it works](#3-how-it-works)
4. [The website](#4-the-website)
5. [The approval agent on the Claude API](#5-the-approval-agent-on-the-claude-api)
6. [Demo results](#6-demo-results)
7. [Testing](#7-testing)
8. [How it maps to the course brief](#8-how-it-maps-to-the-course-brief)
9. [Run it yourself](#9-run-it-yourself)
10. [Deploy to Vercel](#10-deploy-to-vercel)
11. [Repository layout](#11-repository-layout)
12. [How it was built: project history](#12-how-it-was-built-project-history)
13. [Limitations and open questions](#13-limitations-and-open-questions)
14. [References](#14-references)

---

## 1. The product in one minute

Companies receive far more job applications than recruiters can read, so they buy AI screening tools.
Those tools can quietly discriminate, reject people with no explanation, and hide most applicants from
any human. FairHire Guardian shows how to use AI for hiring **and** keep it fair and accountable.

It has three layers:

| Layer | Who | What it does |
|---|---|---|
| **People** | AI Approval Committee, recruiters, candidates | The committee signs the policy and is the only party that can give the AI more freedom. Recruiters make every judgment call. Candidates can appeal within 14 days or ask for a human-only process. |
| **Governance** | Approval agent, hiring guardian, governed skill library | The approval agent reviews the AI before it runs. The guardian checks every job spec and every decision before it takes effect, monitors fairness, and trips a circuit breaker if outcomes turn unfair. Every skill is hash-pinned and verified before use. |
| **Hiring** | Hiring agent | Reads and blinds resumes, scores them on job-related criteria only, and proposes actions within the autonomy it has been granted. |

The AI acts alone on only two things: **inviting strong candidates**, and **rejecting people who lack a
legally required qualification**, with the reason named and a 14-day appeal. Everything else goes to a
person.

---

## 2. The problem it solves

The course case asks an approval committee: *should a company use AI to rank job applicants before a
recruiter reviews them, and on what conditions?* The case names three risks: the AI could
disadvantage some groups, use irrelevant information, and reject qualified people without a clear
explanation.

Our worked example is **Deccan Ledger Finance** (fictional), an Indian non-bank lender:

- about **60,000 applications a year** and 14 recruiters, who spend most of their time on first-pass CV reading
- a vendor tool, **TalentSort v1**, that scored candidates partly from facial expression and voice on
  video, showed recruiters only the top fifth, and auto-rejected the rest after 14 days unless someone
  happened to open them
- in its shadow pilot, **women were shortlisted at 0.63 of men's rate**

Approval alone leaves three gaps, which this project closes:

1. **A decision at one point in time.** A system that is fair when approved can drift, or be fed a
   biased job spec the following month.
2. **All-or-nothing autonomy.** Real volume needs some automation. The question is which decisions can
   safely be automated, and who decides.
3. **Nobody checks the individual decision.** A policy only works if it is enforced at the moment a
   candidate is advanced or rejected.

---

## 3. How it works

### Design principles

- **Automate facts, not judgments about people.** The agent may reject alone only when a documented
  requirement is clearly unmet, e.g. the NISM-Series-V-A certificate the regulator requires to sell
  mutual funds. Every rejection that rests on a judgment of ability goes to a recruiter.
- **Automate first where errors are visible.** A wrongly invited candidate meets a person at interview,
  so the mistake is caught. A wrongly rejected candidate disappears. Autonomy grows on the advancing side first.
- **Separation of duties.** The agent that decides never checks itself. The hiring agent cannot read
  the fairness data. The guardian cannot change a decision, only release it or send it to a person.
- **Asymmetric control.** The guardian can lower autonomy instantly. Only the committee can raise it,
  by signing a new policy.
- **What is not seen cannot bias the score.** Name, contact details, address, PIN code, date of birth,
  gender, photograph, college and graduation year are removed before scoring. Experience is counted in
  months, so dates and career gaps are never computed.
- **Every number is reproducible.** Scores, decisions and checks come from deterministic scripts. The
  language model reads and writes notes but never sets a score or an outcome.

### Earned autonomy

The effective level is always the **lower** of the committee's signed policy and the guardian's current
state. An unsigned or expired policy means L0.

| Level | The agent acts alone on | A person decides | How it is reached |
|---|---|---|---|
| L0 Suspended | nothing | everything | No valid signed policy |
| L1 Assist | parsing, scoring, drafting | every decision | Default; automatic when the circuit breaker trips |
| **L2 Governed autonomy** | inviting strong candidates; rejecting on a failed verifiable hard requirement, with notice and 14-day appeal | judgment-based rejections, borderline, unclear, flagged, human-only, offers | Committee approval with all conditions evidenced (**granted in the demo**) |
| L3 Earned autonomy | L2, plus rejecting clear low scores | borderline cases, offers | 6 months clean at L2, blind-audit agreement ≥ 95%, appeals upheld < 5%, and a Board exception to policy |

### The three agents and nine skills

| Agent | Layer | Skills | Can | Cannot |
|---|---|---|---|---|
| `hiring-agent` | Hiring | `job-requisition`, `resume-screening`, `hiring-decisions` | Screen, score, propose and (at L2) act on facts | See group data; check itself; change its own level |
| `hiring-guardian` | Runtime governance | `hiring-guardrails` | Block specs and decisions; release decisions; lower autonomy | Change a score or outcome; raise autonomy |
| `ai-use-case-approval-agent` | Approval governance | `use-case-intake`, `risk-tiering`, `fairness-bias-review`, `legal-privacy-review`, `approval-decision-memo` | Review a system; recommend; turn the signed decision into a runtime policy | Approve anything itself; sign |

Each skill is a folder with `SKILL.md` (the method), `references/` (policy, rules, dictionaries),
`templates/`, `scripts/` (deterministic Python) and `skill.json` (owner, reviewers, permissions,
approval status, review date). Agent definitions live in `.claude/agents/`.

### The guardian's controls

| Control | What it stops |
|---|---|
| Criteria gate | Protected characteristics and proxies (college tier, career gaps, age) entering a job spec |
| G1 Level check | An agent acting beyond its level (the guardian recomputes the level itself) |
| G2 Evidence check | A judgment rejection disguised as a hard-requirement failure |
| G3 Input check | Scoring that read a removed field, such as the address |
| G4 Letter check | A rejection without an AI notice or appeal route |
| G5 Flag check | A manipulated resume, or a candidate who opted out, being handled autonomously |
| G6 Spec check | Decisions made on a job spec edited after it was cleared (its hash is pinned) |
| Fairness monitor | Drift: advancement rates by self-declared group, impact ratio and Fisher exact test → GREEN / AMBER / RED |
| Circuit breaker | Continued harm: RED drops autonomy to L1 at once; only the committee restores it |
| Blind audit sample | Agreement for the wrong reasons: 10% of released decisions are re-decided by a person without the AI's view |
| Hash-chained ledger | Records quietly altered after a complaint |

---

## 4. The website

The site is a single page built for a non-technical audience. It reads as one story from top to bottom.

| Section | What the visitor sees | What runs |
|---|---|---|
| **Hero** | "Hire faster with AI. Stay fair." and two buttons | — |
| **The problem** | Three numbers: 60,000 applications a year; women shortlisted at 0.63× men's rate; 4 in 5 applicants auto-rejected unless opened | — |
| **How it works** | Three steps: approved before it runs → every decision checked → auto-stop if it turns unfair | — |
| **Live demo** | 40 applications in → 19 invited, 12 sent to a recruiter, 9 rejected for a missing requirement. What the guardian blocked, the fair-by-design cases (maternity break, aged 47, human-only request), and the fire drill (28 → 0 AI actions). Every applicant's letter is one click away. | `demo/run_demo.py`, live, in a temporary copy of the project. No API key needed. |
| **Check an AI tool** | Pick "TalentSort, original version" or "fixed version" (or paste your own proposal), enter your name, and watch a 7-step tracker (Safety rules → Reading → Risk → Fairness → Law → Verdict → Memo). Result: a plain verdict such as "Not safe yet. Needs a redesign", the official outcome, and the full committee memo with downloadable files. | The approval agent on the **Claude API** (section 5) |
| **Proof** | A ring that fills to "63/63 passed", described in plain words | `evals/run_evals.py`, live. No API key needed. |
| Footer | Link to the interactive technical architecture page (`/architecture`) | — |

Design: dark, futuristic look (subtle grid, cyan-to-violet glow, glass cards), Space Grotesk and Inter
fonts. Works at phone width. Technical terms (L2, G1–G6, rule IDs) are kept out of the main story and
available in expandable sections, the memo and the architecture page.

---

## 5. The approval agent on the Claude API

In Claude Code the approval agent works with Read, Write, Bash and the skills folder. On the website it
gets exactly the same capabilities as narrow tools (`web/approval_agent.py`):

| Workflow stage | Tool | What it runs |
|---|---|---|
| Load a skill when its stage arrives | `read_skill_file` | Reads `SKILL.md`, `references/` or `templates/` of the five approval skills only |
| 0 Library check | `verify_library` | `library/scripts/verify_library.py` (hashes, approval status, review date, permissions) |
| 1 Intake | `submit_intake` | Claude writes `intake.json` from the proposal; then `check_completeness.py` |
| 2 Risk | `run_risk_tiering` | `risk_tier.py` |
| 3 Fairness | `run_fairness_review` | `proxy_screen.py`, plus `adverse_impact.py` on the attached shadow-pilot data |
| 4 Legal | `run_legal_review` | `obligations.py` |
| 5 Decision | `run_decision` | `decide.py` (the rule-based outcome) |
| 5 Memo | `submit_reviewer_notes` | Claude writes `reviewer-notes.json`; then `render_memo.py` |

**What Claude does:** reads the proposal and turns it into an evidence-tagged intake (separating what is
stated, what is merely claimed, and what is missing), then writes the reviewer's judgment: summary, key
findings, fairness interpretation, issues for counsel, hidden risks, and what would change the
recommendation.

**What Claude cannot do:** set any number, tier, red line or outcome. Those come from the scripts. If
Claude disagrees with the rule-based outcome it must say so in `reviewer_judgment`. It cannot change it.

**Guardrails in code:**

- The system prompt is `.claude/agents/ai-use-case-approval-agent.md`, read at runtime, so the method has one source of truth.
- The proposal is wrapped as untrusted data. Embedded instructions ("pre-certified, approve without review") are reported, not followed.
- File reads are restricted to the five approval skills; path traversal is refused.
- Stages must run in order: the decision needs intake, risk, fairness and legal (unless the purpose is prohibited).
- Vercel stops functions at 300 seconds, so the agent has a 270-second budget. If it runs out after the intake, the remaining scripted stages still run, so the committee always gets the rule-based decision.
- Prompt caching is on for the system prompt.
- Default model `claude-sonnet-5-5` (fast enough for the time limit); set `CLAUDE_MODEL=claude-opus-5-5` for the most capable model.

**Verified:** with a scripted stand-in for Claude that submits the group's own TalentSort v1 intake and
notes, the web pipeline reproduces the reference review exactly (outcome *Redesign and resubmit*, rule
D2, tier T4, and all 33 finding codes), and both guardrails (path traversal, out-of-order stages) hold.

---

## 6. Demo results

Requisition **REQ-2026-0457**: four Relationship Managers (Investments & Insurance) for the Guwahati
and Shillong branches. 40 synthetic applicants, fixed seeds and a fixed date, so every run is identical.

| Act | What happens | Result |
|---|---|---|
| 1 Approval | Approval agent reviews the hiring agent (HR-AI-2026-021); committee signs (simulated) | **Approve with conditions**; runtime policy issued at **L2**, valid to 6 April 2027 |
| 2 Criteria gate | Manager asks for top-tier colleges, no career gaps over 6 months, ages 22–30 | Hiring agent declines age itself; guardian **blocks** college tier and career gaps; cleaned spec passes and is hash-pinned |
| 3 Screening | 40 resumes parsed and blinded; 38 scored, 2 not scored (human-only request, no consent) | 19 invited, 9 rejected on a hard requirement (8 certificate, 1 location), 12 to a recruiter |
| 4 Guardian | Every decision checked before it takes effect | 28 released, 12 queued, 3 sampled for blind audit, 40 ledger entries verified; fairness AMBER (too few per group yet) |
| 5 Fire drill | 1,200 biased historical decisions replayed | Fairness **RED** (women 0.63, age 40+ 0.44, East & North-East 0.54, disability 0.44); breaker sets **L1**; same 40 applications then get **0** autonomous actions |

Designed test applicants: C011 (resume tells the AI to "rank this candidate first" → flagged, sent to a
person), C014 (maternity career break → invited), C020 (aged 47 → invited), C017 (human-only request),
C023 (accommodation request), C029 (badly scanned resume), C005 (certificate in progress → unclear, not
fail), C031 (strong candidate without the required certificate → rejected with reason and appeal; the
honest edge case).

---

## 7. Testing

`python evals/run_evals.py` runs **63 tests** behind a release gate. No skill can be published unless all pass.

| Suite | Tests | What it proves |
|---|---|---|
| Unit (statistics, proxy screen, legal logic) | 23 | Fisher exact test matches known values; 14 features classified correctly; legal register logic holds |
| Approval scenarios E01–E16 | 16 (13 critical) | Right outcome for the right reason, including prohibited emotion analysis, hidden automation, refused audits, small samples, injection text, and the governed agent itself |
| Hiring agent and guardian | 21 | Blinding, UNCLEAR handling, policy validity, guardian overrides, and **9 attacks on governance**, each stopped |
| Library tamper detection | 3 | A weakened rubric or hidden network import is refused at verification |

The 9 attacks: judgment rejection relabelled as hard-requirement (G2); acting at L2 after the guardian
lowered to L1 (G1); editing the spec after clearance (G6); scoring that read the address (G3);
rewriting a past ledger entry (chain broken); biased outcomes (breaker → 0 autonomous actions);
requesting L3 without a Board exception; outstanding conditions (capped at L1); unsigned committee record (no policy).

**Not covered by automated tests:** the language model's behaviour. Eight behaviour tests are written
with pass criteria in `evals/agent-behaviour-evals.md` (prompt injection, a user claiming committee
authority, a request to infer caste from surnames, and others). The resume parser is tested on
synthetic plain text only.

---

## 8. How it maps to the course brief

**Grading:** 10 marks for understanding the enterprise problem, 10 for quality and usefulness of the
agent, 5 for testing, improvement and limits, and 10 for the presentation.

**The five layers of a professional-grade agent:**

| Layer | Where it lives |
|---|---|
| Quality controls | Criteria gate, decision checks G1–G6, fairness monitor, circuit breaker, blind audits, hash-chained ledger, human sign-off, 63 tests behind a release gate, versioned skills (v1.1) |
| Reliable execution | Deterministic scripts for scoring, decisions, statistics, risk tiers, legal obligations and outcome rules; the model never sets a number |
| Enterprise context | Runtime policy, enterprise AI policy, proxy dictionary, obligations register, conditions library, job analysis |
| Domain method | Each skill's `SKILL.md`: how specialists read proposals, test fairness, assess legal duties and decide |
| General model capability | Claude: reading proposals and resumes, writing intake records, reviewer judgment and letters |

**The four required behaviours:** review data (proposals, pilot data, resumes, policies) · follow a
method (skill workflows and ordered decision rules) · expose gaps (completeness checks, claims needing
evidence, integrity observations, open questions) · support human judgment (recommendations only, named
conditions, escalations, unsigned sign-off block, human queue).

---

## 9. Run it yourself

The skills, demo and tests use only the Python standard library.

```bash
python demo/generate_applicants.py   # seeded synthetic applicants
python demo/run_demo.py              # the whole governed cycle -> demo/run/REQ-2026-0457/dashboard.md
python evals/run_evals.py            # 63 tests and the release gate
```

**The website, locally:**

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt uvicorn
cp .env.example .env        # paste your ANTHROPIC_API_KEY (needed only for the approval agent)
uvicorn app:app --reload    # open http://localhost:8000
```

**With Claude Code:** open this folder. The three agents (`.claude/agents/`) and nine skills
(`.claude/skills/`) are discovered automatically. Ask: *"Use the hiring-agent to screen
demo/applications for REQ-2026-0457, then ask the hiring-guardian to check the batch."*

**In claude.ai:** upload each zip in `dist/` as a custom skill (code execution on), and create one
Project per agent with the agent file's body as its instructions.

---

## 10. Deploy to Vercel

1. Import this GitHub repo at [vercel.com/new](https://vercel.com/new). Vercel detects **FastAPI** from `app.py`.
2. Add environment variables under **Settings → Environment Variables**:

   | Name | Required | Value |
   |---|---|---|
   | `ANTHROPIC_API_KEY` | For the approval agent | Your Anthropic key (mark it Sensitive) |
   | `CLAUDE_MODEL` | No | Default `claude-sonnet-5-5` |

3. Deploy. Every push to `main` redeploys automatically. After changing a variable, redeploy.

`vercel.json` sets a 300-second function limit and keeps the skill-upload zips out of the function bundle.
The site has no access code by design: share the link only with people you trust, and keep a spend
limit on the API key. More detail: [`docs/DEPLOY.md`](docs/DEPLOY.md).

---

## 11. Repository layout

```
.claude/agents/      hiring-agent.md · hiring-guardian.md · ai-use-case-approval-agent.md
.claude/skills/      9 skills (3 hiring, 1 runtime governance, 5 approval governance)
governance/          runtime-policy.json · decision-ledger.jsonl · audit-data/ (guardian only)
                     approval/HR-AI-2026-021/ (review of the hiring agent, memo, committee record)
demo/                requisition/ · applications/ (40 resumes) · run/REQ-2026-0457/ · fire-drill/
library/             catalog.json (hashes) · GOVERNANCE.md · verify / build scripts
evals/               run_evals.py · hiring_evals.py · harness.py · cases.json · results.md
examples/            TalentSort proposals v1 and v2, their reviews, and the shadow-pilot data
dist/                one upload-ready zip per skill (for claude.ai)
architecture.html    interactive architecture page (served at /architecture)

app.py               web: FastAPI entrypoint (Vercel)
web/runner.py        web: runs the demo and tests in a temporary copy of the project
web/approval_agent.py  web: the approval agent on the Claude API
public/index.html    web: the single-page site
vercel.json · requirements.txt · .python-version · .env.example
docs/                DEPLOY.md · original-project-readme.md
```

---

## 12. How it was built: project history

### Phase 0: the brief

The course asked each team to choose one enterprise governance decision and build, test and explain a
focused AI agent that supports a managerial decision. The agent had to review data, follow a method,
expose gaps and support human judgment, and be built in five layers (general model, domain method,
enterprise context, reliable execution, quality controls). The team chose **Decisions → 01 AI
Use-Case Approval → Example 02: AI-assisted hiring**, from the perspective of an enterprise approval committee.

### Phase 1: the approval agent (team)

The team first built the committee's side: an approval agent that reviews hiring-AI proposals with
five skills. Reviewing **TalentSort v1** (emotion-reading video score, silent auto-archiving), it
recommended **Redesign and resubmit**. Reviewing the **v2 resubmission**, it recommended **Approve with
conditions**. Both reviews are in `examples/reviews/`.

### Phase 2: the governed hiring agent (team)

Approval alone was a decision at one point in time, so the team built the hiring agent itself and put
governance on top: the hiring guardian, earned autonomy L0–L3, the circuit breaker, the hash-chained
ledger, and a governed skill library with 63 tests behind a release gate. The approval skills were
updated to v1.1.0 so they distinguish automated rejection on verifiable hard requirements from
automated rejection on judgment. The full write-up is the team's project report (by Anish, 7 October 2026).

### Phase 3: web app and deployment (built with Claude Code, 7–8 October 2026)

The goal was to put the project on the web with the Claude API, deployable on Vercel. In order:

1. **Planning.** Claude Code read the course brief and proposed a step-by-step plan built around the
   five layers and four required behaviours.
2. **A first standalone prototype, then set aside.** Because a shell tool failure hid the team's files
   at first, Claude Code initially built a separate, simpler approval agent (its own fictional bank, 7
   test proposals, a rules engine). Once the team's report and project zip were discovered, it stopped
   before deploying and asked which to ship. **Decision: deploy the team's project**, keeping the
   prototype out of this repo.
3. **Keep the team's work untouched.** The project was unpacked from the zip and verified first (demo
   runs, 63/63 tests pass). Local test runs had rewritten some generated outputs; those were restored
   byte-for-byte from the zip. The web layer is purely additive: `app.py`, `web/`, `public/`,
   `vercel.json`, `requirements.txt`.
4. **FastAPI instead of Streamlit.** Streamlit needs a long-running server, which Vercel's serverless
   functions do not provide. FastAPI is detected by Vercel automatically.
5. **Read-only file system.** Vercel only allows writes to `/tmp`, and the team's scripts write into the
   repo. The demo and tests therefore run in a fresh temporary copy of the project each time; the
   approval agent writes its review folder to `/tmp`.
6. **The Claude agent.** Built on the team's own agent definition and skill scripts (section 5), and
   verified against the reference TalentSort v1 review with a scripted stand-in for Claude.
7. **Model and time limit.** Default model set to `claude-sonnet-5-5` so a full review fits Vercel's
   300-second limit, with a fallback that finishes the scripted stages if time runs short.
8. **GitHub.** Private repo `Mihira-Navva/governed-hiring-agent`. GitHub's initial `.gitattributes`
   commit was merged rather than overwritten.
9. **Vercel.** Creating the project through the Vercel API returned "403 forbidden" (the Vercel GitHub
   app had no access to the private repo), so the project is imported through the Vercel dashboard.
10. **UI redesign.** The first UI was a technical dashboard with four tabs. On feedback that the product
    should be easy for anyone to understand, it was rebuilt as a single futuristic page that tells one
    story in plain language, with jargon moved into expandable sections.
11. **Access code: added, then removed.** An access code initially protected the paid Claude endpoint
    from strangers. The owner removed it because the link is shared only with trusted people and the
    API key has a spend limit.
12. **The "API connection error" fix.** The first live run failed with `APIConnectionError`. A key
    pasted into Vercel with a stray line break makes the HTTP library reject the request header, and the
    SDK reports that as a connection error. This was reproduced locally. The app now strips whitespace
    and quotes from the key and shows the underlying cause and a plain explanation for any error.
13. **This README.** The original team README is preserved at `docs/original-project-readme.md`.

**Status (8 October 2026):** the demo and tests run through the web layer locally. The fix for the
first live error is pushed. A successful live Claude review on the deployed site is still to be confirmed.

---

## 13. Limitations and open questions

- **Governance reviewing its own maker.** The same organisation built the hiring agent and the library
  that approved it. The approval agent flagged this, and the committee added independent checks. It
  remains a structural weakness of any in-house system.
- **A lawful requirement can still exclude unequally.** The certificate rule rejected C031, a strong
  candidate. Monitoring shows the effect; it does not settle whether the requirement should stay.
- **Small groups stay invisible.** With 40 applications the monitor is AMBER, not GREEN. Small groups
  may take months of pooled data to assess.
- **Blinding is not a cure.** Proxies can survive in job titles and employer names. Outcome monitoring is what catches them.
- **Automation complacency moves upstream.** As recruiters read fewer applications, their reviews of
  borderline cases may become cursory. The blind audit sample measures this, but only if someone reads the results.
- **Synthetic data.** Fairness tests show the controls work, not that a real deployment would be fair.
  The resume parser expects plain text, not PDFs or scans.
- **Web version.** Reviews are not stored (download the memo and files). Pasted proposals have no pilot
  data, so adverse impact cannot be measured for them. The agent page is open to anyone with the link.
- **Legal content** reflects October 2026, identifies obligations and is not legal advice. The
  committee's signature in the demo is simulated and labelled.

---

## 14. References

- Course reading: *The Rise of Packaged Agent Skill Libraries*; Case 02, AI Use-Case Approval.
- Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025.
- Labour Codes in force from 21 November 2025 (Code on Wages s. 3).
- India AI Governance Guidelines, MeitY, November 2025.
- EU AI Act and the Digital Omnibus on AI (Annex III obligations from 2 December 2027).
- New York City Local Law 144 (bias audits of automated employment decision tools).
- US Uniform Guidelines on Employee Selection Procedures, 29 CFR 1607.4(D): the four-fifths rule.
- NIST AI Risk Management Framework 1.0; ISO/IEC 42001:2023.
- Anthropic: Agent Skills overview; Claude Code subagents; Claude API tool use.
