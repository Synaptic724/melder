"""Build CI's Python matrices and installs from the repository's per-release manifests; verify coverage.

Every Python release CI runs is named by a manifest: one per release under .github/python/tests/ for the
runtime tests (and the release candidate's install probes), exactly one under .github/python/speed/ for the
speed tests. Nothing is looked up on the network, so a new Python release runs only after a manifest adds it.
"""

import argparse
import dataclasses
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import sysconfig
import tomllib
from collections.abc import Mapping, Sequence
from typing import Optional

from ci_policy import CIPolicy, object_value


class RuntimeMatrixPolicy:
    """Keep manifest locations and keys, the matrix bound and the supported runner architectures in one place."""

    TESTS_DIRECTORY = pathlib.Path(".github/python/tests")
    SPEED_DIRECTORY = pathlib.Path(".github/python/speed")
    MANIFEST_KEYS = frozenset({"python", "freethreaded", "dependencies", "build_from_source"})
    MAX_JOBS = 256
    TARGETS = (
        ("ubuntu-latest", "linux", "x64"),
        ("windows-latest", "win32", "x64"),
        ("macos-latest", "darwin", "arm64"),
    )


@dataclasses.dataclass(frozen=True)
class PythonManifest:
    """One validated Python release manifest: the exact release CI installs and the pins installed with it.

    Attributes:
        python: The exact stable release, which is also the manifest's file stem (for example "3.14.7").
        release: The same release as (major, minor, patch), for ordering and floor checks.
        dependencies: Exact name==version pins, each optionally followed by "; marker", in manifest order.
        build_from_source: Pinned distributions pip builds from their sdist because no usable wheel exists.
    """

    python: str
    release: tuple[int, int, int]
    dependencies: tuple[str, ...]
    build_from_source: tuple[str, ...]


def supported_floor(project: Optional[pathlib.Path] = None) -> tuple[int, int, int]:
    """Read the declared Python floor without importing Melder or guessing complex constraints.

    Accept one >=major.minor[.patch] requirement, matching this repository's
    supported-version policy. Refuse other constraint forms so a metadata change
    cannot silently produce a matrix outside the package's declared support.
    """
    path = project if project is not None else pathlib.Path(__file__).resolve().parents[2] / "pyproject.toml"
    with path.open("rb") as stream:
        document = tomllib.load(stream)
    requirement = object_value(document.get("project"), "project").get("requires-python")
    match = re.fullmatch(r">=([1-9]\d*)\.(0|[1-9]\d*)(?:\.(0|[1-9]\d*))?", str(requirement))
    if match is None:
        raise ValueError("Python matrix needs one >=major.minor[.patch] floor in project.requires-python.")
    return int(match[1]), int(match[2]), int(match[3] or 0)


def stable_version(value: object) -> tuple[int, int, int]:
    """Parse one exact final Python release; reject prereleases, ranges and unsafe artifact labels."""
    if not isinstance(value, str) or re.fullmatch(r"[1-9]\d*\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", value) is None:
        raise ValueError(f"Expected an exact stable Python release, received {value!r}.")
    major, minor, patch = value.split(".")
    return int(major), int(minor), int(patch)


def version_matrix(versions: Sequence[str], floor: tuple[int, int, int]) -> dict[str, list[dict[str, str]]]:
    """Build the complete OS/release product for every selected stable Python release.

    Every release is its own entry, several patches of one minor included: a user's
    other dependencies can hold them on an older patch, and the package claims that
    patch too. Every release gets all three runner architectures, ordered by release
    then runner; an excessive matrix fails instead of truncating tests.

    Args:
        versions: Exact stable releases such as "3.14.0"; order does not matter.
        floor: The supported floor read from project.requires-python.

    Returns:
        The {"include": [...]} matrix GitHub Actions expands into jobs.

    Raises:
        ValueError: When the list is empty, repeats a release, holds a release below the
            floor, omits the floor's minor, names an unsafe or non-final version, or needs
            more jobs than RuntimeMatrixPolicy.MAX_JOBS.
    """
    parsed = [stable_version(version) for version in versions]
    if not parsed:
        raise ValueError("Runtime matrix needs at least one stable Python release.")
    if len(set(parsed)) != len(parsed):
        raise ValueError(f"Runtime matrix lists a Python release more than once: {sorted(versions)}.")
    floor_label = ".".join(map(str, floor))
    if any(version < floor for version in parsed) or floor[:2] not in {version[:2] for version in parsed}:
        raise ValueError(f"Runtime matrix must cover the supported floor {floor_label} and nothing below it; "
                         f"received {sorted(versions)}.")
    jobs = len(parsed) * len(RuntimeMatrixPolicy.TARGETS)
    if jobs > RuntimeMatrixPolicy.MAX_JOBS:
        raise ValueError(f"Runtime matrix needs {jobs} jobs, over the job limit of {RuntimeMatrixPolicy.MAX_JOBS}; "
                         "raise the floor in project.requires-python or raise the limit deliberately.")
    return {"include": [
        {"os": runner, "python": ".".join(map(str, version)), "architecture": architecture}
        for version in sorted(parsed)
        for runner, _, architecture in RuntimeMatrixPolicy.TARGETS
    ]}


