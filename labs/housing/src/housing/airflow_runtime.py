"""File/ML boundary for the Airflow exercises; no Airflow or ML imports here."""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from course_tasks import course_root

ML_PYTHON = "/opt/housing-venv/bin/python"
ARTIFACTS = ("model.joblib", "metrics.json", "manifest.json", "split.json")
_TRAIN_SCRIPT = """
import json
import sys
from pathlib import Path
import joblib
from housing.train import train
output = Path(sys.argv[2])
train(Path(sys.argv[1]), output, int(sys.argv[3]))
bundle = joblib.load(output / 'model.joblib')
print('COURSE_TRAIN_RESULT=' + json.dumps({'model_version': bundle['model_version']}))
"""


def _sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def training_revision() -> str:
    """Fingerprint saved training definitions and their CLI adapter."""
    root = course_root()
    files = [root / "modules/01-ml/housing.ipynb", Path(__file__).with_name("train.py")]
    return hashlib.sha256("\n".join(_sha(p) for p in files).encode()).hexdigest()


def interval_metadata(start: datetime, end: datetime) -> dict:
    """Normalize a real daily Airflow interval, never derive one from now()."""
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        raise ValueError("Expected aware datetime interval boundaries")
    if start.utcoffset() is None or end.utcoffset() is None:
        raise ValueError("Interval boundaries must be timezone-aware")
    start, end = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    if end - start != timedelta(days=1) or start.time().isoformat() != "00:00:00":
        raise ValueError("Expected a midnight-to-midnight UTC daily interval")
    return {
        "data_interval_start": start.isoformat(),
        "data_interval_end": end.isoformat(),
        "partition": start.date().isoformat(),
    }


def prepare_training(
    data_path: str | Path,
    seed: int = 42,
    *,
    output_root: str | Path = "/work/runs",
    interval: dict | None = None,
) -> dict:
    """Validate inputs and return small JSON configuration for the training task."""
    data = Path(data_path).resolve()
    if not data.is_file() or data.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty training CSV: {data}")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if interval is not None:
        normalized = interval_metadata(
            datetime.fromisoformat(interval["data_interval_start"]),
            datetime.fromisoformat(interval["data_interval_end"]),
        )
        if normalized != interval:
            raise ValueError("Use normalized interval_metadata output")
    inputs = {
        "data_sha256": _sha(data),
        "seed": seed,
        "code_revision": training_revision(),
        "interval": interval,
    }
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:24]
    return {
        **inputs,
        "data_path": str(data),
        "run_key": key,
        "path": str(Path(output_root).resolve() / key),
    }


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(
                value, stream, ensure_ascii=False, sort_keys=True, allow_nan=False
            )
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run_training(configuration: dict) -> dict:
    """Execute the learner's saved train in the ML venv, then verify its files."""
    if _sha(Path(configuration["data_path"])) != configuration["data_sha256"]:
        raise ValueError("Training data changed after validate_data")
    if training_revision() != configuration["code_revision"]:
        raise ValueError("Training source changed after validate_data")
    try:
        result = subprocess.run(
            [
                ML_PYTHON,
                "-c",
                _TRAIN_SCRIPT,
                configuration["data_path"],
                configuration["path"],
                str(configuration["seed"]),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        logging.getLogger(__name__).error(
            "ML training failed: %s", error.stderr or "no stderr"
        )
        raise
    output = Path(configuration["path"])
    for name in ARTIFACTS:
        path = output / name
        if not path.is_file() or path.stat().st_size == 0:
            raise FileNotFoundError(f"Training did not create {path}")
        if path.suffix == ".json" and not isinstance(
            json.loads(path.read_text()), dict
        ):
            raise ValueError(f"Expected JSON object in {path}")
    lines = [
        line.removeprefix("COURSE_TRAIN_RESULT=")
        for line in result.stdout.splitlines()
        if line.startswith("COURSE_TRAIN_RESULT=")
    ]
    if len(lines) != 1:
        raise ValueError("ML process did not return one model version")
    version = json.loads(lines[0])["model_version"]
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Expected nonempty bundle model_version")
    metadata = {
        "path": str(output),
        "run_key": configuration["run_key"],
        "model_version": version,
    }
    if configuration["interval"] is not None:
        _atomic_json(
            output / "orchestration.json",
            {
                **metadata,
                "interval": configuration["interval"],
                "data_sha256": configuration["data_sha256"],
                "code_revision": configuration["code_revision"],
                "seed": configuration["seed"],
            },
        )
    return metadata


def quality_gate(metadata: dict, ratio: float = 0.9) -> bool:
    """Return the decision; the learner translates rejection into an Airflow error."""
    metrics = json.loads((Path(metadata["path"]) / "metrics.json").read_text())
    candidate = metrics["candidate"]["test"]["mae"]
    baseline = metrics["baseline"]["test"]["mae"]
    for value in (candidate, baseline, ratio):
        if (
            isinstance(value, bool)
            or not isinstance(value, (float, int))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError("Metrics and ratio must be finite nonnegative numbers")
    if baseline == 0 or ratio > 1:
        raise ValueError("Expected positive baseline and ratio between 0 and 1")
    return candidate <= ratio * baseline


def publish_release(metadata: dict, release_dir: str | Path = "/work/releases") -> dict:
    """Idempotent local publication; safe under the course's max_active_runs=1."""
    key, version = metadata["run_key"], metadata["model_version"]
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", key):
        raise ValueError("Unsafe run_key")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Expected model_version")
    model = Path(metadata["path"]) / "model.joblib"
    if not model.is_file() or model.stat().st_size == 0:
        raise FileNotFoundError(model)
    value = {"run_key": key, "model_path": str(model), "model_version": version}
    path = Path(release_dir) / f"{key}.json"
    if path.exists():
        if json.loads(path.read_text()) != value:
            raise ValueError("Conflicting existing release")
        return value
    _atomic_json(path, value)
    return value
