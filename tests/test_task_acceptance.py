"""Regression checks: the course must accept valid student Helm renders."""

import copy
import json
import subprocess
from types import SimpleNamespace

import pytest
from course_tasks import load_task


@pytest.mark.parametrize(
    "extra_labels,memory",
    [
        ({"app.kubernetes.io/name": "housing"}, ("128Mi", "768Mi")),
        ({}, ("128M", "768M")),
        ({}, ("128Mi", "2Gi")),
    ],
)
def test_helm_accepts_selector_subset_and_valid_resource_quantities(
    monkeypatch, extra_labels, memory
):
    checker = load_task("08-helm/01-values", filename="test_task.py")
    selector = {"app": "housing"}
    resources = [
        {
            "kind": "Service",
            "metadata": {"name": "housing-demo"},
            "spec": {"selector": selector},
        },
        {
            "kind": "ConfigMap",
            "metadata": {"name": "housing-config"},
            "data": {"MODEL_PATH": "/models/model.joblib"},
        },
        {
            "kind": "Deployment",
            "spec": {
                "replicas": 1,
                "template": {
                    "metadata": {
                        "labels": {**selector, **extra_labels},
                        "annotations": {"checksum/config": "a" * 64},
                    },
                    "spec": {
                        "containers": [
                            {
                                "image": "housing:v1",
                                "resources": {
                                    "requests": {"memory": memory[0], "cpu": "100m"},
                                    "limits": {"memory": memory[1], "cpu": "1"},
                                },
                                "readinessProbe": {"httpGet": {"path": "/ready"}},
                                "livenessProbe": {"httpGet": {"path": "/live"}},
                                "envFrom": [
                                    {"configMapRef": {"name": "housing-config"}}
                                ],
                            }
                        ]
                    },
                },
            },
        },
    ]
    calls = []

    def render(command, **kwargs):
        result = copy.deepcopy(resources)
        if calls:
            result[1]["data"]["MODEL_PATH"] += "-changed"
            result[2]["spec"]["template"]["metadata"]["annotations"][
                "checksum/config"
            ] = "b" * 64
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, json.dumps(result), "")

    # YAML parsing is orthogonal here: feed parsed resources from two render calls.
    monkeypatch.setattr(
        checker,
        "yaml",
        SimpleNamespace(safe_load_all=json.loads, safe_dump=json.dumps),
    )
    monkeypatch.setenv("MLOPS_RUN_INTEGRATION", "1")
    monkeypatch.setattr(checker.shutil, "which", lambda name: "/test/helm")
    monkeypatch.setattr(checker.subprocess, "run", render)
    checker.test_values_config_and_checksum()
    assert len(calls) == 2
