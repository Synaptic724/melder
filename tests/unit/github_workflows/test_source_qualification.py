"""Exercise full-CI evidence across distinct merge SHAs, source changes, and stale GitHub state."""

import io
import json
import os
import pathlib
import urllib.request
from collections.abc import Mapping, Sequence
from types import ModuleType
from typing import TypedDict

import pytest


class SourceApiData(TypedDict):
    """Hold per-test JSON responses and the observed external request sequence."""

    commits: dict[str, dict[str, object]]
    pulls: dict[str, list[dict[str, object]]]
    manual: dict[str, list[dict[str, object]]]
    runs: list[dict[str, object]]
    artifacts: list[dict[str, object]]
    calls: list[str]


class GitState(TypedDict):
    """Describe the independent Git-process answers used by a record-producing CI job."""

    sha: str
    tree: str
    dirty: str
    parents: list[str]


def pull_request(base: str = "preprod", head: str = "dev", head_sha: str = "c" * 40,
                 merged_sha: str = "a" * 40, number: int = 12) -> dict[str, object]:
    """Build one authentic same-repository merged PR with explicit source/base identity."""
    return {"number": number, "merge_commit_sha": merged_sha, "merged_at": "2026-09-06T00:00:00Z",
            "base": {"ref": base, "sha": "d" * 40, "repo": {"full_name": "owner/repo"}},
            "head": {"ref": head, "sha": head_sha, "repo": {"full_name": "owner/repo"}}}


def ci_run(**changes: object) -> dict[str, object]:
    """Describe full PR CI; an empty association list models GitHub's actual post-merge response."""
    return {"id": 70, "run_number": 10, "run_attempt": 1,
            "repository": {"full_name": "owner/repo"}, "head_repository": {"full_name": "owner/repo"},
            "path": ".github/workflows/ci.yml", "head_sha": "c" * 40, "head_branch": "dev",
            "event": "pull_request", "pull_requests": [], "status": "completed",
            "conclusion": "success", **changes}


@pytest.fixture
def source_api(source_qualification: ModuleType, monkeypatch: pytest.MonkeyPatch) -> SourceApiData:
    """Model only GitHub's network boundary while exercising the real selection algorithm."""
    data: SourceApiData = {
        "commits": {"a" * 40: {"sha": "a" * 40, "tree": {"sha": "b" * 40},
                               "parents": [{"sha": "d" * 40}, {"sha": "c" * 40}]}},
        "pulls": {"a" * 40: [pull_request()]}, "manual": {}, "runs": [ci_run()],
        "artifacts": [{"id": 900, "name": "source-qualification-70-1", "expired": False}],
        "calls": [],
    }

    def request(repository: str, endpoint: str, query: Mapping[str, object]) -> object:
        """Return mutable external state without replacing policy or proof validation."""
        assert repository == "owner/repo"
        data["calls"].append(endpoint)
        if endpoint.startswith("git/commits/"):
            return data["commits"][endpoint.rsplit("/", 1)[1]]
        if endpoint.startswith("commits/"):
            return data["pulls"][endpoint.split("/")[1]]
        if endpoint == "actions/workflows/ci.yml/runs":
            if query["event"] == "workflow_dispatch":
                return {"workflow_runs": data["manual"].get(str(query["head_sha"]), [])}
            return {"workflow_runs": data["runs"]}
        if endpoint.endswith("/artifacts"):
            return {"artifacts": data["artifacts"]}
        raise AssertionError(f"Unexpected API endpoint: {endpoint}")

    monkeypatch.setattr(source_qualification, "github_json", request)
    return data


@pytest.fixture
def record_environment(source_qualification: ModuleType, tmp_path: pathlib.Path,
                       monkeypatch: pytest.MonkeyPatch) -> GitState:
    """Provide a real event file and independently controlled Git answers for full CI."""
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps({"pull_request": pull_request()}), encoding="utf-8")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_REF", "refs/pull/12/merge")
    monkeypatch.setenv("GITHUB_SHA", "e" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "70")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
    monkeypatch.setenv("CI_RUNTIME_REQUIRED", "true")
    monkeypatch.setenv("CI_PACKAGE_REQUIRED", "true")
    monkeypatch.setenv("CI_SOURCE_REQUIRED", "false")
    results = {name: {"result": "success"} for name in (
        "branch-policy", "hygiene", "source-assets", "repo-assets", "tests", "documentation", "packages",
    )}
    results["source-qualification"] = {"result": "skipped"}
    monkeypatch.setenv("CI_JOB_RESULTS", json.dumps(results))
    state: GitState = {"sha": "e" * 40, "tree": "b" * 40, "dirty": "",
                       "parents": ["e" * 40, "d" * 40, "c" * 40]}

    def git(arguments: Sequence[str]) -> str:
        """Model the process boundary without masking a wrong event SHA or merge parents."""
        if arguments[0] == "status":
            return state["dirty"]
        if arguments[0] == "rev-list":
            return " ".join(state["parents"])
        if arguments == ("rev-parse", "HEAD^{commit}"):
            return state["sha"]
        if arguments == ("rev-parse", "HEAD^{tree}"):
            return state["tree"]
        raise AssertionError(f"Unexpected Git request: {arguments}")

    monkeypatch.setattr(source_qualification, "git_output", git)
    return state


