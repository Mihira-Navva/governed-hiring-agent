#!/usr/bin/env python3
"""Verify that every skill the agent is about to use is the approved, unaltered version.

Usage:
    python library/scripts/verify_library.py [--out reviews/<id>/library-check.json] [--skills-dir PATH]

Checks, for each skill in library/catalog.json:
  1. integrity   - the folder's content hash equals the hash recorded at approval;
  2. status      - skill.json says 'approved' and the version matches the catalog;
  3. currency    - the review date has not passed;
  4. format      - SKILL.md frontmatter meets the Agent Skills rules;
  5. permissions - scripts import only what the manifest declares, and never call
                   eval/exec, shell commands or deletion functions.
Exit code 0 if all pass, 1 otherwise. The agent must not use a skill that fails.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from library_tools import CATALOG, SKILLS_DIR, check_frontmatter, load, scan_scripts, skill_hash, today  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--skills-dir", default=SKILLS_DIR)
    ap.add_argument("--catalog", default=CATALOG)
    args = ap.parse_args()

    catalog = load(args.catalog)
    results, ok_all = [], True
    for entry in catalog["skills"]:
        folder = os.path.join(args.skills_dir, entry["name"])
        checks = {}
        if not os.path.isdir(folder):
            checks["present"] = "FAIL: folder missing"
        else:
            m = load(os.path.join(folder, "skill.json"))
            h = skill_hash(folder)
            checks["integrity"] = "PASS" if h == entry["sha256"] else f"FAIL: content changed since approval ({h[:12]} != {entry['sha256'][:12]})"
            checks["status"] = "PASS" if m["status"] == "approved" and m["version"] == entry["version"] else \
                f"FAIL: status '{m['status']}', version {m['version']} vs catalog {entry['version']}"
            checks["currency"] = "PASS" if m["review_due"] >= today() else f"FAIL: review was due {m['review_due']}"
            fm = check_frontmatter(folder)
            checks["format"] = "PASS" if not fm else "FAIL: " + "; ".join(fm)
            perm = scan_scripts(folder, m["permissions"]["allowed_imports"])
            checks["permissions"] = "PASS" if not perm else "FAIL: " + "; ".join(perm)
        ok = all(v == "PASS" for v in checks.values())
        ok_all &= ok
        results.append({"name": entry["name"], "version": entry["version"], "result": "PASS" if ok else "FAIL", "checks": checks})

    report = {"status": "PASS" if ok_all else "FAIL", "checked_at": today(),
              "catalog_published_on": catalog.get("published_on"), "skills": results}
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
            fh.write("\n")

    for r in results:
        bad = {k: v for k, v in r["checks"].items() if v != "PASS"}
        print(f"  {r['result']}  {r['name']} v{r['version']}" + (f"  -> {bad}" if bad else ""))
    print(f"Library check: {report['status']}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