def canonical_name(name: str) -> str:
    """Normalize a distribution name the way package indexes compare names (PEP 503)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def load_manifest(path: pathlib.Path) -> PythonManifest:
    """Read and validate one Python release manifest.

    A manifest is a TOML file named after its exact stable release (3.14.7.toml). It holds python (that
    release), freethreaded (true: Melder CI qualifies free-threaded builds only), dependencies (exact
    name==version pins, each optionally followed by "; marker", one entry per distribution) and, optionally,
    build_from_source (pinned distributions pip must build from their sdist).

    Args:
        path: The manifest file.

    Returns:
        The validated manifest.

    Raises:
        ValueError: When the path is not a .toml file or not valid TOML, names another release or a
            non-final one, has missing or unknown keys, is not free-threaded, pins a dependency inexactly
            or twice, or builds from source a distribution it does not pin.
    """
    if path.suffix != ".toml" or not path.is_file():
        raise ValueError(f"Python manifest must be a .toml file: {path.name!r}.")
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"Python manifest {path.name!r} is not valid TOML: {error}.") from error
    keys = set(document)
    if keys - RuntimeMatrixPolicy.MANIFEST_KEYS or not {"python", "freethreaded", "dependencies"} <= keys:
        raise ValueError(f"Python manifest {path.name!r} needs python, freethreaded and dependencies and may add only "
                         f"build_from_source; found {sorted(keys)}.")
    python = document["python"]
    release = stable_version(python)
    if path.stem != python:
        raise ValueError(f"Python manifest {path.name!r} declares python = {python!r}; name the file {python}.toml.")
    if document["freethreaded"] is not True:
        raise ValueError(f"Python manifest {path.name!r} must set freethreaded = true; CI qualifies free-threaded "
                         "builds only.")
    dependencies = document["dependencies"]
    if not isinstance(dependencies, list) or not dependencies:
        raise ValueError(f"Python manifest {path.name!r} must list its exact dependency pins.")
    names: list[str] = []
    for dependency in dependencies:
        pin = (re.fullmatch(r"([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)==([0-9][A-Za-z0-9.+!_-]*)(?:\s*;\s*\S.*)?",
                            dependency) if isinstance(dependency, str) else None)
        if pin is None:
            raise ValueError(f"Python manifest {path.name!r} lists {dependency!r}; every dependency must be an exact "
                             "name==version pin, optionally followed by '; marker'.")
        names.append(canonical_name(pin[1]))
    if len(set(names)) != len(names):
        raise ValueError(f"Python manifest {path.name!r} pins a distribution more than once: {sorted(names)}.")
    source = document.get("build_from_source", [])
    if (not isinstance(source, list) or not all(isinstance(name, str) for name in source)
            or not {canonical_name(name) for name in source} <= set(names)):
        raise ValueError(f"Python manifest {path.name!r} may build from source only distributions it pins; "
                         f"build_from_source = {source!r}.")
    return PythonManifest(python, release, tuple(dependencies), tuple(source))


def load_manifests(directory: pathlib.Path, floor: tuple[int, int, int]) -> list[PythonManifest]:
    """Load every manifest in one directory, ordered by release.

    Every entry must be a manifest. A stray file or a release below the supported floor is refused rather
    than skipped, so raising project.requires-python forces the old manifests out instead of leaving them
    silently unused.

    Raises:
        ValueError: When the directory is missing or empty, holds a non-manifest entry, a manifest fails
            load_manifest, or a release sits below the floor.
    """
    if not directory.is_dir():
        raise ValueError(f"Python manifest directory is missing: {directory}.")
    loaded = sorted((load_manifest(path) for path in sorted(directory.iterdir())), key=lambda item: item.release)
    if not loaded:
        raise ValueError(f"Python manifest directory is empty: {directory}; add one manifest per release.")
    floor_label = ".".join(map(str, floor))
    below = [manifest.python for manifest in loaded if manifest.release < floor]
    if below:
        raise ValueError(f"Python manifests {below} sit below the supported floor {floor_label}; delete them or "
                         "lower project.requires-python.")
    return loaded


def discover_matrix(directory: pathlib.Path, floor: tuple[int, int, int],
                    releases: str = CIPolicy.FULL_RELEASES) -> dict[str, list[dict[str, str]]]:
    """Build the runtime (and release-candidate) matrix from the test manifests: the selected releases, every runner.

    Nothing is looked up on the network: a Python release runs only once a manifest names it (owner
    ruling, 2026-10-05). The supported floor release itself must have a manifest, so CI tests the oldest
    release the package claims.

    Args:
        directory: The test manifest directory.
        floor: The supported floor read from project.requires-python.
        releases: CIPolicy.FULL_RELEASES ("all", the default) keeps every manifest. CIPolicy.SLICED_RELEASES
            ("floor-and-newest") keeps the floor and the newest manifest, picked by version, which is what a
            pull request into dev runs (ci_policy.runtime_releases); with one manifest that is one release.

    Raises:
        ValueError: For an unknown release selection, as load_manifests, when the floor release has no
            manifest, or when the matrix needs more jobs than RuntimeMatrixPolicy.MAX_JOBS.
    """
    if releases not in CIPolicy.RUNTIME_RELEASES:
        raise ValueError(f"Unknown runtime release selection {releases!r}; expected one of "
                         f"{list(CIPolicy.RUNTIME_RELEASES)}.")
    loaded = load_manifests(directory, floor)
    if floor not in {manifest.release for manifest in loaded}:
        floor_label = ".".join(map(str, floor))
        raise ValueError(f"Python {floor_label} (the supported floor) has no test manifest; add {floor_label}.toml "
                         "or raise project.requires-python.")
    if releases == CIPolicy.SLICED_RELEASES:
        # load_manifests orders by release and refuses anything below the floor, so the first manifest is the
        # floor release itself and the last is the newest.
        loaded = [loaded[0]] if len(loaded) == 1 else [loaded[0], loaded[-1]]
    return version_matrix([manifest.python for manifest in loaded], floor)


def speed_manifest(directory: pathlib.Path, floor: tuple[int, int, int]) -> PythonManifest:
    """Return the single speed-test manifest: benchmark numbers compare only on one fixed release.

    Raises:
        ValueError: As load_manifests, or when the directory holds more than one manifest.
    """
    loaded = load_manifests(directory, floor)
    if len(loaded) != 1:
        raise ValueError(f"Speed tests need exactly one manifest in {directory}; found "
                         f"{[manifest.python for manifest in loaded]}. Replace the manifest to move them.")
    return loaded[0]


def requirements_text(manifest: PythonManifest) -> str:
    """Render a manifest's pins as a requirements file: one pin per line, in manifest order."""
    return "\n".join(manifest.dependencies) + "\n"


