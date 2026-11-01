"""Offline проверки поведения; исходная заготовка должна быть RED."""

import subprocess

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def test_training_uses_cli_and_metadata(tmp_path, monkeypatch):
    data = tmp_path / "input with spaces.csv"
    data.write_text("x\n1\n")
    out = tmp_path / "runs" / "key-1"
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        assert isinstance(command, list) and kwargs.get("check") is True
        assert not kwargs.get("shell", False)
        assert command[:3] == ["/opt/housing-venv/bin/python", "-m", "housing.train"]
        assert command[command.index("--data") + 1] == str(data)
        assert command[command.index("--output") + 1] == str(out)
        assert command[command.index("--seed") + 1] == "42"
        out.mkdir(parents=True, exist_ok=True)
        for name in ["model.joblib", "metrics.json", "manifest.json", "split.json"]:
            (out / name).write_text("{}")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert s.run_training(data, out) == {"path": str(out), "run_key": "key-1"}
    assert len(calls) == 1


def test_failed_training_propagates(tmp_path, monkeypatch):
    data = tmp_path / "input.csv"
    data.touch()

    def failure(*a, **kw):
        raise subprocess.CalledProcessError(1, a[0])

    monkeypatch.setattr(subprocess, "run", failure)
    with pytest.raises(subprocess.CalledProcessError):
        s.run_training(data, tmp_path / "out")
