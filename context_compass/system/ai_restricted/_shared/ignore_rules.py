"""
context_compass.system.ai_restricted._shared.ignore_rules

Ignore-rule helpers for repo scanning.

Contracts
- Apply include/exclude rules from SQLite-backed ignore configuration tables.
- Support include_dirs allowlist filtering.
"""

import fnmatch
from pathlib import Path
from typing import Iterable
from context_compass.system.ai_restricted._shared.paths import repo_relative_path
from context_compass.system.ai_restricted.database_management import sqlite_crud
from context_compass.system.ai_restricted.database_management.orm_session import system_db_path


CONFIG_IGNORE_CORE_TABLE = "config_ignore_core"
CONFIG_IGNORE_RULES_TABLE = "config_ignore_rules"
CONFIG_LANGUAGES_CORE_TABLE = "config_languages_core"
CONFIG_LANGUAGES_EXTENSIONS_TABLE = "config_languages_extensions"
CONFIG_LANGUAGES_DIRECTORY_HINTS_TABLE = "config_languages_directory_hints"
CONFIG_IGNORE_ACTION = "by_config_id"
CONFIG_LANGUAGES_ACTION = "by_config_id"
CONFIG_IGNORE_ID = 1
CONFIG_LANGUAGES_ID = 1
CONFIG_ACTOR_ID = "system:ignore_rules"


def _default_ignore_config() -> dict:
    """
    Return the default ignore configuration for scanning.

    Returns:
        dict: Default ignore configuration payload.
    """
    return {
        "schema_version": 1,
        "include_globs": [],
        "exclude_globs": [
            ".coverage",
        ],
        "include_dirs": [],
        "exclude_dirs": [
            ".git",
            ".idea",
            ".vscode",
            "**/node_modules",
            "**/dist",
            "**/build",
            "**/__pycache__",
            "**/.pytest_cache",
            "**/.mypy_cache",
            "**/.ruff_cache",
            "**/.venv",
            "**/venv",
            "**/.tox",
            "**/coverage",
            "**/*.egg-info",
            "context_compass",
        ],
        "code_extensions": [],
    }


def _normalize_glob(value: str) -> str:
    """
    Normalize a glob pattern to POSIX form.

    Args:
        value (str): Glob pattern.

    Returns:
        str: Normalized glob.
    """
    normalized = value.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("/"):
        normalized = normalized[1:]
    return normalized


def _dedupe_list(values: Iterable[str]) -> list[str]:
    """
    Deduplicate a list while preserving order.

    Args:
        values (Iterable[str]): Input values.

    Returns:
        list[str]: Deduplicated list.
    """
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _normalize_glob_list(values: Iterable[str]) -> list[str]:
    """
    Normalize a list of glob patterns to POSIX form.

    Args:
        values (Iterable[str]): Glob patterns.

    Returns:
        list[str]: Normalized glob patterns.
    """
    normalized: list[str] = []
    for value in values:
        text = _normalize_glob(str(value))
        if text:
            normalized.append(text)
    return _dedupe_list(normalized)


def _normalize_dir_patterns(values: Iterable[str]) -> list[str]:
    """
    Normalize directory patterns for consistent matching.

    Args:
        values (Iterable[str]): Directory patterns.

    Returns:
        list[str]: Normalized directory patterns.
    """
    normalized: list[str] = []
    for value in values:
        text = _normalize_glob(str(value)).rstrip("/")
        if text:
            normalized.append(text)
    return _dedupe_list(normalized)


def _is_glob_pattern(value: str) -> bool:
    """
    Return True if a pattern contains glob wildcards.

    Args:
        value (str): Pattern string.

    Returns:
        bool: True if the pattern includes glob wildcards.
    """
    return any(token in value for token in ("*", "?", "["))


def _raise_crud_error(exc: sqlite_crud.SqliteCrudError, db_path: Path, message: str) -> None:
    """
    Raise a consistent error for CRUD lookup failures.

    Args:
        exc (sqlite_crud.SqliteCrudError): CRUD error to map.
        db_path (Path): System database path for error context.
        message (str): Message to use for missing record cases.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or records are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
    """

    if exc.code == "db_missing":
        raise FileNotFoundError(f"System database not found: {db_path}") from exc
    if exc.code in {"table_missing", "table_not_registered", "action_not_registered", "registry_missing"}:
        raise RuntimeError("Missing configuration tables in system.db.") from exc
    if exc.code == "record_not_found":
        raise RuntimeError(message) from exc
    raise exc


