#!/usr/bin/env python3
"""Parse plain-text resumes into a restricted full profile and a blind profile for scoring.

Usage:
    python parse_resumes.py <resumes_dir> --out-full profiles.json --out-blind blind-profiles.json \
        [--audit-log audit-log.jsonl]

For each resume (<candidate_id>.txt):
  * full profile: contact details and everything parsed (restricted: for contacting the candidate only);
  * blind profile: experience as durations (no dates), certifications and skills, with protected terms
    redacted; header fields, education, languages, summary and personal sections removed;
  * integrity flags: text addressed to an AI reviewer is detected, removed from the blind profile and
    flagged for a person;
  * parse confidence (0-1): low confidence routes the candidate to a person instead of being scored.
Standard library only. Real deployments would use a stronger parser; the blinding and flagging logic
is the part being demonstrated.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skillkit import audit, load_json, write_json  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RULES = os.path.join(HERE, "..", "references", "blinding-rules.json")
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
AS_OF = (2026, 10)  # months for "Present" are counted to the review month
DATE_RE = re.compile(r"(?P<sm>[A-Za-z]{3})[a-z]*\.?\s+(?P<sy>\d{4})\s*[-–to]+\s*(?:(?P<present>present|current|now)|(?P<em>[A-Za-z]{3})[a-z]*\.?\s+(?P<ey>\d{4}))", re.I)
HEADING_RE = re.compile(r"^[A-Z][A-Z &/]{2,}$")


def months_between(sm, sy, em, ey):
    return max(0, (ey - sy) * 12 + (em - sm) + 1)


def split_sections(lines):
    header, sections, current = [], {}, None
    for line in lines:
        s = line.strip()
        if HEADING_RE.match(s):
            current = s.lower()
            sections.setdefault(current, [])
        elif current is None:
            header.append(s)
        else:
            sections[current].append(s)
    return header, sections


def redact(text, terms):
    out = text
    for t in terms:
        out = re.sub(rf"\b{re.escape(t)}\w*", "[redacted]", out, flags=re.I)
    return out


def parse(text, rules):
    flags, kept_lines = [], []
    for line in text.splitlines():
        hit = next((p for p in rules["injection_patterns"] if re.search(p, line, re.I)), None)
        if hit:
            flags.append({"type": "INSTRUCTION_TO_AI", "text": line.strip()[:160]})
            continue
        if re.search(r"[​‌‍⁠]", line):
            flags.append({"type": "HIDDEN_CHARACTERS", "text": "zero-width characters removed"})
            line = re.sub(r"[​‌‍⁠]", "", line)
        kept_lines.append(line)

    header, sections = split_sections(kept_lines)
    full = {"header": {}, "sections": {k: [l for l in v if l] for k, v in sections.items()}}
    removed = []
    for h in header:
        if ":" in h:
            k, v = h.split(":", 1)
            key = k.strip().lower()
            full["header"][key] = v.strip()
            if key in rules["removed_header_fields"]:
                removed.append(key)
        elif h:
            full["header"].setdefault("name", h)
            removed.append("name")

    experience, current = [], None
    for line in sections.get("experience", []):
        m = DATE_RE.search(line)
        if m and "|" in line:
            title = line.split("|")[0].strip()
            sm, sy = MONTHS.get(m.group("sm")[:3].lower()), int(m.group("sy"))
            if m.group("present"):
                em, ey = AS_OF[1], AS_OF[0]
            else:
                em, ey = MONTHS.get(m.group("em")[:3].lower()), int(m.group("ey"))
            months = months_between(sm, sy, em, ey) if sm and em else None
            current = {"title": redact(title, rules["redact_terms_in_kept_text"]), "months": months, "details": []}
            experience.append(current)
        elif line and current is not None:
            current["details"].append(redact(line.lstrip("-• ").strip(), rules["redact_terms_in_kept_text"]))

    certs = [redact(l, rules["redact_terms_in_kept_text"]) for l in sections.get("certifications", []) if l]
    skills_text = " ".join(l for l in sections.get("skills", []) if l)
    skills = [s.strip() for s in re.split(r"[,;|]", skills_text) if s.strip()]
    removed += [s for s in sections if s in rules["removed_sections"]]

    # parse confidence: did we find the sections scoring needs, and does the text look like words?
    letters = sum(c.isalpha() for c in text)
    noise = 1 - letters / max(1, sum(not c.isspace() for c in text))
    conf = 1.0
    if not experience and "fresher" not in text.lower():
        conf -= 0.4
    if "certifications" not in sections:
        conf -= 0.15
    if "skills" not in sections:
        conf -= 0.15
    if noise > 0.25:
        conf -= 0.4
    if any(e["months"] is None for e in experience):
        conf -= 0.2
    blind = {"experience": experience, "certifications": certs, "skills": skills}
    return full, blind, sorted(set(removed)), flags, round(max(0.0, conf), 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("resumes_dir")
    ap.add_argument("--out-full", required=True)
    ap.add_argument("--out-blind", required=True)
    ap.add_argument("--audit-log")
    args = ap.parse_args()
    rules = load_json(RULES)

    fulls, blinds = [], []
    files = sorted(f for f in os.listdir(args.resumes_dir) if f.endswith(".txt"))
    for f in files:
        cid = f[:-4]
        with open(os.path.join(args.resumes_dir, f), encoding="utf-8") as fh:
            text = fh.read()
        full, blind, removed, flags, conf = parse(text, rules)
        fulls.append({"candidate_id": cid, **full})
        blinds.append({"candidate_id": cid, "parse_confidence": conf, "removed_before_scoring": removed,
                       "integrity_flags": flags, **blind})

    write_json(args.out_full, {"_access": "RESTRICTED: contact use only; never read by scoring", "profiles": fulls})
    write_json(args.out_blind, {"_access": "Scoring input. Contains no direct identifiers or protected fields.",
                                "profiles": blinds})
    flagged = [b["candidate_id"] for b in blinds if b["integrity_flags"]]
    low = [b["candidate_id"] for b in blinds if b["parse_confidence"] < 0.7]
    audit(args.audit_log, "parse_resumes.py", [os.path.join(args.resumes_dir, f) for f in files],
          [args.out_full, args.out_blind], {"resumes": len(files), "integrity_flags": flagged, "low_confidence": low})
    print(f"Parsed {len(files)} resumes; {len(flagged)} with integrity flags; {len(low)} low parse confidence")


if __name__ == "__main__":
    main()
