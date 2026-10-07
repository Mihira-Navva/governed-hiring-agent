#!/usr/bin/env python3
"""Publish the approved skills into the library catalog (library owner only).

Usage:
    python library/scripts/build_catalog.py [--eval-results evals/results.json]

Records each skill's version, status, approval dates and content hash. Run only after a skill
has passed review and the evaluation suite; the hash then pins exactly what was approved.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from library_tools import CATALOG, SKILLS_DIR, check_frontmatter, load, scan_scripts, skill_hash, today  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval-results")
    args = ap.parse_args()

    evals = load(args.eval_results) if args.eval_results and os.path.exists(args.eval_results) else {}
    entries = []
    for name in sorted(os.listdir(SKILLS_DIR)):
        folder = os.path.join(SKILLS_DIR, name)
        if not os.path.isdir(folder):
            continue
        m = load(os.path.join(folder, "skill.json"))
        problems = check_frontmatter(folder) + scan_scripts(folder, m["permissions"]["allowed_imports"])
        if problems:
            sys.exit(f"Refusing to publish {name}: " + "; ".join(problems))
        entries.append({
            "name": name, "version": m["version"], "status": m["status"],
            "path": f".claude/skills/{name}", "sha256": skill_hash(folder),
            "owner": m["owner"], "approved_by": m["approved_by"], "approved_on": m["approved_on"],
            "review_due": m["review_due"], "network": m["permissions"]["network"],
            "evals": evals.get("by_skill", {}).get(name),
        })

    catalog = {
        "library": "AI Hiring Approval Skill Library",
        "library_version": "1.0.0",
        "owner": "AI Governance Office",
        "published_on": today(),
        "eval_summary": evals.get("summary"),
        "skills": entries,
    }
    with open(CATALOG, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, indent=2)
        fh.write("\n")
    print(f"Catalog published: {len(entries)} skills")


if __name__ == "__main__":
    main()
