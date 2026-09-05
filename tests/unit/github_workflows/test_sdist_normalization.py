"""Guard reproducible source uploads without hiding changes to packaged file contents."""

import hashlib
import io
import pathlib
import tarfile
from types import ModuleType

import pytest


def source_archive(path: pathlib.Path, timestamp: int, content: bytes = b"source", reverse: bool = False) -> None:
    """Write identical payloads with deliberately different member order, ownership, and time metadata."""
    folder = tarfile.TarInfo("melder-0.2.4")
    folder.type = tarfile.DIRTYPE
    source = tarfile.TarInfo("melder-0.2.4/module.py")
    source.size = len(content)
    source.mode = 0o644
    members = [folder, source]
    with tarfile.open(path, "w:gz", format=tarfile.PAX_FORMAT) as output:
        for member in reversed(members) if reverse else members:
            member.mtime = timestamp
            member.uid = member.gid = timestamp
            member.uname = member.gname = str(timestamp)
            member.pax_headers = {"mtime": str(timestamp), "atime": str(timestamp)}
            output.addfile(member, io.BytesIO(content) if member.isfile() else None)


def test_same_contents_become_identical_and_normalization_is_idempotent(normalizer: ModuleType,
                                                                      tmp_path: pathlib.Path) -> None:
    """Metadata-only build differences must not force another candidate version on TestPyPI."""
    left = tmp_path / "left.tar.gz"
    right = tmp_path / "right.tar.gz"
    source_archive(left, 100)
    source_archive(right, 200, reverse=True)
    normalizer.normalize_archive(left, 123456789)
    normalizer.normalize_archive(right, 123456789)
    assert left.read_bytes() == right.read_bytes()
    digest = hashlib.sha256(left.read_bytes()).digest()
    normalizer.normalize_archive(left, 123456789)
    assert hashlib.sha256(left.read_bytes()).digest() == digest
    with tarfile.open(left, "r:gz") as archive:
        member = archive.getmember("melder-0.2.4/module.py")
        assert member.mode == 0o644
        with archive.extractfile(member) as stream:
            assert stream.read() == b"source"


def test_changed_source_still_has_different_distribution_identity(normalizer: ModuleType,
                                                                 tmp_path: pathlib.Path) -> None:
    """Normalization must never make two versions of package code share a distribution hash."""
    left = tmp_path / "left.tar.gz"
    right = tmp_path / "right.tar.gz"
    source_archive(left, 100, b"before")
    source_archive(right, 200, b"after")
    normalizer.normalize_archive(left, 123456789)
    normalizer.normalize_archive(right, 123456789)
    assert left.read_bytes() != right.read_bytes()


@pytest.mark.parametrize(("name", "kind"), [("../escape", tarfile.REGTYPE), ("link", tarfile.SYMTYPE)])
def test_invalid_archive_refusal_preserves_original_file(normalizer: ModuleType, tmp_path: pathlib.Path,
                                                        name: str, kind: bytes) -> None:
    """Escaped names and links cannot be rewritten into a seemingly approved distribution."""
    path = tmp_path / "unsafe.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        member = tarfile.TarInfo(name)
        member.type = kind
        member.linkname = "target" if kind == tarfile.SYMTYPE else ""
        archive.addfile(member)
    original = path.read_bytes()
    with pytest.raises(ValueError, match="unsafe or non-regular"):
        normalizer.normalize_archive(path, 123456789)
    assert path.read_bytes() == original


@pytest.mark.parametrize("epoch", [-1, 2**32])
def test_invalid_timestamp_refuses_before_rewriting(normalizer: ModuleType, tmp_path: pathlib.Path,
                                                  epoch: int) -> None:
    """Bad timestamp configuration must preserve the original artifact for inspection."""
    path = tmp_path / "source.tar.gz"
    source_archive(path, 100)
    original = path.read_bytes()
    with pytest.raises(ValueError, match="SOURCE_DATE_EPOCH"):
        normalizer.normalize_archive(path, epoch)
    assert path.read_bytes() == original
