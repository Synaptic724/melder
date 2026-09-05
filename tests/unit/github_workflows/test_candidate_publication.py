"""Prove exact-source qualification, immutable uploads, and isolated TestPyPI installation."""

import hashlib
import io
import json
import pathlib
import subprocess
import urllib.error
from collections.abc import Sequence
from types import ModuleType

import pytest


def qualified_run(**changes: object) -> dict[str, object]:
    """Describe one successful exact-SHA branch workflow with explicit repository identity."""
    return {"id": 101, "run_number": 4, "run_attempt": 1,
            "repository": {"full_name": "owner/repo"}, "head_repository": {"full_name": "owner/repo"},
            "head_sha": "a" * 40, "head_branch": "release_candidate", "event": "push",
            "path": ".github/workflows/release-candidate.yml", "status": "completed",
            "conclusion": "success", **changes}


def candidate_pr(**head_changes: object) -> dict[str, object]:
    """Describe the legitimate same-repository candidate-to-prod promotion route."""
    return {"pull_request": {
        "head": {"ref": "release_candidate", "sha": "a" * 40,
                 "repo": {"full_name": "owner/repo"}, **head_changes},
        "base": {"ref": "prod", "repo": {"full_name": "owner/repo"}},
    }}


def test_pr_and_prod_merge_identify_the_same_candidate(candidate_proof: ModuleType) -> None:
    """PR merge testing and the eventual production merge must refer to the same source head."""
    assert candidate_proof.candidate_source("pull_request", candidate_pr(), "owner/repo", []) == "a" * 40
    assert candidate_proof.candidate_source("release", {}, "owner/repo",
                                            ["c" * 40, "b" * 40, "a" * 40]) == "a" * 40


@pytest.mark.parametrize("head", [
    {"ref": "preprod"}, {"repo": {"full_name": "fork/repo"}}, {"sha": "short"},
])
def test_candidate_provenance_refuses_forged_heads(candidate_proof: ModuleType, head: dict[str, object]) -> None:
    """A familiar branch name in a fork or an unapproved source cannot stand in for the candidate."""
    with pytest.raises(ValueError):
        candidate_proof.candidate_source("pull_request", candidate_pr(**head), "owner/repo", [])


@pytest.mark.parametrize("parents", [[], ["a" * 40], ["a" * 40, "b" * 40], ["short"] * 3, ["a" * 40] * 4])
def test_direct_squashed_or_ambiguous_prod_history_is_refused(candidate_proof: ModuleType,
                                                            parents: list[str]) -> None:
    """Production history must preserve one explicit candidate merge parent."""
    with pytest.raises(ValueError):
        candidate_proof.candidate_source("release", {}, "owner/repo", parents)


def test_latest_candidate_run_must_pass(candidate_proof: ModuleType) -> None:
    """A newer failed/pending run must not silently fall back to an older green result."""
    green = qualified_run()
    assert candidate_proof.require_qualified_run({"workflow_runs": [green]}, "owner/repo", "a" * 40) == green
    for state in ({"status": "in_progress", "conclusion": None}, {"conclusion": "failure"}):
        with pytest.raises(ValueError, match="unsuccessful"):
            candidate_proof.require_qualified_run(
                {"workflow_runs": [green, qualified_run(run_number=5, **state)]}, "owner/repo", "a" * 40,
            )


@pytest.mark.parametrize("change", [
    {"head_sha": "b" * 40}, {"head_branch": "preprod"}, {"event": "pull_request"},
    {"path": ".github/workflows/ci.yml"}, {"repository": {"full_name": "other/repo"}},
    {"head_repository": {"full_name": "fork/repo"}}, {"status": "queued"},
    {"conclusion": "skipped"}, {"run_attempt": 0}, {"run_attempt": True},
    {"id": "101"}, {"run_number": -1},
])
def test_wrong_or_incomplete_hosted_evidence_blocks_prod(candidate_proof: ModuleType,
                                                        change: dict[str, object]) -> None:
    """Require trusted workflow, source, event, conclusion, and attempt without coercive defaults."""
    with pytest.raises(ValueError):
        candidate_proof.require_qualified_run({"workflow_runs": [qualified_run(**change)]}, "owner/repo", "a" * 40)


@pytest.mark.parametrize("payload", [{}, {"workflow_runs": []}, {"workflow_runs": None},
                                      {"workflow_runs": [qualified_run(), qualified_run()]}])
def test_missing_or_ambiguous_workflow_runs_fail_closed(candidate_proof: ModuleType,
                                                       payload: dict[str, object]) -> None:
    """Absent qualification and duplicate run identity are refusals, never implicit success."""
    with pytest.raises(ValueError):
        candidate_proof.require_qualified_run(payload, "owner/repo", "a" * 40)


