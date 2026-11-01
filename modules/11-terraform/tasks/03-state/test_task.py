import json
import os
import shutil
import subprocess
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


def test_state_matches_existing_container():
    directory = workdir()
    data = json.loads(terraform(directory, "show", "-json").stdout)
    resources = data.get("values", {}).get("root_module", {}).get("resources", [])
    found = {r["address"]: r for r in resources}
    assert {"docker_image.web", "docker_container.web"} <= found.keys(), (
        "Apply the task manually before checking state"
    )
    identifier = found["docker_container.web"]["values"]["id"]
    assert shutil.which("docker"), (
        "Install Docker CLI and start the task Docker endpoint"
    )
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.Id}}", "mlops-course-terraform"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        pytest.fail("Docker inspect failed; check Docker endpoint", pytrace=False)
    if result.returncode != 0:
        pytest.fail(
            "Docker inspect failed; check Docker context matches TF_VAR_docker_host",
            pytrace=False,
        )
    assert identifier == result.stdout.strip(), (
        "State binding differs from actual container ID"
    )
