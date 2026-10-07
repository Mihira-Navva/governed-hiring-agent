# Decision rules

The decision script applies these rules in order and stops at the first that fires. Order
matters, and each ordering choice is deliberate.

| Rule | Condition | Outcome |
|---|---|---|
| D1 | Risk tier is PROHIBITED (primary function is a prohibited practice) | **Reject** |
| D2 | Any red line (RL-01 to RL-06) from risk, proxy screen or fairness review | **Redesign and resubmit** (open questions attached) |
| D3 | Intake status INCOMPLETE | **Return for information** |
| D4 | No outcome evidence: no shadow or pilot data analysed **and** no completed bias audit | **Pilot only** (shadow mode) |
| D5 | Tier T3 or T4, or any open mandatory obligation, or any fairness CONCERN | **Approve with conditions** |
| D6 | Otherwise (T1 or T2, all mandatory obligations met, fairness PASS or not applicable) | **Approve** |

Why D1 comes first: asking a proposer for more information about a prohibited purpose wastes
everyone's time and implies it could be approved.

Why D2 precedes D3: if the design already crosses a red line, returning it only for missing
information would cost a full cycle and then reject it anyway. The proposer gets the redesign
requirements and the open questions together.

Why D2 precedes D4: a red line is a design flaw visible on paper. Running a pilot of a design
that cannot be approved exposes candidates' data for nothing.

Why D4 exists: without outcome data the committee would be approving on vendor assurance.
The pilot is how a promising proposal earns evidence.

## Conditions

For every outcome except Reject, the script collects finding codes and attaches every condition
in `conditions-library.json` whose triggers match:

- red line IDs (RL-xx) from all skills;
- legal gap codes for obligations that are GAP or UNKNOWN;
- intake-derived codes: `HO-TRAIN`, `HO-LOG`, `HO-ANCHOR`, `CO-APPEAL`, `TR-NOTICE`, `TR-DOCS`,
  `FA-LABELS`, `FA-JOBREL`;
- fairness codes: `FA-PROXY-STRONG`, `FA-PROXY-JUSTIFY`, `FA-NO-DATA`, `FA-CONCERN`;
- `TIER-HIGH` for T3, T4;
- consistency warnings (e.g. `W-DEFACTO-AUTO`) and `INT-INJECTION` for integrity observations.

For **Redesign and resubmit** the conditions become *requirements for resubmission*.

## Disagreeing with the script

The rules encode policy; the reviewer supplies judgment. If the agent believes the rules give
the wrong answer for this case, it does not change `decision.json`. It writes its view and
reasons in the memo's *Reviewer judgment* section, so the committee sees both and decides.
Repeated disagreements of the same kind are reported to the library owner as evidence that the
rules need revision.
