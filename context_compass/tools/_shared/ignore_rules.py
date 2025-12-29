"""
context_compass.tools._shared.ignore_rules

Ignore-rule helpers for repo scanning.

Contracts
- Apply ignore globs from context_compass/config/ignore.json.
- Support optional only_roots filtering.
"""

import fnmatch
from pathlib import Path
from typing import Iterable, Optional

from context_compass.tools._shared.json_io import load_json
from context_compass.tools._shared.paths import repo_relative_path


def _normalize_glob(value: str) -> str:
    """
    Normalize a glob pattern to POSIX form.

    Args:
        value (str): Glob pattern.

    Returns:
        str: Normalized glob.
    """
    return value.replace("\\", "/").lstrip("./")


def _normalize_roots(roots: Iterable[str]) -> list[str]:
    """
    Normalize only_roots entries for consistent matching.

    Args:
        roots (Iterable[str]): Root entries.

    Returns:
        list[str]: Normalized roots.
    """
    normalized: list[str] = []
    for root in roots:
        text = _normalize_glob(root).rstrip("/")
        if text:
            normalized.append(text)
    return normalized


def load_ignore_config(repo_root: Path, config_path: Optional[Path] = None) -> dict:
    """
    Load ignore configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.
        config_path (Optional[Path]): Optional override path.

    Returns:
        dict: Ignore configuration.
    """
    path = config_path or (repo_root / "context_compass" / "config" / "ignore.json")
    if not path.exists():
        return {"schema_version": 1, "globs": [], "only_roots": [], "code_extensions": []}
    data = load_json(path)
    if not isinstance(data, dict):
        return {"schema_version": 1, "globs": [], "only_roots": [], "code_extensions": []}
    data.setdefault("globs", [])
    data.setdefault("only_roots", [])
    data.setdefault("code_extensions", [])
    return data


def load_language_config(repo_root: Path, config_path: Optional[Path] = None) -> dict:
    """
    Load language configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.
        config_path (Optional[Path]): Optional override path.

    Returns:
        dict: Language configuration.
    """
    path = config_path or (repo_root / "context_compass" / "config" / "languages.json")
    if not path.exists():
        return {"schema_version": 1, "extensions": {}, "default_language": "unknown", "directory_hints": {}}
    data = load_json(path)
    if not isinstance(data, dict):
        return {"schema_version": 1, "extensions": {}, "default_language": "unknown", "directory_hints": {}}
    data.setdefault("extensions", {})
    data.setdefault("default_language", "unknown")
    data.setdefault("directory_hints", {})
    return data


def _matches_glob(rel_path: str, glob_pattern: str) -> bool:
    """
    Return True if a relative path matches a glob pattern.

    Args:
        rel_path (str): Repo-relative path.
        glob_pattern (str): Glob pattern.

    Returns:
        bool: True if matched.
    """
    pattern = _normalize_glob(glob_pattern)
    if pattern.endswith("/"):
        prefix = pattern.rstrip("/")
        return rel_path == prefix or rel_path.startswith(prefix + "/")
    return fnmatch.fnmatch(rel_path, pattern)


def is_ignored_path(repo_root: Path, path: Path, config: dict) -> bool:
    """
    Return True if a path should be ignored by scanning rules.

    Args:
        repo_root (Path): Repository root.
        path (Path): Path to test.
        config (dict): Ignore configuration.

    Returns:
        bool: True if ignored.
    """
    rel_path = repo_relative_path(repo_root, path)
    globs = config.get("globs", [])
    for pattern in globs:
        if _matches_glob(rel_path, pattern):
            return True
    return False


def _is_within_roots(rel_path: str, roots: list[str]) -> bool:
    """
    Return True if rel_path is within any root prefix.

    Args:
        rel_path (str): Repo-relative path.
        roots (list[str]): Normalized root prefixes.

    Returns:
        bool: True if within roots.
    """
    if not roots:
        return True
    for root in roots:
        if rel_path == root or rel_path.startswith(root + "/"):
            return True
    return False


def is_dir_relevant(rel_dir: str, roots: Iterable[str]) -> bool:
    """
    Return True if a directory should be traversed under only_roots.

    Args:
        rel_dir (str): Repo-relative directory.
        roots (Iterable[str]): only_roots entries.

    Returns:
        bool: True if the directory is relevant.
    """
    normalized_roots = _normalize_roots(roots)
    if not normalized_roots:
        return True
    if rel_dir in ("", "."):
        return True
    for root in normalized_roots:
        if rel_dir == root:
            return True
        if root.startswith(rel_dir + "/"):
            return True
        if rel_dir.startswith(root + "/"):
            return True
    return False


def is_within_only_roots(repo_root: Path, path: Path, roots: Iterable[str]) -> bool:
    """
    Return True if a path is within the only_roots set.

    Args:
        repo_root (Path): Repository root.
        path (Path): Path to test.
        roots (Iterable[str]): only_roots entries.

    Returns:
        bool: True if within any root.
    """
    normalized = _normalize_roots(roots)
    if not normalized:
        return True
    rel_path = repo_relative_path(repo_root, path)
    return _is_within_roots(rel_path, normalized)


def code_extensions(ignore_config: dict, language_config: dict) -> dict:
    """
    Return a mapping of code extensions to language names.

    Args:
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.

    Returns:
        dict: Extension -> language mapping.
    """
    extensions = language_config.get("extensions", {})
    if ignore_config.get("code_extensions"):
        filtered = {}
        for ext in ignore_config["code_extensions"]:
            key = str(ext).lstrip(".")
            if key in extensions:
                filtered[key] = extensions[key]
            else:
                filtered[key] = language_config.get("default_language", "unknown")
        return filtered
    return extensions


def is_code_file(path: Path, ignore_config: dict, language_config: dict) -> tuple[bool, str]:
    """
    Determine whether a file is a code file and return its language.

    Args:
        path (Path): File path.
        ignore_config (dict): Ignore configuration.
        language_config (dict): Language configuration.

    Returns:
        tuple[bool, str]: (is_code, language).
    """
    suffix = path.suffix.lstrip(".").lower()
    mapping = code_extensions(ignore_config, language_config)
    if suffix in mapping:
        return True, mapping[suffix]
    return False, language_config.get("default_language", "unknown")
