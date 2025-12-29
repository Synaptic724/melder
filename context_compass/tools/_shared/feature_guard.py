"""Feature gate helpers for context_compass tools."""

from pathlib import Path

from typing import Optional

from context_compass.tools._shared.context_compass_configuration import load_configuration
from context_compass.tools._shared.json_io import load_json
from context_compass.tools._shared import branch_paths


class FeatureDisabledError(RuntimeError):
    """
    Raised when a feature is disabled by configuration.
    """


class RepoStateDisabledError(RuntimeError):
    """
    Raised when repo_state disables a feature.
    """


def _load_repo_state(repo_root: Path) -> Optional[dict]:
    """
    Load repo_state.json for the active branch if available.

    Args:
        repo_root (Path): Repository root.

    Returns:
        dict | None: Repo state payload or None if unavailable.
    """
    current_path = branch_paths.current_branch_path(repo_root)
    if not current_path.exists():
        return None
    data = load_json(current_path)
    if not isinstance(data, dict):
        return None
    branch_name = data.get("branch_name")
    if not branch_name:
        return None
    state_path = branch_paths.branch_root(repo_root, str(branch_name)) / "state" / "repo_state.json"
    if not state_path.exists():
        return None
    state = load_json(state_path)
    return state if isinstance(state, dict) else None


def _disabled_features_from_state(state: dict) -> list[str]:
    """
    Determine disabled features from repo_state lifecycle and tooling policy.

    Args:
        state (dict): Repo state payload.

    Returns:
        list[str]: Disabled features list.
    """
    lifecycle = state.get("lifecycle") if isinstance(state.get("lifecycle"), dict) else {}
    tooling = state.get("tooling_policy") if isinstance(state.get("tooling_policy"), dict) else {}
    stage = lifecycle.get("stage")
    mode = tooling.get("mode")
    disabled = tooling.get("disabled_features")
    if not isinstance(disabled, list):
        disabled = []
    disabled = [item for item in disabled if isinstance(item, str)]
    if mode == "restricted" and not disabled:
        if stage == "new":
            return ["scan", "context_profiles"]
        return []
    if mode is None and stage == "new" and not disabled:
        return ["scan", "context_profiles"]
    return disabled


def ensure_feature_enabled(repo_root: Path, feature: str, action: str) -> None:
    """
    Ensure a feature is enabled in context_compass_configuration.json.

    Args:
        repo_root (Path): Repository root.
        feature (str): Feature flag name.
        action (str): Human-readable action description.

    Raises:
        FeatureDisabledError: If the feature is disabled.
    """
    config = load_configuration(repo_root)
    features = config.get("features", {})
    enabled = features.get(feature)
    if enabled is False:
        raise FeatureDisabledError(
            f"Feature '{feature}' is disabled in context_compass_configuration.json; cannot {action}."
        )
    state = _load_repo_state(repo_root)
    if state:
        disabled = _disabled_features_from_state(state)
        if feature in disabled:
            raise RepoStateDisabledError(
                f"Feature '{feature}' is disabled by repo_state; update repo_state.json to enable before {action}."
            )
