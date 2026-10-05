"""Prove safety-relevant workflow wiring using parsed YAML rather than substring matches."""

import ast
import pathlib
import json
import re
from types import ModuleType, SimpleNamespace
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
    assert aggregate["env"]["CI_GAUNTLET_REQUIRED"] == "${{ needs.branch-policy.outputs.gauntlet-required }}"
    assert jobs["branch-policy"]["outputs"]["gauntlet-required"] == "${{ steps.route.outputs.gauntlet-required }}"
    assert jobs["real-world-gauntlet"]["if"] == "needs.branch-policy.outputs.gauntlet-required == 'true'"
    assert jobs["packages"]["if"] == "needs.branch-policy.outputs.package-required == 'true'"
    for name in policy.CIPolicy.FULL_JOBS:
        assert jobs[name]["needs"] == "branch-policy"
        assert jobs[name]["if"] == "needs.branch-policy.outputs.runtime-required == 'true'"
    for name in ("branch-policy", "hygiene"):
        assert "if" not in jobs[name]
    for name in policy.CIPolicy.REQUIRED_JOBS:
        assert "continue-on-error" not in jobs[name]
    assert jobs["source-qualification"]["if"] == "needs.branch-policy.outputs.source-required == 'true'"


@pytest.mark.parametrize("name", ["build-src-assets.yml", "build-repo-assets.yml", "test-runtime.yml", "real-world-gauntlet.yml", "persistent-runtime-gauntlet.yml", "shallow-all-thread-scaling.yml", "docs.yml"])
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


