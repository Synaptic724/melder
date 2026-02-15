# context_compass

Purpose
- Central place for planning, refactor notes, and architectural decisions.
- Capture new ideas from our discussions so they are easy to resume later.
- `core/` contains reusable process mechanics.
- `profiles/` contains repository-specific policy overlays.
- `config/` contains runtime-style policy switches (including microcycle mode).

Rules
- Finish TODOs here before starting new feature work.
- Add new plans or decisions here as they arise.
- Move finished items to the matching completed folder (`epics/completed/`,
  `stories/completed/`, `tasks/completed/`) with a short summary and date.
- Use `attention_board.md` as canonical routing state for active work.
- Keep a `## Notes` section in active tickets and append evidence-backed
  findings (`path:start_line-end_line`, use `start=end` for one-line evidence)
  during execution as each meaningful finding occurs.
- UNKNOWN is the default claim state until evidence promotes it to FACT.
- Git commands are active-only; certification must include environment (`active` or `inactive`).

DO NOT ASSUME / Unknowns Gate
Rule: No Unverified Claims.
Any statement that is not directly supported by evidence must be treated as UNKNOWN.

Evidence means at least one of:
- A specific source file reference (preferred: file + symbol/method/class name).
- A citation to an explicit, already-verified artifact (e.g., a prior approved doc section).

If not evidenced => UNKNOWN.

UNKNOWN items must be explicitly labeled UNKNOWN (or added to an Unknowns section).
UNKNOWN items must be investigated by reading the relevant source(s).
If investigation cannot be completed (missing source access, ambiguity, or time),
the item must remain UNKNOWN and must not be promoted to fact.

No reasonable assumptions.
Do not infer behavior from naming, patterns, conventions, or typical frameworks.
Only the code/docs count.

When unsure:
- Mark it UNKNOWN.
- Identify the most likely evidence target (file + symbol).
- Investigate, then update the doc (or leave it UNKNOWN).

Files
- `attention_board.md` - canonical active routing board (`work_item/status/next/ticket/reread`).
- `AGENTS.MD` - local agent rules for this directory.
- `SKILLS.MD` - ticket-writing guidance and deep descriptive model.
- `WORKFLOW.md` - epic/story/task lifecycle and tracking rules.
- `CONTEXT_COMPACTION.md` - context compaction and handoff policy.
- `agent_onboarding/` - required onboarding docs (general + engineer) for agent behavior and execution standards.
- `architecture/` - C4 architecture docs for src and tests.
- `components/` - C3/C2/C1 component docs for src and tests.
- `examples/` - example tickets and doc references for modeling new work.
- `templates/` - epic/story/task templates (GitHub-style).
- `epics/` - active epic tickets.
- `epics/completed/` - completed epic tickets with summary + date.
- `stories/` - active story tickets.
- `stories/completed/` - completed story tickets with summary + date.
- `tasks/` - active task tickets.
- `tasks/completed/` - completed task tickets with summary + date.
- `completed/` - legacy completed ticket archive (pre-split).

Packaging Model
- `core/`:
  - Canonical reusable mechanics that can be shared across repositories.
  - Keep implementation-neutral language where possible.
- `profiles/`:
  - Local policy overlays, quality bars, and repo constraints.
  - Keep profile notes pragmatic and override-focused.
- `config/context_compass_config.yaml`:
  - Toggle strict Ticket Microcycle enforcement on/off.
  - Define relaxed mode behavior without deleting documentation discipline.

Completed (legacy archive)
- 2026-01-17 - Melder DI resolution contract docs (see `completed/2026-01-17_melder_di_resolution_contract_docs_task_completed.md`).
- 2026-01-17 - Melder DI contract decision alignment (see `completed/2026-01-17_melder_di_contract_decisions_doc_alignment_task_completed.md`).
- 2026-01-17 - Melder scan bind module work (see `completed/2026-01-17_melder_scan_bind_module_task_completed.md`).
- 2026-01-18 - Melder src architecture doc (see `completed/2026-01-18_melder_src_architecture_doc_task_completed.md`).
- 2026-01-18 - Melder src components doc (see `completed/2026-01-18_melder_src_components_doc_task_completed.md`).
