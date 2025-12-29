"""Load context_compass configuration for feature gating and skill overrides."""

from pathlib import Path

from context_compass.tools._shared.json_io import load_json


def _default_features() -> dict:
    """
    Return default feature flags.

    Returns:
        dict: Feature flag defaults.
    """
    return {
        "scan": True,
        "context_profiles": True,
        "architecture_contexts": True,
        "environment_check": True,
        "repo_state": True,
        "memory": True,
        "command_registry": True,
        "work_management": True,
        "ticket_intake": True,
        "validation": True,
    }


def _default_skills() -> dict:
    """
    Return default skill override settings.

    Returns:
        dict: Skill override defaults.
    """
    return {"disabled_skill_ids": [], "disabled_skill_prefixes": []}


def default_configuration() -> dict:
    """
    Build a default configuration payload.

    Returns:
        dict: Default configuration payload.
    """
    return {
        "schema_version": 1,
        "features": _default_features(),
        "skills": _default_skills(),
        "work_mode": "hard",
        "notes": None,
    }


def configuration_path(repo_root: Path) -> Path:
    """
    Return the context_compass configuration path.

    Args:
        repo_root (Path): Repository root.

    Returns:
        Path: Configuration JSON path.
    """
    return repo_root / "context_compass" / "config" / "context_compass_configuration.json"


def _merge_features(target: dict, data: dict) -> None:
    """
    Merge feature overrides into the target config.

    Args:
        target (dict): Target configuration payload.
        data (dict): Source configuration payload.
    """
    incoming = data.get("features")
    if not isinstance(incoming, dict):
        return
    for key in target["features"]:
        value = incoming.get(key)
        if isinstance(value, bool):
            target["features"][key] = value


def _merge_skills(target: dict, data: dict) -> None:
    """
    Merge skill override lists into the target config.

    Args:
        target (dict): Target configuration payload.
        data (dict): Source configuration payload.
    """
    incoming = data.get("skills")
    if not isinstance(incoming, dict):
        return
    disabled_ids = incoming.get("disabled_skill_ids")
    if isinstance(disabled_ids, list):
        target["skills"]["disabled_skill_ids"] = [
            item for item in disabled_ids if isinstance(item, str)
        ]
    disabled_prefixes = incoming.get("disabled_skill_prefixes")
    if isinstance(disabled_prefixes, list):
        target["skills"]["disabled_skill_prefixes"] = [
            item for item in disabled_prefixes if isinstance(item, str)
        ]


def _merge_notes(target: dict, data: dict) -> None:
    """
    Merge optional notes into the target config.

    Args:
        target (dict): Target configuration payload.
        data (dict): Source configuration payload.
    """
    notes = data.get("notes")
    if notes is None or isinstance(notes, str):
        target["notes"] = notes


def _merge_work_mode(target: dict, data: dict) -> None:
    """
    Merge work_mode into the target config.

    Args:
        target (dict): Target configuration payload.
        data (dict): Source configuration payload.
    """
    mode = data.get("work_mode")
    if mode in ("hard", "soft"):
        target["work_mode"] = mode


def load_configuration(repo_root: Path) -> dict:
    """
    Load context_compass configuration from disk with defaults applied.

    Contract:
    - Missing configuration returns defaults.
    - Only known keys and valid value types are applied.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict: Configuration payload.
    """
    config = default_configuration()
    path = configuration_path(repo_root)
    if not path.exists():
        return config
    data = load_json(path)
    if not isinstance(data, dict):
        return config
    schema_version = data.get("schema_version")
    if isinstance(schema_version, int) and schema_version >= 1:
        config["schema_version"] = schema_version
    _merge_features(config, data)
    _merge_skills(config, data)
    _merge_work_mode(config, data)
    _merge_notes(config, data)
    return config
