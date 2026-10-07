#!/usr/bin/env python3
"""Tamper-evident decision ledger (a hash chain).

Usage:
    python ledger.py verify governance/decision-ledger.jsonl

Each entry stores the SHA-256 of the previous entry. Changing, deleting or reordering any past
decision breaks every hash after it, so an auditor can prove the record of who was advanced or
rejected, under which policy and level, has not been edited afterwards.
"""
import hashlib
import json
import os
import sys

GENESIS = "0" * 64


def _digest(entry):
    body = {k: v for k, v in entry.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def append(path, records):
    entries = read(path)
    prev = entries[-1]["hash"] if entries else GENESIS
    seq = entries[-1]["seq"] if entries else 0
    out = []
    for r in records:
        seq += 1
        e = {"seq": seq, **r, "prev_hash": prev}
        e["hash"] = _digest(e)
        prev = e["hash"]
        out.append(e)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        for e in out:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    return out


def verify(path):
    prev = GENESIS
    for i, e in enumerate(read(path), 1):
        if e.get("prev_hash") != prev:
            return False, f"entry {i}: chain broken (previous hash does not match)"
        if _digest(e) != e.get("hash"):
            return False, f"entry {i}: content altered after it was written"
        prev = e["hash"]
    return True, f"{len(read(path))} entries intact"


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "verify":
        sys.exit(__doc__)
    ok, msg = verify(sys.argv[2])
    print(("INTACT: " if ok else "TAMPERED: ") + msg)
    sys.exit(0 if ok else 1)
