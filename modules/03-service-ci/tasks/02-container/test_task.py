"""Проверяем заполненный артефакт; Docker сам не запускаем."""

import os
import urllib.request
from pathlib import Path

import pytest
from course_tasks import read_json


def test_image_and_runtime_evidence():
    e = read_json(Path(__file__).parent / "evidence.json")
    assert e["user"] not in [None, "", "0", "root", "0:0"]
    assert e["model_read_only"] is True
    assert e["embedded_paths"] == []
    assert e["ready_status"] == 200 and e["predictions_count"] == 1
    assert isinstance(e["image_id"], str) and e["image_id"].startswith("sha256:")
    assert e["dependency_versions"] and "python" in e["dependency_versions"]
    assert isinstance(e["image_size_bytes"], int) and e["image_size_bytes"] > 0


def test_missing_model_experiment():
    e = read_json(Path(__file__).parent / "evidence.json")
    assert e["without_model_ready_status"] == 503
    assert e["without_model_predict_status"] == 503
    assert e["without_model_live_status"] == 200
    assert e["model_removed_only_in_temporary_copy"] is True


def test_running_container_read_only_probe():
    if os.environ.get("MLOPS_RUN_INTEGRATION") != "1":
        pytest.skip("Требуется уже запущенный Compose: opt-in")
    with urllib.request.urlopen("http://127.0.0.1:8000/ready", timeout=5) as response:
        assert response.status == 200
