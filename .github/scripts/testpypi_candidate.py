"""Verify TestPyPI uploads and exercise the exact downloaded wheel without checkout imports."""

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import venv
from collections.abc import Mapping, Sequence
from typing import Optional, TypedDict

from ci_policy import git_output, object_value, text_value
from verify_distributions import assignment, verify_distributions


class FileIdentity(TypedDict):
    """Value-only identity of one distribution, shared with the TestPyPI JSON API."""

    sha256: str
    size: int


class TestIndexPolicy:
    """Keep fixed service endpoints and bounded index-propagation retry policy together."""

    INDEX = "https://test.pypi.org/simple/"
    JSON_ROOT = "https://test.pypi.org/pypi/melder/"
    DOWNLOAD_ATTEMPTS = 6
    RETRY_SECONDS = 10


def package_version() -> str:
    """Read the committed stable/RC version without importing or rewriting Melder."""
    version = assignment(pathlib.Path("src/melder/__version__.py").read_text(encoding="utf-8"), "__version__")
    if re.fullmatch(r"\d+\.\d+\.\d+(?:rc\d+)?", version) is None:
        raise ValueError("Use an explicit X.Y.Z or X.Y.ZrcN candidate version and regenerate its assets.")
    return version


def file_identity(path: pathlib.Path) -> FileIdentity:
    """Hash a regular local file and close the stream; never follow distribution symlinks."""
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Distribution must be a regular file: {path.name}")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"sha256": digest, "size": path.stat().st_size}


def verified_files(directory: pathlib.Path, version: str) -> dict[str, FileIdentity]:
    """Inspect the wheel/sdist contents before treating their names and hashes as expected inputs."""
    verify_distributions(directory, version)
    return {path.name: file_identity(path) for path in sorted(directory.iterdir())}


