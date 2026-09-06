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
    assert set(events["pull_request"]["branches"]) == {"dev", "preprod", "release_candidate", "prod"}
    assert "edited" in events["pull_request"]["types"]
    assert "paths" not in events["pull_request"]
    assert "paths-ignore" not in events["pull_request"]
    assert set(events) == {"pull_request", "workflow_dispatch"}
    jobs = document["jobs"]
    final = jobs["merge-ready"]
    assert final["name"] == "CI / merge-ready"
    assert final["if"] == "always()"
    assert set(final["needs"]) == set(policy.CIPolicy.REQUIRED_JOBS) | {"packages"}
    aggregate = next(step for step in final["steps"]
                     if step.get("run") == "python .github/scripts/ci_policy.py merge-ready")
    assert "if" not in aggregate
    assert aggregate["env"]["CI_JOB_RESULTS"] == "${{ toJSON(needs) }}"
    assert aggregate["env"]["CI_PACKAGE_REQUIRED"] == "${{ needs.branch-policy.outputs.package-required }}"
    assert aggregate["env"]["CI_RUNTIME_REQUIRED"] == "${{ needs.branch-policy.outputs.runtime-required }}"
    assert aggregate["env"]["CI_SOURCE_REQUIRED"] == "${{ needs.branch-policy.outputs.source-required }}"
    assert jobs["packages"]["if"] == "needs.branch-policy.outputs.package-required == 'true'"
    for name in policy.CIPolicy.FULL_JOBS:
        assert jobs[name]["needs"] == "branch-policy"
        assert jobs[name]["if"] == "needs.branch-policy.outputs.runtime-required == 'true'"
    for name in ("branch-policy", "hygiene"):
        assert "if" not in jobs[name]
    for name in policy.CIPolicy.REQUIRED_JOBS:
        assert "continue-on-error" not in jobs[name]
    assert jobs["source-qualification"]["if"] == "needs.branch-policy.outputs.source-required == 'true'"


@pytest.mark.parametrize("name", ["build-src-assets.yml", "build-repo-assets.yml", "test-runtime.yml", "docs.yml"])
def test_reusable_mandatory_jobs_cannot_be_disabled(name: str) -> None:
    """Callers own triggers/concurrency; no helper silently skips a mandatory validation job."""
    document = workflow(name)
    assert set(document["on"]) == {"workflow_call", "workflow_dispatch"}
    assert document["permissions"] == {"contents": "read"}
    assert "concurrency" not in document
    for job_name, job in document["jobs"].items():
        if name == "test-runtime.yml" and job_name == "coverage":
            # Report delivery is not a mandatory test or publication gate.
            continue
        assert "if" not in job
        assert "continue-on-error" not in job
        assert "environment" not in job
        assert "timeout-minutes" in job


@pytest.mark.parametrize(("name", "job_name"), [
    ("test-runtime.yml", "test"),
    ("release-candidate.yml", "install"),
    ("build-distributions.yml", "build"),
])
def test_python_setup_does_not_force_gil_off_in_standard_bootstrap_helpers(name: str, job_name: str) -> None:
    """Mac certificate installation uses standard Python even when installing a free-threaded build.

    Resolve the environment inherited by setup-python. Forcing PYTHON_GIL=0 at
    this boundary crashes that helper before package installation or tests run.
    """
    document = workflow(name)
    job = document["jobs"][job_name]
    setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
    inherited = {**document.get("env", {}), **job.get("env", {}), **setup.get("env", {})}
    assert inherited.get("PYTHON_GIL") != "0"


def test_supported_runtime_matrix_and_test_driver_are_shared() -> None:
    """All three supported OSes use 3.14t with the GIL off and retain failing-test evidence."""
    job = workflow("test-runtime.yml")["jobs"]["test"]
    assert set(job["strategy"]["matrix"]["os"]) == {"ubuntu-latest", "windows-latest", "macos-latest"}
    assert job["strategy"]["fail-fast"] == "false"
    setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "3.14t"
    runner = next(step for step in job["steps"] if "run_runtime_tests.py" in step.get("run", ""))
    assert runner["env"]["PYTHON_GIL"] == "0"
    report = job["steps"][-1]
    assert report["if"] == "always()"
    assert report["uses"].startswith("actions/upload-artifact@")


