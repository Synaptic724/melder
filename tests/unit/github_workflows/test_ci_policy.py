"""Behavioral regression tests for branch routes, required results, and release authorization."""

import json
import pathlib
from types import ModuleType

import pytest


def result_map() -> dict[str, object]:
    """Build the complete, successful dependency report emitted by the CI workflow."""
    return {name: {"result": "success"} for name in
            ("branch-policy", "hygiene", "source-assets", "repo-assets", "tests", "packages")}


def pr_event(base: str = "dev", head: str = "feature/example",
             head_repository: str = "owner/repo") -> dict[str, object]:
    """Build a minimal GitHub PR event with explicit head/base repository identities."""
    return {"pull_request": {
        "base": {"ref": base, "repo": {"full_name": "owner/repo"}},
        "head": {"ref": head, "repo": {"full_name": head_repository}},
    }}


def final_release() -> dict[str, object]:
    """Build a published, non-draft, non-prerelease event for a fixed tag."""
    return {"action": "published", "release": {
        "tag_name": "v0.3.0", "draft": False, "prerelease": False,
    }}


@pytest.mark.parametrize(("base", "head", "repository", "packages"), [
    ("dev", "feature/example", "owner/repo", False),
    ("dev", "feature/example", "fork/repo", False),
    ("dev", "dev", "fork/repo", False),
    ("dev", "preprod", "owner/repo", False),
    ("dev", "prod", "owner/repo", False),
    ("preprod", "dev", "owner/repo", True),
    ("prod", "preprod", "owner/repo", True),
])
def test_valid_routes_choose_the_package_requirement(policy: ModuleType, base: str,
                                                     head: str, repository: str,
                                                     packages: bool) -> None:
    """Allow contributions and authentic staged promotion while classifying package gates."""
    assert policy.validate_route(base, head, repository, "owner/repo") is packages


@pytest.mark.parametrize(("base", "head", "repository"), [
    ("main", "feature/example", "owner/repo"),
    ("dev", "dev", "owner/repo"),
    ("dev", "preprod", "fork/repo"),
    ("preprod", "feature/example", "owner/repo"),
    ("preprod", "dev", "fork/repo"),
    ("prod", "dev", "owner/repo"),
    ("prod", "preprod", "fork/repo"),
    ("prod", "release/arbitrary", "owner/repo"),
    ("dev", "", "owner/repo"),
])
def test_invalid_or_forged_routes_are_refused(policy: ModuleType, base: str,
                                             head: str, repository: str) -> None:
    """Refuse stage skipping, forged fork promotions, ambiguous bases, and self-PRs."""
    with pytest.raises(ValueError):
        policy.validate_route(base, head, repository, "owner/repo")


def test_pr_payload_drives_route_and_rejects_missing_identity(policy: ModuleType) -> None:
    """Require complete event evidence instead of guessing repository or base identity."""
    assert policy.package_required("pull_request", pr_event("preprod", "dev"),
                                   "refs/pull/1/merge", "owner/repo") is True
    for event in ({}, {"pull_request": None}, {"pull_request": {"head": {}}}):
        with pytest.raises(ValueError):
            policy.package_required("pull_request", event, "refs/pull/1/merge", "owner/repo")
    with pytest.raises(ValueError, match="base repository"):
        policy.package_required("pull_request", pr_event(), "refs/pull/1/merge", "different/repo")


@pytest.mark.parametrize(("event", "ref", "packages"), [
    ("push", "refs/heads/dev", False),
    ("push", "refs/heads/preprod", True),
    ("workflow_dispatch", "refs/heads/prod", True),
])
def test_permanent_refs_are_classified(policy: ModuleType, event: str,
                                      ref: str, packages: bool) -> None:
    """Validate dev pushes and promotion/manual revisions against their proper gates."""
    assert policy.package_required(event, {}, ref, "owner/repo") is packages