def test_full_record_qualifies_identical_tree_across_merge_shas(source_qualification: ModuleType,
                                                              source_api: SourceApiData,
                                                              record_environment: GitState) -> None:
    """The tested PR merge and real preprod merge may differ in SHA while carrying identical contents."""
    proof = source_qualification.full_record()
    selected = source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "b" * 40)
    assert proof["checkout_sha"] == "e" * 40
    assert selected["source_sha"] == "a" * 40
    assert selected["artifact_id"] == 900
    source_qualification.validate_proof(proof, selected["expected"])


@pytest.mark.parametrize(("field", "value"), [
    ("tree_sha", "f" * 40), ("repository", "fork/repo"), ("run_id", 71), ("run_attempt", 2),
    ("run_attempt", True), ("pull_request", 99), ("target_branch", "dev"),
    ("head_sha", "f" * 40), ("base_sha", "f" * 40), ("event", "workflow_dispatch"),
    ("schema", True), ("schema", 2), ("full_runtime", False), ("full_runtime", 1),
    ("package_required", False),
])
def test_altered_full_record_is_refused(source_qualification: ModuleType, source_api: SourceApiData,
                                       record_environment: GitState, field: str, value: object) -> None:
    """A familiar artifact name cannot qualify another run, PR, profile, version, or tree."""
    proof = source_qualification.full_record()
    proof[field] = value
    selected = source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "b" * 40)
    with pytest.raises(ValueError, match="differs"):
        source_qualification.validate_proof(proof, selected["expected"])


@pytest.mark.parametrize("change", [
    {"conclusion": "failure"}, {"status": "in_progress", "conclusion": None},
    {"conclusion": "cancelled"}, {"conclusion": "skipped"}, {"run_attempt": True},
    {"id": "70"}, {"path": ".github/workflows/release-candidate.yml"},
    {"head_sha": "f" * 40}, {"head_branch": "preprod"}, {"event": "push"},
    {"repository": {"full_name": "fork/repo"}}, {"head_repository": {"full_name": "fork/repo"}},
])
def test_newest_bad_run_never_falls_back_to_old_green(source_qualification: ModuleType,
                                                     source_api: SourceApiData,
                                                     change: dict[str, object]) -> None:
    """Newer failed, pending or mismatched full-CI evidence invalidates reuse instead of falling back."""
    source_api["runs"].append(ci_run(id=71, run_number=11, **{key: value for key, value in change.items()
                                                            if key != "id"}))
    if "id" in change:
        source_api["runs"][-1]["id"] = change["id"]
    with pytest.raises(ValueError):
        source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "b" * 40)
    assert not any(endpoint.endswith("/artifacts") for endpoint in source_api["calls"])


@pytest.mark.parametrize("mode", ["missing", "expired", "duplicate", "old-attempt", "invalid-id"])
def test_missing_or_stale_artifact_is_not_qualification(source_qualification: ModuleType,
                                                       source_api: SourceApiData, mode: str) -> None:
    """Require exactly one non-expired artifact belonging to the current attempt."""
    if mode == "missing":
        source_api["artifacts"].clear()
    elif mode == "expired":
        source_api["artifacts"][0]["expired"] = True
    elif mode == "duplicate":
        source_api["artifacts"].append(dict(source_api["artifacts"][0]))
    elif mode == "old-attempt":
        source_api["runs"][0]["run_attempt"] = 2
    else:
        source_api["artifacts"][0]["id"] = False
    with pytest.raises(ValueError):
        source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "b" * 40)


def test_different_promotion_tree_refuses_before_querying_runs(source_qualification: ModuleType,
                                                             source_api: SourceApiData) -> None:
    """A merge introducing different contents must earn fresh full qualification."""
    with pytest.raises(ValueError, match="tree differs"):
        source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "f" * 40)
    assert source_api["calls"] == ["git/commits/" + "a" * 40]


