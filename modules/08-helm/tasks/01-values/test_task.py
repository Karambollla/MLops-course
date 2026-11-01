"""Render student chart twice; compare real resources, no cluster access."""

import os
import re
import shutil
import subprocess
import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def quantity(value):
    """Compare rendered SI/binary/exponent quantities without float rounding.

    Format: https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/quantity/
    Server-side resource validation remains a separate kubectl/Helm operation.
    """
    match = re.fullmatch(
        r"([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))([KMGTPE]i|[mkMGTPE]|[eE][+-]?[0-9]+)?",
        str(value),
    )
    assert match, f"Invalid resource quantity: {value}"
    number, suffix = match.groups()
    if suffix and suffix.endswith("i"):
        factor = Decimal(1024) ** ("KMGTPE".index(suffix[0]) + 1)
    elif suffix and len(suffix) > 1 and suffix[0] in "eE":
        factor = Decimal(10) ** int(suffix[1:])
    else:
        factor = (
            Decimal(10)
            ** {None: 0, "m": -3, "k": 3, "M": 6, "G": 9, "T": 12, "P": 15, "E": 18}[
                suffix
            ]
        )
    return Decimal(number) * factor


def test_values_config_and_checksum():
    if os.getenv("MLOPS_RUN_INTEGRATION") != "1":
        pytest.skip(
            "Install Helm 3 and PyYAML, complete values/chart, then MLOPS_RUN_INTEGRATION=1; see README"
        )
    assert shutil.which("helm"), "Install Helm 3; see SETUP.md"
    try:
        import yaml
    except ImportError:
        pytest.fail("Install PyYAML in the test environment to inspect rendered YAML")
    task = Path(__file__).parent

    def render():
        command = [
            "helm",
            "template",
            "housing-demo",
            str(task / "chart"),
            "-f",
            str(task / "values-dev.yaml"),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired) as exc:
            pytest.fail(f"helm template failed: {exc}")
        assert result.returncode == 0, result.stderr
        return list(yaml.safe_load_all(result.stdout))

    first = render()
    resources = {r["kind"]: r for r in first if r}
    deployment = resources["Deployment"]
    spec = deployment["spec"]
    assert spec["replicas"] == 1
    assert resources["Service"]["metadata"]["name"] == "housing-demo"
    selector = resources["Service"]["spec"]["selector"]
    labels = spec["template"]["metadata"]["labels"]
    assert selector and all(labels.get(key) == value for key, value in selector.items())
    container = spec["template"]["spec"]["containers"][0]
    assert container["image"] == "housing:v1"

    resources_limits = container["resources"]
    assert (
        0
        < quantity(resources_limits["requests"]["memory"])
        <= quantity(resources_limits["limits"]["memory"])
    )
    assert (
        0
        < quantity(resources_limits["requests"]["cpu"])
        <= quantity(resources_limits["limits"]["cpu"])
    )
    assert container["readinessProbe"]["httpGet"]["path"] == "/ready"
    assert container["livenessProbe"]["httpGet"]["path"] == "/live"
    config = resources["ConfigMap"]
    assert config["data"], "Add ordinary config, not credentials"
    assert any(
        item.get("configMapRef", {}).get("name") == config["metadata"]["name"]
        for item in container.get("envFrom", [])
    ), "Connect ConfigMap through envFrom"
    # Change one existing key in a temporary override, never modify student files.
    key, value = next(iter(config["data"].items()))
    with tempfile.TemporaryDirectory() as directory:
        override = Path(directory) / "changed.yaml"
        override.write_text(yaml.safe_dump({"config": {key: str(value) + "-changed"}}))
        command = [
            "helm",
            "template",
            "housing-demo",
            str(task / "chart"),
            "-f",
            str(task / "values-dev.yaml"),
            "-f",
            str(override),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired) as exc:
            pytest.fail(f"helm template failed: {exc}")
        assert result.returncode == 0, result.stderr
        second = {r["kind"]: r for r in yaml.safe_load_all(result.stdout) if r}
    assert second["ConfigMap"]["data"] != config["data"]
    before = spec["template"]["metadata"]["annotations"]["checksum/config"]
    after = second["Deployment"]["spec"]["template"]["metadata"]["annotations"][
        "checksum/config"
    ]
    assert len(before) == len(after) == 64
    int(before, 16)
    int(after, 16)
    assert before != after
