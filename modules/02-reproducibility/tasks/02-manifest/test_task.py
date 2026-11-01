"""Offline проверки поведения; исходная заготовка должна быть RED."""

import hashlib

import pytest
import copy
from course_tasks import load_solution
from housing.features import FEATURES

s = load_solution(__file__)


class Predictor:
    def predict(self, values):
        return [0] * len(values)


def example(tmp_path):
    data = tmp_path / "data.csv"
    data.write_text("a\n1\n")
    digest = hashlib.sha256(data.read_bytes()).hexdigest()
    split = {"train": [0], "validation": [1], "test": [2]}
    manifest = s.build_manifest(data, 42, split, {"python": "3.12"}, {"alpha": 1.0})
    assert manifest["schema_version"] == 1 and manifest["seed"] == 42
    assert manifest["feature_order"] == FEATURES and manifest["data_sha256"] == digest
    assert manifest["split"] == split and manifest["versions"] == {"python": "3.12"}
    assert manifest["parameters"] == {"alpha": 1.0}
    split["train"].append(99)
    assert manifest["split"]["train"] == [0]
    return (
        {
            "schema_version": 1,
            "pipeline": Predictor(),
            "features": FEATURES.copy(),
            "model_version": "v1",
        },
        manifest,
        digest,
    )


def test_manifest_and_bundle(tmp_path):
    bundle, manifest, digest = example(tmp_path)
    assert s.validate_bundle(bundle, manifest, digest) is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", 2),
        ("features", ["wrong"]),
        ("model_version", ""),
        ("pipeline", None),
    ],
)
def test_reject_bundle(tmp_path, field, value):
    b, m, d = example(tmp_path)
    b[field] = value
    with pytest.raises(ValueError):
        s.validate_bundle(b, m, d)


def test_reject_wrong_provenance(tmp_path):
    b, m, d = example(tmp_path)
    with pytest.raises(ValueError):
        s.validate_bundle(b, m, "0" * 64)
    m["feature_order"] = list(reversed(m["feature_order"]))
    with pytest.raises(ValueError):
        s.validate_bundle(b, m, d)


def test_manifest_is_a_deep_snapshot(tmp_path):
    data = tmp_path / "data.csv"
    data.write_bytes(b"a\n2\n")
    split = {"train": [0, 1], "validation": [2], "test": [3]}
    versions = {"packages": {"numpy": "test"}}
    parameters = {"estimator": {"depths": [2, 4]}}
    expected = copy.deepcopy((split, versions, parameters))
    result = s.build_manifest(data, 13, split, versions, parameters)
    split["train"].append(99)
    versions["packages"]["numpy"] = "changed"
    parameters["estimator"]["depths"].append(9)
    assert (result["split"], result["versions"], result["parameters"]) == expected
    assert result["seed"] == 13
    assert result["data_sha256"] == hashlib.sha256(data.read_bytes()).hexdigest()


class NonCallablePredict:
    predict = 123


@pytest.mark.parametrize(
    "side,field,value",
    [
        ("bundle", "features", FEATURES[::-1]),
        ("bundle", "pipeline", NonCallablePredict()),
        ("manifest", "schema_version", 2),
        ("manifest", "data_sha256", "f" * 64),
        ("manifest", "feature_order", FEATURES[1:] + FEATURES[:1]),
    ],
)
def test_additional_bundle_incompatibilities(tmp_path, side, field, value):
    bundle, manifest, digest = example(tmp_path)
    (bundle if side == "bundle" else manifest)[field] = value
    with pytest.raises(ValueError):
        s.validate_bundle(bundle, manifest, digest)