def test_docs_metadata_validation_precedes_artifact_upload_and_rtd_staging() -> None:
    """Both publication paths must apply the shared metadata policy after building HTML."""
    job = workflow("docs.yml")["jobs"]["site"]
    assert job["env"]["READTHEDOCS_CANONICAL_URL"] == "https://melder.readthedocs.io/en/latest/"
    command = (
        'python docs/tools/check_seo.py docs/_build/html --base-url "$READTHEDOCS_CANONICAL_URL" '
        '--policy docs/seo.toml --json docs/_build/seo-report.json'
    )
    steps = job["steps"]
    build = next(index for index, step in enumerate(steps) if step.get("run") == "python docs/tools/build_docs.py build")
    audit = next(index for index, step in enumerate(steps) if step.get("run") == command)
    assert build < audit < len(steps) - 1
    assert "if" not in steps[audit] and "continue-on-error" not in steps[audit]
    root = pathlib.Path(__file__).resolve().parents[3]
    rtd = yaml.load((root / ".readthedocs.yaml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    html_commands = rtd["build"]["jobs"]["build"]["html"]
    assert html_commands.index("python docs/tools/build_docs.py build") < html_commands.index(command)
    assert html_commands.index(command) < html_commands.index("python docs/tools/build_docs.py stage --builder html")


@pytest.mark.parametrize(("name", "job_name"), [
    ("test-runtime.yml", "test"),
    ("real-world-gauntlet.yml", "gauntlet"),
    ("persistent-runtime-gauntlet.yml", "gauntlet"),
    ("shallow-all-thread-scaling.yml", "scaling"),
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


def test_every_python_ci_runs_is_named_by_a_manifest_or_is_the_helper_pin(runtime_matrix: ModuleType) -> None:
    """CI never chooses a Python release itself: a manifest names it, or it is the one helper release.

    Test cells and release-candidate probes take their release from the matrix built out of the test
    manifests, and the speed tests from their manifest job. Every single-version helper job requests one
    exact release that a test manifest also covers. Nothing asks for the newest patch (check-latest),
    reads a version file or allows a pre-release, so a new Python runs only once a manifest adds it
    (owner, 2026-10-05).
    """
    speed_tests = {"real-world-gauntlet.yml", "persistent-runtime-gauntlet.yml", "shallow-all-thread-scaling.yml"}
    from_manifests = {"${{ matrix.python }}": {"test-runtime.yml", "release-candidate.yml"},
                      "${{ needs.manifest.outputs.python }}": speed_tests}
    root = pathlib.Path(__file__).resolve().parents[3]
    helpers: set[str] = set()
    for path in sorted((root / ".github/workflows").glob("*.yml")):
        for job in workflow(path.name)["jobs"].values():
            for step in job.get("steps", []):
                if not step.get("uses", "").startswith("actions/setup-python@"):
                    continue
                settings = step["with"]
                assert settings.get("allow-prereleases", "false") == "false", path.name
                assert "check-latest" not in settings and "python-version-file" not in settings, path.name
                version = settings["python-version"]
                if version.startswith("${{"):
                    assert path.name in from_manifests.get(version, set()), (path.name, version)
                    continue
                runtime_matrix.stable_version(version)
                helpers.add(version)
    assert len(helpers) == 1, helpers
    tested = root / runtime_matrix.RuntimeMatrixPolicy.TESTS_DIRECTORY / f"{min(helpers)}.toml"
    assert tested.is_file(), tested


@pytest.mark.parametrize(("name", "job_name"), [
    ("real-world-gauntlet.yml", "gauntlet"),
    ("persistent-runtime-gauntlet.yml", "gauntlet"),
    ("shallow-all-thread-scaling.yml", "scaling"),
])
def test_speed_tests_take_their_python_from_the_speed_manifest(name: str, job_name: str) -> None:
    """Each speed test measures the one release its manifest names and asserts it before measuring.

    A manifest job reads .github/python/speed/ (exactly one manifest) and hands the release to the
    benchmark job, which sets it up free-threaded with no Python matrix. The provenance step asserts the
    running interpreter is that release, so replacing the manifest is the only way to move the speed tests.
    """
    jobs = workflow(name)["jobs"]
    assert set(jobs) == {"manifest", job_name}
    reader = jobs["manifest"]
    assert reader["outputs"] == {"python": "${{ steps.speed.outputs.python }}"}
    speed = next(step for step in reader["steps"] if step.get("id") == "speed")
    assert speed["run"] == "python .github/scripts/python_runtime_matrix.py speed"
    job = jobs[job_name]
    assert job["needs"] == "manifest"
    assert "python" not in job["strategy"]["matrix"]
    assert job["env"]["SPEED_PYTHON"] == "${{ needs.manifest.outputs.python }}"
    setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "${{ needs.manifest.outputs.python }}"
    assert setup["with"]["freethreaded"] == "true"
    scripts = "\n".join(step.get("run", "") for step in job["steps"])
    assert scripts.count("assert platform.python_version() == os.environ['SPEED_PYTHON']") == 1
    assert "version_info[:3]" not in scripts and "version_info[:2]" not in scripts


@pytest.mark.parametrize(("name", "job_name"), [
    ("real-world-gauntlet.yml", "gauntlet"),
    ("persistent-runtime-gauntlet.yml", "gauntlet"),
    ("shallow-all-thread-scaling.yml", "scaling"),
])
def test_speed_tests_install_the_speed_manifest_into_their_evidence(name: str, job_name: str) -> None:
    """The install step installs the speed manifest and keeps its pins, log and pip report with the results.

    The pins live only in the manifest. The step names the directory the upload step preserves, so the
    install evidence travels with the benchmark's artifact.
    """
    steps = workflow(name)["jobs"][job_name]["steps"]
    install = next(step for step in steps if step.get("name") == "Install identical pinned benchmark dependencies")
    results = steps[-1]["with"]["path"].rstrip("/")
    assert install["run"] == f"python .github/scripts/python_runtime_matrix.py speed-install --results {results}"
    assert "if" not in install and "continue-on-error" not in install


def test_supported_runtime_matrix_and_test_driver_are_shared() -> None:
    """Every discovered OS/version uses free threading and retains independent failing-test evidence."""
    jobs = workflow("test-runtime.yml")["jobs"]
    job = jobs["test"]
    assert job["needs"] == "discover"
    assert job["strategy"]["matrix"] == "${{ fromJSON(needs.discover.outputs.matrix) }}"
    assert job["strategy"]["fail-fast"] == "false"
    setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "${{ matrix.python }}"
    assert setup["with"]["architecture"] == "${{ matrix.architecture }}"
    assert setup["with"]["freethreaded"] == "true"
    assert setup["with"]["allow-prereleases"] == "false"
    runner = next(step for step in job["steps"] if "run_runtime_tests.py" in step.get("run", ""))
    assert runner["env"]["PYTHON_GIL"] == "0"
    report = job["steps"][-1]
    assert report["if"] == "always()"
    assert report["uses"].startswith("actions/upload-artifact@")
    assert report["with"]["name"] == (
        "runtime-results-${{ matrix.os }}-python-${{ matrix.python }}-${{ github.run_id }}-${{ github.run_attempt }}"
    )


@pytest.mark.parametrize(("name", "job_name", "artifact"), [
    ("test-runtime.yml", "discover", "runtime-python-matrix"),
    ("release-candidate.yml", "authorize", "candidate-python-matrix"),
])
def test_discovery_is_required_and_retains_the_selected_matrix(name: str, job_name: str, artifact: str) -> None:
    """Runtime and RC consumers share discovery policy and retain evidence before downstream execution."""
    job = workflow(name)["jobs"][job_name]
    assert "if" not in job and "continue-on-error" not in job
    assert job["outputs"]["matrix"] == "${{ steps.runtimes.outputs.matrix }}"
    selection = next(step for step in job["steps"] if step.get("id") == "runtimes")
    assert selection["run"] == "python .github/scripts/python_runtime_matrix.py discover"
    assert "continue-on-error" not in selection and "if" not in selection
    retained = job["steps"][-1]
    assert retained["uses"].startswith("actions/upload-artifact@")
    assert retained["with"]["name"] == artifact + "-${{ github.run_id }}-${{ github.run_attempt }}"
    assert retained["with"]["path"] == "reports/python-matrix.json"
    assert retained["with"]["if-no-files-found"] == "error"
    if name == "test-runtime.yml":
        setup = next(step for step in job["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
        assert "python-version-file" not in setup["with"]
        assert setup["with"]["allow-prereleases"] == "false"


def test_coverage_uses_existing_tests_and_separate_current_run_artifacts() -> None:
    """Measure in the one runtime invocation and keep each OS/version report separate from JUnit."""
    document = workflow("test-runtime.yml")
    assert set(document["jobs"]) == {"discover", "test", "coverage"}
    test = document["jobs"]["test"]
    runners = [step for step in test["steps"] if "run_runtime_tests.py" in step.get("run", "")]
    assert len(runners) == 1
    assert runners[0]["run"] == (
        "uv run --no-sync python .github/scripts/run_runtime_tests.py --report reports/runtime.xml "
        "--coverage-report reports/${{ env.COVERAGE_ARTIFACT }}.xml"
    )
    assert runners[0].get("continue-on-error", "false") == "false"
    retained = next(step for step in test["steps"] if step.get("name") == "Retain coverage report")
    assert retained["if"] == "success()"
    assert retained["continue-on-error"] == "true"
    assert test["env"]["COVERAGE_ARTIFACT"] == (
        "coverage-${{ matrix.os }}-python-${{ matrix.python }}-${{ github.run_id }}-${{ github.run_attempt }}"
    )
    assert retained["with"]["name"] == "${{ env.COVERAGE_ARTIFACT }}"
    assert retained["with"]["path"] == "reports/${{ env.COVERAGE_ARTIFACT }}.xml"
    assert retained["with"]["archive"] == "true"
    reporting = document["jobs"]["coverage"]
    download = next(step for step in reporting["steps"]
                    if step.get("uses", "").startswith("actions/download-artifact@"))
    assert download["with"] == {
        "github-token": "${{ github.token }}", "repository": "${{ github.repository }}",
        "run-id": "${{ github.run_id }}", "pattern": "coverage-*-${{ github.run_id }}-*",
        "path": "coverage-reports", "merge-multiple": "true",
    }
    complete = next(step for step in reporting["steps"] if step.get("name") == "Require the complete coverage matrix")
    assert complete["run"] == "python .github/scripts/python_runtime_matrix.py coverage"
    assert complete["env"] == {"CI_PYTHON_MATRIX": "${{ needs.discover.outputs.matrix }}"}
    assert reporting["steps"].index(download) < reporting["steps"].index(complete) < len(reporting["steps"]) - 1


def test_coverage_upload_is_nonblocking_token_only_and_skips_fork_prs() -> None:
    """Coverage cannot grant publication rights, run after failed tests, or expose tokens to forks."""
    document = workflow("test-runtime.yml")
    assert document["on"]["workflow_call"]["secrets"]["CODECOV_TOKEN"]["required"] == "false"
    job = document["jobs"]["coverage"]
    assert set(job["needs"]) == {"discover", "test"}
    assert job["continue-on-error"] == "true"
    assert job["if"] == (
        "github.event_name != 'pull_request' || "
        "github.event.pull_request.head.repo.full_name == github.repository"
    )
    assert document["permissions"] == {"contents": "read"}
    assert job["permissions"] == {"contents": "read", "actions": "read"}
    assert "environment" not in job and "env" not in job
    credential_check = job["steps"][0]
    assert credential_check["id"] == "credentials"
    assert credential_check["env"] == {"CODECOV_TOKEN": "${{ secrets.CODECOV_TOKEN }}"}
    assert 'enabled=false' in credential_check["run"] and '::warning::' in credential_check["run"]
    assert all(step["if"] == "steps.credentials.outputs.enabled == 'true'" for step in job["steps"][1:-1])
    assert job["steps"][-1]["if"].startswith("steps.credentials.outputs.enabled == 'true' && ")
    for upload in job["steps"][-2:]:
        assert upload["uses"] == "codecov/codecov-action@v7"
        assert upload["with"]["token"] == "${{ secrets.CODECOV_TOKEN }}"
        assert upload["with"]["directory"] == "selected-coverage"
        assert upload["with"]["fail_ci_if_error"] == "true"
        assert upload["with"].get("use_oidc", "false") == "false"
        assert upload["with"]["override_branch"] == "${{ github.event_name == 'release' && 'prod' || '' }}"
    selection = job["steps"][-3]
    assert selection["uses"].startswith("actions/upload-artifact@")
    assert selection["with"]["name"] == "selected-coverage-${{ github.run_id }}-${{ github.run_attempt }}"
    assert selection["with"]["path"] == "reports/coverage-selection.json"
    assert selection["with"]["if-no-files-found"] == "error"


def test_codecov_upload_retries_with_the_pypi_uploader_only_after_a_failed_first_attempt() -> None:
    """A Codecov download outage gets one PyPI-installed retry; the signed download stays the first attempt."""
    job = workflow("test-runtime.yml")["jobs"]["coverage"]
    uploads = [step for step in job["steps"] if step.get("uses", "").startswith("codecov/codecov-action@")]
    assert uploads == job["steps"][-2:]
    first, fallback = uploads
    assert first["id"] == "codecov"
    assert first["continue-on-error"] == "true"
    assert first["with"].get("use_pypi", "false") == "false"
    assert first["with"].get("skip_validation", "false") == "false"
    assert fallback["if"] == (
        "steps.credentials.outputs.enabled == 'true' && steps.codecov.outcome == 'failure'"
    )
    assert "continue-on-error" not in fallback
    assert fallback["with"].get("use_pypi") == "true"
    assert {key: value for key, value in fallback["with"].items() if key != "use_pypi"} == first["with"]


@pytest.mark.parametrize("name", ["ci.yml", "python-publish.yml"])
def test_runtime_callers_forward_only_the_coverage_secret(name: str) -> None:
    """Nested reporting receives its own token without inheriting package upload credentials."""
    caller = workflow(name)["jobs"]["tests"]
    assert caller["secrets"] == {"CODECOV_TOKEN": "${{ secrets.CODECOV_TOKEN }}"}
    assert caller["permissions"] == {"contents": "read", "actions": "read"}
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
    setup = next(step for step in steps if step.get("uses", "").startswith("actions/setup-python@"))
    assert "python-version-file" not in setup["with"]
    assert setup["with"]["freethreaded"] == "true"
    assert setup["with"]["allow-prereleases"] == "false"
    assert "uv run --no-sync python -m build --no-isolation --sdist --wheel" in commands
    assert 'uv venv --python "${{ steps.python.outputs.python-path }}"' in commands[smoke]
    assert 'uv pip install --python "$RUNNER_TEMP/melder-wheel-probe/bin/python" --no-deps dist/*.whl' in commands[smoke]


def test_locked_build_uses_the_selected_interpreter() -> None:
    """Distribution builds install the locked build group into the chosen no-GIL interpreter and refuse a stale lock."""
    steps = workflow("build-distributions.yml")["jobs"]["build"]["steps"]
    python = next(step for step in steps if step.get("uses", "").startswith("actions/setup-python@"))
    uv = next(step for step in steps if step.get("uses", "").startswith("astral-sh/setup-uv@"))
    sync = next(step for step in steps if step.get("run", "").startswith("uv sync "))
    assert python["id"] == "python" and python["with"]["freethreaded"] == "true"
    assert "cache" not in python["with"]
    assert uv["with"]["version-file"] == "pyproject.toml"
    assert uv["with"]["resolution-strategy"] == "lowest"
    assert "python-version" not in uv["with"]
    assert uv["with"]["enable-cache"] == "true"
    assert uv["with"]["cache-dependency-glob"] == "uv.lock"
    assert uv["with"]["cache-suffix"] == "build-${{ steps.python.outputs.python-version }}-${{ runner.arch }}"
    assert sync["run"] == 'uv sync --locked --only-group build --python "${{ steps.python.outputs.python-path }}"'
    assert "if" not in sync and "continue-on-error" not in sync
    assert steps.index(python) < steps.index(uv) < steps.index(sync)


def test_runtime_cells_install_exactly_their_release_manifest() -> None:
    """Each test cell installs its own manifest's pins and Melder, with no resolver and no lockfile.

    The manifest named after the cell's release is the whole dependency set: --no-deps keeps anything unpinned
    out, and the uv cache follows that manifest. The test driver then runs in the same environment.
    """
    steps = workflow("test-runtime.yml")["jobs"]["test"]["steps"]
    python = next(step for step in steps if step.get("uses", "").startswith("actions/setup-python@"))
    uv = next(step for step in steps if step.get("uses", "").startswith("astral-sh/setup-uv@"))
    install = next(step for step in steps
                   if step.get("name") == "Install exactly this release's manifest pins and Melder")
    runner = next(step for step in steps if "run_runtime_tests.py" in step.get("run", ""))
    assert python["id"] == "python" and "cache" not in python["with"]
    assert python["with"]["python-version"] == "${{ matrix.python }}"
    assert python["with"]["architecture"] == "${{ matrix.architecture }}"
    assert uv["with"]["version-file"] == "pyproject.toml"
    assert "python-version" not in uv["with"]
    assert uv["with"]["enable-cache"] == "true"
    assert uv["with"]["cache-dependency-glob"] == ".github/python/tests/${{ matrix.python }}.toml"
    assert uv["with"]["cache-suffix"] == "runtime-${{ matrix.python }}t-${{ matrix.architecture }}"
    assert install["shell"] == "bash"
    assert install["run"].splitlines() == [
        'python .github/scripts/python_runtime_matrix.py requirements --manifest '
        '".github/python/tests/${{ matrix.python }}.toml" --output reports/requirements.txt',
        'uv venv --python "${{ steps.python.outputs.python-path }}" .venv',
        "uv pip install --no-deps -r reports/requirements.txt",
        "uv pip install --no-deps -e .",
    ]
    assert "if" not in install and "continue-on-error" not in install
    assert steps.index(python) < steps.index(uv) < steps.index(install) < steps.index(runner)
    assert not any(step.get("run", "").startswith("uv sync") for step in steps)


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
    assert set(install["needs"]) == {"authorize", "build", "publish"}
    assert install["strategy"]["matrix"] == "${{ fromJSON(needs.authorize.outputs.matrix) }}"
    setup = next(step for step in install["steps"] if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "${{ matrix.python }}"
    assert setup["with"]["architecture"] == "${{ matrix.architecture }}"
    assert setup["with"]["freethreaded"] == "true"
    assert setup["with"]["allow-prereleases"] == "false"
    assert install["steps"][-1]["with"]["name"] == (
        "candidate-install-${{ matrix.os }}-python-${{ matrix.python }}-${{ github.run_id }}-${{ github.run_attempt }}"
    )
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


def test_gauntlet_reports_all_counts_and_keeps_setup_outside_gil_override() -> None:
    """Promotion CI uses its smaller iteration relay and preserves evidence from all three OSes."""
    document = workflow("real-world-gauntlet.yml")
    assert set(document["on"]) == {"workflow_call", "workflow_dispatch"}
    for event in document["on"].values():
        assert event["inputs"]["thread-counts"]["default"] == ""
        assert event["inputs"]["iteration-counts"]["default"] == "500,1000,2500,5000,10000"
    job = document["jobs"]["gauntlet"]
    assert job["strategy"]["matrix"]["os"] == ["ubuntu-24.04", "windows-2025", "macos-15-intel"]
    assert job["strategy"]["fail-fast"] == "false"
    assert "PYTHON_GIL" not in job["env"]
    assert "DI_GAUNTLET_THREADS" not in job["env"]
    assert "DI_GAUNTLET_ITERS" not in job["env"]
    assert job["env"]["REAL_WORLD_GAUNTLET_ITERATION_COUNTS"] == "${{ inputs.iteration-counts }}"
    steps = job["steps"]
    setup = next(step for step in steps if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "${{ needs.manifest.outputs.python }}"
    assert "check-latest" not in setup["with"]
    assert setup["with"]["architecture"] == "x64"
    assert setup["with"]["freethreaded"] == "true"
    install = next(index for index, step in enumerate(steps) if step.get("name") == "Install identical pinned benchmark dependencies")
    provenance = next(index for index, step in enumerate(steps) if step.get("name") == "Record source and runtime provenance")
    assert install < provenance
    assert "gauntlet._gauntlet_thread_counts()" in steps[provenance]["run"]
    measured = next(step for step in steps if step.get("name") == "Run configured real-world gauntlet")
    assert measured["env"]["PYTHON_GIL"] == "0"
    assert int(measured["timeout-minutes"]) < int(job["timeout-minutes"])
    assert "GITHUB_STEP_SUMMARY" in measured["run"]
    assert "expected_pairs" in measured["run"]
    assert "assert all(verified.values())" in measured["run"]
    retained = steps[-1]
    assert retained["if"] == "always()"
    assert retained["with"]["path"] == "gauntlet-results/"
    assert retained["with"]["retention-days"] == "30"
    caller = workflow("ci.yml")["jobs"]["real-world-gauntlet"]
    assert caller["uses"] == "./.github/workflows/real-world-gauntlet.yml"
    assert "secrets" not in caller


def test_gauntlet_inline_python_parses_after_yaml_indentation() -> None:
    """Every Python step is valid executable syntax after YAML removes its indentation."""
    import ast
    for step in workflow("real-world-gauntlet.yml")["jobs"]["gauntlet"]["steps"]:
        if step.get("shell") == "python":
            ast.parse(step["run"], filename=step["name"])


def test_persistent_gauntlet_runs_in_parallel_on_independent_promotion_runners() -> None:
    """Neither benchmark waits for the other; each owns its OS jobs and result artifacts."""
    jobs = workflow("ci.yml")["jobs"]
    for name in ("real-world-gauntlet", "persistent-runtime-gauntlet", "shallow-all-thread-scaling"):
        assert jobs[name]["needs"] == "branch-policy"
        assert jobs[name]["if"] == "needs.branch-policy.outputs.gauntlet-required == 'true'"
        assert name in jobs["merge-ready"]["needs"]
    assert jobs["persistent-runtime-gauntlet"]["uses"] == "./.github/workflows/persistent-runtime-gauntlet.yml"
    document = workflow("persistent-runtime-gauntlet.yml")
    for event in document["on"].values():
        assert event["inputs"]["duration-seconds"]["default"] == "60,180,300"
        assert event["inputs"]["thread-counts"]["default"] == "3,5"
    job = document["jobs"]["gauntlet"]
    assert job["strategy"]["matrix"]["os"] == ["ubuntu-24.04", "windows-2025", "macos-15-intel"]
    assert job["env"]["PERSISTENT_SERIES_SECONDS"] == "${{ inputs.duration-seconds }}"
    assert job["env"]["PERSISTENT_SERIES_THREADS"] == "${{ inputs.thread-counts }}"
    assert job["env"]["PERSISTENT_SERIES_OUTPUT_DIR"] == "${{ github.workspace }}/persistent-gauntlet-results"
    assert "PYTHON_GIL" not in job["env"]
    measured = next(step for step in job["steps"] if step.get("name") == "Run persistent duration and thread series")
    assert measured["env"]["PYTHON_GIL"] == "0"
    assert int(measured["timeout-minutes"]) < int(job["timeout-minutes"])
    assert "test_persistent_runtime_gauntlet_series.py" in measured["run"]
    assert "observed == cells" in measured["run"] and "assert valid" in measured["run"]
    assert "GITHUB_STEP_SUMMARY" in measured["run"]
    upload = job["steps"][-1]
    assert upload["if"] == "always()"
    assert upload["with"]["path"] == "persistent-gauntlet-results/"
    assert upload["with"]["name"].startswith("persistent-gauntlet-")
    for step in job["steps"]:
        if step.get("shell") == "python":
            compile(step["run"], step["name"], "exec")


def test_shallow_thread_scaling_measures_each_library_in_its_own_gil_off_process() -> None:
    """The scaling benchmark is a parallel promotion job that isolates every library in a fresh interpreter."""
    caller = workflow("ci.yml")["jobs"]["shallow-all-thread-scaling"]
    assert caller["uses"] == "./.github/workflows/shallow-all-thread-scaling.yml"
    assert "secrets" not in caller
    document = workflow("shallow-all-thread-scaling.yml")
    for event in document["on"].values():
        assert event["inputs"]["thread-counts"]["default"] == "1,2,3,4,5"
        assert event["inputs"]["duration-seconds"]["default"] == "15"
    job = document["jobs"]["scaling"]
    assert job["strategy"]["matrix"]["os"] == ["ubuntu-24.04", "windows-2025", "macos-15-intel"]
    assert job["strategy"]["fail-fast"] == "false"
    assert job["env"]["DI_THREAD_COUNTS"] == "${{ inputs.thread-counts }}"
    assert job["env"]["DI_DURATION_S"] == "${{ inputs.duration-seconds }}"
    assert "PYTHON_GIL" not in job["env"]
    assert "DI_LIBS" not in job["env"]
    steps = job["steps"]
    setup = next(step for step in steps if step.get("uses", "").startswith("actions/setup-python@"))
    assert setup["with"]["python-version"] == "${{ needs.manifest.outputs.python }}"
    assert "check-latest" not in setup["with"]
    assert setup["with"]["architecture"] == "x64"
    assert setup["with"]["freethreaded"] == "true"
    names = [step.get("name") for step in steps]
    install = names.index("Install identical pinned benchmark dependencies")
    provenance = names.index("Record thread scaling provenance")
    measured = names.index("Run thread scaling for each library in its own process")
    assert install < provenance < measured
    assert steps[provenance]["env"]["PYTHON_GIL"] == "0"
    assert steps[measured]["env"]["PYTHON_GIL"] == "0"
    assert int(steps[measured]["timeout-minutes"]) < int(job["timeout-minutes"])
    script = steps[measured]["run"]
    assert "DI_LIBS=lib" in script and "'-X', 'gil=0'" in script
    assert "test_shallow_all_thread_scaling.py" in script
    assert "GITHUB_STEP_SUMMARY" in script and "assert valid" in script
    retained = steps[-1]
    assert retained["if"] == "always()"
    assert retained["with"]["path"] == "thread-scaling-results/"
    assert retained["with"]["name"].startswith("shallow-thread-scaling-")
    assert retained["with"]["retention-days"] == "30"
    for step in steps:
        if step.get("shell") == "python":
            compile(step["run"], step["name"], "exec")


def test_shallow_thread_scaling_parser_accepts_the_lines_the_benchmark_prints() -> None:
    """Render the benchmark's own print expressions and require the workflow's parser to read them back."""
    root = pathlib.Path(__file__).resolve().parents[3]
    benchmark = ast.parse((root / "benchmarks/testing_other_di/test_shallow_all_thread_scaling.py")
                          .read_text(encoding="utf-8"))
    printed = sorted((call for call in ast.walk(benchmark)
                      if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "print"),
                     key=lambda call: call.lineno)
    assert len(printed) == 2, "The workflow parses exactly one config line and one result line per thread count."
    namespace = {
        "lib": "dependency-injector",
        "_gil_status": lambda: "disabled",
        "cfg": SimpleNamespace(duration_s=15.0, thread_counts=(1, 2, 3, 4, 5),
                               graph_pattern="random", root_pattern="alternating"),
        "graphs": [SimpleNamespace(name="solo"), SimpleNamespace(name="deep")],
        "thread_count": 4,
        "result": SimpleNamespace(elapsed_s=15.004, steps=1234567, steps_per_s=82271.1, spellspaces=61728, errors=0),
        "speedup": 3.2,
        "efficiency": 0.8,
        "per_graph_summary": "solo=1, deep=2",
    }
    config_text, result_text = (eval(compile(ast.Expression(call.args[0]), "<benchmark print>", "eval"), namespace)
                                for call in printed)
    measured = next(step for step in workflow("shallow-all-thread-scaling.yml")["jobs"]["scaling"]["steps"]
                    if step.get("name") == "Run thread scaling for each library in its own process")
    patterns = {node.targets[0].id: ast.literal_eval(node.value) for node in ast.parse(measured["run"]).body
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in ("config_line", "result_line")}
    assert set(patterns) == {"config_line", "result_line"}
    node_id = ("benchmarks/testing_other_di/test_shallow_all_thread_scaling.py::"
               "test_threaded_shallow_all_graph_mix_scaling[dependency-injector] ")

    def pattern(name: str, lib: str) -> str:
        """Specialize one workflow regular expression for a library, as the measured step does."""
        return patterns[name].replace("{lib}", re.escape(lib))

    # With -s -v pytest prints the first benchmark line directly after the node id.
    assert re.findall(pattern("config_line", "dependency-injector"), node_id + config_text) == [
        ("disabled", "15.00", "(1, 2, 3, 4, 5)")]
    assert re.findall(pattern("result_line", "dependency-injector"), result_text) == [
        ("4", "15.00", "1234567", "82,271", "3.20", "80.0", "61728", "0")]
    assert not re.findall(pattern("config_line", "melder"), node_id + config_text)
    assert not re.findall(pattern("result_line", "melder"), result_text)


def test_ci_guide_names_every_workflow_script_and_ruleset() -> None:
    """The agent CI guide in .github/ci_cd/ covers every CI file, so a new one cannot arrive undocumented.

    Agents learn from that folder what each workflow, script and ruleset is for and how to extend it (owner,
    2026-10-05). A file counts as covered when its name appears in backticks on one of the guide's pages.
    """
    root = pathlib.Path(__file__).resolve().parents[3]
    guide = "\n".join(page.read_text(encoding="utf-8") for page in sorted((root / ".github/ci_cd").glob("*.md")))
    files = [*sorted((root / ".github/workflows").glob("*.yml")), *sorted((root / ".github/scripts").glob("*.py")),
             *sorted((root / ".github/rulesets").glob("*.json"))]
    missing = [path.name for path in files if f"`{path.name}`" not in guide]
    assert not missing, f"Describe these in .github/ci_cd/: {missing}"


def test_ci_guide_pages_are_linked_and_their_links_resolve() -> None:
    """The guide's README links every page, and every relative link in the guide names an existing file."""
    root = pathlib.Path(__file__).resolve().parents[3]
    pages = sorted((root / ".github/ci_cd").glob("*.md"))
    readme = (root / ".github/ci_cd/README.md").read_text(encoding="utf-8")
    assert [page.name for page in pages if page.name != "README.md" and f"]({page.name})" not in readme] == []
    broken = [f"{page.name} -> {target}" for page in pages
              for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", page.read_text(encoding="utf-8"))
              if "://" not in target and not (page.parent / target).resolve().is_file()]
    assert broken == []
