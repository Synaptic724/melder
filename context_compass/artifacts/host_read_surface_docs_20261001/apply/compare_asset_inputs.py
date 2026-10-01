"""
Compare the build-asset inputs of the device tree and the VM mirror, and optionally
bring the mirror to the device's versions.

Purpose:
    The asset runner cannot run on the device tree (its system-documents builder
    deletes stale payloads, and the connected folder refuses deletes), so it runs
    in the VM mirror. Its output is only valid for the device when the mirror's
    INPUTS equal the device's. This script proves that, file by file.

Contract:
    - Inputs compared: every `*.py` under `src/melder` outside `__pycache__` and
      `__melder_cache__` (newline-canonical bytes, as the builders hash them),
      and the six system documents the system-documents builder ingests (raw
      bytes, as its index proof hashes them).
    - Generated outputs (`_build_assets/*/manifest/`, `_build_assets/*/payloads/`)
      are listed apart: they are expected to differ and are never synced here.
    - `--sync` copies the DEVICE version of each differing or mirror-missing input
      into the mirror, byte for byte. It never deletes; mirror-only inputs are
      reported for a decision.
    - Writes go to the mirror only. The device tree is read, never written.

Usage:
    python compare_asset_inputs.py <device repo root> <mirror repo root> [--sync]
"""

import hashlib
import pathlib
import shutil
import sys
from typing import Dict, List, Tuple


class AssetInputPolicy:
    """
    Constants describing which files are asset inputs.

    Attributes:
        SOURCE_ROOT: Repo-relative package directory both code builders scan.
        SKIP_DIR_NAMES: Directories no builder reads.
        GENERATED_DIR_NAMES: Output directories under `_build_assets`.
        SYSTEM_DOCUMENTS: Repo-relative documents and indexes the
            system-documents builder ingests.
    """

    SOURCE_ROOT: str = "src/melder"
    SKIP_DIR_NAMES: Tuple[str, ...] = ("__pycache__", "__melder_cache__")
    GENERATED_DIR_NAMES: Tuple[str, ...] = ("manifest", "payloads")
    SYSTEM_DOCUMENTS: Tuple[str, ...] = (
        "context_compass/system_docs/src_architecture.md",
        "context_compass/system_docs/src_architecture_index.md",
        "context_compass/system_docs/src_components.md",
        "context_compass/system_docs/src_components_index.md",
        "context_compass/system_docs/src_graph.md",
        "context_compass/system_docs/src_graph_index.md",
    )


def canonical(data: bytes) -> bytes:
    """
    Return `data` with CRLF and lone CR line endings converted to LF.

    Args:
        data: Raw file bytes.

    Returns:
        bytes: Newline-canonical bytes, as the code builders hash them.
    """
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def is_generated(relative: str) -> bool:
    """
    Report whether a repo-relative path is a generated build-asset output.

    Args:
        relative: Repo-relative POSIX path.

    Returns:
        bool: True for files under `_build_assets/<asset>/manifest|payloads/`.
    """
    parts = relative.split("/")
    if "_build_assets" not in parts:
        return False
    return any(part in AssetInputPolicy.GENERATED_DIR_NAMES for part in parts)


def source_digests(repo: pathlib.Path) -> Dict[str, str]:
    """
    Hash every scanned Python source file under the package root.

    Args:
        repo: Repository root.

    Returns:
        Dict[str, str]: Repo-relative path to sha256 of newline-canonical bytes.
    """
    root = repo / AssetInputPolicy.SOURCE_ROOT
    digests: Dict[str, str] = {}
    for path in sorted(root.rglob("*.py")):
        if any(part in AssetInputPolicy.SKIP_DIR_NAMES for part in path.parts):
            continue
        relative = path.relative_to(repo).as_posix()
        digests[relative] = hashlib.sha256(canonical(path.read_bytes())).hexdigest()
    return digests


def document_digests(repo: pathlib.Path) -> Dict[str, str]:
    """
    Hash the system documents and indexes the builder ingests, raw bytes.

    Args:
        repo: Repository root.

    Returns:
        Dict[str, str]: Repo-relative path to sha256 of the raw bytes; a missing
            file maps to the string "<absent>".
    """
    digests: Dict[str, str] = {}
    for relative in AssetInputPolicy.SYSTEM_DOCUMENTS:
        path = repo / relative
        digests[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "<absent>"
    return digests


def compare(device: Dict[str, str], mirror: Dict[str, str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Split two digest maps into differing, device-only and mirror-only paths.

    Args:
        device: Digests of the device tree.
        mirror: Digests of the mirror.

    Returns:
        Tuple[List[str], List[str], List[str]]: Sorted differing, device-only and
            mirror-only paths.
    """
    differing = sorted(p for p in device.keys() & mirror.keys() if device[p] != mirror[p])
    device_only = sorted(device.keys() - mirror.keys())
    mirror_only = sorted(mirror.keys() - device.keys())
    return differing, device_only, mirror_only


def main(argv: List[str]) -> int:
    """
    Compare, report, and optionally sync the mirror's inputs from the device.

    Args:
        argv: `<device root> <mirror root> [--sync]`.

    Returns:
        int: 0 when the inputs agree (after a sync, when requested), else 1.
    """
    device_root = pathlib.Path(argv[0]).resolve()
    mirror_root = pathlib.Path(argv[1]).resolve()
    sync = "--sync" in argv[2:]

    device = {**source_digests(device_root), **document_digests(device_root)}
    mirror = {**source_digests(mirror_root), **document_digests(mirror_root)}
    differing, device_only, mirror_only = compare(device, mirror)

    print(f"inputs: device {len(device)}, mirror {len(mirror)}")
    pending: List[str] = []
    for label, paths in (("DIFFERS", differing), ("DEVICE-ONLY", device_only), ("MIRROR-ONLY", mirror_only)):
        for relative in paths:
            kind = "generated" if is_generated(relative) else "input"
            print(f"{label:12} {kind:9} {relative}")
            if kind == "input" and label != "MIRROR-ONLY":
                pending.append(relative)

    if sync:
        for relative in pending:
            destination = mirror_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(device_root / relative, destination)
            print(f"SYNCED       input     {relative}")
        mirror = {**source_digests(mirror_root), **document_digests(mirror_root)}
        differing, device_only, mirror_only = compare(device, mirror)

    remaining = [p for p in differing + device_only + mirror_only if not is_generated(p)]
    print(f"input differences remaining: {len(remaining)}")
    return 0 if not remaining else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
