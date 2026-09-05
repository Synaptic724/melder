"""Prove safety-relevant workflow wiring using parsed YAML rather than substring matches."""

import pathlib
import json
from types import ModuleType
from typing import cast

import pytest
import yaml


def workflow(name: str) -> dict[str, object]:
    """Parse one workflow preserving Actions' on key and scalar spellings."""
    root = pathlib.Path(__file__).resolve().parents[3]
    # BaseLoader avoids YAML 1.1 interpreting the Actions key 'on' as boolean True.
    result: object = yaml.load((root / ".github/workflows" / name).read_text(encoding="utf-8"),
                               Loader=yaml.BaseLoader)
    if not isinstance(result, dict):
        raise ValueError(f"Workflow {name} must contain a YAML mapping.")
    return cast(dict[str, object], result)


def test_every_pr_reports_a_fail_closed_required_status(policy: ModuleType) -> None:
    """CI must run for each protected destination and aggregate every mandatory job."""
    document = workflow("ci.yml")
    events = document["on"]
    assert set(events["pull_request"]["branches"]) == {"dev", "preprod", "prod"}
    assert "edited" in events["pull_request"]["types"]
    assert "paths" not in events["pull_request"]
    assert "paths-ignore" not in events["pull_request"]
    assert set(events["push"]["branches"]) == {"dev", "preprod", "prod"}
    jobs = document["jobs"]
    final = jobs["merge-ready"]
    assert final["name"] == "CI / merge-ready"
    assert final["if"] == "always()"
    assert set(final["needs"]) == set(policy.CIPolicy.REQUIRED_JOBS) | {"packages"}
    assert "merge-ready" in final["steps"][-1]["run"]
    assert jobs["packages"]["if"] == "needs.branch-policy.outputs.package-required == 'true'"
    for name in policy.CIPolicy.REQUIRED_JOBS:
        assert "if" not in jobs[name]
        assert "continue-on-error" not in jobs[name]


@pytest.mark.parametrize("name", ["build-src-assets.yml", "build-repo-assets.yml", "test-runtime.yml", "docs.yml"])
def test_reusable_mandatory_jobs_cannot_be_disabled(name: str) -> None:
    """Callers own triggers/concurrency; no helper silently skips a mandatory validation job."""
    document = workflow(name)
    assert set(document["on"]) == {"workflow_call", "workflow_dispatch"}
    assert document["permissions"] == {"contents": "read"}
    assert "concurrency" not in document
    for job in document["jobs"].values():
        assert "if" not in job
        assert "continue-on-error" not in job
        assert "environment" not in job
        assert "timeout-minutes" in job


def test_supported_runtime_matrix_and_test_driver_are_shared() -> None:
    """Both supported OSes use 3.14t with the GIL off and retain failing-test evidence."""
    job = workflow("test-runtime.yml")["jobs"]["test"]
    assert set(job["strategy"]["matrix"]["os"]) == {"ubuntu-latest", "windows-latest"}
    assert job["strategy"]["fail-fast"] == "false"
    assert job["env"]["PYTHON_GIL"] == "0"
    setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "3.14t"
    assert any("run_runtime_tests.py" in step.get("run", "") for step in job["steps"])
    report = job["steps"][-1]
    assert report["if"] == "always()"
    assert report["uses"].startswith("actions/upload-artifact@")


def test_publication_repeats_validation_and_checks_prod_last() -> None:
    """A green historical PR cannot replace fresh release validation or the last head check."""
    document = workflow("python-publish.yml")
    assert set(document["on"]) == {"release", "workflow_dispatch"}
    assert document["concurrency"] == {"group": "pypi-publication", "cancel-in-progress": "false"}
    jobs = document["jobs"]
    assert jobs["tests"]["uses"] == "./.github/workflows/test-runtime.yml"
    assert jobs["tests"]["needs"] == "release-gate"
    required = {"release-gate", "hygiene", "source-assets", "repo-assets", "tests"}
    assert set(jobs["release-build"]["needs"]) == required
    publisher = jobs["pypi-publish"]
    assert set(publisher["needs"]) == required | {"release-build"}
    assert publisher["environment"]["name"] == "pypi"
    steps = publisher["steps"]
    assert steps[-2]["run"] == "python .github/scripts/ci_policy.py release-head"
    assert steps[-3]["run"].startswith("python .github/scripts/verify_distributions.py")
    assert steps[-1]["uses"].startswith("pypa/gh-action-pypi-publish@")
    assert "skip-existing" not in steps[-1]["with"]
    uploaded = jobs["release-build"]["with"]["artifact-name"]
    downloaded = next(step["with"]["name"] for step in steps
                      if step.get("uses", "").startswith("actions/download-artifact@"))
    assert uploaded == downloaded
    assert "github.run_attempt" in uploaded
    assert all("environment" not in job for name, job in jobs.items() if name != "pypi-publish")


def test_package_verification_precedes_artifact_upload() -> None:
    """Only built, inspected, installed-wheel-verified files become distributable artifacts."""
    document = workflow("build-distributions.yml")
    assert document["permissions"] == {"contents": "read"}
    steps = document["jobs"]["build"]["steps"]
    assert "environment" not in document["jobs"]["build"]
    commands = [step.get("run", "") for step in steps]
    verify = next(index for index, command in enumerate(commands) if "verify_distributions.py" in command)
    smoke = next(index for index, command in enumerate(commands) if "smoke_wheel.py" in command)
    assert verify < smoke < len(steps) - 1
    assert " -I " in commands[smoke]
    assert steps[-1]["uses"].startswith("actions/upload-artifact@")


@pytest.mark.parametrize("branch", ["dev", "preprod", "prod"])
def test_rulesets_require_the_real_final_check_and_preserve_promotion_history(branch: str) -> None:
    """Ruleset payloads must name the actual aggregate check and block direct destructive updates."""
    root = pathlib.Path(__file__).resolve().parents[3]
    document = json.loads((root / ".github/rulesets" / f"{branch}.json").read_text(encoding="utf-8"))
    assert document["conditions"]["ref_name"]["include"] == [f"refs/heads/{branch}"]
    assert document["bypass_actors"] == []
    rules = {rule["type"]: rule for rule in document["rules"]}
    assert {"deletion", "non_fast_forward", "pull_request", "required_status_checks"} <= set(rules)
    required = rules["required_status_checks"]["parameters"]
    assert required["required_status_checks"] == [{
        "context": workflow("ci.yml")["jobs"]["merge-ready"]["name"], "integration_id": 15368,
    }]
    assert required["strict_required_status_checks_policy"] is (branch == "dev")
    if branch != "dev":
        assert rules["pull_request"]["parameters"]["allowed_merge_methods"] == ["merge"]
        assert "required_linear_history" not in rules
