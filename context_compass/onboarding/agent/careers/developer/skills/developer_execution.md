# developer_execution

Purpose
- Define how developer agents plan and implement code changes in context_compass.

Core rules
- Follow `context_compass/onboarding/AGENTS.md` and the shared baseline skills in `general`.
- Propose a plan before editing; keep scope tight and reviewable.
- Use SQLite CRUD for single-table operations; use Query API only for atomic multi-table work.
- Update docstrings for every touched function/class and add tests for behavioral changes.

Preferred workflow
1) Clarify the goal, constraints, and affected files.
2) Review existing docstrings and contracts in the target modules.
3) Implement changes with small, cohesive functions and explicit error handling.
4) Run tests (or report "Not run" with reasoning).
5) Summarize changes and list follow-ups.

References
- `context_compass/onboarding/agent/general/skills/python/docstrings.md`
- `context_compass/onboarding/agent/general/skills/python/typing.md`
- `context_compass/onboarding/agent/general/skills/testing/testing_overview.md`
- `context_compass/onboarding/agent/general/skills/command_registry.md`
