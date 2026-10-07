# Governed Hiring Agent

**Course:** Responsible AI and Governance · **Case 02:** AI-assisted hiring, from the perspective of an
enterprise approval committee.

A working AI hiring agent that takes in applications and resumes, screens them, and acts: it invites
strong candidates to interview and rejects candidates who clearly fail a legal or operational
requirement. **A governance system sits on top of it.** That system approves it before it runs, sets
how much it may do alone, checks every decision before it takes effect, and withdraws its autonomy
automatically if outcomes become unfair. Everything is built from portable skills, published from a
governed library, as the course reading on packaged agent skill libraries describes.

## Three layers

```
 ┌───────────────────────────────────────────────────────────────────────────────────────┐
 │ PEOPLE            AI Approval Committee · recruiters · candidates (appeal, opt out)    │
 ├───────────────────────────────────────────────────────────────────────────────────────┤
 │ GOVERNANCE        Approval agent (before deployment)   →  signed runtime policy        │
 │                   Hiring guardian (at every decision)  →  release / route / breaker    │
 │                   Governed skill library (hashes, permissions, 63 tests, release gate) │
 ├───────────────────────────────────────────────────────────────────────────────────────┤
 │ HIRING            Hiring agent: requisition → parse & blind → screen → decide          │
 └───────────────────────────────────────────────────────────────────────────────────────┘
```

| Agent | Role | Skills |
|---|---|---|
| `hiring-agent` | Does the hiring work, within its granted autonomy | `job-requisition`, `resume-screening`, `hiring-decisions` |
| `hiring-guardian` | Checks every spec and decision before it takes effect; can only lower autonomy | `hiring-guardrails` |
| `ai-use-case-approval-agent` | Reviews the hiring agent before deployment; turns the committee's decision into a runtime policy | `use-case-intake`, `risk-tiering`, `fairness-bias-review`, `legal-privacy-review`, `approval-decision-memo` |

**Separation of duties:** the agent that decides never checks itself. The hiring agent never sees the
fairness audit data; only the guardian does. Only the committee can raise autonomy; the guardian can
lower it at once.

## Earned autonomy

| Level | Acts alone on | A person decides |
|---|---|---|
| L0 Suspended | nothing | everything |
| L1 Assist | parsing, scoring, drafting | every decision |
| **L2 Governed autonomy** (granted in the demo) | invite strong candidates; reject on a failed **verifiable hard requirement**, with notice and 14-day appeal | judgment-based rejections, borderline, unclear, flagged, human-only, offers |
| L3 Earned autonomy | L2 + reject clear low scores | borderline, offers. Needs 6 months clean at L2 and a Board exception to policy |

The level is the **lower** of the committee's signed policy and the guardian's state. An unsigned or
expired policy means L0.

## The demo (one requisition, 40 synthetic applications)

```bash
python demo/generate_applicants.py   # seeded synthetic applicants
python demo/run_demo.py              # the whole governed cycle
python evals/run_evals.py            # 63 tests, release gate
```

| Act | What happens | Result |
|---|---|---|
| 1 | Approval agent reviews the hiring agent (HR-AI-2026-021) | Approve with conditions, no red lines; committee signs (simulated); runtime policy issued at **L2** |
| 2 | Manager asks for "top colleges" and "no career gaps" | Guardian's criteria gate **blocks** both; the cleaned spec passes and its hash is pinned |
| 3 | Hiring agent screens 40 applications | 19 invited to interview, 9 rejected on a hard requirement (8 certificate, 1 location), 12 to a person |
| 4 | Guardian checks the batch | 28 released, 12 queued for recruiters, 3 sampled for blind audit, 40 ledger entries; fairness AMBER (too few per group yet) |
| 5 | Fire drill: 1,200 biased historical decisions replayed | Fairness **RED**, circuit breaker drops autonomy to **L1**; the same 40 applications then get **0** autonomous actions |

Designed test applicants include a resume with instructions aimed at the AI (C011), a strong candidate
with a maternity career break (C014), a 47-year-old (C020), a human-only request (C017), an
accommodation request (C023), a badly scanned resume (C029), and a certificate still in progress (C005).
Each reaches the intended outcome (test H10).

## Folders

```
.claude/agents/      hiring-agent.md · hiring-guardian.md · ai-use-case-approval-agent.md
.claude/skills/      9 skills (3 hiring, 1 runtime governance, 5 approval governance)
governance/          runtime-policy.json · decision-ledger.jsonl · audit-data/ (guardian only)
                     approval/HR-AI-2026-021/ (review, memo, committee record)
demo/                requisition/ · applications/ · run/REQ-2026-0457/ (dashboard, queue, letters) · fire-drill/
library/             catalog.json (hashes) · GOVERNANCE.md · verify_library.py
evals/               run_evals.py · hiring_evals.py · cases.json · results.md
examples/            the earlier TalentSort reviews (v1 Redesign, v2 Approve with conditions)
dist/                one upload-ready zip per skill
```

## Run with Claude

- **Claude Code:** open this folder. The agents and skills are discovered automatically. Ask: *"Use the
  hiring-agent to screen demo/applications for REQ-2026-0457, then ask the hiring-guardian to check the batch."*
- **claude.ai:** upload the zips in `dist/` as custom skills (code execution on), and create one Project
  per agent with the agent file's body as instructions.

## Limits

All people, organisations and data are fictional and synthetic. The resume parser is rule-based and
expects plain text. Legal content reflects October 2026 and identifies obligations; it is not legal
advice. The committee's signature in the demo is simulated and labelled as such.
