"""Offline проверки поведения; исходная заготовка должна быть RED."""

from types import SimpleNamespace

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


class Client:
    def get_model_version_by_alias(self, name, alias):
        assert (name, alias) == ("housing", "champion")
        return SimpleNamespace(version="7", run_id="run-1")


class Model:
    def __init__(self, values):
        self.values = values

    def predict(self, batch):
        return self.values


def test_alias_is_resolved():
    assert s.resolve_release(Client(), "housing", "champion", "run-1") == {
        "model_name": "housing",
        "alias": "champion",
        "version": "7",
        "run_id": "run-1",
        "model_uri": "models:/housing/7",
    }
    with pytest.raises(ValueError):
        s.resolve_release(Client(), "housing", "champion", "other")


def test_prediction_parity():
    assert (
        s.assert_parity(Model([1.0, 2.0]), Model([1.0 + 1e-9, 2.0]), [{}, {}]) is None
    )
    for values in [[1.0], [1.0, 3.0], [1.0, float("nan")]]:
        with pytest.raises(ValueError):
            s.assert_parity(Model([1.0, 2.0]), Model(values), [{}, {}])