def test_coverage_uses_existing_tests_and_separate_current_run_artifacts() -> None:
    """Measure in the one runtime invocation and keep each OS report separate from JUnit."""
    document = workflow("test-runtime.yml")
    assert set(document["jobs"]) == {"test", "coverage"}
    test = document["jobs"]["test"]
    runners = [step for step in test["steps"] if "run_runtime_tests.py" in step.get("run", "")]
    assert len(runners) == 1
    assert runners[0]["run"] == (
        "python .github/scripts/run_runtime_tests.py --report reports/runtime.xml "
        "--coverage-report reports/coverage.xml"
    )
    assert runners[0].get("continue-on-error", "false") == "false"
    retained = next(step for step in test["steps"] if step.get("name") == "Retain coverage report")
    assert retained["if"] == "always()"
    assert retained["continue-on-error"] == "true"
    assert retained["with"]["name"] == "coverage-${{ matrix.os }}-${{ github.run_id }}-${{ github.run_attempt }}"
    assert retained["with"]["path"] == "reports/coverage.xml"
    reporting = document["jobs"]["coverage"]
    download = next(step for step in reporting["steps"]
                    if step.get("uses", "").startswith("actions/download-artifact@"))
    assert download["with"] == {
        "pattern": "coverage-*-${{ github.run_id }}-${{ github.run_attempt }}",
        "path": "coverage-reports", "merge-multiple": "false",
    }
    complete = next(step for step in reporting["steps"] if step.get("name") == "Require the complete coverage matrix")
    for os in test["strategy"]["matrix"]["os"]:
        assert os in complete["run"]
    assert 'coverage-$os-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}/coverage.xml' in complete["run"]
    assert 'exit 1' in complete["run"]
    assert reporting["steps"].index(download) < reporting["steps"].index(complete) < len(reporting["steps"]) - 1


def test_coverage_upload_is_nonblocking_token_only_and_skips_fork_prs() -> None:
    """Coverage cannot grant publication rights, run after failed tests, or expose tokens to forks."""
    document = workflow("test-runtime.yml")
    assert document["on"]["workflow_call"]["secrets"]["CODECOV_TOKEN"]["required"] == "false"
    job = document["jobs"]["coverage"]
    assert job["needs"] == "test"
    assert job["continue-on-error"] == "true"
    assert job["if"] == (
        "github.event_name != 'pull_request' || "
        "github.event.pull_request.head.repo.full_name == github.repository"
    )
    assert document["permissions"] == {"contents": "read"}
    assert "permissions" not in job and "environment" not in job and "env" not in job
    credential_check = job["steps"][0]
    assert credential_check["id"] == "credentials"
    assert credential_check["env"] == {"CODECOV_TOKEN": "${{ secrets.CODECOV_TOKEN }}"}
    assert 'enabled=false' in credential_check["run"] and '::warning::' in credential_check["run"]
    assert all(step["if"] == "steps.credentials.outputs.enabled == 'true'" for step in job["steps"][1:])
    upload = job["steps"][-1]
    assert upload["uses"] == "codecov/codecov-action@v7"
    assert upload["with"]["token"] == "${{ secrets.CODECOV_TOKEN }}"
    assert upload["with"]["directory"] == "coverage-reports"
    assert upload["with"]["fail_ci_if_error"] == "true"
    assert upload["with"].get("use_oidc", "false") == "false"
    assert upload["with"]["override_branch"] == "${{ github.event_name == 'release' && 'prod' || '' }}"


@pytest.mark.parametrize("name", ["ci.yml", "python-publish.yml"])
def test_runtime_callers_forward_only_the_coverage_secret(name: str) -> None:
    """Nested reporting receives its own token without inheriting package upload credentials."""
    caller = workflow(name)["jobs"]["tests"]
    assert caller["secrets"] == {"CODECOV_TOKEN": "${{ secrets.CODECOV_TOKEN }}"}
    assert caller.get("permissions", {}).get("id-token") != "write"