@pytest.mark.parametrize("mode", ["missing", "duplicate", "unrelated", "fork", "squashed"])
def test_source_must_be_the_authentic_merged_pr(source_qualification: ModuleType,
                                               source_api: SourceApiData, mode: str) -> None:
    """Containing a commit, an unrelated PR, or a forged route cannot establish promotion provenance."""
    if mode == "missing":
        source_api["pulls"]["a" * 40] = []
    elif mode == "duplicate":
        source_api["pulls"]["a" * 40].append(pull_request(number=13))
    elif mode == "unrelated":
        source_api["pulls"]["a" * 40][0]["merge_commit_sha"] = "f" * 40
    elif mode == "fork":
        source_api["pulls"]["a" * 40][0]["head"] = {
            "ref": "dev", "sha": "c" * 40, "repo": {"full_name": "fork/repo"},
        }
    else:
        source_api["commits"]["a" * 40]["parents"] = [{"sha": "d" * 40}]
    with pytest.raises(ValueError):
        source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "b" * 40)


@pytest.mark.parametrize("failed", [False, True])
def test_exact_manual_ci_takes_precedence(source_qualification: ModuleType, source_api: SourceApiData,
                                        failed: bool) -> None:
    """Manual requalification is explicit, and a failed manual rerun cannot reuse older PR success."""
    source_api["manual"]["a" * 40] = [
        ci_run(event="workflow_dispatch", head_branch="preprod", head_sha="a" * 40,
               conclusion="failure" if failed else "success"),
    ]
    if failed:
        with pytest.raises(ValueError):
            source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "b" * 40)
    else:
        result = source_qualification.select_for_commit("owner/repo", "a" * 40, "preprod", "b" * 40)
        assert result["expected"]["pull_request"] == 0
        assert result["expected"]["head_sha"] == "a" * 40
    assert not any(endpoint.endswith("/pulls") for endpoint in source_api["calls"])


def test_rc_promotion_follows_qualified_preprod_tree(source_qualification: ModuleType,
                                                   source_api: SourceApiData) -> None:
    """The slim RC push can prove full preprod validation through its actual promotion parent."""
    source_api["commits"]["f" * 40] = {
        "sha": "f" * 40, "tree": {"sha": "b" * 40},
        "parents": [{"sha": "d" * 40}, {"sha": "a" * 40}],
    }
    source_api["pulls"]["f" * 40] = [
        pull_request("release_candidate", "preprod", "a" * 40, "f" * 40, 14),
    ]
    result = source_qualification.select_for_commit("owner/repo", "f" * 40, "release_candidate", "b" * 40)
    assert result["source_sha"] == "a" * 40
    assert result["expected"]["target_branch"] == "preprod"


def test_rc_fix_uses_its_own_full_pr_qualification(source_qualification: ModuleType,
                                                 source_api: SourceApiData) -> None:
    """Changed candidate contents require the release-fix PR's full run rather than old preprod proof."""
    source_api["pulls"]["a" * 40] = [pull_request("release_candidate", "release-fix/code")]
    source_api["runs"][0]["head_branch"] = "release-fix/code"
    result = source_qualification.select_for_commit("owner/repo", "a" * 40, "release_candidate", "b" * 40)
    assert result["expected"]["target_branch"] == "release_candidate"
    assert result["expected"]["pull_request"] == 12


