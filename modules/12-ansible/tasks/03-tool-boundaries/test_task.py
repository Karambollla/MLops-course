import json
from pathlib import Path


def test_comparison_contains_all_three_tools_and_own_decision():
    report = json.loads(Path(__file__).with_name("comparison.json").read_text())
    assert set(report["tools"]) == {"Dockerfile", "Terraform", "Ansible"}
    for name, row in report["tools"].items():
        for field in ["input", "state", "repeat", "rollback", "example"]:
            assert (
                isinstance(row[field], str)
                and row[field].strip()
                and "TODO" not in row[field]
            ), f"{name}: заполни {field}"
    assert report["terraform_state_in_git"] is False
    assert report["ansible_vault_is_hashicorp_vault"] is False
    assert isinstance(report["decision"], str) and report["decision"].strip()