@pytest.mark.parametrize(("event", "ref"), [
    ("release", "refs/tags/v0.3.0"), ("push", "refs/heads/random"),
    ("workflow_dispatch", "refs/tags/dev"), ("pull_request_target", "refs/heads/dev"),
])
def test_unsupported_ci_events_fail_closed(policy: ModuleType, event: str, ref: str) -> None:
    """Prevent unsupported event contexts from accidentally obtaining a merge-ready result."""
    with pytest.raises(ValueError):
        policy.package_required(event, {}, ref, "owner/repo")


@pytest.mark.parametrize("job", ["branch-policy", "hygiene", "source-assets", "repo-assets", "tests"])
@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped", "timed_out", "neutral", None])
def test_any_unsuccessful_mandatory_job_blocks_merge(policy: ModuleType, job: str,
                                                    conclusion: object) -> None:
    """A skipped/cancelled dependency must not count as successful mandatory CI."""
    results = result_map()
    results[job] = {"result": conclusion}
    with pytest.raises(ValueError, match="Required CI did not succeed"):
        policy.require_success(results, False)


def test_package_skip_is_allowed_only_for_dev(policy: ModuleType) -> None:
    """Accept the planned dev-only package omission, but block the same omission on promotion."""
    results = result_map()
    policy.require_success(results, True)
    results["packages"] = {"result": "skipped"}
    policy.require_success(results, False)
    with pytest.raises(ValueError, match="packages"):
        policy.require_success(results, True)
    results["packages"] = {"result": "failure"}
    with pytest.raises(ValueError, match="packages"):
        policy.require_success(results, False)


@pytest.mark.parametrize("job", ["branch-policy", "hygiene", "source-assets", "repo-assets", "tests", "packages"])
def test_missing_dependency_evidence_never_passes(policy: ModuleType, job: str) -> None:
    """Deleting a failed job from the report must not conceal its absence."""
    results = result_map()
    del results[job]
    with pytest.raises(ValueError, match="Incomplete"):
        policy.require_success(results, False)


def test_malformed_or_unknown_dependency_reports_are_refused(policy: ModuleType) -> None:
    """Require intentional policy updates when the workflow's dependency set changes."""
    results = result_map()
    results["unexpected"] = {"result": "success"}
    with pytest.raises(ValueError, match="unexpected"):
        policy.require_success(results, False)
    results = result_map()
    results["tests"] = "success"
    with pytest.raises(ValueError, match="JSON object"):
        policy.require_success(results, False)


def test_case_collision_reports_are_deterministic(policy: ModuleType) -> None:
    """Expose names that can coexist on Linux but overwrite one another on Windows."""
    assert policy.case_collisions(["src/A.py", "src/a.py", "docs/readme.md"]) == [
        ["src/A.py", "src/a.py"],
    ]
    assert policy.case_collisions(["src/a.py", "src/b.py"]) == []


def test_release_and_manual_prod_accept_equal_commit_ids(policy: ModuleType) -> None:
    """Preserve final published releases and explicit manual-prod publication."""
    sha = "a" * 40
    policy.validate_release("release", "refs/tags/v0.3.0", final_release(), sha, sha, sha)
    policy.validate_release("workflow_dispatch", "refs/heads/prod", {}, sha, sha, sha)


@pytest.mark.parametrize("position", [0, 1, 2])
def test_stale_event_checkout_or_prod_prevents_publication(policy: ModuleType, position: int) -> None:
    """A prod movement during validation or an alternate checkout must refuse upload."""
    shas = ["a" * 40] * 3
    shas[position] = "b" * 40
    with pytest.raises(ValueError, match="current prod HEAD"):
        policy.validate_release("workflow_dispatch", "refs/heads/prod", {}, *shas)


@pytest.mark.parametrize(("event", "ref"), [
    ("push", "refs/heads/prod"), ("pull_request", "refs/pull/1/merge"),
    ("workflow_dispatch", "refs/heads/dev"), ("release", "refs/tags/wrong"),
])
def test_unapproved_publication_contexts_are_refused(policy: ModuleType, event: str, ref: str) -> None:
    """Neither ordinary CI nor a mismatched release tag can authorize publication."""
    with pytest.raises(ValueError):
        policy.validate_release(event, ref, final_release(), *("a" * 40,) * 3)


