"""Work mode guard for enforcing task linkage."""

from pathlib import Path
from typing import Optional

from context_compass.system.ai_restricted._shared.context_compass_configuration import load_configuration


class WorkModeError(RuntimeError):
    """
    Raised when hard work mode requirements are not met.
    """


def ensure_work_mode(repo_root: Path, work_id: Optional[str], action: str) -> None:
    """
    Ensure work mode constraints are satisfied.

    Args:
        repo_root (Path): Repository root.
        work_id (Optional[str]): Work identifier supplied by the caller.
        action (str): Human-readable action description.

    Raises:
        WorkModeError: If hard mode is enabled and work_id is missing.
    """
    config = load_configuration(repo_root)
    mode = config.get("work_mode", "soft")
    if mode not in ("hard", "soft"):
        mode = "soft"
    if mode == "soft":
        return
    if work_id:
        return
    raise WorkModeError(
        f"work_mode is hard; a work_id is required to {action}."
    )
