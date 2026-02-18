

# Plan: Codex Todo Ticketing System + Skills Docs (2026-01-17)

- Completed: 2026-01-17
- Summary: Built epic/story/task folders and templates; added SKILLS/WORKFLOW/CONTEXT_COMPACTION docs and updated AGENTS/README.

## Goal
- Establish a durable epic/story/task workflow inside ``.
- Add robust GitHub-style templates for epics, stories, and tasks.
- Add SKILLS documentation for deep, descriptive ticket writing and tracking.
- Wire `AGENTS.MD` to the SKILLS guidance.
- Add supporting docs that explain the workflow, structure, and usage.

## Scope (files and folders)
- New folders: `tickets/epics/`, `tickets/stories/`, `tickets/tasks/`, `templates/`.
- New templates: `templates/epic_template.md`, `templates/story_template.md`, `templates/task_template.md`.
- New guidance: `SKILLS.MD` and `WORKFLOW.md`.
- Updates: `AGENTS.MD` to reference `SKILLS.MD` and the workflow.
- Optional update: `README.md` to list the new structure.

## Steps (to check off as completed)
- [x] Create the epic/story/task folder structure and template directory.
- [x] Write epic/story/task templates with deep descriptive sections, milestones, and task tracking.
- [x] Write `SKILLS.MD` with GitHub-style ticketing guidance and cross-link to templates.
- [x] Write `WORKFLOW.md` with usage rules (create, track, complete, move to completed).
- [x] Write `CONTEXT_COMPACTION.md` with compaction/handoff rules.
- [x] Update `AGENTS.MD` to point to SKILLS and workflow docs.
- [x] (Optional) Update `README.md` to reflect the new structure.

## Deliverables
- Folder structure and templates for `tickets/epics/`, `tickets/stories/`, and
  `tickets/tasks/`.
- `SKILLS.MD`, `WORKFLOW.md`, and `CONTEXT_COMPACTION.md` documentation.
- `AGENTS.MD` references to the new docs.
- (Optional) `README.md` structure update.

## Questions / Assumptions
- Assumption: the new workflow docs should live in `` for proximity.
- Assumption: templates will be GitHub-issue style with checklists and deep descriptive sections.
- Assumption: checkboxes (`- [ ]`) are the preferred way to "scratch off" completed items.