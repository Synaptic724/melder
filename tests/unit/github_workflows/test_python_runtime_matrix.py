"""Prove stable no-GIL discovery and complete version-aware report handling at external boundaries."""

import io
import json
import pathlib
import urllib.error
import zipfile
from types import ModuleType

import pytest


def release(version: str, stable: bool = True) -> dict[str, object]:
    """Model the official manifest's three required free-threaded platform assets."""
    return {"version": version, "stable": stable, "files": [
        {"platform": "linux", "arch": "x64-freethreaded"},
        {"platform": "win32", "arch": "x64-freethreaded"},
        {"platform": "darwin", "arch": "arm64-freethreaded"},
    ]}


def test_discovers_latest_patch_for_every_stable_minor(runtime_matrix: ModuleType) -> None:
    """Future stable minors enter automatically; numeric patch ordering excludes RCs and older Python."""
    payload = [release("3.14.9"), release("3.13.12"), release("3.16.0-rc.2", False),
               release("3.15.0"), release("3.14.10"), release("4.0.0"), release("3.15.1-beta.1", False)]
    matrix = runtime_matrix.discover_matrix(payload, (3, 14, 0))
    assert matrix == {"include": [
        {"os": runner, "python": version, "architecture": architecture}
        for version in ("3.14.10", "3.15.0", "4.0.0")
        for runner, architecture in (("ubuntu-latest", "x64"), ("windows-latest", "x64"), ("macos-latest", "arm64"))
    ]}


@pytest.mark.parametrize("position", [0, 1, 2])
def test_missing_free_threaded_platform_cannot_fall_back(runtime_matrix: ModuleType, position: int) -> None:
    """An older working patch or standard-Python archive cannot hide absent newest-patch support."""
    newest = release("3.14.2")
    newest["files"][position]["arch"] = "x64"
    with pytest.raises(ValueError, match="lacks free-threaded assets"):
        runtime_matrix.discover_matrix([release("3.14.1"), newest], (3, 14, 0))


@pytest.mark.parametrize("payload", [
    {}, [], [release("3.15.0")], [release("3.14.0-rc.1", False)],
    [release("3.14.0-rc.1")], [{"version": "3.14.1", "stable": "true"}],
    [{"version": "3.14.1", "stable": True}],
    [{"version": "3.14.1", "stable": True, "files": [None]}],
    [{"version": "3.14.1", "stable": True, "files": [{"arch": "x64-freethreaded"}]}],
], ids=["not-list", "empty", "missing-floor", "only-prerelease", "false-stable-claim", "bad-stable-flag",
        "no-files", "bad-asset", "missing-platform"])
def test_incomplete_or_malformed_discovery_refuses(runtime_matrix: ModuleType, payload: object) -> None:
    """Discovery cannot quietly yield a smaller or imaginary compatibility guarantee."""
    with pytest.raises(ValueError):
        runtime_matrix.discover_matrix(payload, (3, 14, 0))


def test_raised_support_floor_and_duplicate_build_records(runtime_matrix: ModuleType) -> None:
    """Project metadata selects the floor; duplicate build records do not duplicate test cells."""
    matrix = runtime_matrix.discover_matrix(
        [release("3.14.10"), release("3.15.0"), release("3.15.1"), release("3.15.1")], (3, 15, 1),
    )
    assert len(matrix["include"]) == 3
    assert {row["python"] for row in matrix["include"]} == {"3.15.1"}


@pytest.mark.parametrize(("constraint", "expected"), [(">=3.14", (3, 14, 0)), (">=3.15.1", (3, 15, 1))])
def test_floor_comes_from_package_metadata(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                          constraint: str, expected: tuple[int, int, int]) -> None:
    """Read metadata as TOML without importing runtime code or relying on the current directory."""
    project = tmp_path / "pyproject.toml"
    project.write_text(f'[project]\nrequires-python = "{constraint}"\n', encoding="utf-8")
    assert runtime_matrix.supported_floor(project) == expected


