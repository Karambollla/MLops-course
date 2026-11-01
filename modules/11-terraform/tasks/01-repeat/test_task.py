import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("MLOPS_RUN_INTEGRATION") != "1",
        reason="Set MLOPS_RUN_INTEGRATION=1 for an existing Terraform lab",
    ),
]


def workdir():
    value = os.getenv("MLOPS_TERRAFORM_DIR")
    assert value, (
        "Set MLOPS_TERRAFORM_DIR to the existing initialized 11-terraform/01-repeat working directory"
    )
    p = Path(value).expanduser().resolve()
    assert (
        p.is_dir() and (p / "main.tf").is_file() and (p / "terraform.tfstate").is_file()
    ), (
        "Expected existing main.tf and local terraform.tfstate; initialize/apply the task manually first"
    )
    assert shutil.which("terraform"), "Install Terraform 1.11.4 and add it to PATH"
    return p


def terraform(directory, *args, codes=(0,)):
    try:
        result = subprocess.run(
            ["terraform", f"-chdir={directory}", *args],
            capture_output=True,
            text=True,
            timeout=90,
        )
    except (OSError, subprocess.TimeoutExpired):
        pytest.fail(
            "Terraform could not run; check CLI, provider and Docker endpoint",
            pytrace=False,
        )
    if result.returncode not in codes:
        pytest.fail(
            "Terraform command failed; inspect diagnostics locally (state/plan may contain secrets). Check init, TF_VAR_docker_host and Docker.",
            pytrace=False,
        )
    return result


def test_actual_plan():
    directory = workdir()
    with tempfile.TemporaryDirectory(prefix="mlops-plan-") as tmp:
        plan = Path(tmp) / "check.tfplan"
        result = terraform(
            directory,
            "plan",
            "-input=false",
            "-lock=false",
            "-detailed-exitcode",
            f"-out={plan}",
            codes=(0, 2),
        )
        data = json.loads(terraform(directory, "show", "-json", str(plan)).stdout)
    changes = {
        row["address"]: row["change"]["actions"]
        for row in data.get("resource_changes", [])
    }
    assert changes.get("docker_container.web") == ["no-op"], (
        "Unexpected web actions: inspect terraform plan in your task directory"
    )
    if result.returncode != 0:
        pytest.fail("Repeat plan must have no changes", pytrace=False)
    assert all(actions == ["no-op"] for actions in changes.values())
