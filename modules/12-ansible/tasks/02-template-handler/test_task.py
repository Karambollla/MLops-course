import hashlib
import os
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("MLOPS_RUN_INTEGRATION") != "1",
        reason="Set MLOPS_RUN_INTEGRATION=1 after manually running the task playbook",
    ),
]


def test_generated_config_and_handler_marker():
    directory = (
        Path(__file__).resolve().parents[4] / "work" / "ansible-template" / "config"
    )
    config = directory / "housing.env"
    marker = directory / "housing.env.sha256"
    assert config.is_file(), (
        "Run task-local controller; template destination must be /course-output/config/housing.env"
    )
    assert marker.is_file(), (
        "Handler must write config SHA256 to /course-output/config/housing.env.sha256"
    )
    settings = dict(
        line.split("=", 1)
        for line in config.read_text().splitlines()
        if line and not line.startswith("#")
    )
    assert settings.get("MODEL_PATH") == "/models/model.joblib"
    assert settings.get("WORKERS") == "2", (
        "Complete workers=1, workers=2, workers=2 runs before checking"
    )
    assert (
        marker.read_text().strip() == hashlib.sha256(config.read_bytes()).hexdigest()
    ), "Handler marker must match actual config digest"
