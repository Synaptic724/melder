"""
Workspace facade for SQLite CRUD command execution.

Purpose
- Provide a workspace-owned entrypoint for registered SQLite CRUD operations.
- Delegate execution to the system sqlite_crud_command implementation.

Contract
- Accepts the same CLI arguments as
  context_compass.system.ai_restricted.database_management.sqlite_crud_command.
- Preserves certification and work_mode enforcement in the delegated tool.
"""

from __future__ import annotations

from context_compass.system.ai_restricted.database_management import (
    sqlite_crud_command as core_sqlite_crud_command,
)


def main() -> None:
    """
    CLI entrypoint for the workspace sql_crud_execute facade.

    Returns:
        None: Delegates to the underlying tool and exits on failure.

    Raises:
        SystemExit: Propagated when the delegated tool reports a non-ok status.

    Contract:
        - Does not mutate sys.argv; delegates argument parsing to the core tool.
        - Does not catch SystemExit; exit status is preserved.
    """

    core_sqlite_crud_command.main()


if __name__ == "__main__":
    main()
