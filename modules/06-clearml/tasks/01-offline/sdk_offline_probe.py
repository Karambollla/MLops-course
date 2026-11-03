"""Test harness: real SDK storage; only the training boundary is synthetic.

Launched in an isolated subprocess by test_task.py, never as a student solution.
"""

import hashlib
import json
import sys
from pathlib import Path
from uuid import uuid4

import housing.train
from clearml import Task, __version__
from course_tasks import load_task


def main(root: Path, seed: int):
    assert __version__ == "1.18.0"
    solution = load_task("06-clearml/01-offline")
    data, output = root / "synthetic.csv", root / "bundle"
    data.write_text(f"training-boundary-fixture-{seed}\n", encoding="utf-8")
    checksum = hashlib.sha256(data.read_bytes()).hexdigest()
    mae, rmse = seed / 1000, seed / 1000 + 0.123
    calls = []

    def synthetic_train(actual_data, actual_output, actual_seed):
        calls.append((Path(actual_data), Path(actual_output), actual_seed))
        output.mkdir()
        (output / "split.json").write_text(
            json.dumps({"train": [0], "validation": [1], "test": [2]})
        )
        (output / "model.joblib").write_bytes(f"synthetic-model-{seed}".encode())
        (output / "manifest.json").write_text(
            json.dumps({"seed": seed, "data_sha256": checksum})
        )
        (output / "metrics.json").write_text(
            json.dumps({"candidate": {"test": {"mae": mae, "rmse": rmse}}})
        )

    # No fake Task/logger/artifact transport: the pinned ClearML SDK stays real.
    housing.train.train = synthetic_train
    Task.set_offline(True)
    task = Task.init(
        project_name="course-sdk-tests",
        task_name="offline-" + uuid4().hex,
        reuse_last_task_id=False,
        auto_connect_frameworks=False,
        auto_connect_arg_parser=False,
        auto_resource_monitoring=False,
        auto_connect_streams=False,
    )
    folder = Path(task.get_offline_mode_folder())
    try:
        solution.train_and_log(task, data, output, seed)
        task.flush(wait_for_uploads=True)
    finally:
        task.close()
    assert calls == [(data, output, seed)]
    assert folder.is_relative_to(root), "SDK cache must remain inside pytest tmp_path"
    stored = json.loads((folder / "task.json").read_text())
    params = {
        key: value["value"]
        for section in stored["hyperparams"].values()
        for key, value in section.items()
    }
    assert int(params["seed"]) == seed
    assert params["data_sha256"] == checksum
    events = [
        event
        for line in (folder / "metrics.jsonl").read_text().splitlines()
        for event in json.loads(line)
    ]
    for series, value in (("mae", mae), ("rmse", rmse)):
        assert any(
            event.get("metric") == "quality"
            and event.get("variant") == series
            and event.get("iter") == 0
            and abs(event.get("value", -100) - value) < 1e-12
            for event in events
        ), f"Missing persisted scalar quality/{series}={value}"
    artifacts = {
        artifact["key"]: artifact for artifact in stored["execution"]["artifacts"]
    }
    for name in ("model.joblib", "manifest.json"):
        artifact = artifacts[name]
        assert artifact["mode"] == "output"
        assert (
            artifact["hash"] == hashlib.sha256((output / name).read_bytes()).hexdigest()
        )
        # Verify the SDK's stored copy, independently of the training output.
        copies = [p for p in (folder / "data").rglob(name) if p.is_file()]
        assert any(p.read_bytes() == (output / name).read_bytes() for p in copies)


if __name__ == "__main__":
    main(Path(sys.argv[1]), int(sys.argv[2]))
