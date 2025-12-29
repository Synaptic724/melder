"""
Load source root configuration for prod and test directories.
"""

from pathlib import Path
from typing import Optional

from context_compass.tools._shared.json_io import load_json


def default_source_roots() -> dict:
    """
    Return default source root configuration.

    Returns:
        dict: Default source root payload.
    """
    return {"schema_version": 1, "prod_roots": [], "test_roots": [], "notes": None}


def load_source_roots(repo_root: Path, config_path: Optional[Path] = None) -> dict:
    """
    Load source root configuration with defaults applied.

    Contract:
    - Missing or invalid files return defaults.
    - Only known keys are applied.

    Args:
        repo_root (Path): Repository root.
        config_path (Optional[Path]): Optional override path.

    Returns:
        dict: Source roots payload.
    """
    config = default_source_roots()
    path = config_path or (repo_root / "context_compass" / "config" / "source_roots.json")
    if not path.exists():
        return config
    data = load_json(path)
    if not isinstance(data, dict):
        return config
    schema_version = data.get("schema_version")
    if isinstance(schema_version, int) and schema_version >= 1:
        config["schema_version"] = schema_version
    prod_roots = data.get("prod_roots")
    if isinstance(prod_roots, list):
        config["prod_roots"] = [item for item in prod_roots if isinstance(item, str)]
    test_roots = data.get("test_roots")
    if isinstance(test_roots, list):
        config["test_roots"] = [item for item in test_roots if isinstance(item, str)]
    notes = data.get("notes")
    if notes is None or isinstance(notes, str):
        config["notes"] = notes
    return config
