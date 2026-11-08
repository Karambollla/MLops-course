"""Notebook import infrastructure; no student ML implementations are tested here."""

import json

import pytest

import course_tasks.notebook as notebooks
import housing.train as training


def write_notebook(path, cells):
    path.write_text(json.dumps({"nbformat": 4, "nbformat_minor": 5, "cells": cells}))


def cell(source, tag=None):
    return {
        "cell_type": "code",
        "metadata": {"tags": [tag] if tag else []},
        "source": source,
    }


def test_import_executes_only_definitions_and_uses_fresh_saved_source(tmp_path):
    path = tmp_path / "demo.ipynb"
    cells = [
        cell("raise AssertionError('installation must not execute')"),
        cell("from pathlib import Path", "course:imports"),
        cell("def identify():\n    return Path('first').name", "course:definitions"),
        cell("raise AssertionError('tests must not execute')", "course:tests"),
    ]
    write_notebook(path, cells)
    first = notebooks.load_notebook(path)
    assert first.identify() == "first"
    cells[2]["source"] = ["def identify():\n", "    return 'second'\n"]
    write_notebook(path, cells)
    second = notebooks.load_notebook(path)
    assert second.identify() == "second"
    assert first.identify() == "first"


@pytest.mark.parametrize("missing", ["course:imports", "course:definitions"])
def test_missing_required_tag_is_explicit(tmp_path, missing):
    path = tmp_path / "demo.ipynb"
    write_notebook(
        path,
        [
            cell("VALUE = 1", tag)
            for tag in ("course:imports", "course:definitions")
            if tag != missing
        ],
    )
    with pytest.raises(ValueError, match=missing):
        notebooks.load_notebook(path)


def test_bad_json_and_syntax_identify_notebook_cell(tmp_path):
    path = tmp_path / "demo.ipynb"
    path.write_text("broken")
    with pytest.raises(ValueError, match="demo.ipynb"):
        notebooks.load_notebook(path)
    write_notebook(
        path,
        [
            cell("import os", "course:imports"),
            cell("def broken(:", "course:definitions"),
        ],
    )
    with pytest.raises(SyntaxError) as failure:
        notebooks.load_notebook(path)
    assert "demo.ipynb" in failure.value.filename
    assert "cell-2" in failure.value.filename


def test_housing_import_is_confined_to_module(tmp_path, monkeypatch):
    (tmp_path / "modules/01-ml").mkdir(parents=True)
    (tmp_path / "modules/tasks.json").write_text('{"schema_version":1,"tasks":[]}')
    outside = tmp_path / "outside.ipynb"
    write_notebook(outside, [])
    (tmp_path / "modules/01-ml/housing.ipynb").symlink_to(outside)
    monkeypatch.setenv("MLOPS_COURSE_ROOT", str(tmp_path))
    with pytest.raises(ValueError):
        notebooks.housing_notebook_path()


def test_missing_housing_notebook_has_clear_path(tmp_path, monkeypatch):
    (tmp_path / "modules/01-ml").mkdir(parents=True)
    (tmp_path / "modules/tasks.json").write_text('{"schema_version":1,"tasks":[]}')
    monkeypatch.setenv("MLOPS_COURSE_ROOT", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="housing.ipynb"):
        notebooks.load_notebook(notebooks.housing_notebook_path())


def test_housing_module_directory_cannot_escape_course(tmp_path, monkeypatch):
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules/tasks.json").write_text('{"schema_version":1,"tasks":[]}')
    outside = tmp_path / "external"
    outside.mkdir()
    (tmp_path / "modules/01-ml").symlink_to(outside, target_is_directory=True)
    monkeypatch.setenv("MLOPS_COURSE_ROOT", str(tmp_path))
    with pytest.raises(ValueError):
        notebooks.housing_notebook_path()


@pytest.mark.parametrize("mode", ["omitted", "none", "configured"])
def test_train_adapter_preserves_legacy_calls_and_forwards_parameters(
    tmp_path, monkeypatch, mode
):
    path = tmp_path / "training.ipynb"
    if mode == "configured":
        definition = (
            "def train(data, output, seed, *, parameters=None):\n"
            "    output.write_text(json.dumps([str(data), seed, parameters]))\n"
        )
    else:
        # A saved three-argument implementation remains callable until updated.
        definition = (
            "def train(data, output, seed):\n"
            "    output.write_text(json.dumps([str(data), seed, None]))\n"
        )
    write_notebook(
        path,
        [
            cell("import json", "course:imports"),
            cell(definition, "course:definitions"),
            cell("raise AssertionError('lab cells must not run')"),
        ],
    )
    monkeypatch.setattr(training, "housing_notebook_path", lambda: path)
    data, receipt = tmp_path / "input.csv", tmp_path / "receipt.json"
    kwargs = {} if mode == "omitted" else {"parameters": None}
    if mode == "configured":
        kwargs = {"parameters": {"alpha": 0.1}}
    assert training.train(data, receipt, 17, **kwargs) is None
    assert json.loads(receipt.read_text()) == [
        str(data), 17, kwargs.get("parameters")
    ]
