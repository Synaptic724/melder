"""Feature gate helpers for context_compass tools."""

from pathlib import Path

from context_compass.tools._shared.context_compass_configuration import load_configuration


class FeatureDisabledError(RuntimeError):
    """
    Raised when a feature is disabled by configuration.
    """


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
