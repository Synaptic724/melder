# Tasks

## Purpose
Tasks are the smallest actionable units that produce concrete deliverables. They must be
precise, testable, and aligned with the MRP-first approach.

## MRP First (Required)
- Every task must contribute to a coherent, durable outcome.
- MRP means "reasonable," not "minimal." Avoid scope that forces a rewrite later.
- MVP shortcuts are disallowed. The task should not create debt that must be rewritten.
- Use MLP only when a task is explicitly about UI/UX polish after core stability.

## What Belongs Here
- A single, concrete unit of work with clear scope and deliverables.
- Work that can be validated and completed within a focused effort window.

## File Naming
Use date-first, descriptive names:
- `YYYY-MM-DD_<slug>_task.md`

When completed, move to `context_compass/tasks/completed/` and rename to:
- `YYYY-MM-DD_<slug>_task_completed.md`

## How To Create A Task (Deep, Not Minimal)
1. Copy `context_compass/templates/task_template.md`.
2. Link the task to its story in Metadata.
3. Write a concrete Objective that defines the smallest meaningful outcome.
4. Define Scope Boundaries (in scope / out of scope) to prevent creep.
5. List Steps / Checklist with clear, ordered actions.
6. Define Deliverables and Files / Paths Impacted.
7. Record Validation status and recommended commands (or "Not run").
8. Capture Risks / Rollback Notes if relevant.
9. Complete the Done Checklist and keep Context / Handoff Summary current.

## Depth Standard (No Handwaving)
- Be explicit about what will change and why.
- Reference relevant files, docs, or diagrams.
- Record open questions or blockers immediately.

## Completion Rules
- Add completion header at the top of the file (see `context_compass/WORKFLOW.md`).
- Move the file to `context_compass/tasks/completed/` with the `_completed` suffix.

## References
- `context_compass/SKILLS.MD` (deep descriptive model and naming rules)
- `context_compass/WORKFLOW.md` (ticket lifecycle and completion format)
- `context_compass/templates/task_template.md`
