"""Offline проверки поведения; исходная заготовка должна быть RED."""

import json

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


def metrics(path, candidate=0.9, baseline=1.0):
    path.write_text(
        json.dumps(
            {
                "candidate": {"test": {"mae": candidate}},
                "baseline": {"test": {"mae": baseline}},
            }
        )
    )
    return path


def test_gate_boundary_and_failure(tmp_path):
    p = tmp_path / "metrics.json"
    assert s.quality_gate(metrics(p, 0.9)) is True
    assert s.quality_gate(metrics(p, 0.90001)) is False
    for candidate, baseline in [
        (float("nan"), 1.0),
        (0.1, 0.0),
        (-1.0, 1.0),
        (True, 1.0),
    ]:
        with pytest.raises(ValueError):
            s.quality_gate(metrics(p, candidate, baseline))


def test_idempotent_publication_and_conflict(tmp_path):
    p = metrics(tmp_path / "metrics.json", 0.8)
    model = tmp_path / "model.joblib"
    model.touch()
    releases = tmp_path / "releases"
    expected = {"run_key": "key-1", "model_path": str(model), "version": "7"}
    assert s.publish("key-1", model, "7", releases, p) == expected
    original = (releases / "key-1.json").read_bytes()
    assert s.publish("key-1", model, "7", releases, p) == expected
    assert (releases / "key-1.json").read_bytes() == original
    assert len(list(releases.glob("*.json"))) == 1
    with pytest.raises(ValueError):
        s.publish("key-1", model, "8", releases, p)
    assert (releases / "key-1.json").read_bytes() == original


def test_gate_blocks_all_publication(tmp_path):
    p = metrics(tmp_path / "metrics.json", 1.1)
    model = tmp_path / "model.joblib"
    model.touch()
    releases = tmp_path / "releases"
    with pytest.raises(ValueError):
        s.publish("bad", model, "7", releases, p)
    assert not list(releases.glob("*.json"))
    with pytest.raises(ValueError):
        s.publish("../escape", model, "7", releases, metrics(p, 0.5))
    assert not (tmp_path / "escape.json").exists()
