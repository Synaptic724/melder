"""
context_compass.tools._shared.hashing

Hashing helpers for deterministic scans.

Contracts
- SHA256 for code files.
- Subtree hash from sorted (relative_path + code_hash) entries.
"""

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping


def hash_bytes(data: bytes) -> str:
    """
    Compute a SHA256 hash for raw bytes.

    Args:
        data (bytes): Raw byte payload.

    Returns:
        str: Hex SHA256 digest.
    """
    return hashlib.sha256(data).hexdigest()


def hash_text(text: str) -> str:
    """
    Compute a SHA256 hash for UTF-8 text.

    Args:
        text (str): Input text.

    Returns:
        str: Hex SHA256 digest.
    """
    return hash_bytes(text.encode("utf-8"))


def hash_file(path: Path) -> str:
    """
    Compute a SHA256 hash for a file.

    Args:
        path (Path): File path.

    Returns:
        str: Hex SHA256 digest.
    """
    return hash_bytes(path.read_bytes())


def hash_json(obj: Mapping[str, object]) -> str:
    """
    Compute a SHA256 hash for canonical JSON content.

    Contract:
    - Uses sorted keys and minified separators for stability.

    Args:
        obj (Mapping[str, object]): JSON-serializable mapping.

    Returns:
        str: Hex SHA256 digest.
    """
    payload = json.dumps(
        obj,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    return hash_text(payload)


def hash_subtree(entries: Iterable[str]) -> str:
    """
    Compute a deterministic subtree hash from sorted entries.

    Args:
        entries (Iterable[str]): Iterable of entries (relative path + hash).

    Returns:
        str: Hex SHA256 digest.
    """
    material = "\n".join(sorted(entries))
    return hash_text(material)
