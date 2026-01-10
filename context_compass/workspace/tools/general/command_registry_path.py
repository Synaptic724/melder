"""
Workspace facade for command registry path lookup.

Purpose
- Provide a workspace-owned entrypoint for resolving a single command path.
- Delegate execution to the ai_restricted command_registry_path tool.

Contract
- Accepts the same CLI arguments as
  context_compass.system.ai_restricted.system_management.command_registry_path.
- Preserves exit status and logging behavior from the delegated tool.
"""

from __future__ import annotations

from context_compass.system.ai_restricted.system_management import (
    command_registry_path as core_command_registry_path,
)


def main() -> None:
    """
    CLI entrypoint for the workspace command_registry_path facade.

    Returns:
        None: Delegates to the underlying tool and exits on failure.

    Raises:
        SystemExit: Propagated when the delegated tool reports a non-ok status.

    Contract:
        - Does not mutate sys.argv; delegates argument parsing to the core tool.
        - Does not catch SystemExit; exit status is preserved.
    """

    core_command_registry_path.main()


if __name__ == "__main__":
    main()