def test_codecov_does_not_create_extra_required_coverage_statuses() -> None:
    """Reporting configuration must not impose a new numerical gate or spam PR comments."""
    root = pathlib.Path(__file__).resolve().parents[3]
    configuration = yaml.safe_load((root / "codecov.yml").read_text(encoding="utf-8"))
    assert configuration == {"coverage": {"status": {"project": False, "patch": False}}, "comment": False}


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
    assert steps[-3]["run"] == "python .github/scripts/check_candidate_run.py"
    assert steps[-4]["run"].startswith("python .github/scripts/verify_distributions.py")
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
    normalize = next(index for index, command in enumerate(commands) if "normalize_sdist.py" in command)
    verify = next(index for index, command in enumerate(commands) if "verify_distributions.py" in command)
    smoke = next(index for index, command in enumerate(commands) if "smoke_wheel.py" in command)
    assert normalize < verify < smoke < len(steps) - 1
    assert " -I " in commands[smoke]
    assert steps[smoke]["env"]["PYTHON_GIL"] == "0"
    assert steps[-1]["uses"].startswith("actions/upload-artifact@")


@pytest.mark.parametrize("branch", ["dev", "preprod", "release_candidate", "prod"])
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


def test_candidate_workflow_is_slim_and_publishing_authority_is_isolated(policy: ModuleType) -> None:
    """Candidate pushes stage one exact build, then run consumer probes without a duplicate source suite."""
    document = workflow("release-candidate.yml")
    assert set(document["on"]) == {"push", "workflow_dispatch"}
    assert document["on"]["push"] == {"branches": ["release_candidate"]}
    assert document["permissions"] == {"contents": "read"}
    assert document["concurrency"]["cancel-in-progress"] == "false"
    jobs = document["jobs"]
    assert jobs["build"]["uses"] == "./.github/workflows/build-distributions.yml"
    assert all(job.get("uses") != "./.github/workflows/test-runtime.yml" for job in jobs.values())
    publisher = jobs["publish"]
    assert set(publisher["needs"]) == {"authorize", "source-qualification", "build"}
    assert set(jobs["build"]["needs"]) == {"authorize", "source-qualification"}
    assert jobs["source-qualification"]["needs"] == "authorize"
    assert jobs["source-qualification"]["uses"] == "./.github/workflows/verify-source-qualification.yml"
    assert publisher["environment"]["name"] == "pypitest"
    assert publisher["permissions"] == {"contents": "read"}
    upload = next(step for step in publisher["steps"]
                  if step.get("uses", "").startswith("pypa/gh-action-pypi-publish@"))
    assert upload["with"]["repository-url"] == "https://test.pypi.org/legacy/"
    assert upload["with"]["packages-dir"] == "upload/"
    assert upload["with"]["user"] == "__token__"
    assert upload["with"]["password"] == "${{ secrets.melder_api_token }}"
    assert upload["with"]["attestations"] == "false"
    assert "skip-existing" not in upload["with"]
    assert upload["if"] == "steps.upload.outputs.upload-required == 'true'"
    credential_check = next(step for step in publisher["steps"]
                            if step.get("env", {}).get("TESTPYPI_API_TOKEN"))
    assert credential_check["env"]["TESTPYPI_API_TOKEN"] == "${{ secrets.melder_api_token }}"
    assert credential_check["if"] == upload["if"]
    assert 'if [ -z "$TESTPYPI_API_TOKEN" ]' in credential_check["run"]
    assert "exit 1" in credential_check["run"]
    assert publisher["steps"].index(credential_check) < publisher["steps"].index(upload)
    for name, job in jobs.items():
        if name != "publish":
            assert "environment" not in job
            assert job.get("permissions", {}).get("id-token") != "write"
    install = jobs["install"]
    assert set(install["strategy"]["matrix"]["os"]) == {"ubuntu-latest", "windows-latest", "macos-latest"}
    probe = next(step for step in install["steps"] if "probe-install" in step.get("run", ""))
    assert probe["env"]["PYTHON_GIL"] == "0"
    artifact = jobs["build"]["with"]["artifact-name"]
    for job in (publisher, install):
        download = next(step for step in job["steps"]
                        if step.get("uses", "").startswith("actions/download-artifact@"))
        assert download["with"]["name"] == artifact
    assert "github.run_attempt" in artifact
    ready = jobs["package-ready"]
    assert ready["if"] == "always()"
    assert set(ready["needs"]) == set(policy.CIPolicy.CANDIDATE_JOBS)
    assert ready["steps"][-2]["run"] == "python .github/scripts/ci_policy.py candidate-ready"
    assert ready["steps"][-1]["run"] == "python .github/scripts/ci_policy.py candidate-head"


