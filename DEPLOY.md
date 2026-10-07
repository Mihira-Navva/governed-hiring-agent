# Web app and deployment

The project runs as a small web app on Vercel. The web layer is additive: `app.py`, `web/`,
`public/`, `vercel.json` and `requirements.txt`. No skill, agent, demo or eval file is changed,
so library verification and the release gate behave exactly as in the repository.

## What the site does

| Tab | What runs | Needs API key? |
|---|---|---|
| Governed demo | `demo/run_demo.py`, all five acts, in a fresh temporary copy of the project | No |
| Approval agent | The `ai-use-case-approval-agent` on the Claude API. Claude reads the proposal, writes `intake.json` and `reviewer-notes.json`; the skill scripts produce everything else (completeness, tier, red lines, proxies, adverse impact, obligations, outcome, memo) | Yes |
| Tests | `evals/run_evals.py`: 63 tests and the release gate | No |

How the Claude agent is wired (`web/approval_agent.py`):

- Its system prompt is `.claude/agents/ai-use-case-approval-agent.md`, read at runtime, plus a short
  section mapping each workflow step to a tool.
- Its tools are the skill scripts themselves, run with the same arguments as `evals/harness.py`.
  It can read only `SKILL.md`, `references/` and `templates/` of the five approval skills.
- Stages must run in order (the decision needs intake, risk, fairness and legal), and the outcome
  always comes from `decide.py`. The model can argue with it in `reviewer_judgment` but cannot change it.
- If the time budget runs out after the intake, the remaining scripted stages still run, so the
  committee always gets the rule-based decision.

## Environment variables (Vercel → Project → Settings → Environment Variables)

| Name | Required | Value |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes, for the agent tab | Your Anthropic API key. Mark it **Sensitive**. |
| `APP_ACCESS_CODE` | Yes, for the agent tab | Any passphrase. The page asks for it, so strangers who find the URL cannot spend your credits. Without it the agent tab is disabled on Vercel. |
| `CLAUDE_MODEL` | No | Default `claude-sonnet-5-5`. `claude-opus-5-5` is more capable but slower; reviews must finish within the 300-second function limit. |

After adding or changing a variable, redeploy (Deployments → ⋯ → Redeploy) so the function picks it up.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt uvicorn
cp .env.example .env    # then fill in ANTHROPIC_API_KEY (APP_ACCESS_CODE optional locally)
uvicorn app:app --reload
# open http://localhost:8000
```

## Limits of the web version

- Reviews are not stored: each run's files are returned to the browser (download buttons) and the
  temporary folder is deleted. Download the memo and audit log if you need to keep them.
- Pasted proposals have no pilot data attached, so adverse impact cannot be measured for them.
- The access code is a single shared passphrase, not per-user authentication.
