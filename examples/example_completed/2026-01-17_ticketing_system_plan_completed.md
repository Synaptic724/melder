# Plan: Codex Todo Ticketing System + Skills Docs (2026-01-17)

- Completed: 2026-01-17
- Summary: Built epic/story/task folders and templates; added SKILLS/WORKFLOW/CONTEXT_COMPACTION docs and updated AGENTS/README.

## Goal
- Establish a durable epic/story/task workflow inside `codex_todo/`.
- Add robust GitHub-style templates for epics, stories, and tasks.
- Add SKILLS documentation for deep, descriptive ticket writing and tracking.
- Wire `codex_todo/AGENTS.MD` to the SKILLS guidance.
- Add supporting docs that explain the workflow, structure, and usage.

## Scope (files and folders)
- New folders: `codex_todo/epics/`, `codex_todo/stories/`, `codex_todo/tasks/`, `codex_todo/templates/`.
- New templates: `codex_todo/templates/epic_template.md`, `codex_todo/templates/story_template.md`, `codex_todo/templates/task_template.md`.
- New guidance: `codex_todo/SKILLS.MD` and `codex_todo/WORKFLOW.md`.
- Updates: `codex_todo/AGENTS.MD` to reference `codex_todo/SKILLS.MD` and the workflow.
- Optional update: `codex_todo/README.md` to list the new structure.

## Steps (to check off as completed)
- [x] Create the epic/story/task folder structure and template directory.
- [x] Write epic/story/task templates with deep descriptive sections, milestones, and task tracking.
- [x] Write `codex_todo/SKILLS.MD` with GitHub-style ticketing guidance and cross-link to templates.
- [x] Write `codex_todo/WORKFLOW.md` with usage rules (create, track, complete, move to completed).
- [x] Write `codex_todo/CONTEXT_COMPACTION.md` with compaction/handoff rules.
- [x] Update `codex_todo/AGENTS.MD` to point to SKILLS and workflow docs.
- [x] (Optional) Update `codex_todo/README.md` to reflect the new structure.

## Deliverables
- Folder structure and templates for epics/stories/tasks.
- `codex_todo/SKILLS.MD`, `codex_todo/WORKFLOW.md`, and `codex_todo/CONTEXT_COMPACTION.md` documentation.
- `codex_todo/AGENTS.MD` references to the new docs.
- (Optional) `codex_todo/README.md` structure update.

## Questions / Assumptions
- Assumption: the new workflow docs should live in `codex_todo/` for proximity.
- Assumption: templates will be GitHub-issue style with checklists and deep descriptive sections.
- Assumption: checkboxes (`- [ ]`) are the preferred way to "scratch off" completed items.