def _read_ignore_core(repo_root: Path, actor_id: str) -> dict:
    """
    Read the ignore core record from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Ignore core record.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or the core record are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_IGNORE_CORE_TABLE,
                action=CONFIG_IGNORE_ACTION,
                payload={"config_id": CONFIG_IGNORE_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(exc, db_path, "Missing config_ignore_core row for config_id=1.")
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_ignore_core read returned an invalid record payload.")
    return record


def _read_ignore_rules(repo_root: Path, actor_id: str) -> list[dict]:
    """
    Read ignore rule records from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Ignore rule records.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_IGNORE_RULES_TABLE,
                action=CONFIG_IGNORE_ACTION,
                payload={"config_id": CONFIG_IGNORE_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(exc, db_path, "Missing config_ignore_rules rows for config_id=1.")
    records = response.output.get("result", {}).get("records")
    if not isinstance(records, list):
        raise ValueError("config_ignore_rules read returned an invalid record payload.")
    return [record for record in records if isinstance(record, dict)]


def _read_languages_core(repo_root: Path, actor_id: str) -> dict:
    """
    Read the language core record from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        dict: Language core record.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or the core record are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_LANGUAGES_CORE_TABLE,
                action=CONFIG_LANGUAGES_ACTION,
                payload={"config_id": CONFIG_LANGUAGES_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(exc, db_path, "Missing config_languages_core row for config_id=1.")
    record = response.output.get("result", {}).get("record")
    if not isinstance(record, dict):
        raise ValueError("config_languages_core read returned an invalid record payload.")
    return record


def _read_languages_extensions(repo_root: Path, actor_id: str) -> list[dict]:
    """
    Read language extension records from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Language extension records.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_LANGUAGES_EXTENSIONS_TABLE,
                action=CONFIG_LANGUAGES_ACTION,
                payload={"config_id": CONFIG_LANGUAGES_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_languages_extensions rows for config_id=1.",
        )
    records = response.output.get("result", {}).get("records")
    if not isinstance(records, list):
        raise ValueError("config_languages_extensions read returned an invalid record payload.")
    return [record for record in records if isinstance(record, dict)]


def _read_languages_directory_hints(repo_root: Path, actor_id: str) -> list[dict]:
    """
    Read language directory hint records from SQLite.

    Args:
        repo_root (Path): Repository root.
        actor_id (str): Actor identifier for audit logging.

    Returns:
        list[dict]: Language directory hint records.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables are missing.
        sqlite_crud.SqliteCrudError: For unexpected CRUD failures.
        ValueError: If the CRUD response payload is invalid.
    """

    db_path = system_db_path(repo_root)
    try:
        response = sqlite_crud.execute_request(
            repo_root,
            sqlite_crud.SqliteCrudRequest(
                operation="read",
                scope="system",
                table_name=CONFIG_LANGUAGES_DIRECTORY_HINTS_TABLE,
                action=CONFIG_LANGUAGES_ACTION,
                payload={"config_id": CONFIG_LANGUAGES_ID},
                actor_id=actor_id,
            ),
        )
    except sqlite_crud.SqliteCrudError as exc:
        _raise_crud_error(
            exc,
            db_path,
            "Missing config_languages_directory_hints rows for config_id=1.",
        )
    records = response.output.get("result", {}).get("records")
    if not isinstance(records, list):
        raise ValueError("config_languages_directory_hints read returned an invalid record payload.")
    return [record for record in records if isinstance(record, dict)]


def load_ignore_config(repo_root: Path) -> dict:
    """
    Load ignore configuration from SQLite.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Ignore configuration.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required configuration tables are missing.
    """

    actor_id = CONFIG_ACTOR_ID
    core = _read_ignore_core(repo_root, actor_id)
    rules = _read_ignore_rules(repo_root, actor_id)

    schema_version = core.get("schema_version")
    if not isinstance(schema_version, int):
        raise ValueError("config_ignore_core.schema_version must be an integer.")

    return {
        "schema_version": schema_version,
        "include_globs": _load_rule_values(rules, "include_glob"),
        "exclude_globs": _load_rule_values(rules, "exclude_glob"),
        "include_dirs": _load_rule_values(rules, "include_dir"),
        "exclude_dirs": _load_rule_values(rules, "exclude_dir"),
        "code_extensions": _load_rule_values(rules, "code_extension"),
    }


def _load_rule_values(rules: list[dict], rule_type: str) -> list[str]:
    """
    Extract ordered rule values for a rule type.

    Args:
        rules (list[dict]): Rule records from the database.
        rule_type (str): Rule type to filter.

    Returns:
        list[str]: Ordered rule values.
    """

    filtered = [rule for rule in rules if rule.get("rule_type") == rule_type]
    filtered.sort(
        key=lambda rule: (
            rule.get("position") is None,
            rule.get("position") if rule.get("position") is not None else 0,
            rule.get("rule_value") or "",
        )
    )
    return [rule.get("rule_value") for rule in filtered if rule.get("rule_value")]


def load_language_config(repo_root: Path) -> dict:
    """
    Load language configuration with defaults applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Language configuration.

    Raises:
        FileNotFoundError: If system.db is missing.
        RuntimeError: If required tables or core rows are missing.
    """

    actor_id = CONFIG_ACTOR_ID
    core = _read_languages_core(repo_root, actor_id)
    extensions = _read_languages_extensions(repo_root, actor_id)
    directory_hints = _read_languages_directory_hints(repo_root, actor_id)

    schema_version = core.get("schema_version")
    default_language = core.get("default_language")
    if not isinstance(schema_version, int):
        raise ValueError("config_languages_core.schema_version must be an integer.")
    if not isinstance(default_language, str):
        raise ValueError("config_languages_core.default_language must be a string.")

    return {
        "schema_version": schema_version,
        "extensions": _load_language_extensions(extensions),
        "default_language": default_language,
        "directory_hints": _load_language_directory_hints(directory_hints),
    }


def _load_language_extensions(entries: list[dict]) -> dict:
    """
    Extract ordered extension mappings from language rows.

    Args:
        entries (list[dict]): Extension records.

    Returns:
        dict: Extension -> language mapping.
    """

    ordered = sorted(
        entries,
        key=lambda entry: (
            entry.get("position") is None,
            entry.get("position") if entry.get("position") is not None else 0,
            entry.get("extension") or "",
        ),
    )
    return {
        entry.get("extension"): entry.get("language")
        for entry in ordered
        if entry.get("extension") and entry.get("language")
    }


def _load_language_directory_hints(
    entries: list[dict],
) -> dict:
    """
    Extract ordered directory hint mappings from language rows.

    Args:
        entries (list[dict]): Directory hint records.

    Returns:
        dict: Directory hint -> language mapping.
    """

    ordered = sorted(
        entries,
        key=lambda entry: (
            entry.get("position") is None,
            entry.get("position") if entry.get("position") is not None else 0,
            entry.get("hint_pattern") or "",
        ),
    )
    return {
        entry.get("hint_pattern"): entry.get("language")
        for entry in ordered
        if entry.get("hint_pattern") and entry.get("language")
    }


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


def _matches_dir_pattern(rel_path: str, pattern: str) -> bool:
    """
    Return True if a path matches a directory pattern.

    Args:
        rel_path (str): Repo-relative path.
        pattern (str): Directory pattern (glob or prefix).

    Returns:
        bool: True if matched.
    """
    normalized = _normalize_glob(pattern).rstrip("/")
    if normalized.startswith("**/"):
        stripped = normalized[3:]
        if stripped and _matches_dir_pattern(rel_path, stripped):
            return True
    if _is_glob_pattern(normalized):
        return fnmatch.fnmatch(rel_path, normalized)
    return rel_path == normalized or rel_path.startswith(normalized + "/")


def _matches_any_dir(rel_path: str, patterns: Iterable[str]) -> bool:
    """
    Return True if rel_path matches any directory pattern.

    Args:
        rel_path (str): Repo-relative path.
        patterns (Iterable[str]): Directory patterns.

    Returns:
        bool: True if any pattern matched.
    """
    for pattern in _normalize_dir_patterns(patterns):
        if _matches_dir_pattern(rel_path, pattern):
            return True
    return False


def _matches_any_glob(rel_path: str, patterns: Iterable[str]) -> bool:
    """
    Return True if rel_path matches any glob pattern.

    Args:
        rel_path (str): Repo-relative path.
        patterns (Iterable[str]): Glob patterns.

    Returns:
        bool: True if any pattern matched.
    """
    for pattern in _normalize_glob_list(patterns):
        if _matches_glob(rel_path, pattern):
            return True
    return False


def _normalize_extension_list(values: Iterable[str]) -> list[str]:
    """
    Normalize file extension values for consistent matching.

    Purpose:
        Normalize extension entries so comparisons are case-insensitive and
        do not depend on a leading dot.

    Args:
        values (Iterable[str]): Extension entries from configuration.

    Returns:
        list[str]: Normalized, deduplicated extensions without leading dots.

    Contract:
        - Empty or non-string entries are ignored.
        - Returned extensions are lowercase and dot-less.
    """
    normalized: list[str] = []
    for value in values:
        text = str(value).strip().lower()
        if text.startswith("."):
            text = text[1:]
        if text:
            normalized.append(text)
    return _dedupe_list(normalized)


def _candidate_extensions(path: Path) -> list[str]:
    """
    Return candidate extensions for a path, including compound suffixes.

    Purpose:
        Provide matching candidates for extensions like ".d.ts" while still
        supporting simple suffixes like ".py".

    Args:
        path (Path): File path to inspect.

    Returns:
        list[str]: Candidate extension strings without leading dots.

    Contract:
        - Returns an empty list when no suffix exists.
        - Includes compound suffixes in order of specificity.
    """
    suffixes = [suffix.lower().lstrip(".") for suffix in path.suffixes if suffix]
    if not suffixes:
        return []
    candidates: list[str] = []
    if len(suffixes) > 1:
        for index in range(len(suffixes) - 1):
            candidates.append(".".join(suffixes[index:]))
    candidates.append(suffixes[-1])
    return _dedupe_list(candidates)


def _resolve_language_for_extension(
    candidates: list[str],
    language_config: dict,
) -> str | None:
    """
    Resolve a language name for the first matching extension candidate.

    Args:
        candidates (list[str]): Normalized extension candidates.
        language_config (dict): Language configuration payload.

    Returns:
        str | None: Language name when found, otherwise None.

    Contract:
        - Returns the first match found in language_config["extensions"].
        - Falls back to language_config["default_language"] when present.
    """
    extensions = language_config.get("extensions")
    if isinstance(extensions, dict):
        for candidate in candidates:
            language = extensions.get(candidate)
            if isinstance(language, str) and language:
                return language
    default_language = language_config.get("default_language")
    if isinstance(default_language, str) and default_language:
        return default_language
    return None


def is_code_file(path: Path, ignore_config: dict, language_config: dict) -> tuple[bool, str | None]:
    """
    Determine whether a file should be treated as code based on configuration.

    Args:
        path (Path): File path to classify.
        ignore_config (dict): Ignore configuration containing code_extensions.
        language_config (dict): Language configuration with extension mappings.

    Returns:
        tuple[bool, str | None]: (is_code, language_name).

    Contract:
        - Respects ignore_config["code_extensions"] when provided.
        - Falls back to language_config["extensions"] if no code_extensions are set.
        - Returns (False, None) for non-files or paths without recognized suffixes.
        - Language is derived from language_config when possible.
    """
    if not path.is_file():
        return False, None
    candidates = _candidate_extensions(path)
    if not candidates:
        return False, None
    code_extensions = _normalize_extension_list(ignore_config.get("code_extensions", []))
    language = _resolve_language_for_extension(candidates, language_config)
    if code_extensions:
        if any(candidate in code_extensions for candidate in candidates):
            return True, language
        return False, None
    extensions = language_config.get("extensions")
    if isinstance(extensions, dict) and any(candidate in extensions for candidate in candidates):
        return True, language
    return False, None


def is_included_path(repo_root: Path, path: Path, config: dict) -> bool:
    """
    Return True if a path passes include_dirs or include_globs allowlists.

    Args:
        repo_root (Path): Repository root.
        path (Path): Path to test.
        config (dict): Ignore configuration with include_dirs/include_globs.

    Returns:
        bool: True if the path is allowed by include rules.

    Contract:
        - include_globs are treated as an explicit allowlist.
        - When include_dirs is empty, paths are included unless excluded later.
        - Exclusion checks are handled separately by is_ignored_path.
    """
    rel_path = repo_relative_path(repo_root, path)
    include_globs = config.get("include_globs", [])
    include_dirs = config.get("include_dirs", [])
    if _matches_any_glob(rel_path, include_globs):
        return True
    if not include_dirs:
        return True
    return is_within_include_dirs(repo_root, path, include_dirs)


def _coerce_list(value: object, fallback: list[str]) -> list[str]:
    """
    Coerce a value to a list of strings using a fallback.

    Args:
        value (object): Value to normalize.
        fallback (list[str]): Fallback list to use when value is invalid.

    Returns:
        list[str]: Valid list of strings.

    Contract:
        - Returns fallback when value is not a list.
        - Filters out non-string entries.
    """
    if not isinstance(value, list):
        return fallback
    return [item for item in value if isinstance(item, str)]


def effective_ignore_config(ignore_config: dict) -> dict:
    """
    Build a normalized ignore configuration snapshot for scan records.

    Args:
        ignore_config (dict): Raw ignore configuration payload.

    Returns:
        dict: Normalized ignore configuration snapshot.

    Contract:
        - Missing or invalid fields fall back to default values.
        - Returned lists are normalized and deduplicated.
        - Intended for persistence inside scan records.
    """
    defaults = _default_ignore_config()
    schema_version = ignore_config.get("schema_version")
    if not isinstance(schema_version, int):
        schema_version = defaults["schema_version"]
    include_globs = _coerce_list(ignore_config.get("include_globs"), defaults["include_globs"])
    exclude_globs = _coerce_list(ignore_config.get("exclude_globs"), defaults["exclude_globs"])
    include_dirs = _coerce_list(ignore_config.get("include_dirs"), defaults["include_dirs"])
    exclude_dirs = _coerce_list(ignore_config.get("exclude_dirs"), defaults["exclude_dirs"])
    code_extensions = _coerce_list(ignore_config.get("code_extensions"), defaults["code_extensions"])

    return {
        "schema_version": schema_version,
        "include_globs": _normalize_glob_list(include_globs),
        "exclude_globs": _normalize_glob_list(exclude_globs),
        "include_dirs": _normalize_dir_patterns(include_dirs),
        "exclude_dirs": _normalize_dir_patterns(exclude_dirs),
        "code_extensions": _normalize_extension_list(code_extensions),
    }


def is_ignored_path(repo_root: Path, path: Path, config: dict) -> bool:
    """
    Return True if a path should be excluded by scanning rules.

    Args:
        repo_root (Path): Repository root.
        path (Path): Path to test.
        config (dict): Ignore configuration.

    Returns:
        bool: True if excluded.
    """
    rel_path = repo_relative_path(repo_root, path)
    if _matches_any_dir(rel_path, config.get("exclude_dirs", [])):
        return True
    if _matches_any_glob(rel_path, config.get("exclude_globs", [])):
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
        if _matches_dir_pattern(rel_path, root):
            return True
    return False


def is_dir_relevant(rel_dir: str, roots: Iterable[str]) -> bool:
    """
    Return True if a directory should be traversed under include_dirs.

    Args:
        rel_dir (str): Repo-relative directory.
        roots (Iterable[str]): include_dirs entries.

    Returns:
        bool: True if the directory is relevant.
    """
    normalized_roots = _normalize_dir_patterns(roots)
    if not normalized_roots:
        return True
    if rel_dir in ("", "."):
        return True
    if any(_is_glob_pattern(root) for root in normalized_roots):
        return True
    for root in normalized_roots:
        if rel_dir == root:
            return True
        if root.startswith(rel_dir + "/"):
            return True
        if rel_dir.startswith(root + "/"):
            return True
    return False


def is_within_include_dirs(repo_root: Path, path: Path, roots: Iterable[str]) -> bool:
    """
    Return True if a path is within the include_dirs allowlist.

    Args:
        repo_root (Path): Repository root.
        path (Path): Path to test.
        roots (Iterable[str]): include_dirs entries.

    Returns:
        bool: True if within any root.
    """
    normalized = _normalize_dir_patterns(roots)
    if not normalized:
        return True
    rel_path = repo_relative_path(repo_root, path)
    return _is_within_roots(rel_path, normalized)
