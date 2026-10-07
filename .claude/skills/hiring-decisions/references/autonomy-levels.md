# Autonomy levels: earned, granted, and taken away

Autonomy is not a setting the hiring team chooses. The committee **grants** it in a signed runtime
policy, the system **earns** higher levels with evidence, and the guardian **takes it away**
automatically when something goes wrong. The effective level is always the lower of the committee's
policy and the guardian's current state.

| Level | Acts alone on | Needs a person for | How it is reached |
|---|---|---|---|
| **L0 Suspended** | nothing | everything | No valid policy, or the committee suspends |
| **L1 Assist** | parsing, scoring, drafting | every decision | Default after approval; automatic fallback when the circuit breaker trips |
| **L2 Governed autonomy** | advancing strong candidates; rejecting for a **verifiable hard requirement** (a licence the regulator requires, a location the candidate said they cannot work at) | judgment-based rejections, borderline cases, unclear evidence, integrity flags, offers | Committee approval after a passed shadow pilot |
| **L3 Earned autonomy** | L2, plus rejecting clear misses below a low floor | borderline cases, offers | Six months at L2 with fairness GREEN in every monthly report, blind-audit agreement of at least 95%, appeal upheld rate under 5%, **and** a Board-approved exception to policy POL-AI-03 |

## Why advancing is easier to automate than rejecting
A wrongly advanced candidate gets an interview: a person meets them, and the error is cheap and
visible. A wrongly rejected candidate disappears: nobody sees the error. So autonomy grows first on the
side where mistakes are seen and corrected.

## Why hard-requirement rejections can be automated at L2
They are checks of fact, not judgments of ability. The requirement has a stated legal or operational
basis, the evidence is quoted, ambiguous evidence goes to a person, the letter explains exactly what
was missing, and the candidate can appeal. The guardian samples 10% of these for a blind human re-check
and monitors their rates by group: even a legitimate requirement can fall unequally on groups, and the
committee should know when it does.

## Why L3 needs the Board
L3 lets the agent reject on a score, which is a judgment. The organisation's policy POL-AI-03 says no
consequential decision about a person is made without meaningful human review. L3 therefore crosses
red line RL-02 by design. It is possible only as an explicit, evidenced, time-limited exception
approved above the committee. It is described here so the path is visible, not because it is
recommended.
