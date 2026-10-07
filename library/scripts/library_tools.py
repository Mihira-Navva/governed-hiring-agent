"""Shared functions for building and verifying the skill library catalog."""
import ast
import datetime as dt
import hashlib
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_DIR = os.path.join(ROOT, ".claude", "skills")
CATALOG = os.path.join(ROOT, "library", "catalog.json")

FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__"}
FORBIDDEN_ATTRS = {("os", "system"), ("os", "popen"), ("os", "remove"), ("os", "rmdir"), ("shutil", "rmtree")}


def skill_files(folder):
    out = []
    for base, dirs, files in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for f in sorted(files):
            if f.endswith(".pyc"):
                continue
            out.append(os.path.join(base, f))
    return out


def skill_hash(folder):
    """One SHA-256 over every file's relative path and bytes, in a fixed order."""
    h = hashlib.sha256()
    for path in skill_files(folder):
        rel = os.path.relpath(path, folder).replace(os.sep, "/")
        h.update(rel.encode() + b"\0")
        with open(path, "rb") as fh:
            h.update(fh.read() + b"\0")
    return h.hexdigest()


def frontmatter(skill_md):
    with open(skill_md, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


def check_frontmatter(folder):
    issues = []
    fm = frontmatter(os.path.join(folder, "SKILL.md"))
    if fm is None:
        return ["SKILL.md has no YAML frontmatter"]
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != os.path.basename(folder):
        issues.append(f"frontmatter name '{name}' does not match folder")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        issues.append("name must be 1-64 lowercase letters, digits or hyphens")
    if any(w in name for w in ("claude", "anthropic")):
        issues.append("name may not contain reserved words")
    if not desc or len(desc) > 1024:
        issues.append(f"description must be 1-1024 characters (is {len(desc)})")
    if "<" in desc or ">" in desc:
        issues.append("description may not contain XML tags")
    return issues


def scan_scripts(folder, allowed_imports):
    """Static check that scripts only do what the manifest says: no network, no shell, no eval."""
    issues = []
    for path in skill_files(folder):
        if not path.endswith(".py"):
            continue
        rel = os.path.relpath(path, folder)
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=rel)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            else:
                names = []
            for n in names:
                if n not in allowed_imports:
                    issues.append(f"{rel}: imports '{n}', not in declared permissions")
            if isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Name) and f.id in FORBIDDEN_CALLS:
                    issues.append(f"{rel}: calls {f.id}()")
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and (f.value.id, f.attr) in FORBIDDEN_ATTRS:
                    issues.append(f"{rel}: calls {f.value.id}.{f.attr}()")
    return issues


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def today():
    return dt.date.today().isoformat()