def remote_files(version: str) -> dict[str, FileIdentity]:
    """Read one exact TestPyPI release; only a 404 means no previous upload.

    Missing/duplicate/malformed file evidence fails closed. Every HTTP stream is
    closed, and no credentials are needed or sent to this public index endpoint.
    """
    request = urllib.request.Request(
        TestIndexPolicy.JSON_ROOT + urllib.parse.quote(version, safe="") + "/json",
        headers={"User-Agent": "melder-candidate-ci", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = object_value(json.load(response), "TestPyPI release")
    except urllib.error.HTTPError as error:
        error.close()
        if error.code == 404:
            return {}
        raise
    if object_value(payload.get("info"), "release.info").get("version") != version:
        raise ValueError("TestPyPI returned a different package version.")
    urls = payload.get("urls")
    if not isinstance(urls, list):
        raise ValueError("TestPyPI release has no file list.")
    files: dict[str, FileIdentity] = {}
    for value in urls:
        item = object_value(value, "release file")
        name = text_value(item.get("filename"), "filename")
        digest = object_value(item.get("digests"), "digests").get("sha256")
        size = item.get("size")
        if (name in files or not isinstance(digest, str)
                or re.fullmatch(r"[0-9a-f]{64}", digest) is None
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0):
            raise ValueError("TestPyPI returned ambiguous or invalid file identity.")
        files[name] = {"sha256": digest, "size": size}
    return files


def missing_files(expected: Mapping[str, FileIdentity], remote: Mapping[str, FileIdentity]) -> list[str]:
    """Allow identical retries/partial uploads and refuse any conflicting or additional remote file."""
    for name, identity in remote.items():
        if name not in expected or identity != expected[name]:
            raise ValueError(
                f"TestPyPI already has different files for this version ({name}). "
                "Choose a new candidate version, regenerate assets, and rebuild."
            )
    return sorted(set(expected) - set(remote))


def write_report(path: pathlib.Path, version: str, files: Mapping[str, FileIdentity], status: str) -> None:
    """Retain this run's exact package and source identity as a small, credential-free JSON report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": status, "version": version, "files": dict(files),
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "commit": git_output(("rev-parse", "HEAD^{commit}")),
        "tree": git_output(("rev-parse", "HEAD^{tree}")),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "local"),
    }
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def prepare_upload(directory: pathlib.Path, upload_directory: pathlib.Path, report: pathlib.Path) -> bool:
    """Stage only absent, verified distributions; never conceal conflicting files with skip-existing."""
    version = package_version()
    files = verified_files(directory, version)
    missing = missing_files(files, remote_files(version))
    upload_directory.mkdir(parents=True, exist_ok=True)
    if any(upload_directory.iterdir()):
        raise ValueError("Upload staging directory must be empty; refusing stale distribution files.")
    for name in missing:
        shutil.copyfile(directory / name, upload_directory / name)
    write_report(report, version, files, "upload-needed" if missing else "identical-upload-present")
    return bool(missing)


def download_wheel(directory: pathlib.Path, version: str, name: str, identity: FileIdentity) -> pathlib.Path:
    """Resolve the exact wheel through TestPyPI's index with a required SHA256 and bounded retries.

    Pip runs without user/environment configuration, extra indexes, dependencies,
    or its cache. Retry download failures for index propagation; package execution
    happens later and is never retried or softened. A final failure propagates.
    """
    requirement = directory / "requirement.txt"
    requirement.write_text(f"melder=={version} --hash=sha256:{identity['sha256']}\n", encoding="utf-8")
    downloads = directory / "downloads"
    downloads.mkdir()
    command = [sys.executable, "-m", "pip", "--isolated", "download", "--no-deps", "--no-cache-dir",
               "--only-binary=:all:", "--index-url", TestIndexPolicy.INDEX, "--require-hashes",
               "--dest", str(downloads), "-r", str(requirement)]
    for attempt in range(TestIndexPolicy.DOWNLOAD_ATTEMPTS):
        try:
            subprocess.run(command, check=True, cwd=directory)
            break
        except subprocess.CalledProcessError:
            if attempt + 1 == TestIndexPolicy.DOWNLOAD_ATTEMPTS:
                raise
            time.sleep(TestIndexPolicy.RETRY_SECONDS)
    wheel = downloads / name
    if set(downloads.iterdir()) != {wheel} or file_identity(wheel) != identity:
        raise ValueError("Downloaded TestPyPI wheel differs from this run's verified candidate.")
    return wheel


def probe_install(directory: pathlib.Path, report: pathlib.Path) -> None:
    """Install the hash-pinned index wheel into a fresh environment and run the isolated smoke probe.

    The repository's conftest and editable installation are never used. Downloads
    and the virtual environment are owned by one temporary-directory context and
    removed on success or failure. The report is written only after the probe passes.
    """
    version = package_version()
    files = verified_files(directory, version)
    name = next(name for name in files if name.endswith(".whl"))
    smoke = pathlib.Path(__file__).with_name("smoke_wheel.py").resolve()
    with tempfile.TemporaryDirectory(prefix="melder-testpypi-", dir=os.environ.get("RUNNER_TEMP")) as scratch:
        root = pathlib.Path(scratch)
        wheel = download_wheel(root, version, name, files[name])
        environment = root / "environment"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run([str(python), "-m", "pip", "--isolated", "install", "--no-deps",
                        "--no-index", str(wheel)], check=True, cwd=root)
        subprocess.run([str(python), "-I", str(smoke), "--expected-version", version], check=True, cwd=root)
    write_report(report, version, files, "installed-package-passed")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Prepare a verified upload or test the exact installed index package; never perform an upload."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("prepare-upload", "probe-install"))
    parser.add_argument("--directory", type=pathlib.Path, default=pathlib.Path("dist"))
    parser.add_argument("--upload-directory", type=pathlib.Path, default=pathlib.Path("upload"))
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args(argv)
    if args.operation == "prepare-upload":
        required = prepare_upload(args.directory, args.upload_directory, args.report)
        with pathlib.Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
            output.write(f"upload-required={str(required).lower()}\n")
    else:
        probe_install(args.directory, args.report)
    print(f"OK: {args.operation}; report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
