"""
Workspace facade for tool registry inspection.

Purpose
- Provide a workspace-owned entrypoint for tool registry inspection.
- Delegate execution to the system tool_registry_describe implementation.

Contract
- Accepts the same CLI arguments as
  context_compass.system.ai_restricted.system_management.tool_registry_describe.
- Preserves exit status and logging behavior from the delegated tool.
"""

from __future__ import annotations

from context_compass.system.ai_restricted.system_management import (
    tool_registry_describe as core_tool_registry_describe,
)


def main() -> None:
    """
    CLI entrypoint for the workspace tool_registry_describe facade.

    Returns:
        None: Delegates to the underlying tool and exits on failure.

    Raises:
        SystemExit: Propagated when the delegated tool reports a non-ok status.

    Contract:
        - Does not mutate sys.argv; delegates argument parsing to the core tool.
        - Does not catch SystemExit; exit status is preserved.
    """

    core_tool_registry_describe.main()


if __name__ == "__main__":
    main()
