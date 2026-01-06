"""Canonical JSON IO helpers for context_compass tools."""

import json
import os
from pathlib import Path
from typing import Any, Mapping


def load_json(path: Path) -> Any:
    """
    Load JSON data from a file.

    Args:
        path (Path): Path to the JSON file.

    Returns:
        Any: Parsed JSON data.

    Raises:
        ValueError: If the file cannot be parsed as JSON.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at {path}") from exc


def dump_minified(obj: Mapping[str, object]) -> str:
    """
    Serialize JSON with canonical minified formatting.

    Args:
        obj (Mapping[str, object]): JSON-serializable mapping.

    Returns:
        str: Minified JSON string.
    """
    return json.dumps(
        obj,
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )


def write_json_minified(path: Path, obj: Mapping[str, object]) -> None:
    """
    Write JSON in canonical minified form.

    Args:
        path (Path): Destination path.
        obj (Mapping[str, object]): JSON-serializable mapping.
    """
    path.write_text(dump_minified(obj), encoding="utf-8")


def write_json_atomic(path: Path, obj: Mapping[str, object]) -> None:
    """
    Atomically write JSON in canonical minified form.

    Contract:
      - Readers never observe partial JSON.
      - Output is stable across runs (sorted keys, no NaN).

    Args:
        path (Path): Destination path.
        obj (Mapping[str, object]): JSON-serializable mapping.
    """
    data = dump_minified(obj).encode("utf-8")
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(data)
    os.replace(tmp_path, path)
