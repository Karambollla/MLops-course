#!/usr/bin/env python3
"""Network QA. Writes a status report; blocked sites require manual review."""

import argparse
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
argparse.ArgumentParser(description="Проверка внешних ссылок курса").parse_args()
urls = set()
for path in ROOT.rglob("*.md"):
    relative = path.relative_to(ROOT)
    if relative.parts[:2] == ("docs", "superpowers") or relative.as_posix() in {
        "docs/progress-ledger.md",
        "docs/task-migration-ledger.md",
    }:
        continue
    if any(
        part
        in {
            "work",
            ".git",
            ".venv",
            ".tools",
            ".terraform",
            "__pycache__",
            ".pytest_cache",
        }
        or part.startswith(".venv-")
        or part.endswith(".egg-info")
        for part in path.relative_to(ROOT).parts
    ):
        continue
    for url in re.findall(
        r"\]\((https?://[^\s)]+)\)", path.read_text(encoding="utf-8")
    ):
        if not re.search(r"https?://(localhost|127\.0\.0\.1)(:|/|$)", url):
            urls.add(url)


def check(url):
    item = {"url": url}
    try:
        request = Request(
            url, headers={"User-Agent": "Mozilla/5.0 (course reference check)"}
        )
        with urlopen(request, timeout=20) as response:
            response.read(1024)
            item.update(status=response.status, final_url=response.url, result="ok")
    except HTTPError as exc:
        result = "missing" if exc.code in {404, 410} else "manual_review"
        item.update(status=exc.code, result=result)
    except Exception as exc:
        item.update(result="manual_review", error=f"{type(exc).__name__}: {exc}")
    return item


with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(check, sorted(urls)))
report = {"method": "HTTP GET with redirects; first 1024 bytes", "results": results}
output = ROOT / "docs" / "external-links.json"
output.write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
for status in ["ok", "manual_review", "missing"]:
    selected = [r for r in results if r["result"] == status]
    print(f"{status}: {len(selected)}")
    if status != "ok":
        for item in selected:
            print(f"  {item['url']}: {item.get('status', item.get('error'))}")
raise SystemExit(1 if any(r["result"] == "missing" for r in results) else 0)
