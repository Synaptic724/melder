"""Prove manifest-driven Python selection and complete version-aware coverage report handling."""

import json
import pathlib
import platform
import re
import sys
import sysconfig
import tomllib
import zipfile
from types import ModuleType

import pytest


def write_manifest(directory: pathlib.Path, version: str, dependencies: tuple[str, ...] = ("pytest==9.1.1",),
                   extra: str = "") -> pathlib.Path:
    """Write one manifest the way a maintainer adds a Python release; json renders valid TOML strings."""
    directory.mkdir(parents=True, exist_ok=True)
    pins = ", ".join(json.dumps(pin) for pin in dependencies)
    path = directory / f"{version}.toml"
    path.write_text(f'python = "{version}"\nfreethreaded = true\ndependencies = [{pins}]\n{extra}', encoding="utf-8")
    return path


def test_discovers_every_manifest_on_every_runner(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """Every manifest is one release on all three runners, ordered numerically, not by file name."""
    for version in ("3.14.10", "3.15.0", "3.14.0", "3.14.9"):
        write_manifest(tmp_path, version)
    matrix = runtime_matrix.discover_matrix(tmp_path, (3, 14, 0))
    assert matrix == {"include": [
        {"os": runner, "python": version, "architecture": architecture}
        for version in ("3.14.0", "3.14.9", "3.14.10", "3.15.0")
        for runner, architecture in (("ubuntu-24.04", "x64"), ("windows-latest", "x64"), ("macos-latest", "arm64"))
    ]}


def test_floor_release_needs_a_manifest(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """The oldest release the package claims must be one CI actually tests."""
    for version in ("3.14.1", "3.14.2"):
        write_manifest(tmp_path, version)
    with pytest.raises(ValueError, match="supported floor"):
        runtime_matrix.discover_matrix(tmp_path, (3, 14, 0))


def test_manifest_below_the_floor_must_be_removed(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """Raising requires-python retires old manifests explicitly instead of leaving them silently unused."""
    for version in ("3.13.9", "3.14.0"):
        write_manifest(tmp_path, version)
    with pytest.raises(ValueError, match="below the supported floor"):
        runtime_matrix.discover_matrix(tmp_path, (3, 14, 0))


def test_raised_floor_selects_only_its_manifests(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """A floor of 3.15.1 needs a 3.15.1 manifest and runs exactly what the directory lists."""
    for version in ("3.15.1", "3.15.2"):
        write_manifest(tmp_path, version)
    matrix = runtime_matrix.discover_matrix(tmp_path, (3, 15, 1))
    assert [row["python"] for row in matrix["include"]] == ["3.15.1"] * 3 + ["3.15.2"] * 3


@pytest.mark.parametrize(("name", "text"), [
    ("3.14.1.toml", 'python = "3.14.2"\nfreethreaded = true\ndependencies = ["pytest==9.1.1"]\n'),
    ("3.14.0rc1.toml", 'python = "3.14.0rc1"\nfreethreaded = true\ndependencies = ["pytest==9.1.1"]\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = false\ndependencies = ["pytest==9.1.1"]\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = true\ndependencies = ["pytest>=9"]\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = true\ndependencies = ["pytest"]\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = true\ndependencies = ["pytest==9.1.1", "PyTest==9.1.0"]\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = true\ndependencies = []\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = true\ndependencies = ["pytest==9.1.1"]\nlatest = true\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = true\n'),
    ("3.14.1.toml", 'python = "3.14.1"\nfreethreaded = true\ndependencies = ["pytest==9.1.1"]\n'
                    'build_from_source = ["dishka"]\n'),
    ("3.14.1.toml", 'python = "3.14.1\nfreethreaded = true\n'),
    ("README.md", "Python releases live here.\n"),
], ids=["file-names-another-release", "prerelease", "not-free-threaded", "range-pin", "unpinned",
        "pinned-twice", "no-pins", "unknown-key", "missing-dependencies", "source-build-not-pinned",
        "invalid-toml", "stray-file"])
def test_malformed_manifest_refuses(runtime_matrix: ModuleType, tmp_path: pathlib.Path, name: str, text: str) -> None:
    """A manifest cannot widen a pin, name the wrong release, or slip a non-manifest file into the directory."""
    (tmp_path / name).write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        runtime_matrix.load_manifests(tmp_path, (3, 14, 0))


def test_empty_or_missing_manifest_directory_refuses(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """No manifest means no release to run, which is an error, never a default."""
    with pytest.raises(ValueError, match="missing"):
        runtime_matrix.discover_matrix(tmp_path / "absent", (3, 14, 0))
    with pytest.raises(ValueError, match="empty"):
        runtime_matrix.discover_matrix(tmp_path, (3, 14, 0))


def test_manifest_keeps_markers_and_source_builds(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """Platform markers and source builds pass through unchanged, in manifest order."""
    path = write_manifest(tmp_path, "3.14.7",
                          ("dependency-injector==4.49.1", "colorama==0.4.6; sys_platform == 'win32'"),
                          'build_from_source = ["dependency_injector"]\n')
    manifest = runtime_matrix.load_manifest(path)
    assert manifest.python == "3.14.7" and manifest.release == (3, 14, 7)
    assert manifest.dependencies == ("dependency-injector==4.49.1", "colorama==0.4.6; sys_platform == 'win32'")
    assert manifest.build_from_source == ("dependency_injector",)
    assert runtime_matrix.requirements_text(manifest) == (
        "dependency-injector==4.49.1\ncolorama==0.4.6; sys_platform == 'win32'\n")


@pytest.mark.parametrize("versions", [(), ("3.14.7", "3.14.8")])
def test_speed_tests_need_exactly_one_manifest(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                               versions: tuple[str, ...]) -> None:
    """Benchmarks compare only on one fixed release, so zero or two speed manifests refuse."""
    for version in versions:
        write_manifest(tmp_path, version)
    with pytest.raises(ValueError):
        runtime_matrix.speed_manifest(tmp_path, (3, 14, 0))


def test_speed_and_requirements_operations_write_their_outputs(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    """The speed job names its release for setup-python; a test cell gets its exact pins as a requirements file."""
    speed = tmp_path / "speed"
    write_manifest(speed, "3.14.7")
    test_manifest = write_manifest(tmp_path / "tests", "3.14.0", ("pytest==9.1.1", "PyYAML==6.0.3"))
    monkeypatch.setattr(runtime_matrix, "supported_floor", lambda: (3, 14, 0))
    outputs = tmp_path / "outputs"
    monkeypatch.setenv("GITHUB_OUTPUT", str(outputs))
    assert runtime_matrix.main(["speed", "--manifests", str(speed)]) == 0
    assert outputs.read_text(encoding="utf-8") == "python=3.14.7\n"
    requirements = tmp_path / "reports/requirements.txt"
    assert runtime_matrix.main(["requirements", "--manifest", str(test_manifest), "--output", str(requirements)]) == 0
    assert requirements.read_text(encoding="utf-8") == "pytest==9.1.1\nPyYAML==6.0.3\n"



def test_speed_install_command_builds_only_the_listed_sources(runtime_matrix: ModuleType,
                                                              tmp_path: pathlib.Path) -> None:
    """Wheels only, except each build_from_source entry; :all: comes first or it would erase the exceptions."""
    manifest = runtime_matrix.load_manifest(write_manifest(
        tmp_path, "3.14.7", ("dependency-injector==4.49.1", "dishka==1.10.1", "lagom==2.7.7"),
        'build_from_source = ["dependency-injector", "lagom"]\n'))
    requirements, report = tmp_path / "requirements.txt", tmp_path / "install-report.json"
    assert runtime_matrix.speed_install_command(manifest, requirements, report) == [
        sys.executable, "-m", "pip", "install", "--only-binary=:all:", "--no-binary=dependency-injector",
        "--no-binary=lagom", "--report", str(report), "-r", str(requirements)]
    wheels_only = runtime_matrix.load_manifest(write_manifest(tmp_path / "wheels", "3.14.7"))
    assert runtime_matrix.speed_install_command(wheels_only, requirements, report)[4:6] == [
        "--only-binary=:all:", "--report"]


@pytest.mark.parametrize("status", [0, 1])
def test_speed_install_runs_pip_once_and_keeps_the_evidence(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                            monkeypatch: pytest.MonkeyPatch, status: int) -> None:
    """The pins and pip's log land in the results directory, pip runs once, and its exit status is returned."""
    manifest = runtime_matrix.load_manifest(write_manifest(
        tmp_path / "speed", "3.14.7", ("dependency-injector==4.49.1", "dishka==1.10.1"),
        'build_from_source = ["dependency-injector"]\n'))
    commands: list[list[str]] = []

    class RecordingPip:
        """Stand in for the pip process: record its command, replay two output lines, exit with the case's status."""

        def __init__(self, command: list[str], **options: object) -> None:
            """Record the command; the streaming options belong to the caller."""
            commands.append(command)
            self.stdout = iter(["Collecting dishka==1.10.1\n", "Successfully installed dishka-1.10.1\n"])

        def wait(self) -> int:
            """Return the exit status this case simulates."""
            return status

    monkeypatch.setattr(runtime_matrix.subprocess, "Popen", RecordingPip)
    results = tmp_path / "results"
    assert runtime_matrix.install_speed_manifest(manifest, results, "3.14.7", True) == status
    assert commands == [runtime_matrix.speed_install_command(manifest, results / "requirements.txt",
                                                             results / "install-report.json")]
    assert (results / "requirements.txt").read_text(encoding="utf-8") == (
        "dependency-injector==4.49.1\ndishka==1.10.1\n")
    assert (results / "install.log").read_text(encoding="utf-8") == (
        "Collecting dishka==1.10.1\nSuccessfully installed dishka-1.10.1\n")


@pytest.mark.parametrize(("release", "freethreaded"), [("3.14.8", True), ("3.14.7", False)])
def test_speed_install_refuses_another_interpreter(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                   monkeypatch: pytest.MonkeyPatch, release: str,
                                                   freethreaded: bool) -> None:
    """Libraries installed into another release or a GIL build would be measured on the wrong interpreter."""
    manifest = runtime_matrix.load_manifest(write_manifest(tmp_path / "speed", "3.14.7"))

    def refuse_pip(*arguments: object, **options: object) -> None:
        """Fail the test if a refused install still reaches pip."""
        raise AssertionError("pip must not run for a refused interpreter")

    monkeypatch.setattr(runtime_matrix.subprocess, "Popen", refuse_pip)
    with pytest.raises(ValueError, match="free-threaded Python 3.14.7"):
        runtime_matrix.install_speed_manifest(manifest, tmp_path / "results", release, freethreaded)
    assert not (tmp_path / "results").exists()


def test_speed_install_operation_passes_the_running_interpreter(runtime_matrix: ModuleType, tmp_path: pathlib.Path,
                                                                monkeypatch: pytest.MonkeyPatch) -> None:
    """speed-install reads the one speed manifest, judges the interpreter running it, and returns pip's status."""
    speed = tmp_path / "speed"
    write_manifest(speed, "3.14.7")
    monkeypatch.setattr(runtime_matrix, "supported_floor", lambda: (3, 14, 0))
    received: list[tuple[object, pathlib.Path, str, bool]] = []

    def install(manifest: object, results: pathlib.Path, release: str, freethreaded: bool) -> int:
        """Record what the operation hands the installer and report a failed pip run."""
        received.append((manifest, results, release, freethreaded))
        return 3

    monkeypatch.setattr(runtime_matrix, "install_speed_manifest", install)
    results = tmp_path / "results"
    assert runtime_matrix.main(["speed-install", "--manifests", str(speed), "--results", str(results)]) == 3
    assert received == [(runtime_matrix.speed_manifest(speed, (3, 14, 0)), results, platform.python_version(),
                         sysconfig.get_config_var("Py_GIL_DISABLED") == 1)]
    with pytest.raises(SystemExit):
        runtime_matrix.main(["speed-install", "--manifests", str(speed)])

def test_repository_manifests_cover_the_floor_and_pin_every_runtime_dependency(runtime_matrix: ModuleType) -> None:
    """The committed manifests build a matrix, and each test cell pins every runtime dependency Melder declares.

    Cells install with --no-deps, so a runtime dependency (LogXide, once added) must be pinned in every test
    manifest or that cell would test without it.
    """
    root = pathlib.Path(__file__).resolve().parents[3]
    floor = runtime_matrix.supported_floor()
    tests = root / runtime_matrix.RuntimeMatrixPolicy.TESTS_DIRECTORY
    runtime_matrix.discover_matrix(tests, floor)
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    declared = {runtime_matrix.canonical_name(re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", requirement)[0])
                for requirement in project.get("dependencies", [])}
    for manifest in runtime_matrix.load_manifests(tests, floor):
        pinned = {runtime_matrix.canonical_name(pin.split("==")[0]) for pin in manifest.dependencies}
        assert declared <= pinned, (manifest.python, sorted(declared - pinned))


def test_repository_speed_manifest_is_tested_and_builds_dependency_injector_from_source(
        runtime_matrix: ModuleType,
) -> None:
    """The speed release is one the test matrix covers, and only dependency-injector is built from source."""
    root = pathlib.Path(__file__).resolve().parents[3]
    floor = runtime_matrix.supported_floor()
    speed = runtime_matrix.speed_manifest(root / runtime_matrix.RuntimeMatrixPolicy.SPEED_DIRECTORY, floor)
    tested = {manifest.python for manifest in runtime_matrix.load_manifests(
        root / runtime_matrix.RuntimeMatrixPolicy.TESTS_DIRECTORY, floor)}
    assert speed.python in tested
    assert speed.build_from_source == ("dependency-injector",)


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


@pytest.mark.parametrize("versions", [[], ["3.13.9"], ["3.14.1", "3.14.1"], ["3.15.0"], ["3.14t"], ["../escape"]])
def test_matrix_refuses_empty_duplicate_or_unsafe_versions(runtime_matrix: ModuleType, versions: list[str]) -> None:
    """The OS product cannot be empty, repeat a release, skip the floor's minor or carry unsafe path labels."""
    with pytest.raises(ValueError):
        runtime_matrix.version_matrix(versions, (3, 14, 0))


def test_matrix_keeps_every_patch_of_a_minor(runtime_matrix: ModuleType) -> None:
    """Several patches of one minor are separate entries, each on all three runners, in release order."""
    matrix = runtime_matrix.version_matrix(["3.14.1", "3.14.0", "3.14.2"], (3, 14, 0))
    assert [row["python"] for row in matrix["include"]] == ["3.14.0"] * 3 + ["3.14.1"] * 3 + ["3.14.2"] * 3
    assert [row["os"] for row in matrix["include"][:3]] == ["ubuntu-24.04", "windows-latest", "macos-latest"]


def test_job_limit_is_not_silent_truncation(runtime_matrix: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    """A matrix too large for its configured bound must fail visibly."""
    monkeypatch.setattr(runtime_matrix.RuntimeMatrixPolicy, "MAX_JOBS", 5)
    with pytest.raises(ValueError, match="job limit"):
        runtime_matrix.version_matrix(["3.14.1", "3.15.1"], (3, 14, 0))


@pytest.mark.parametrize("defect", ["missing-os", "duplicate", "architecture", "extra-field", "unsafe-version"])
def test_report_matrix_must_match_the_whole_product(runtime_matrix: ModuleType, defect: str) -> None:
    """An incomplete or forged matrix cannot make a partial coverage upload appear complete."""
    matrix = runtime_matrix.version_matrix(["3.14.0", "3.14.1", "3.15.0"], (3, 14, 0))
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
    """Exercise manifest discovery, retained JSON and coverage verification through real filesystem boundaries."""
    manifests = tmp_path / "manifests"
    for version in ("3.14.0", "3.14.7", "3.15.0"):
        write_manifest(manifests, version)
    monkeypatch.setattr(runtime_matrix, "supported_floor", lambda: (3, 14, 0))
    outputs = tmp_path / "outputs"
    report = tmp_path / "reports/python-matrix.json"
    monkeypatch.setenv("GITHUB_OUTPUT", str(outputs))
    assert runtime_matrix.main(["discover", "--manifests", str(manifests), "--report", str(report)]) == 0
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
    entries = [("ubuntu-24.04", "3.14.7", 1), ("ubuntu-24.04", "3.14.7", 2),
               ("windows-latest", "3.14.7", 1), ("macos-latest", "3.14.7", 1),
               ("ubuntu-24.04", "3.14.6", 1)]
    for runner, version, attempt in entries:
        filename = f"coverage-{runner}-python-{version}-70-{attempt}.xml"
        archive = tmp_path / (filename + ".zip")
        with zipfile.ZipFile(archive, "w") as writer:
            writer.writestr(filename, f'<coverage platform="{runner}" attempt="{attempt}"/>')
        with zipfile.ZipFile(archive) as reader:
            reader.extractall(root)
    matrix = runtime_matrix.version_matrix(["3.14.7"], (3, 14, 0))
    reports = runtime_matrix.require_coverage(root, matrix, "70", "2")
    expected = {"coverage-ubuntu-24.04-python-3.14.7-70-2.xml",
                "coverage-windows-latest-python-3.14.7-70-1.xml",
                "coverage-macos-latest-python-3.14.7-70-1.xml"}
    assert {path.name for path in reports} == expected
    selected = tmp_path / "selected"
    runtime_matrix.stage_coverage(reports, selected, tmp_path / "selection.json")
    assert {path.name for path in selected.iterdir()} == expected
    assert 'attempt="2"' in (selected / "coverage-ubuntu-24.04-python-3.14.7-70-2.xml").read_text()


@pytest.mark.parametrize("filename", [
    "coverage.xml", "coverage-ubuntu-24.04-python-3.14.7-71-1.xml",
    "coverage-ubuntu-24.04-python-3.14.7-70-3.xml", "coverage-other-python-3.14.7-70-1.xml",
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
    (tmp_path / "coverage-ubuntu-24.04-python-3.14.7-70-2.xml").write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="Newest coverage report is empty"):
        runtime_matrix.require_coverage(tmp_path, matrix, "70", "2")


def test_one_flat_report_cannot_claim_a_complete_matrix(runtime_matrix: ModuleType, tmp_path: pathlib.Path) -> None:
    """The exact singleton-download symptom still refuses if the other platforms truly have no evidence."""
    (tmp_path / "coverage-ubuntu-24.04-python-3.14.7-70-2.xml").write_text("<coverage/>", encoding="utf-8")
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
