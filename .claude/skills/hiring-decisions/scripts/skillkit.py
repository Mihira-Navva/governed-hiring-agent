"""Small shared helpers for this skill's scripts.

Each skill carries its own copy so that it stays self-contained and portable: a skill can be
reviewed, versioned, moved or retired without breaking another skill. Standard library only;
no network access.
"""
import datetime as _dt
import hashlib
import json
import os

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, data):
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def get(record, dotted, default=None):
    """Read a nested value with a dotted path, e.g. get(r, "system.automation_level")."""
    cur = record
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def is_missing(value):
    return value is None or value == "" or value == []


def skill_meta():
    path = os.path.join(_SKILL_DIR, "skill.json")
    try:
        meta = load_json(path)
        return {"skill": meta.get("name"), "version": meta.get("version")}
    except (OSError, ValueError):
        return {"skill": os.path.basename(_SKILL_DIR), "version": "unknown"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso():
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def audit(log_path, script, inputs, outputs, summary):
    """Append one line to the review's audit log: who ran what, on which inputs, with what result.

    Input and output files are recorded by SHA-256 so an auditor can later prove that the memo
    rests on exactly these files and that none was edited afterwards.
    """
    if not log_path:
        return
    entry = {
        "ts": now_iso(),
        **skill_meta(),
        "script": script,
        "inputs": {os.path.basename(p): sha256_file(p) for p in inputs if p and os.path.exists(p)},
        "outputs": {os.path.basename(p): sha256_file(p) for p in outputs if p and os.path.exists(p)},
        "summary": summary,
    }
    os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