def speed_install_command(manifest: PythonManifest, requirements: pathlib.Path,
                          report: pathlib.Path) -> list[str]:
    """Return the pip command that installs exactly one speed manifest into the running interpreter.

    Every pin installs as a prebuilt wheel except the manifest's build_from_source entries, which pip builds
    from their sdist (dependency-injector publishes no free-threaded wheel). --only-binary=:all: comes first:
    pip applies the two options in command-line order, and :all: discards every exception named before it.

    Args:
        manifest: The validated speed manifest.
        requirements: The file holding the manifest's pins, as requirements_text renders them.
        report: Where pip writes its JSON installation report.

    Returns:
        The argument vector, starting with the running interpreter.
    """
    return [sys.executable, "-m", "pip", "install", "--only-binary=:all:",
            *(f"--no-binary={name}" for name in manifest.build_from_source),
            "--report", str(report), "-r", str(requirements)]


def install_speed_manifest(manifest: PythonManifest, results: pathlib.Path, release: str,
                           freethreaded: bool) -> int:
    """Install a speed manifest's pins into the running interpreter and keep the install evidence.

    The install runs only in the free-threaded release the manifest names, so a benchmark never measures
    libraries installed for another Python. requirements.txt, install.log and install-report.json land in
    results beside the benchmark's other evidence; pip's output is also echoed to the job log as it arrives.

    Args:
        manifest: The validated speed manifest.
        results: The benchmark's evidence directory; created when missing.
        release: The running interpreter's release, as platform.python_version() reports it.
        freethreaded: Whether the running interpreter is a free-threaded build.

    Returns:
        pip's exit status; zero means every pin installed.

    Raises:
        ValueError: When the running interpreter is not the manifest's free-threaded release. Nothing is
            written or installed then.
    """
    if release != manifest.python or not freethreaded:
        build = "free-threaded" if freethreaded else "GIL-enabled"
        raise ValueError(f"The speed manifest names free-threaded Python {manifest.python}, but this interpreter "
                         f"is {build} Python {release}; set up the release the manifest names before installing.")
    results.mkdir(parents=True, exist_ok=True)
    requirements = results / "requirements.txt"
    requirements.write_text(requirements_text(manifest), encoding="utf-8")
    command = speed_install_command(manifest, requirements, results / "install-report.json")
    with (results / "install.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   encoding="utf-8", errors="replace")
        for line in process.stdout:
            print(line, end="", flush=True)
            log.write(line)
            log.flush()
        return process.wait()


def validate_matrix(value: object, floor: tuple[int, int, int]) -> dict[str, list[dict[str, str]]]:
    """Require the exact complete matrix shape before using its labels in report paths."""
    document = object_value(value, "runtime matrix")
    entries = document.get("include")
    if set(document) != {"include"} or not isinstance(entries, list):
        raise ValueError("Runtime matrix must contain an include list only.")
    versions: set[str] = set()
    for entry in entries:
        version = object_value(entry, "matrix entry").get("python")
        stable_version(version)
        versions.add(str(version))
    expected = version_matrix(sorted(versions, key=stable_version), floor)
    if document != expected:
        raise ValueError("Runtime matrix has missing, duplicate or unexpected OS/version entries.")
    return expected


def require_coverage(directory: pathlib.Path, matrix: Mapping[str, list[dict[str, str]]],
                     run_id: str, attempt: str) -> list[pathlib.Path]:
    """Select the newest report for every required OS/version within this immutable workflow run.

    Partial reruns retain successful cells from earlier attempts. Payload names
    preserve OS/version/run/attempt even when the download action flattens one
    artifact. Reject missing cells, foreign/future evidence and an empty newest
    report; never fall back past that invalid report. Valid obsolete version
    cells are excluded from the upload. Inputs must pass validate_matrix first.
    """
    if re.fullmatch(r"[1-9]\d*", run_id) is None or re.fullmatch(r"[1-9]\d*", attempt) is None:
        raise ValueError("Coverage reports require positive run and attempt identifiers.")
    if not directory.is_dir():
        raise ValueError("No coverage reports were downloaded for this workflow run.")
    required = {(entry["os"], entry["python"]) for entry in matrix["include"]}
    selected: dict[tuple[str, str], tuple[int, pathlib.Path]] = {}
    for report in sorted(directory.iterdir()):
        identity = re.fullmatch(r"coverage-(.+)-python-(\d+\.\d+\.\d+)-([1-9]\d*)-([1-9]\d*)\.xml", report.name)
        if identity is None or report.is_symlink() or not report.is_file():
            raise ValueError(f"Coverage report lacks a regular identity-bearing XML payload: {report.name!r}.")
        runner, version, source_run, source_attempt = identity.groups()
        stable_version(version)
        if runner not in {target[0] for target in RuntimeMatrixPolicy.TARGETS}:
            raise ValueError(f"Unknown coverage platform in {report.name!r}.")
        if source_run != run_id or int(source_attempt) > int(attempt):
            raise ValueError(f"Coverage report belongs to another run or a future attempt: {report.name!r}.")
        cell = runner, version
        if cell in required and (cell not in selected or int(source_attempt) > selected[cell][0]):
            selected[cell] = int(source_attempt), report
    missing = required - set(selected)
    if missing:
        raise ValueError(f"Coverage matrix is incomplete; missing OS/Python cells: {sorted(missing)}.")
    reports = [selected[cell][1] for cell in sorted(required)]
    for report in reports:
        if report.stat().st_size == 0:
            raise ValueError(f"Newest coverage report is empty: {report.name!r}; regenerate that cell's report.")
    return reports


def stage_coverage(reports: Sequence[pathlib.Path], directory: pathlib.Path, record: pathlib.Path) -> None:
    """Copy only the verified selection to an empty upload directory and record its original identities.

    Never delete or overwrite an existing output set. Validation must finish
    before this function is called; a copy failure prevents the upload step.
    """
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("Selected coverage output must be empty; choose a fresh upload directory.")
    for report in reports:
        shutil.copyfile(report, directory / report.name)
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps({"reports": [report.name for report in reports]}, indent=2) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Build a matrix, name or install the speed-test release, write one cell's pins, or verify coverage.

    discover writes the runtime/RC matrix built from the test manifests to --report and to
    GITHUB_OUTPUT (matrix=...); --releases picks every manifest (all, the default) or the floor and newest
    (floor-and-newest, for a pull request into dev). speed writes the single speed-test release to
    GITHUB_OUTPUT (python=...).
    speed-install installs the speed manifest's pins into the running interpreter, which must be that
    manifest's free-threaded release, keeps the evidence under --results and returns pip's exit status.
    requirements writes one manifest's pins to --output for an install without dependency resolution.
    coverage verifies and stages this run's reports against CI_PYTHON_MATRIX. Every failure raises;
    nothing falls back to a default release.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("discover", "speed", "speed-install", "requirements", "coverage"))
    parser.add_argument("--manifests", type=pathlib.Path)
    parser.add_argument("--releases", choices=CIPolicy.RUNTIME_RELEASES, default=CIPolicy.FULL_RELEASES)
    parser.add_argument("--manifest", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("reports/requirements.txt"))
    parser.add_argument("--results", type=pathlib.Path)
    parser.add_argument("--report", type=pathlib.Path, default=pathlib.Path("reports/python-matrix.json"))
    parser.add_argument("--directory", type=pathlib.Path, default=pathlib.Path("coverage-reports"))
    parser.add_argument("--selected-directory", type=pathlib.Path, default=pathlib.Path("selected-coverage"))
    parser.add_argument("--selection-report", type=pathlib.Path, default=pathlib.Path("reports/coverage-selection.json"))
    args = parser.parse_args(argv)
    floor = supported_floor()
    root = pathlib.Path(__file__).resolve().parents[2]
    if args.operation == "discover":
        directory = args.manifests or root / RuntimeMatrixPolicy.TESTS_DIRECTORY
        matrix = discover_matrix(directory, floor, args.releases)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
        with pathlib.Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write("matrix=" + json.dumps(matrix, separators=(",", ":")) + "\n")
        print(f"Selected {len(matrix['include'])} OS/Python combinations from the test manifests "
              f"({args.releases}).")
    elif args.operation == "speed":
        manifest = speed_manifest(args.manifests or root / RuntimeMatrixPolicy.SPEED_DIRECTORY, floor)
        with pathlib.Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"python={manifest.python}\n")
        print(f"Speed tests run Python {manifest.python} free-threaded.")
    elif args.operation == "speed-install":
        if args.results is None:
            parser.error("speed-install needs --results")
        manifest = speed_manifest(args.manifests or root / RuntimeMatrixPolicy.SPEED_DIRECTORY, floor)
        return install_speed_manifest(manifest, args.results, platform.python_version(),
                                      sysconfig.get_config_var("Py_GIL_DISABLED") == 1)
    elif args.operation == "requirements":
        if args.manifest is None:
            parser.error("requirements needs --manifest")
        manifest = load_manifest(args.manifest)
        if manifest.release < floor:
            raise ValueError(f"Python {manifest.python} sits below the supported floor; its manifest cannot run.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(requirements_text(manifest), encoding="utf-8")
        print(f"Wrote {len(manifest.dependencies)} pins for Python {manifest.python} to {args.output}.")
    else:
        matrix = validate_matrix(json.loads(os.environ["CI_PYTHON_MATRIX"]), floor)
        reports = require_coverage(args.directory, matrix, os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"])
        stage_coverage(reports, args.selected_directory, args.selection_report)
        print(f"OK: selected {len(reports)} same-run reports covering the complete no-GIL matrix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
