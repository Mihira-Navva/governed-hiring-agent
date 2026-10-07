# Screening method notes

## What blinding achieves, and what it does not
Removing names, addresses, dates of birth, college names and graduation years stops the scorer from
using them directly. It does not stop proxies hidden in what remains: job titles at a community
organisation, a regional employer, a phrase in a bullet point. That is why outcome monitoring by the
guardian is still needed after blinding. Blinding is a first defence, not a guarantee.

## Reading a screening result
| Result | Meaning | What happens next |
|---|---|---|
| Hard requirement PASS | Evidence quoted | Scoring continues |
| Hard requirement FAIL | Searched everywhere it could appear; nothing found | Eligible for automated rejection at L2, with an appeal route |
| Hard requirement UNCLEAR | Partial or in-progress evidence ("appearing for NISM exam in Nov") | A person decides |
| Criterion score null | The input is missing (e.g. assessment not taken) | A person decides; never scored as zero |
| Low parse confidence | The resume could not be read reliably | A person reads it |
| Integrity flag | Text addressed to an AI was found and removed | A person reads the original; the flag is not a penalty |

## Why missing is not zero
A candidate who could not take the assessment (a connectivity failure, an accommodation pending) has
not scored zero; we simply don't know. Treating missing as zero is one of the most common ways
automated screening excludes people with disabilities or poor internet access.

## Experience
Only months in roles matching the job's relevant words count, up to the cap. A career break is
neither counted nor penalised: it is not computed at all.
