#!/usr/bin/env python3
"""Offline QA for course structure and authored source files; no dependencies."""
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {"work", ".venv", ".tools", ".git", "__pycache__", ".pytest_cache", ".terraform"}
errors = []


def authored_files():
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if path.is_file() and not any(part in EXCLUDED or part.startswith(".venv-") or part.endswith(".egg-info") for part in relative.parts):
            yield path


paths = list(authored_files())
markdown = [path for path in paths if path.suffix == ".md"]
for path in markdown:
    text = path.read_text(encoding="utf-8")
    name = path.relative_to(ROOT)
    if "\ufffd" in text:
        errors.append(f"{name}: replacement character")
    if not text.startswith("# "):
        errors.append(f"{name}: missing H1")
    in_fence = False
    prose = []
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence:
            prose.append(line)
        if line.rstrip() != line:
            errors.append(f"{name}:{number}: trailing whitespace")
    if in_fence:
        errors.append(f"{name}: unclosed code fence")
    for match in re.finditer(r"!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", "\n".join(prose)):
        target = match.group(1).strip("<>")
        if urlsplit(target).scheme or target.startswith("#"):
            continue
        local = unquote(target.split("#", 1)[0])
        resolved = (path.parent / local).resolve()
        if not resolved.is_relative_to(ROOT) or not resolved.exists():
            errors.append(f"{name}: missing local link {target}")
for path in paths:
    if path.suffix == ".py":
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    elif path.suffix == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
modules = sorted((ROOT / "modules").glob("[0-9][0-9]-*"))
if len(modules) != 18 or [p.name[:2] for p in modules] != [f"{i:02d}" for i in range(18)]:
    errors.append("Expected exactly 18 ordered modules 00–17")
for folder in modules:
    for name in ["README.md", "practice.md", "hints.md"]:
        if not (folder / name).is_file():
            errors.append(f"{folder.name}: missing {name}")
    if (folder / "README.md").is_file() and "## Материалы" not in (folder / "README.md").read_text():
        errors.append(f"{folder.name}: no annotated sources")
if errors:
    print("\n".join(errors))
    sys.exit(1)
words = sum(len(re.findall(r"\b[\w-]+\b", p.read_text())) for p in markdown)
print(f"PASS: {len(modules)} modules, {len(markdown)} Markdown files, {words} words; local links, fences, UTF-8, Python AST and JSON")
