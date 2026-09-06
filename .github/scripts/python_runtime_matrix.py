"""Discover stable supported no-GIL runtimes and verify their coverage report inventory."""

import argparse
import json
import os
import pathlib
import re
import tomllib
import urllib.request
from collections.abc import Mapping, Sequence
from typing import Optional

from ci_policy import object_value


class RuntimeMatrixPolicy:
    """Keep discovery bounds and the supported runner architectures in one place."""

    MANIFEST_URL = "https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json"
    MAX_MANIFEST_BYTES = 8 * 1024 * 1024
    MAX_JOBS = 256
    TARGETS = (
        ("ubuntu-latest", "linux", "x64"),
        ("windows-latest", "win32", "x64"),
        ("macos-latest", "darwin", "arm64"),
    )


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
    """Build the complete OS/version product, refusing empty, duplicate, or below-floor versions.

    One patch per minor is intentional. Every selected minor gets all three
    runner architectures; an excessive matrix fails instead of truncating tests.
    """
    parsed = [stable_version(version) for version in versions]
    minors = [version[:2] for version in parsed]
    if (not parsed or len(set(minors)) != len(minors) or floor[:2] not in minors
            or any(version < floor for version in parsed)
            or len(parsed) * len(RuntimeMatrixPolicy.TARGETS) > RuntimeMatrixPolicy.MAX_JOBS):
        raise ValueError("Runtime matrix must cover the supported floor and one patch per minor within the job limit.")
    return {"include": [
        {"os": runner, "python": ".".join(map(str, version)), "architecture": architecture}
        for version in sorted(parsed)
        for runner, _, architecture in RuntimeMatrixPolicy.TARGETS
    ]}


def discover_matrix(payload: object, floor: tuple[int, int, int]) -> dict[str, list[dict[str, str]]]:
    """Select the latest stable patch per supported minor from the official release manifest.

    Stable false entries are excluded, including prereleases. Every chosen
    release must advertise free-threaded assets for all supported platforms.
    Missing assets fail rather than substituting normal Python or an older patch.
    Asset URLs are never followed here; setup-python owns interpreter installation.
    """
    if not isinstance(payload, list):
        raise ValueError("Python release manifest must be a list.")
    releases: dict[tuple[int, int, int], set[tuple[str, str]]] = {}
    for value in payload:
        release = object_value(value, "Python release")
        if type(release.get("stable")) is not bool:
            raise ValueError("Python release is missing its explicit stable flag.")
        if not release["stable"]:
            continue
        version = stable_version(release.get("version"))
        if version < floor:
            continue
        files = release.get("files")
        if not isinstance(files, list):
            raise ValueError("Stable Python release is missing its asset list.")
        available = releases.setdefault(version, set())
        for item in files:
            asset = object_value(item, "Python asset")
            platform, architecture = asset.get("platform"), asset.get("arch")
            if not isinstance(platform, str) or not isinstance(architecture, str):
                raise ValueError("Python asset must identify its platform and architecture.")
            available.add((platform, architecture))
    latest: dict[tuple[int, int], tuple[int, int, int]] = {}
    for version in sorted(releases):
        latest[version[:2]] = version
    versions = [".".join(map(str, version)) for version in sorted(latest.values())]
    matrix = version_matrix(versions, floor)
    for version in latest.values():
        missing = [runner for runner, platform, architecture in RuntimeMatrixPolicy.TARGETS
                   if (platform, architecture + "-freethreaded") not in releases[version]]
        if missing:
            label = ".".join(map(str, version))
            raise ValueError(f"Python {label} lacks free-threaded assets for {missing}; cannot qualify every platform.")
    return matrix


def fetch_manifest() -> object:
    """Read bounded public release metadata with a timeout and no authentication or executable content."""
    request = urllib.request.Request(RuntimeMatrixPolicy.MANIFEST_URL,
                                     headers={"User-Agent": "melder-runtime-ci", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(RuntimeMatrixPolicy.MAX_MANIFEST_BYTES + 1)
    if len(raw) > RuntimeMatrixPolicy.MAX_MANIFEST_BYTES:
        raise ValueError("Python release manifest exceeds the permitted size.")
    return json.loads(raw)


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
                     run_id: str, attempt: str) -> None:
    """Require a nonempty coverage report for every discovered OS/version from this run attempt.

    Reject missing and unexpected report directories before Codecov receives a
    partial matrix. Inputs must already have passed validate_matrix.
    """
    if re.fullmatch(r"[1-9]\d*", run_id) is None or re.fullmatch(r"[1-9]\d*", attempt) is None:
        raise ValueError("Coverage reports require positive run and attempt identifiers.")
    names = {f"coverage-{entry['os']}-python-{entry['python']}-{run_id}-{attempt}" for entry in matrix["include"]}
    observed = {path.name for path in directory.iterdir()}
    if observed != names:
        raise ValueError(f"Coverage matrix differs: missing={sorted(names - observed)}, unexpected={sorted(observed - names)}.")
    for name in sorted(names):
        report = directory / name / "coverage.xml"
        if not report.is_file() or report.stat().st_size == 0:
            raise ValueError(f"Missing or empty coverage report: {name}/coverage.xml")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Discover/record a matrix or verify reports; propagate discovery and completeness failures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("discover", "coverage"))
    parser.add_argument("--report", type=pathlib.Path, default=pathlib.Path("reports/python-matrix.json"))
    parser.add_argument("--directory", type=pathlib.Path, default=pathlib.Path("coverage-reports"))
    args = parser.parse_args(argv)
    floor = supported_floor()
    if args.operation == "discover":
        matrix = discover_matrix(fetch_manifest(), floor)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
        with pathlib.Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write("matrix=" + json.dumps(matrix, separators=(",", ":")) + "\n")
        print(f"Selected {len(matrix['include'])} stable no-GIL OS/version combinations.")
    else:
        matrix = validate_matrix(json.loads(os.environ["CI_PYTHON_MATRIX"]), floor)
        require_coverage(args.directory, matrix, os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"])
        print("OK: coverage reports cover the complete discovered no-GIL matrix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
