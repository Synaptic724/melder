"""
Onboarding facade for python_certified.

Purpose
- Provide an onboarding-owned entrypoint for certification finalization.
- Delegate execution to the ai_restricted python_certified tool.

Contract
- Accepts the same CLI arguments as
  context_compass.system.ai_restricted.agent_management.python_certified.
- Preserves exit status and logging behavior from the delegated tool.
"""

from __future__ import annotations

from context_compass.system.ai_restricted.agent_management import python_certified as core_python_certified


def main() -> None:
    """
    CLI entrypoint for the onboarding python_certified facade.

    Returns:
        None: Delegates to the underlying tool and exits on failure.

    Raises:
        SystemExit: Propagated when the delegated tool reports a failure.

    Contract:
        - Does not mutate sys.argv; delegates argument parsing to the core tool.
        - Does not catch SystemExit; exit status is preserved.
    """

    core_python_certified.main()


if __name__ == "__main__":
    main()
