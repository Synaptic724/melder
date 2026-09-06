"""Prove checkout identity using real Git EOL behavior and explicit mutation boundaries."""

import os
import pathlib
import subprocess
from collections.abc import Sequence
from types import ModuleType
from typing import Optional

import pytest


def fixture_git(repository: pathlib.Path, *arguments: str, data: Optional[bytes] = None) -> str:
    """Run Git only in a disposable test repository, without signing or using the owner's identity."""
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", "commit.gpgSign=false",
         "-c", "user.name=CI-test", "-c", "user.email=ci-test@example.invalid",
         "-C", str(repository), *arguments],
        input=data, capture_output=True, check=True,
    )
    return result.stdout.decode("utf-8").strip()


@pytest.fixture
def legacy_checkout(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Commit a raw CRLF fixture beneath a later LF policy, reproducing the hosted false-dirty state.

    Git plumbing creates test objects only in tmp_path. No real repository ref,
    user commit, signature or network operation is involved. Touching mtime
    forces Git to inspect bytes instead of accepting its fresh checkout stat cache.
    """
    repository = tmp_path / "repository"
    repository.mkdir()
    fixture_git(repository, "init", "--quiet")
    fixture_git(repository, "config", "core.autocrlf", "false")
    fixture_git(repository, "config", "core.safecrlf", "false")
    for name, content in ((".gitattributes", b"legacy.md text eol=lf\n"), ("legacy.md", b"unchanged\r\n")):
        blob = fixture_git(repository, "hash-object", "-w", "--stdin", data=content)
        fixture_git(repository, "update-index", "--add", "--cacheinfo", f"100644,{blob},{name}")
    tree = fixture_git(repository, "write-tree")
    commit = fixture_git(repository, "commit-tree", tree, data=b"Disposable qualification fixture\n")
    fixture_git(repository, "update-ref", "HEAD", commit)
    fixture_git(repository, "checkout-index", "--all", "--force")
    legacy = repository / "legacy.md"
    current = legacy.stat()
    os.utime(legacy, ns=(current.st_atime_ns, current.st_mtime_ns + 10_000_000_000))
    monkeypatch.chdir(repository)
    monkeypatch.setenv("GITHUB_SHA", commit)
    return repository


def test_identical_crlf_blob_qualifies_despite_git_dirty_flag(source_qualification: ModuleType,
                                                           legacy_checkout: pathlib.Path) -> None:
    """A Git normalization discrepancy must not reject byte-identical committed source."""
    assert "M legacy.md" in fixture_git(legacy_checkout, "status", "--porcelain", "--untracked-files=no")
    assert (legacy_checkout / "legacy.md").read_bytes() == b"unchanged\r\n"
    (legacy_checkout / "untracked-report.json").write_text("{}", encoding="utf-8")
    assert source_qualification.checkout_identity() == (
        fixture_git(legacy_checkout, "rev-parse", "HEAD"),
        fixture_git(legacy_checkout, "rev-parse", "HEAD^{tree}"),
    )


@pytest.mark.parametrize("change", ["content", "trailing-space", "line-endings", "deleted", "staged", "renamed"])
def test_real_changes_still_refuse_and_identify_the_path(source_qualification: ModuleType,
                                                       legacy_checkout: pathlib.Path, change: str) -> None:
    """The EOL correction cannot waive real bytes, index changes, removal or renaming."""
    legacy = legacy_checkout / "legacy.md"
    if change == "deleted":
        legacy.unlink()
    elif change == "staged":
        fixture_git(legacy_checkout, "add", "--", "legacy.md")
    elif change == "renamed":
        fixture_git(legacy_checkout, "mv", "legacy.md", "renamed.md")
    else:
        legacy.write_bytes({"content": b"different\r\n", "trailing-space": b"unchanged \r\n",
                            "line-endings": b"unchanged\n"}[change])
    with pytest.raises(ValueError, match="legacy.md"):
        source_qualification.checkout_identity()


@pytest.mark.parametrize(("before", "after", "status"), [
    ("100644", "100755", "M"), ("100755", "100644", "M"),
    ("100644", "120000", "T"), ("120000", "120000", "M"),
    ("160000", "160000", "M"), ("100644", "000000", "D"),
    ("000000", "100644", "A"),
])
def test_mode_type_and_structural_changes_cannot_pass_by_hash(source_qualification: ModuleType,
                                                            monkeypatch: pytest.MonkeyPatch,
                                                            before: str, after: str, status: str) -> None:
    """Matching file bytes cannot authorize changed executable mode, symlinks, submodules or structure."""
    def git(arguments: Sequence[str]) -> str:
        """Expose raw Git metadata and forbid content hashing of an already invalid mode/type."""
        if "--cached" in arguments:
            return ""
        assert arguments[0] == "diff"
        return f":{before} {after} {'a' * 40} {'0' * 40} {status}\0changed.py\0"

    monkeypatch.setattr(source_qualification, "git_output", git)
    with pytest.raises(ValueError, match="changed.py"):
        source_qualification.require_clean_tracked_checkout()


@pytest.mark.parametrize("length", [40, 64])
def test_raw_hash_comparison_preserves_unusual_paths(source_qualification: ModuleType,
                                                    monkeypatch: pytest.MonkeyPatch, length: int) -> None:
    """NUL records and explicit argument vectors preserve spaces/newlines without shell interpolation."""
    path = "directory/name with space\nand newline.md"

    def git(arguments: Sequence[str]) -> str:
        """Supply matching native Git object IDs for either supported object format."""
        if "--cached" in arguments:
            return ""
        if arguments[0] == "diff":
            return f":100644 100644 {'a' * length} {'0' * length} M\0{path}\0"
        assert arguments == ("hash-object", "--no-filters", "--", path)
        return "a" * length

    monkeypatch.setattr(source_qualification, "git_output", git)
    source_qualification.require_clean_tracked_checkout()


@pytest.mark.parametrize("raw", ["incomplete", "header\0", "header\0path\0", "bad\0path\0extra\0",
                                  f":100644 100644 {'a' * 40} {'0' * 40} M\0\0"])
def test_malformed_raw_diff_never_becomes_clean(source_qualification: ModuleType,
                                               monkeypatch: pytest.MonkeyPatch, raw: str) -> None:
    """Incomplete Git output must fail closed, including absent metadata/path boundaries."""
    monkeypatch.setattr(source_qualification, "git_output", lambda arguments: "" if "--cached" in arguments else raw)
    with pytest.raises(ValueError, match="Malformed"):
        source_qualification.require_clean_tracked_checkout()
