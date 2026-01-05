# pm_execution

Purpose
- Define how project manager agents coordinate work and maintain system flow.

Core rules
- Use work queues to assign, move, and close items.
- Keep statuses consistent with the source of truth in SQLite.
- Prefer clear, minimal updates with explicit rationale.

Preferred workflow
1) Confirm the outcome and priority.
2) Move items to the correct queue (global, branch, or agent).
3) Update status and record a brief reason.
4) Communicate the result and next steps.

References
- `context_compass/onboarding/agent/general/skills/work_management.md`
- `context_compass/onboarding/agent/general/skills/branch_management.md`