@pytest.mark.parametrize(("tree_matches", "version"), [(False, "0.2.4"), (True, "0.2.4rc1")])
def test_prod_rejects_different_tree_or_prerelease_before_querying_runs(candidate_proof: ModuleType,
                                                                     monkeypatch: pytest.MonkeyPatch,
                                                                     tree_matches: bool, version: str) -> None:
    """Qualification of one tree or an RC version cannot authorize different final contents."""
    def git_read(arguments: Sequence[str]) -> str:
        """Supply only the relevant Git boundary responses, with an optional tree mismatch."""
        if arguments[0] == "rev-list":
            return f"{'c' * 40} {'b' * 40} {'a' * 40}"
        return "tree-a" if tree_matches or arguments[-1] == "HEAD^{tree}" else "tree-b"

    def unexpected_query(*arguments: object) -> None:
        """A wrong tree/version should fail before consuming any remote qualification."""
        raise AssertionError("API must not be queried for an invalid production candidate")

    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "release")
    monkeypatch.setattr(candidate_proof, "read_event", lambda: {})
    monkeypatch.setattr(candidate_proof, "git_output", git_read)
    monkeypatch.setattr(candidate_proof, "assignment", lambda *arguments: version)
    monkeypatch.setattr(candidate_proof, "github_runs", unexpected_query)
    with pytest.raises(ValueError, match="tree differs|final package version"):
        candidate_proof.main()


def test_identical_and_partial_index_uploads_are_safe(candidate: ModuleType) -> None:
    """Retries can reuse identical bytes and upload only missing files, without skip-existing."""
    wheel = {"sha256": "a" * 64, "size": 100}
    source = {"sha256": "b" * 64, "size": 200}
    expected = {"melder-0.2.4-py3-none-any.whl": wheel, "melder-0.2.4.tar.gz": source}
    assert candidate.missing_files(expected, {}) == sorted(expected)
    assert candidate.missing_files(expected, expected) == []
    assert candidate.missing_files(expected, {"melder-0.2.4.tar.gz": source}) == ["melder-0.2.4-py3-none-any.whl"]


@pytest.mark.parametrize("remote", [
    {"package.whl": {"sha256": "b" * 64, "size": 100}},
    {"package.whl": {"sha256": "a" * 64, "size": 101}},
    {"other.whl": {"sha256": "a" * 64, "size": 100}},
])
def test_changed_or_extra_index_files_require_a_new_version(candidate: ModuleType,
                                                          remote: dict[str, object]) -> None:
    """A name collision must never turn into a green retry of different package bytes."""
    with pytest.raises(ValueError, match="new candidate version"):
        candidate.missing_files({"package.whl": {"sha256": "a" * 64, "size": 100}}, remote)


