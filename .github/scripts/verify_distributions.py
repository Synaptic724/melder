"""Verify wheel/sdist boundaries and version identity without importing Melder."""

import argparse
import ast
import email.parser
import pathlib
import re
import tarfile
import zipfile
from collections.abc import Sequence
from typing import Optional


class DistributionPolicy:
    """Define the package files and archive boundaries required for a Melder release."""

    REQUIRED: frozenset[str] = frozenset({
        "melder/py.typed",
        "melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py",
        "melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py",
        "melder/_build_assets/_system_documents/manifest/graph_adjacency_manifest.py",
        "melder/_build_assets/_system_documents/manifest/system_documents_index.py",
        "melder/_build_assets/_system_documents/manifest/system_documents_manifest.py",
        "melder/_build_assets/_system_documents/payloads/src_architecture_payload.py",
        "melder/_build_assets/_system_documents/payloads/src_components_payload.py",
        "melder/_build_assets/_system_documents/payloads/src_graph_payload.py",
    })
    VERSION_MANIFESTS: tuple[str, ...] = (
        "melder/_build_assets/_agent_documentation/manifest/agent_documentation_manifest.py",
        "melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py",
        "melder/_build_assets/_system_documents/manifest/system_documents_manifest.py",
    )
    ROOT_FILES: frozenset[str] = frozenset({
        "LICENSE", "NOTICE", "README.md", "pyproject.toml", "PKG-INFO", "setup.cfg",
    })
    FORBIDDEN_SUFFIXES: tuple[str, ...] = (
        ".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".melc", ".prof", ".pstats",
    )


def assignment(source: str, name: str) -> str:
    """Read one literal string assignment through AST; never execute package source."""
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            value = ast.literal_eval(node.value)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a nonempty literal version string.")
            return value
    raise ValueError(f"Required version assignment {name} is absent.")


def unsafe(name: str) -> bool:
    """Identify absolute, traversing, backslash, or drive-qualified archive paths."""
    path = pathlib.PurePosixPath(name)
    return (path.is_absolute() or ".." in path.parts or "\\" in name or "\x00" in name
            or bool(re.match(r"^[A-Za-z]:", name)))


def forbidden(name: str) -> bool:
    """Return whether an archive member is a forbidden cache, database, or profiler output."""
    return "__pycache__" in pathlib.PurePosixPath(name).parts or name.lower().endswith(
        DistributionPolicy.FORBIDDEN_SUFFIXES
    )


