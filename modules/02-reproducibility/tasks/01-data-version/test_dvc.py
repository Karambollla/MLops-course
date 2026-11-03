"""Local DVC remote round trip; no downloads, server or real work/ directory."""

import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys

import pytest
from course_tasks import load_solution

s = load_solution(__file__)


@pytest.mark.sdk
@pytest.mark.skipif(
    os.getenv("MLOPS_RUN_SDK") != "1",
    reason="Set MLOPS_RUN_SDK=1 for the real local DVC round trip",
)
def test_dvc_restores_bytes_verified_by_student_functions(tmp_path):
    if importlib.util.find_spec("dvc") is None:
        pytest.fail(
            "Install python -m pip install -r labs/dvc/requirements.txt", pytrace=False
        )
    project = tmp_path / "project"
    project.mkdir()
    data = project / "housing.csv"
    original = b"feature,target\n1,2\n3,4\n"
    data.write_bytes(original)
    expected = hashlib.sha256(original).hexdigest()
    assert s.sha256_file(data) == expected
    global_config = tmp_path / "global-config"
    global_config.mkdir()
    (global_config / "config").write_text(
        f"[core]\n    site_cache_dir = {tmp_path / 'site-cache'}\n"
    )
    environment = {
        **os.environ,
        "DVC_NO_ANALYTICS": "1",
        "DVC_SITE_CACHE_DIR": str(tmp_path / "site-cache"),
        "DVC_GLOBAL_CONFIG_DIR": str(global_config),
    }

    def dvc(*arguments):
        subprocess.run(
            [sys.executable, "-m", "dvc", *arguments],
            cwd=project,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )

    dvc("init", "--no-scm")
    dvc("remote", "add", "-d", "local", str(tmp_path / "remote"))
    dvc("config", "cache.dir", str(project / ".dvc/cache"))
    dvc("add", "housing.csv")
    dvc("push")
    data.unlink()
    # Clear only this test project's explicitly configured cache.
    shutil.rmtree(project / ".dvc/cache")
    dvc("pull")
    assert data.read_bytes() == original
    assert s.verify_restore(expected, data) is None
    assert s.sha256_file(data) == expected
