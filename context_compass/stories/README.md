# Stories

## Purpose
Stories define a user- or system-facing slice of value within an epic. They translate an
epic outcome into a coherent, testable unit of delivery that strengthens the MRP core.

## MRP First (Required)
- Every story must explain how it hardens or extends the core system.
- MRP means "reasonable," not "minimal." Avoid scope that forces a rewrite later.
- MVP framing is disallowed. Do not trade durability for speed.
- MLP is allowed only when the story is explicitly about UI/UX polish.

## What Belongs Here
- A single, cohesive slice of value inside one epic.
- A scope that can be completed by a small set of tasks with clear deliverables.

## File Naming
Use date-first, descriptive names:
- `YYYY-MM-DD_<slug>_story.md`

When completed, move to `context_compass/stories/completed/` and rename to:
- `YYYY-MM-DD_<slug>_story_completed.md`

## How To Create A Story (Deep, Not Minimal)
1. Copy `context_compass/templates/story_template.md`.
2. Link the story to its epic in Metadata.
3. Write a precise User Narrative with a concrete outcome.
4. Explain Value / MRP Alignment with system-level impact.
5. Define Functional + Non-Functional requirements.
6. Set Scope Boundaries and list Dependencies.
7. Create a task checklist with explicit task IDs.
8. Define Acceptance Criteria that are observable and testable.
9. Add Validation / Test Plan and any UX/API/Data notes.
10. Record Risks / Mitigations, Decision Log, and keep Context / Handoff Summary current.

## Depth Standard (No Handwaving)
- Cite relevant code paths, docs, or diagrams.
- Make uncertainties and open questions explicit.
- Write so a future reader can execute without additional context.

## Completion Rules
- Add completion header at the top of the file (see `context_compass/WORKFLOW.md`).
- Move the file to `context_compass/stories/completed/` with the `_completed` suffix.

## References
- `context_compass/SKILLS.MD` (deep descriptive model and naming rules)
- `context_compass/WORKFLOW.md` (ticket lifecycle and completion format)
- `context_compass/templates/story_template.md`