def test_remote_file_reads_close_stream_and_preserve_exact_identity(candidate: ModuleType,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful API response provides validated digest/size evidence and leaves no open stream."""
    response = io.BytesIO(json.dumps({"info": {"version": "0.2.4rc1"}, "urls": [{
        "filename": "melder.whl", "digests": {"sha256": "a" * 64}, "size": 100,
    }]}).encode())

    def get_release(request: object, timeout: int) -> io.BytesIO:
        """Assert the fixed public index boundary without any live network request."""
        assert request.full_url == "https://test.pypi.org/pypi/melder/0.2.4rc1/json"
        assert request.get_header("Authorization") is None
        assert timeout == 30
        return response

    monkeypatch.setattr(candidate.urllib.request, "urlopen", get_release)
    assert candidate.remote_files("0.2.4rc1") == {"melder.whl": {"sha256": "a" * 64, "size": 100}}
    assert response.closed


@pytest.mark.parametrize("status", [404, 403, 500])
def test_only_index_404_means_no_previous_upload(candidate: ModuleType, monkeypatch: pytest.MonkeyPatch,
                                                status: int) -> None:
    """Authorization/network/service failures must not be mistaken for an empty package version."""
    def failure(*arguments: object, **keywords: object) -> None:
        """Raise a representative HTTP boundary error without opening a network connection."""
        raise urllib.error.HTTPError("https://test.pypi.org/", status, "test failure", {}, None)

    monkeypatch.setattr(candidate.urllib.request, "urlopen", failure)
    if status == 404:
        assert candidate.remote_files("0.2.4") == {}
    else:
        with pytest.raises(urllib.error.HTTPError):
            candidate.remote_files("0.2.4")


@pytest.mark.parametrize("file", [
    {"filename": "package.whl", "digests": {"sha256": "bad"}, "size": 100},
    {"filename": "package.whl", "digests": {"sha256": "a" * 64}, "size": True},
    {"filename": "package.whl", "digests": {}, "size": 100},
])
def test_malformed_index_identity_is_refused(candidate: ModuleType, monkeypatch: pytest.MonkeyPatch,
                                           file: dict[str, object]) -> None:
    """Malformed metadata cannot authorize upload reuse or partial publication."""
    response = io.BytesIO(json.dumps({"info": {"version": "0.2.4"}, "urls": [file]}).encode())
    monkeypatch.setattr(candidate.urllib.request, "urlopen", lambda *args, **kwargs: response)
    with pytest.raises(ValueError):
        candidate.remote_files("0.2.4")


def test_prepare_upload_copies_only_absent_verified_files(candidate: ModuleType, tmp_path: pathlib.Path,
                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    """An identical existing wheel is retained; a missing sdist is staged for the upload action."""
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "melder.whl").write_bytes(b"wheel")
    (dist / "melder.tar.gz").write_bytes(b"source")
    files = {path.name: candidate.file_identity(path) for path in dist.iterdir()}
    monkeypatch.setattr(candidate, "package_version", lambda: "0.2.4")
    monkeypatch.setattr(candidate, "verified_files", lambda *args: files)
    monkeypatch.setattr(candidate, "remote_files", lambda version: {"melder.whl": files["melder.whl"]})
    monkeypatch.setattr(candidate, "git_output", lambda arguments: "a" * 40)
    upload = tmp_path / "upload"
    report = tmp_path / "report.json"
    assert candidate.prepare_upload(dist, upload, report) is True
    assert [path.name for path in upload.iterdir()] == ["melder.tar.gz"]
    assert (upload / "melder.tar.gz").read_bytes() == b"source"
    assert json.loads(report.read_text())["files"] == files


def test_index_download_pins_version_hash_and_uses_no_fallback(candidate: ModuleType, tmp_path: pathlib.Path,
                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Index propagation gets a bounded retry, then the returned bytes must match the selected wheel."""
    payload = b"verified-wheel"
    identity = {"sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}
    calls: list[list[str]] = []

    def download(command: list[str], check: bool, cwd: pathlib.Path) -> None:
        """Model pip's process boundary and a transient first-attempt index miss."""
        calls.append(command)
        assert check
        assert "--isolated" in command and "--no-deps" in command and "--require-hashes" in command
        assert "--extra-index-url" not in command
        assert command[command.index("--index-url") + 1] == "https://test.pypi.org/simple/"
        assert (cwd / "requirement.txt").read_text() == f"melder==0.2.4rc1 --hash=sha256:{identity['sha256']}\n"
        if len(calls) == 1:
            raise subprocess.CalledProcessError(1, command)
        (cwd / "downloads/melder.whl").write_bytes(payload)

    monkeypatch.setattr(candidate.subprocess, "run", download)
    monkeypatch.setattr(candidate.time, "sleep", lambda seconds: None)
    wheel = candidate.download_wheel(tmp_path, "0.2.4rc1", "melder.whl", identity)
    assert wheel.read_bytes() == payload
    assert len(calls) == 2


def test_download_retries_are_bounded(candidate: ModuleType, tmp_path: pathlib.Path,
                                     monkeypatch: pytest.MonkeyPatch) -> None:
    """A permanently missing index release never becomes an infinite or successful retry."""
    calls: list[int] = []

    def failure(command: list[str], **keywords: object) -> None:
        """Fail the pip boundary deterministically on every attempt."""
        calls.append(1)
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(candidate.subprocess, "run", failure)
    monkeypatch.setattr(candidate.time, "sleep", lambda seconds: None)
    with pytest.raises(subprocess.CalledProcessError):
        candidate.download_wheel(tmp_path, "0.2.4", "melder.whl", {"sha256": "a" * 64, "size": 100})
    assert len(calls) == candidate.TestIndexPolicy.DOWNLOAD_ATTEMPTS


def test_altered_download_is_refused_even_if_pip_reports_success(candidate: ModuleType, tmp_path: pathlib.Path,
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    """The final file check independently binds the downloaded bytes to the tested candidate."""
    def wrong_bytes(command: list[str], check: bool, cwd: pathlib.Path) -> None:
        """Model a wrong external download without executing pip."""
        (cwd / "downloads/melder.whl").write_bytes(b"wrong")

    monkeypatch.setattr(candidate.subprocess, "run", wrong_bytes)
    with pytest.raises(ValueError, match="differs"):
        candidate.download_wheel(tmp_path, "0.2.4", "melder.whl", {"sha256": "a" * 64, "size": 100})
