# agent_lifecycle

Purpose
- Define how session tracking and handoffs are handled in this repo.

Rules
- Track active routing in `attention_board.md` and detailed execution state in ticket notes/checklists.
- Use UNKNOWN as the default claim stance until evidence is recorded.
- Do not invent external lifecycle tooling or databases.

Worklists
- Use `epics/`, `stories/`, and `tasks/` for active work.
- Move completed tickets to `epics/completed/`, `stories/completed/`, or
  `tasks/completed/` only after user confirmation.