@pytest.mark.parametrize("constraint", ["", ">=3.14,<4", "~=3.14", ">=3.14rc1", "3.14t"])
def test_new_constraint_forms_require_deliberate_policy(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                       constraint: str) -> None:
    """Refuse unsupported constraint syntax instead of broadening the declared version range."""
    project = tmp_path / "pyproject.toml"
    project.write_text(f'[project]\nrequires-python = "{constraint}"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="floor"):
        runtime_matrix.supported_floor(project)


@pytest.mark.parametrize("versions", [[], ["3.13.9"], ["3.14.1", "3.14.2"], ["3.14t"], ["../escape"]])
def test_matrix_refuses_empty_duplicate_or_unsafe_versions(runtime_matrix: ModuleType, versions: list[str]) -> None:
    """The canonical OS product cannot be empty, repeat a minor or introduce unsafe path labels."""
    with pytest.raises(ValueError):
        runtime_matrix.version_matrix(versions, (3, 14, 0))


def test_job_limit_is_not_silent_truncation(runtime_matrix: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """A matrix too large for its configured bound must fail visibly."""
    monkeypatch.setattr(runtime_matrix.RuntimeMatrixPolicy, "MAX_JOBS", 5)
    with pytest.raises(ValueError, match="job limit"):
        runtime_matrix.version_matrix(["3.14.1", "3.15.1"], (3, 14, 0))


@pytest.mark.parametrize("oversized", [False, True])
def test_manifest_fetch_is_bounded_public_and_closes_stream(runtime_matrix: ModuleType,
                                                          monkeypatch: pytest.MonkeyPatch, oversized: bool) -> None:
    """Only public metadata is fetched; credentials, interpreter downloads and unbounded reads are absent."""
    response = io.BytesIO(b"x" * 33 if oversized else b"[]")
    monkeypatch.setattr(runtime_matrix.RuntimeMatrixPolicy, "MAX_MANIFEST_BYTES", 32)

    def open_manifest(request: object, timeout: int) -> io.BytesIO:
        """Observe the real HTTP boundary without contacting the service."""
        assert request.full_url == "https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json"
        assert request.get_header("Authorization") is None
        assert timeout == 30
        return response

    monkeypatch.setattr(runtime_matrix.urllib.request, "urlopen", open_manifest)
    if oversized:
        with pytest.raises(ValueError, match="size"):
            runtime_matrix.fetch_manifest()
    else:
        assert runtime_matrix.fetch_manifest() == []
    assert response.closed


@pytest.mark.parametrize("defect", ["missing-os", "duplicate", "architecture", "extra-field", "unsafe-version"])
def test_report_matrix_must_match_the_whole_product(runtime_matrix: ModuleType, defect: str) -> None:
    """An incomplete or forged matrix cannot make a partial coverage upload appear complete."""
    matrix = runtime_matrix.version_matrix(["3.14.1", "3.15.0"], (3, 14, 0))
    if defect == "missing-os":
        matrix["include"].pop()
    elif defect == "duplicate":
        matrix["include"].append(matrix["include"][0])
    elif defect == "architecture":
        matrix["include"][0]["architecture"] = "arm64"
    elif defect == "extra-field":
        matrix["unexpected"] = []
    else:
        matrix["include"][0]["python"] = "../../escape"
    with pytest.raises(ValueError):
        runtime_matrix.validate_matrix(matrix, (3, 14, 0))


@pytest.mark.parametrize("defect", ["none", "missing", "empty", "unexpected", "reporting-rerun", "future-attempt"])
def test_discovery_to_coverage_cli_checks_every_version(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                       monkeypatch: pytest.MonkeyPatch, defect: str) -> None:
    """Exercise discovery outputs, retained JSON and coverage verification through real filesystem boundaries."""
    monkeypatch.setattr(runtime_matrix, "fetch_manifest", lambda: [release("3.14.7"), release("3.15.0")])
    monkeypatch.setattr(runtime_matrix, "supported_floor", lambda: (3, 14, 0))
    outputs = tmp_path / "outputs"
    report = tmp_path / "reports/python-matrix.json"
    monkeypatch.setenv("GITHUB_OUTPUT", str(outputs))
    assert runtime_matrix.main(["discover", "--report", str(report)]) == 0
    matrix = json.loads(report.read_text(encoding="utf-8"))
    assert json.loads(outputs.read_text(encoding="utf-8").removeprefix("matrix=")) == matrix
    monkeypatch.setenv("CI_PYTHON_MATRIX", json.dumps(matrix))
    monkeypatch.setenv("GITHUB_RUN_ID", "70")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    root = tmp_path / "coverage"
    root.mkdir()
    for row in matrix["include"]:
        last_report = root / f"coverage-{row['os']}-python-{row['python']}-70-2.xml"
        last_report.write_text("<coverage />", encoding="utf-8")
    if defect == "missing":
        last_report.unlink()
    elif defect == "empty":
        last_report.write_text("", encoding="utf-8")
    elif defect == "unexpected":
        (root / "unrelated").mkdir()
    elif defect == "reporting-rerun":
        monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "3")
    elif defect == "future-attempt":
        monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
    selected = tmp_path / "selected"
    provenance = tmp_path / "selection.json"
    args = ["coverage", "--directory", str(root), "--selected-directory", str(selected),
            "--selection-report", str(provenance)]
    if defect in ("none", "reporting-rerun"):
        assert runtime_matrix.main(args) == 0
        assert {path.name for path in selected.iterdir()} == {path.name for path in root.iterdir()}
        assert set(json.loads(provenance.read_text(encoding="utf-8"))["reports"]) == {
            path.name for path in root.iterdir()
        }
    else:
        with pytest.raises(ValueError):
            runtime_matrix.main(args)
        assert not selected.exists()


def test_partial_rerun_archive_merge_preserves_each_platform(runtime_matrix: ModuleType,
                                                           tmp_path: pathlib.Path) -> None:
    """Unique XML payloads survive merged extraction and choose Ubuntu 2 with Windows/macOS 1."""
    root = tmp_path / "downloads"
    root.mkdir()
    entries = [("ubuntu-latest", "3.14.7", 1), ("ubuntu-latest", "3.14.7", 2),
               ("windows-latest", "3.14.7", 1), ("macos-latest", "3.14.7", 1),
               ("ubuntu-latest", "3.14.6", 1)]
    for runner, version, attempt in entries:
        filename = f"coverage-{runner}-python-{version}-70-{attempt}.xml"
        archive = tmp_path / (filename + ".zip")
        with zipfile.ZipFile(archive, "w") as writer:
            writer.writestr(filename, f'<coverage platform="{runner}" attempt="{attempt}"/>')
        with zipfile.ZipFile(archive) as reader:
            reader.extractall(root)
    matrix = runtime_matrix.version_matrix(["3.14.7"], (3, 14, 0))
    reports = runtime_matrix.require_coverage(root, matrix, "70", "2")
    expected = {"coverage-ubuntu-latest-python-3.14.7-70-2.xml",
                "coverage-windows-latest-python-3.14.7-70-1.xml",
                "coverage-macos-latest-python-3.14.7-70-1.xml"}
    assert {path.name for path in reports} == expected
    selected = tmp_path / "selected"
    runtime_matrix.stage_coverage(reports, selected, tmp_path / "selection.json")
    assert {path.name for path in selected.iterdir()} == expected
    assert 'attempt="2"' in (selected / "coverage-ubuntu-latest-python-3.14.7-70-2.xml").read_text()


@pytest.mark.parametrize("filename", [
    "coverage.xml", "coverage-ubuntu-latest-python-3.14.7-71-1.xml",
    "coverage-ubuntu-latest-python-3.14.7-70-3.xml", "coverage-other-python-3.14.7-70-1.xml",
])
def test_ambiguous_foreign_and_future_payloads_refuse(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                    filename: str) -> None:
    """Neither a flattened anonymous file nor another run/attempt can replace missing platforms."""
    (tmp_path / filename).write_text("<coverage/>", encoding="utf-8")
    matrix = runtime_matrix.version_matrix(["3.14.7"], (3, 14, 0))
    with pytest.raises(ValueError):
        runtime_matrix.require_coverage(tmp_path, matrix, "70", "2")


def test_invalid_newest_report_cannot_fall_back_to_older_success(runtime_matrix: ModuleType,
                                                               tmp_path: pathlib.Path) -> None:
    """A failed newest upload must be visible even when an earlier complete set exists."""
    matrix = runtime_matrix.version_matrix(["3.14.7"], (3, 14, 0))
    for row in matrix["include"]:
        (tmp_path / f"coverage-{row['os']}-python-3.14.7-70-1.xml").write_text("<coverage/>", encoding="utf-8")
    (tmp_path / "coverage-ubuntu-latest-python-3.14.7-70-2.xml").write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Newest coverage report is empty"):
        runtime_matrix.require_coverage(tmp_path, matrix, "70", "2")


def test_one_flat_report_cannot_claim_a_complete_matrix(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """The exact singleton-download symptom still refuses if the other platforms truly have no evidence."""
    (tmp_path / "coverage-ubuntu-latest-python-3.14.7-70-2.xml").write_text("<coverage/>", encoding="utf-8")
    matrix = runtime_matrix.version_matrix(["3.14.7"], (3, 14, 0))
    with pytest.raises(ValueError, match="missing OS/Python cells"):
        runtime_matrix.require_coverage(tmp_path, matrix, "70", "2")


def test_staging_preserves_existing_output(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """A rerun cannot silently upload stale files left in a nonempty staging directory."""
    existing = tmp_path / "existing.xml"
    existing.write_text("preserve", encoding="utf-8")
    with pytest.raises(ValueError, match="must be empty"):
        runtime_matrix.stage_coverage([], tmp_path, tmp_path / "selection.json")
    assert existing.read_text(encoding="utf-8") == "preserve"


def test_network_failure_never_issues_fallback_matrix(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed discovery must block downstream tests/publication, not issue an old static version."""
    def unavailable() -> object:
        """Fail at the HTTP boundary."""
        raise urllib.error.URLError("unavailable")

    monkeypatch.setattr(runtime_matrix, "fetch_manifest", unavailable)
    output = tmp_path / "outputs"
    report = tmp_path / "matrix.json"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    with pytest.raises(urllib.error.URLError):
        runtime_matrix.main(["discover", "--report", str(report)])
    assert not output.exists() and not report.exists()
