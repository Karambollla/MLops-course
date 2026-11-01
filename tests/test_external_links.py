"""Run network QA in an isolated course copy with fake HTTP responses."""

import io
import json
import runpy
import shutil
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("missing", [False, True])
def test_link_report_keeps_statuses_without_dates_or_private_sources(
    tmp_path, monkeypatch, capsys, missing
):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "docs/superpowers").mkdir(parents=True)
    script = tmp_path / "scripts/check_external_links.py"
    shutil.copy2(ROOT / "scripts/check_external_links.py", script)
    (tmp_path / "README.md").write_text(
        "# Sources\n[ok](https://example.test/ok)\n[blocked](https://example.test/blocked)\n[maybe missing](https://example.test/missing)\n[local](http://localhost:8000/ready)\n"
    )
    (tmp_path / "docs/superpowers/plan.md").write_text(
        "# Private\n[private](https://example.test/private)\n"
    )
    (tmp_path / "docs/progress-ledger.md").write_text(
        "# Private\n[private](https://example.test/ledger)\n"
    )
    visited = set()

    class Response(io.BytesIO):
        status = 200

        def __init__(self, url):
            super().__init__(b"fixture response")
            self.url = url

    def fake_urlopen(request, timeout):
        url = request.full_url
        visited.add(url)
        if url.endswith("/blocked"):
            raise HTTPError(url, 403, "forbidden", None, None)
        if url.endswith("/missing") and missing:
            raise HTTPError(url, 410, "gone", None, None)
        return Response(url)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    monkeypatch.setattr(sys, "argv", [str(script)])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_path(str(script), run_name="__main__")
    assert exit_info.value.code == int(missing)
    report = json.loads((tmp_path / "docs/external-links.json").read_text())
    assert set(report) == {"method", "results"}
    results = {row["url"].rsplit("/", 1)[-1]: row for row in report["results"]}
    assert set(results) == {"ok", "blocked", "missing"}
    assert results["ok"]["status"] == 200 and results["ok"]["result"] == "ok"
    assert (
        results["blocked"]["status"] == 403
        and results["blocked"]["result"] == "manual_review"
    )
    assert results["missing"]["status"] == (410 if missing else 200)
    assert results["missing"]["result"] == ("missing" if missing else "ok")
    assert visited == {"https://example.test/" + name for name in results}
    output = capsys.readouterr().out
    assert "manual_review: 1" in output
    assert f"missing: {int(missing)}" in output
