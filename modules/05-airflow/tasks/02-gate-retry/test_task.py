"""Offline проверки поведения; исходная заготовка должна быть RED."""

import json
import os

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


@pytest.mark.parametrize(
    "candidate,baseline,ratio,expected",
    [
        (0.0, 2.0, 0.9, True),
        (1.8, 2.0, 0.9, True),
        (1.80001, 2.0, 0.9, False),
        (1.0, 2.0, 0.5, True),
        (1.01, 2.0, 0.5, False),
    ],
)
def test_gate_reads_numbers_and_custom_ratio(
    tmp_path, candidate, baseline, ratio, expected
):
    assert (
        s.quality_gate(metrics(tmp_path / "metrics.json", candidate, baseline), ratio)
        is expected
    )


@pytest.mark.parametrize(
    "value", [float("inf"), -float("inf"), float("nan"), -0.1, True, "0.2", None]
)
@pytest.mark.parametrize("field", ["candidate", "baseline"])
def test_gate_rejects_invalid_documented_measurements(tmp_path, field, value):
    values = {"candidate": 0.5, "baseline": 1.0}
    values[field] = value
    with pytest.raises(ValueError):
        s.quality_gate(metrics(tmp_path / "metrics.json", **values))


@pytest.mark.parametrize(
    "key", ["", ".", "..", "../escape", "a/b", "a\\b", "/absolute", "key space"]
)
def test_unsafe_keys_cannot_create_release(tmp_path, key):
    model = tmp_path / "model.joblib"
    model.touch()
    releases = tmp_path / "releases"
    with pytest.raises(ValueError):
        s.publish(key, model, "7", releases, metrics(tmp_path / "metrics.json", 0.5))
    assert not list(releases.glob("*.json"))


@pytest.mark.parametrize("key", ["run_17", "a.b-c_9"])
def test_safe_key_and_missing_model(tmp_path, key):
    releases = tmp_path / "releases"
    p = metrics(tmp_path / "metrics.json", 0.5)
    model = tmp_path / "model.joblib"
    with pytest.raises((ValueError, FileNotFoundError)):
        s.publish(key, model, "7", releases, p)
    assert not list(releases.glob("*.json"))
    model.touch()
    assert s.publish(key, model, "7", releases, p)["run_key"] == key


def test_conflicting_model_path_leaves_manifest_unchanged(tmp_path):
    p = metrics(tmp_path / "metrics.json", 0.5)
    model = tmp_path / "model.joblib"
    other = tmp_path / "other.joblib"
    model.touch()
    other.touch()
    releases = tmp_path / "releases"
    s.publish("key", model, "7", releases, p)
    path = releases / "key.json"
    before = path.read_bytes()
    with pytest.raises(ValueError):
        s.publish("key", other, "7", releases, p)
    assert path.read_bytes() == before


def test_failed_atomic_replacement_keeps_existing_release(tmp_path, monkeypatch):
    p = metrics(tmp_path / "metrics.json", 0.5)
    model = tmp_path / "model.joblib"
    model.touch()
    releases = tmp_path / "releases"
    s.publish("existing", model, "7", releases, p)
    path = releases / "existing.json"
    before = path.read_bytes()

    def fail(*args, **kwargs):
        raise OSError("injected replacement failure")

    monkeypatch.setattr(os, "replace", fail)
    monkeypatch.setattr(os, "rename", fail)
    with pytest.raises(OSError, match="injected replacement failure"):
        s.publish("new", model, "8", releases, p)
    assert path.read_bytes() == before
    assert not (releases / "new.json").exists()
