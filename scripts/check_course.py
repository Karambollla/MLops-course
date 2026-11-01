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
# Every original practice assignment has its own physical starter and tests.
catalog_path = ROOT / "modules" / "tasks.json"
if not catalog_path.is_file():
    errors.append("Missing modules/tasks.json")
else:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    tasks = catalog.get("tasks", [])
    identifiers = [task.get("id", "") for task in tasks]
    if len(tasks) != 53 or len(set(identifiers)) != len(tasks):
        errors.append("Expected 53 unique tasks")
    actual = {f"{module.name}/{folder.name}" for module in modules
              for folder in (module / "tasks").glob("[0-9][0-9]-*") if folder.is_dir()}
    if actual != set(identifiers):
        errors.append(f"Task directory/catalog mismatch: {actual.symmetric_difference(identifiers)}")
    for task in tasks:
        parts = task["id"].split("/")
        if len(parts) != 2:
            errors.append(f"Invalid task ID: {task['id']}")
            continue
        directory = ROOT / "modules" / parts[0] / "tasks" / parts[1]
        for name in ["README.md", task.get("starter", "solution.py"), task.get("tests", "test_task.py")]:
            target = (directory / name).resolve()
            if not target.is_relative_to(directory.resolve()) or not target.is_file():
                errors.append(f"{task['id']}: missing/invalid {name}")
        entrypoint = task.get("entrypoint")
        if entrypoint and not (directory / entrypoint).is_file():
            errors.append(f"{task['id']}: missing entrypoint {entrypoint}")
        if f"tasks/{parts[1]}/README.md" not in (directory.parent.parent / "practice.md").read_text():
            errors.append(f"{task['id']}: not linked from practice.md")

if errors:
    print("\n".join(errors))
    sys.exit(1)
words = sum(len(re.findall(r"\b[\w-]+\b", p.read_text())) for p in markdown)
print(f"PASS: {len(modules)} modules / 53 tasks, {len(markdown)} Markdown files, {words} words; local links, fences, UTF-8, Python AST and JSON")
