"""Shared helpers for context_compass memory stores."""

import secrets
import time
from pathlib import Path
from typing import Optional

from context_compass.tools._shared.json_io import load_json, write_json_atomic
from context_compass.tools._shared.timeutils import utc_now_iso


def _allowed_store(store: str) -> str:
    """
    Validate memory store names.

    Args:
        store (str): Store name (user/system).

    Returns:
        str: Normalized store name.

    Raises:
        ValueError: If the store name is invalid.
    """
    normalized = str(store or "").strip().lower()
    if normalized not in ("user", "system"):
        raise ValueError("store must be 'user' or 'system'")
    return normalized


def memory_store_path(repo_root: Path, store: str) -> Path:
    """
    Return the memory store path for the given store.

    Args:
        repo_root (Path): Repository root.
        store (str): Store name (user/system).

    Returns:
        Path: Memory store path.
    """
    normalized = _allowed_store(store)
    return repo_root / "context_compass" / "memory" / f"{normalized}_memory.json"


def memory_locks_dir(repo_root: Path) -> Path:
    """
    Return the memory locks directory.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Locks directory.
    """
    return repo_root / "context_compass" / "memory" / "locks"


def default_store(now: Optional[str] = None) -> dict:
    """
    Build a default memory store payload.

    Args:
        now (Optional[str]): Override timestamp.

    Returns:
        dict: Default memory store payload.
    """
    timestamp = now or utc_now_iso()
    return {"schema_version": 1, "updated_at": timestamp, "memories": []}


def load_store(repo_root: Path, store: str) -> tuple[Path, dict]:
    """
    Load a memory store from disk, returning a default payload if missing.

    Args:
        repo_root (Path): Repository root.
        store (str): Store name (user/system).

    Returns:
        tuple[Path, dict]: Store path and payload.
    """
    path = memory_store_path(repo_root, store)
    if not path.exists():
        return path, default_store()
    data = load_json(path)
    if not isinstance(data, dict):
        return path, default_store()
    return path, data


def _encode_crockford(value: int, length: int) -> str:
    """
    Encode an integer into Crockford base32 with fixed length.

    Args:
        value (int): Non-negative integer to encode.
        length (int): Fixed output length.

    Returns:
        str: Base32 encoded string.
    """
    if value < 0:
        raise ValueError("value must be non-negative")
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    chars: list[str] = []
    for _ in range(length):
        chars.append(alphabet[value & 31])
        value >>= 5
    return "".join(reversed(chars))


def _generate_ulid(now_ms: Optional[int] = None, randomness: Optional[int] = None) -> str:
    """
    Generate a lowercase ULID string (26 chars, Crockford base32).

    Args:
        now_ms (Optional[int]): Override timestamp in milliseconds.
        randomness (Optional[int]): Override 80-bit randomness integer.

    Returns:
        str: ULID string in lowercase.
    """
    if now_ms is None:
        now_ms = int(time.time() * 1000)
    if now_ms < 0 or now_ms >= (1 << 48):
        raise ValueError("now_ms must fit in 48 bits")
    if randomness is None:
        randomness = secrets.randbits(80)
    if randomness < 0 or randomness >= (1 << 80):
        raise ValueError("randomness must fit in 80 bits")
    time_part = _encode_crockford(now_ms, 10)
    rand_part = _encode_crockford(randomness, 16)
    return f"{time_part}{rand_part}".lower()


def generate_memory_id() -> str:
    """
    Generate a memory id using a ULID.

    Returns:
        str: Memory identifier.
    """
    return f"mem_{_generate_ulid()}"


def normalize_tags(tags: Optional[list[str]]) -> list[str]:
    """
    Normalize tags into a sorted, de-duplicated list.

    Args:
        tags (Optional[list[str]]): Input tag values.

    Returns:
        list[str]: Normalized tags.
    """
    if not tags:
        return []
    filtered = [str(tag).strip() for tag in tags if str(tag).strip()]
    deduped = sorted({tag for tag in filtered})
    return deduped


def find_memory(memories: list[dict], memory_id: str) -> Optional[dict]:
    """
    Find a memory entry by id.

    Args:
        memories (list[dict]): Memory list.
        memory_id (str): Memory identifier.

    Returns:
        Optional[dict]: Memory entry or None.
    """
    for entry in memories:
        if entry.get("memory_id") == memory_id:
            return entry
    return None


def write_store(path: Path, data: dict) -> None:
    """
    Write a memory store payload atomically.

    Args:
        path (Path): Store path.
        data (dict): Store payload.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(path, data)
