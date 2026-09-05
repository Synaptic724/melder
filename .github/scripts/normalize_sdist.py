"""Normalize source-archive metadata for repeatable same-commit package uploads."""

import argparse
import copy
import gzip
import os
import pathlib
import tarfile
import tempfile
from collections.abc import Sequence
from typing import Optional

from verify_distributions import assignment, unsafe, verify_sdist


def normalized_member(member: tarfile.TarInfo, epoch: int) -> tarfile.TarInfo:
    """Copy a regular file/directory header, preserving its name, permissions, size, and payload contract."""
    if unsafe(member.name) or not (member.isfile() or member.isdir()):
        raise ValueError(f"Cannot normalize unsafe or non-regular archive member: {member.name}")
    result = copy.copy(member)
    result.mtime = epoch
    result.uid = result.gid = 0
    result.uname = result.gname = ""
    result.pax_headers = {key: value for key, value in member.pax_headers.items()
                          if key not in {"mtime", "atime", "ctime", "uid", "gid", "uname", "gname"}}
    return result


def normalize_archive(path: pathlib.Path, epoch: int) -> None:
    """Atomically rewrite tar/gzip metadata while preserving all file contents.

    Setuptools' sdist includes generated-file and directory timestamps even with
    SOURCE_DATE_EPOCH. Sort members and normalize timestamps/ownership plus the
    gzip header. Reject links/devices/escaped names. Streams and the temporary
    directory are closed on every path; failed normalization leaves the original
    archive intact. This does not rewrite package versions or file contents.
    """
    if not 0 <= epoch <= 0xFFFFFFFF:
        raise ValueError("SOURCE_DATE_EPOCH must fit the gzip timestamp field (0..4294967295).")
    if path.is_symlink() or not path.is_file():
        raise ValueError("Source distribution must be a regular local file.")
    with tempfile.TemporaryDirectory(prefix=".sdist-", dir=path.parent) as scratch:
        target = pathlib.Path(scratch) / path.name
        with tarfile.open(path, "r:gz") as source, target.open("wb") as raw:
            members = sorted(source.getmembers(), key=lambda member: member.name)
            if len({member.name for member in members}) != len(members):
                raise ValueError("Source distribution contains duplicate members.")
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=epoch) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as output:
                    for member in members:
                        header = normalized_member(member, epoch)
                        if member.isdir():
                            output.addfile(header)
                            continue
                        stream = source.extractfile(member)
                        if stream is None:
                            raise ValueError(f"Cannot read source member: {member.name}")
                        with stream:
                            output.addfile(header, stream)
        target.replace(path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Verify package contents, normalize the one sdist, and verify it again using the committed version."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=pathlib.Path, default=pathlib.Path("dist"))
    args = parser.parse_args(argv)
    archives = list(args.directory.glob("*.tar.gz"))
    if len(archives) != 1:
        raise ValueError("Expected exactly one sdist to normalize.")
    version = assignment(pathlib.Path("src/melder/__version__.py").read_text(encoding="utf-8"), "__version__")
    verify_sdist(archives[0], version)
    normalize_archive(archives[0], int(os.environ["SOURCE_DATE_EPOCH"]))
    verify_sdist(archives[0], version)
    print(f"OK: normalized source archive metadata for {version}; package contents verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