def test_prod_promotion_and_publication_consume_candidate_proof() -> None:
    """Qualify the exact candidate after normal CI finishes, without weakening final publication.

    An early lookup can reject an RC still publishing while the longer test
    matrix runs. The required final job must retain API access, candidate Git
    history and the same prod-only proof after its dependency-success check.
    """
    jobs = workflow("ci.yml")["jobs"]
    command = "python .github/scripts/check_candidate_run.py"
    assert all(step.get("run") != command for step in jobs["branch-policy"]["steps"])
    final = jobs["merge-ready"]
    assert final["permissions"] == {"contents": "read", "actions": "read"}
    assert final.get("continue-on-error", "false") == "false"
    steps = final["steps"]
    checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
    depth = int(checkout["with"]["fetch-depth"])
    assert depth == 0 or depth >= 2
    aggregate = next(index for index, step in enumerate(steps)
                     if step.get("run") == "python .github/scripts/ci_policy.py merge-ready")
    proof = steps[-1]
    assert aggregate < len(steps) - 1
    assert proof["run"] == "python .github/scripts/check_candidate_run.py --wait-seconds 600"
    assert int(final["timeout-minutes"]) * 60 > 600
    assert proof["if"] == "github.base_ref == 'prod' || github.ref == 'refs/heads/prod'"
    assert proof["env"]["GITHUB_TOKEN"] == "${{ github.token }}"
    assert proof.get("continue-on-error", "false") == "false"
    release = workflow("python-publish.yml")["jobs"]["release-gate"]
    assert release["steps"][-1]["run"] == "python .github/scripts/check_candidate_run.py"
    assert release["permissions"]["actions"] == "read"


def test_only_full_ci_records_qualification_after_successful_aggregation() -> None:
    """Light promotions cannot issue a substitute full-test record."""
    final = workflow("ci.yml")["jobs"]["merge-ready"]
    steps = final["steps"]
    aggregate = next(index for index, step in enumerate(steps)
                     if step.get("run") == "python .github/scripts/ci_policy.py merge-ready")
    record = next(index for index, step in enumerate(steps)
                  if step.get("run") == "python .github/scripts/ci_qualification.py record")
    upload = next(index for index, step in enumerate(steps)
                  if step.get("uses", "").startswith("actions/upload-artifact@"))
    assert aggregate < record < upload
    assert steps[record]["if"] == steps[upload]["if"] == "needs.branch-policy.outputs.runtime-required == 'true'"
    assert steps[record]["env"] == steps[aggregate]["env"]
    assert steps[upload]["with"]["name"] == "source-qualification-${{ github.run_id }}-${{ github.run_attempt }}"
    assert steps[upload]["with"]["if-no-files-found"] == "error"
    assert steps[upload]["with"].get("archive", "true") == "true"


def test_source_proof_download_is_pinned_and_has_only_read_permissions() -> None:
    """A reusable verifier downloads one immutable artifact and checks it without publication authority."""
    document = workflow("verify-source-qualification.yml")
    assert set(document["on"]) == {"workflow_call"}
    assert document["permissions"] == {"contents": "read", "actions": "read", "pull-requests": "read"}
    job = document["jobs"]["verify"]
    assert "environment" not in job and "continue-on-error" not in job
    steps = job["steps"]
    select = next(index for index, step in enumerate(steps)
                  if step.get("run") == "python .github/scripts/ci_qualification.py select")
    download = next(index for index, step in enumerate(steps)
                    if step.get("uses", "").startswith("actions/download-artifact@"))
    assert select < download < len(steps) - 1
    inputs = steps[download]["with"]
    assert inputs["artifact-ids"] == "${{ steps.source.outputs.artifact-id }}"
    assert inputs["run-id"] == "${{ steps.source.outputs.run-id }}"
    assert inputs["repository"] == "${{ github.repository }}"
    assert inputs["github-token"] == "${{ github.token }}"
    assert inputs.get("digest-mismatch", "error") == "error"
    assert steps[-1]["run"] == (
        "python .github/scripts/ci_qualification.py verify --record source-proof/qualification.json"
    )
    for name in ("ci.yml", "release-candidate.yml"):
        caller = workflow(name)["jobs"]["source-qualification"]
        assert caller["permissions"] == document["permissions"]