def metadata_version(text: str, label: str) -> str:
    """Require matching package name and supported-Python metadata; return the version."""
    metadata = email.parser.Parser().parsestr(text)
    if metadata.get("Name") != "melder" or metadata.get("Requires-Python") != ">=3.14":
        raise ValueError(f"{label} must describe melder with Requires-Python >=3.14.")
    version = metadata.get("Version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"{label} has no package version.")
    return version


def verify_wheel(path: pathlib.Path, expected_version: str) -> None:
    """Verify the wheel's members, metadata, source version, and required generated assets.

    Archive resources are closed on every path. Unexpected roots, duplicate names,
    unsafe/cache members, absent assets, or any version mismatch raise ValueError.
    No wheel contents are imported or extracted.
    """
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if len(names) != len(set(names)):
            raise ValueError("Wheel contains duplicate members.")
        for member in archive.infolist():
            # ZipInfo normalizes separators/NULs on some platforms. Validate the
            # original archive spelling before trusting its normalized lookup key.
            name = member.filename
            if unsafe(member.orig_filename) or unsafe(name) or forbidden(name):
                raise ValueError(f"Unsafe/forbidden wheel member: {name}")
            if not (name.startswith("melder/") or re.match(r"melder-[^/]+\.dist-info/", name)):
                raise ValueError(f"Unexpected wheel root: {name}")
        missing = DistributionPolicy.REQUIRED.difference(names)
        if missing:
            raise ValueError(f"Wheel is missing required assets: {sorted(missing)}")
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("Wheel must contain exactly one METADATA file.")
        versions = {
            metadata_version(archive.read(metadata_names[0]).decode("utf-8"), "wheel METADATA"),
            assignment(archive.read("melder/__version__.py").decode("utf-8"), "__version__"),
        }
        versions.update(assignment(archive.read(name).decode("utf-8"), "BUILT_FOR_VERSION")
                        for name in DistributionPolicy.VERSION_MANIFESTS)
        if versions != {expected_version}:
            raise ValueError(f"Wheel/source/asset versions {sorted(versions)} differ from {expected_version}.")


def tar_text(archive: tarfile.TarFile, name: str) -> str:
    """Read one regular tar member as UTF-8 and close its file handle; fail when missing."""
    member = archive.getmember(name)
    if not member.isfile():
        raise ValueError(f"Required sdist member is not a regular file: {name}")
    stream = archive.extractfile(member)
    if stream is None:
        raise ValueError(f"Cannot read required sdist member: {name}")
    with stream:
        return stream.read().decode("utf-8")


def verify_sdist(path: pathlib.Path, expected_version: str) -> None:
    """Verify sdist boundaries and independently check its metadata/source/asset versions.

    Directories are allowed; links, devices, duplicate files, escaped paths, and
    unrelated project roots are refused. Inspection never extracts the archive.
    """
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        roots = {member.name.split("/", 1)[0] for member in members}
        if len(roots) != 1:
            raise ValueError(f"Sdist must contain one package root, found {sorted(roots)}.")
        root = next(iter(roots))
        names: set[str] = set()
        for member in members:
            if unsafe(member.name) or forbidden(member.name):
                raise ValueError(f"Unsafe/forbidden sdist member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError(f"Sdist contains a non-regular member: {member.name}")
            if member.name in names:
                raise ValueError(f"Duplicate sdist member: {member.name}")
            names.add(member.name)
            relative = member.name.removeprefix(root + "/")
            if not (relative in DistributionPolicy.ROOT_FILES or relative.startswith("src/melder/")
                    or relative.startswith("src/melder.egg-info/")):
                raise ValueError(f"Unexpected sdist member: {member.name}")
        required = {f"{root}/src/{name}" for name in DistributionPolicy.REQUIRED}
        if missing := required.difference(names):
            raise ValueError(f"Sdist is missing required assets: {sorted(missing)}")
        versions = {
            metadata_version(tar_text(archive, f"{root}/PKG-INFO"), "sdist PKG-INFO"),
            assignment(tar_text(archive, f"{root}/src/melder/__version__.py"), "__version__"),
        }
        versions.update(assignment(tar_text(archive, f"{root}/src/{name}"), "BUILT_FOR_VERSION")
                        for name in DistributionPolicy.VERSION_MANIFESTS)
        if versions != {expected_version}:
            raise ValueError(f"Sdist/source/asset versions {sorted(versions)} differ from {expected_version}.")


def verify_distributions(directory: pathlib.Path, expected_version: str,
                         release_tag: str = "") -> None:
    """Require exactly one wheel and sdist matching the selected checkout and optional tag."""
    wheels = list(directory.glob("*.whl"))
    sdists = list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError(f"Expected one wheel and one sdist; found {len(wheels)} and {len(sdists)}.")
    if set(directory.iterdir()) != set(wheels + sdists):
        raise ValueError("Distribution directory contains files outside the verified wheel/sdist pair.")
    if release_tag and release_tag.removeprefix("v") != expected_version:
        raise ValueError(f"Release tag {release_tag!r} does not match package version {expected_version!r}.")
    verify_wheel(wheels[0], expected_version)
    verify_sdist(sdists[0], expected_version)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Inspect built/downloaded distributions against the checked-out source version."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=pathlib.Path, default=pathlib.Path("dist"))
    parser.add_argument("--release-tag", default="")
    args = parser.parse_args(argv)
    version = assignment(pathlib.Path("src/melder/__version__.py").read_text(encoding="utf-8"),
                         "__version__")
    verify_distributions(args.directory, version, args.release_tag)
    print(f"OK: wheel and sdist are bounded, complete, and version-consistent ({version}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
