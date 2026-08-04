# Task: Scaffold Crystallizer Package Layout

## Metadata
- Task ID: TASK-2026-04-26-scaffold-crystallizer-package-layout
- Story:
- Epic: EPIC-2026-04-26-design-crystallizer-asset-provenance-layer
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-04-26T21:08:13Z
- Updated: 2026-04-26T21:25:20Z

## Objective
Lay down the initial `src/melder/crystallizer/` package structure so the
Crystallizer subsystem has the agreed concern boundaries before component
implementation begins.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved the current crystallizer package
  shape and requested that the scaffold be created now.
- EXECUTION_BOUNDARY:
  - `src/melder/crystallizer/`
  - this task ticket
  - `attention_board.md`
  - the parent crystallizer epic only where task staging notes need to be
    synchronized
- DEPENDENCIES:
  - `tickets/epics/2026-04-26_design_crystallizer_asset_provenance_epic.md`
  - current crystallizer artifact stack
- EXIT_GATE: the filesystem layout matches the agreed package shape, obsolete
  crystallizer-local directories are removed, and the scaffold is ready for
  iterative component authoring.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if existing repo references or
  hidden files make the agreed package move unsafe.

## Scope Boundaries
- In scope:
  - create agreed files and folders
  - delete `src/melder/crystallizer/info`
  - remove old `crystal_management/` and crystallizer-local
    `mutation_research/` directories
- Out of scope:
  - implementing real Crystallizer logic
  - wiring runtime imports to the new modules
  - tests beyond filesystem verification

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested the filesystem scaffold now so later
  work can iterate inside a stable package shape.

## Steps / Checklist
- [ ] Stage the scaffold task and route it on the attention board.
- [ ] Create the agreed crystallizer package directories and files.
- [ ] Remove obsolete crystallizer-local directories and the old `info` file.
- [ ] Record the resulting package shape in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- scaffolded `src/melder/crystallizer/` package tree
- obsolete crystallizer-local directories removed

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-26_scaffold_crystallizer_package_layout_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/tickets/epics/2026-04-26_design_crystallizer_asset_provenance_epic.md
- src/melder/crystallizer/

## Validation
- Not run.
- Recommended commands:
  - `Get-ChildItem -Recurse src/melder/crystallizer`

## Risks / Rollback Notes
- Risk: the scaffold could preserve obsolete directories that mislead later
  implementation.
  Rollback: remove only the explicitly obsolete crystallizer-local directories
  now and keep the new shape minimal.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-26T21:08:13Z
  TYPE: PLAN
  CLAIM: The agreed scaffold keeps first-class crystallizer concepts at package
    top level, moves persistence and event plumbing into `asset_management/`,
    adds a strategy-based `crystal_analysis/`, and removes the
    crystallizer-local `mutation_research/` model copies because the real MR
    classes should live in the MutationResearch system itself.
  EVIDENCE:
  - user_instruction: agreed crystallizer package layout with `asset_management`, `crystal_analysis`, `crystal_loader`, and no local MR assets
  IMPACT: The initial filesystem pass should focus on package boundaries only,
    not premature class implementation.
  NEXT: create the scaffold and remove the obsolete local directories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T21:11:04Z
  TYPE: FACT
  CLAIM: The filesystem scaffold is now in place. The old `info` file and the
    crystallizer-local `crystal_management/` and `mutation_research/`
    directories are gone. The package now has the agreed top-level files plus
    `configuration/`, `crystal_analysis/`, `asset_management/`, and
    `crystal_loader/`.
  EVIDENCE:
  - src/melder/crystallizer/: filesystem inventory after scaffold
  IMPACT: Later implementation work can now iterate directly inside the agreed
    package shape instead of re-litigating directories first.
  NEXT: return the scaffold for review and then start filling the first
    components incrementally.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-26T21:25:20Z
  TYPE: DECISION
  CLAIM: The scaffold shape is now simplified further. Generic persistence
    traffic should funnel through one shared `asset_transaction.py`, and the
    loader side should own one `bootstrap_manifest.py`. The separate
    crystallizer-local MutationResearch transaction uploader/downloader files
    were removed because the generic asset upload/download surfaces already
    cover that persistence path.
  EVIDENCE:
  - user_instruction: add `asset_transaction.py`
  - user_instruction: add `bootstrap_manifest.py`
  - user_instruction: remove separate MR transaction uploader/downloader files
  IMPACT: The package shape is leaner and clearer before component
    implementation starts.
  NEXT: use the new transaction and bootstrap-manifest files as the shared
    anchor points when we begin authoring concrete contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task owns the first filesystem scaffold for the Crystallizer package.