@pytest.mark.parametrize("mode", ["sha", "dirty", "parents", "failed-tests"])
def test_record_refuses_unqualified_checkout(source_qualification: ModuleType, record_environment: GitState,
                                            monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    """Only the exact clean tested checkout and genuinely successful required jobs can issue a record."""
    if mode == "sha":
        monkeypatch.setenv("GITHUB_SHA", "f" * 40)
    elif mode == "dirty":
        record_environment["dirty"] = " M src/melder/example.py"
    elif mode == "parents":
        record_environment["parents"][-1] = "f" * 40
    else:
        results = json.loads(os.environ["CI_JOB_RESULTS"])
        results["tests"]["result"] = "failure"
        monkeypatch.setenv("CI_JOB_RESULTS", json.dumps(results))
    with pytest.raises(ValueError):
        source_qualification.full_record()


def test_light_run_cannot_record_full_evidence(source_qualification: ModuleType, record_environment: GitState,
                                              monkeypatch: pytest.MonkeyPatch) -> None:
    """Even a successful light promotion is not a full-test producer."""
    pathlib.Path(os.environ["GITHUB_EVENT_PATH"]).write_text(json.dumps({
        "pull_request": pull_request("release_candidate", "preprod", "a" * 40),
    }), encoding="utf-8")
    monkeypatch.setenv("CI_RUNTIME_REQUIRED", "false")
    monkeypatch.setenv("CI_PACKAGE_REQUIRED", "false")
    monkeypatch.setenv("CI_SOURCE_REQUIRED", "true")
    results = json.loads(os.environ["CI_JOB_RESULTS"])
    for name in ("source-assets", "repo-assets", "tests", "documentation", "packages"):
        results[name]["result"] = "skipped"
    results["source-qualification"]["result"] = "success"
    monkeypatch.setenv("CI_JOB_RESULTS", json.dumps(results))
    with pytest.raises(ValueError, match="light CI"):
        source_qualification.full_record()


def test_record_select_verify_roundtrip_rejects_changed_attempt(source_qualification: ModuleType,
                                                               source_api: SourceApiData,
                                                               record_environment: GitState,
                                                               tmp_path: pathlib.Path,
                                                               monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise real JSON I/O and CLI phases, then invalidate a selected record by rerunning its producer."""
    proof = tmp_path / "proof.json"
    selection = tmp_path / "selection.json"
    outputs = tmp_path / "outputs.txt"
    assert source_qualification.main(["record", "--record", str(proof)]) == 0
    record_environment["sha"] = "f" * 40
    monkeypatch.setenv("GITHUB_SHA", "f" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "80")
    monkeypatch.setenv("GITHUB_OUTPUT", str(outputs))
    pathlib.Path(os.environ["GITHUB_EVENT_PATH"]).write_text(json.dumps({
        "pull_request": pull_request("release_candidate", "preprod", "a" * 40, number=14),
    }), encoding="utf-8")
    assert source_qualification.main(["select", "--selection", str(selection)]) == 0
    assert outputs.read_text(encoding="utf-8") == "run-id=70\nartifact-id=900\n"
    arguments = ["verify", "--selection", str(selection), "--record", str(proof)]
    assert source_qualification.main(arguments) == 0
    source_api["runs"][0]["run_attempt"] = 2
    source_api["artifacts"][0]["name"] = "source-qualification-70-2"
    with pytest.raises(ValueError, match="changed while downloading"):
        source_qualification.main(arguments)


def test_api_pagination_is_complete_and_bounded(source_qualification: ModuleType,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    """Later pages cannot disappear from the evidence search and unbounded histories refuse."""
    pages: list[object] = []

    def response(repository: str, endpoint: str, query: Mapping[str, object]) -> object:
        """Return a full first page followed by a short final page."""
        pages.append(query["page"])
        return [{"id": index} for index in range(100 if query["page"] == 1 else 1)]

    monkeypatch.setattr(source_qualification, "github_json", response)
    assert len(source_qualification.github_items("owner/repo", "commits/a/pulls")) == 101
    assert pages == [1, 2]
    monkeypatch.setattr(source_qualification, "github_json", lambda *args: [{"id": 1}] * 100)
    with pytest.raises(ValueError, match="pagination bound"):
        source_qualification.github_items("owner/repo", "commits/a/pulls")


def test_api_reader_uses_fixed_host_and_closes_response(source_qualification: ModuleType,
                                                      monkeypatch: pytest.MonkeyPatch) -> None:
    """GitHub JSON requests carry only the job's read token and close their stream."""
    stream = io.BytesIO(b'{"workflow_runs":[]}')

    def response(request: urllib.request.Request, timeout: int) -> io.BytesIO:
        """Inspect the external request without contacting GitHub."""
        assert request.full_url == "https://api.github.com/repos/owner/repo/actions/runs?page=1"
        assert request.get_header("Authorization") == "Bearer fixture-credential"
        assert timeout == 30
        return stream

    monkeypatch.setenv("GITHUB_TOKEN", "fixture-credential")
    monkeypatch.setattr(source_qualification.urllib.request, "urlopen", response)
    assert source_qualification.github_json("owner/repo", "actions/runs", {"page": 1}) == {"workflow_runs": []}
    assert stream.closed
    with pytest.raises(ValueError, match="repository identity"):
        source_qualification.github_json("owner/repo/escape", "actions/runs", {})


@pytest.mark.parametrize("payload", [b"[]", b"{", b"x" * 65537])
def test_downloaded_record_is_bounded_json_data(source_qualification: ModuleType, tmp_path: pathlib.Path,
                                               payload: bytes) -> None:
    """Invalid, non-object, and oversized downloads never become executable or accepted proof."""
    path = tmp_path / "qualification.json"
    path.write_bytes(payload)
    with pytest.raises(ValueError):
        source_qualification.read_record(path)
