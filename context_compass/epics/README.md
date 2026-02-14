# Epics

## Purpose
Epics capture multi-story outcomes that define durable, MRP-aligned changes. They are the
top-level planning unit and must be rich enough to survive context compaction.

## MRP First (Required)
- Every epic must describe the holistic core being built and why it is the right foundation.
- MRP means "reasonable," not "minimal." Avoid scope that forces a rewrite later.
- MVP framing is disallowed. If there is doubt, default to MRP and durability.
- Use MLP only when explicitly tied to UI/UX polish after the core is solid.

## What Belongs Here
- Multi-story outcomes that change core system behavior or architecture.
- Cross-cutting initiatives that require multiple stories and tasks.
- Policy or documentation programs that affect how we work or ship.

## File Naming
Use date-first, descriptive names:
- `YYYY-MM-DD_<slug>_epic.md`

When completed, move to `context_compass/epics/completed/` and rename to:
- `YYYY-MM-DD_<slug>_epic_completed.md`

## How To Create An Epic (Deep, Not Minimal)
1. Copy `context_compass/templates/epic_template.md`.
2. Fill Metadata and keep `Status` and `Updated` current.
3. Document Problem / Opportunity with concrete evidence and context.
4. Write MRP Alignment as a durable, coherent core (not a quick experiment).
5. Define Goals, Non-Goals, Scope Boundaries, and Requirements.
6. Add Success Metrics and Acceptance Criteria that are observable.
7. Add Milestones with clear success criteria (`- [ ]` checkboxes required).
8. List Stories required to complete the epic, each with an ID.
9. Add Epic-level Tasks like "Complete story <STORY-ID>" to make progress explicit.
10. Record Risks / Mitigations, Validation plan, and Decision Log.
11. Keep the Context / Handoff Summary current and specific (context is gold).

## Depth Standard (No Handwaving)
- Use concrete evidence and references (docs, code paths, diagrams).
- Make assumptions explicit and list open questions.
- Write so a future reader can resume without hidden knowledge.

## Completion Rules
- Add completion header at the top of the file (see `context_compass/WORKFLOW.md`).
- Move the file to `context_compass/epics/completed/` with the `_completed` suffix.

## References
- `context_compass/SKILLS.MD` (deep descriptive model and naming rules)
- `context_compass/WORKFLOW.md` (ticket lifecycle and completion format)
- `context_compass/templates/epic_template.md`
