#!/usr/bin/env python3
"""Generate the synthetic shadow-mode datasets used in the worked examples.

The data is invented. It is built so that version 1 of the proposal reproduces patterns
documented in hiring-AI research (penalties linked to career gaps, age, accent and college
tier), and version 2 shows what a redesigned, job-related model might look like. Seeded, so
the examples are reproducible.

    python generate_pilot_data.py
"""
import csv
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))


def pick(rng, dist):
    r, acc = rng.random(), 0.0
    for value, p in dist:
        acc += p
        if r < acc:
            return value
    return dist[-1][0]


GENDER = [("Man", 0.615), ("Woman", 0.355), ("Transgender / non-binary", 0.012), ("Prefer not to say", 0.018)]
AGE = [("21-29", 0.55), ("30-39", 0.33), ("40+", 0.12)]
REGION = [("West", 0.40), ("South", 0.22), ("North", 0.18), ("East & North-East", 0.20)]
DISABILITY = [("No", 0.915), ("Yes", 0.045), ("Prefer not to say", 0.04)]


def make(path, n, seed, penalties, base, qual_effect, rated_share):
    rng = random.Random(seed)
    rows = []
    for i in range(1, n + 1):
        g, a, r, d = pick(rng, GENDER), pick(rng, AGE), pick(rng, REGION), pick(rng, DISABILITY)
        qualified = 1 if rng.random() < 0.45 else 0
        logit = base + qual_effect * qualified + rng.gauss(0, 0.6)
        logit -= penalties.get(("gender", g), 0) + penalties.get(("age", a), 0)
        logit -= penalties.get(("region", r), 0) + penalties.get(("disability", d), 0)
        if g == "Woman" and a == "30-39":
            logit -= penalties.get(("women30s", True), 0)
        shortlisted = 1 if rng.random() < 1 / (1 + math.exp(-logit)) else 0
        rated = rng.random() < rated_share
        rows.append({"candidate_id": f"C{seed % 100:02d}-{i:05d}", "gender": g, "age_band": a, "home_region": r,
                     "disability": d, "ai_shortlisted": shortlisted,
                     "expert_qualified": qualified if rated else ""})
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    sel = sum(r["ai_shortlisted"] for r in rows) / n
    print(f"{os.path.basename(path)}: {n} rows, shortlist rate {sel:.1%}")


if __name__ == "__main__":
    make(os.path.join(HERE, "deccan-v1-shadow-pilot.csv"), n=1200, seed=2026, base=-2.0, qual_effect=2.4, rated_share=0.5,
         penalties={("gender", "Woman"): 0.55, ("women30s", True): 0.6, ("age", "40+"): 1.1,
                    ("region", "East & North-East"): 0.65, ("disability", "Yes"): 0.7})
    make(os.path.join(HERE, "deccan-v2-shadow-pilot.csv"), n=1500, seed=3141, base=-1.9, qual_effect=2.6, rated_share=0.5,
         penalties={("age", "40+"): 0.12, ("region", "East & North-East"): 0.05})