@pytest.mark.parametrize("field", ["draft", "prerelease"])
def test_draft_or_prerelease_is_not_final_publication(policy: ModuleType, field: str) -> None:
    """Publishing an RC in GitHub must not silently upload a final release package."""
    event = {"action": "published", "release": {
        "tag_name": "v0.3.0", "draft": False, "prerelease": False, field: True,
    }}
    with pytest.raises(ValueError, match="Draft/prerelease"):
        policy.validate_release("release", "refs/tags/v0.3.0", event, *("a" * 40,) * 3)


def test_abbreviated_sha_is_not_release_identity(policy: ModuleType) -> None:
    """Require resolved immutable identity even when three abbreviated values happen to match."""
    with pytest.raises(ValueError, match="full, resolved"):
        policy.validate_release("workflow_dispatch", "refs/heads/prod", {}, "abc", "abc", "abc")


def test_merge_cli_propagates_failure_and_missing_stage(policy: ModuleType,
                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    """Return a failing process result for skipped tests or missing branch-policy outputs."""
    monkeypatch.setenv("CI_JOB_RESULTS", json.dumps(result_map()))
    monkeypatch.setenv("CI_PACKAGE_REQUIRED", "false")
    assert policy.main(["merge-ready"]) == 0
    failed = result_map()
    failed["tests"] = {"result": "skipped"}
    monkeypatch.setenv("CI_JOB_RESULTS", json.dumps(failed))
    assert policy.main(["merge-ready"]) == 1
    monkeypatch.delenv("CI_PACKAGE_REQUIRED")
    assert policy.main(["merge-ready"]) == 1


def test_branch_cli_writes_the_actual_package_requirement(policy: ModuleType,
                                                         tmp_path: pathlib.Path,
                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    """Emit a GitHub output only after the promotion payload passes route validation."""
    event = tmp_path / "event.json"
    output = tmp_path / "output.txt"
    event.write_text(json.dumps(pr_event("preprod", "dev")), encoding="utf-8")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_REF", "refs/pull/1/merge")
    assert policy.main(["branch"]) == 0
    assert output.read_text(encoding="utf-8") == "package-required=true\n"


@pytest.mark.parametrize(("version", "supported", "gil", "valid"), [
    ((3, 14), 1, False, True), ((3, 15), 1, False, True),
    ((3, 13), 1, False, False), ((3, 14), 0, False, False),
    ((3, 14), None, False, False), ((3, 14), 1, True, False),
])
def test_runtime_guard_checks_actual_free_threading(runtime: ModuleType, version: tuple[int, int],
                                                   supported: object, gil: bool, valid: bool) -> None:
    """Checking the Python version alone must not admit a GIL-enabled runtime."""
    if valid:
        runtime.require_free_threading(version, supported, gil)
    else:
        with pytest.raises(RuntimeError, match="GIL disabled"):
            runtime.require_free_threading(version, supported, gil)


def test_test_driver_preserves_tiers_failure_code_and_runtime_checks(runtime: ModuleType,
                                                                  tmp_path: pathlib.Path,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """The shared driver must propagate pytest failure and verify this process on both sides."""
    calls: list[object] = []

    def fake_pytest(arguments: list[str]) -> int:
        """Record the invocation boundary without recursively running pytest."""
        calls.append(arguments)
        return 1

    def runtime_check(*arguments: object) -> None:
        """Record each before/after runtime check; its predicate has separate behavioral tests."""
        calls.append("runtime-check")

    monkeypatch.setattr(pytest, "main", fake_pytest)
    monkeypatch.setattr(runtime, "require_free_threading", runtime_check)
    report = tmp_path / "reports/runtime.xml"
    assert runtime.main(["--report", str(report)]) == 1
    assert calls == ["runtime-check", [
        "-q", "tests/unit", "tests/component", "tests/integration", f"--junitxml={report}",
    ], "runtime-check"]
