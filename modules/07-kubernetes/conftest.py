"""Opt-in readers for an already prepared lab. No cluster mutations."""

import json
import os
import shutil
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pytest


@pytest.fixture
def kube():
    if os.getenv("MLOPS_RUN_INTEGRATION") != "1":
        pytest.skip(
            "Prepare task state, set MLOPS_KUBE_CONTEXT and MLOPS_RUN_INTEGRATION=1; see task README"
        )
    context = os.getenv("MLOPS_KUBE_CONTEXT")
    if not context:
        pytest.fail(
            "Set explicit MLOPS_KUBE_CONTEXT (e.g. kind-mlops-course); current-context is never used"
        )
    if not shutil.which("kubectl"):
        pytest.fail("Install kubectl and prepare the task cluster; see SETUP.md")
    namespace = os.getenv("MLOPS_KUBE_NAMESPACE", "default")

    def get(resource, *args):
        command = [
            "kubectl",
            "--context",
            context,
            "--namespace",
            namespace,
            "--request-timeout=10s",
            "get",
            resource,
            *args,
            "-o",
            "json",
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired) as exc:
            pytest.fail(
                f"kubectl read failed; check explicit context and access: {exc}"
            )
        if result.returncode:
            pytest.fail(
                f"kubectl get {resource} failed; prepare this task's state: {result.stderr}"
            )
        try:
            return json.loads(result.stdout)
        except ValueError:
            pytest.fail("kubectl did not return JSON")

    return get


@pytest.fixture
def http(kube):
    base = os.getenv("MLOPS_API_URL")
    if not base:
        pytest.fail(
            "Set MLOPS_API_URL=http://127.0.0.1:8000 after starting task-specific port-forward"
        )

    def request(path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request(
            base.rstrip("/") + path,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(req, timeout=10) as response:
                return response.status, json.load(response)
        except HTTPError as exc:
            return exc.code, json.load(exc)
        except (OSError, URLError, ValueError) as exc:
            pytest.fail(f"Cannot read prepared API {base}: {exc}")

    return request
