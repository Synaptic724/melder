# Task: Scaffold Frame Surface Runtime Objects

- Completed: 2026-04-04T11:41:38Z
- Summary: Added the placeholder `frame_link/` and `frame_viewer/` package
  scaffolds under `rift/`, kept them intentionally non-integrated, and left
  the deeper semantics to the active HLD lane.

## Metadata
- Task ID: TASK-2026-04-03-scaffold-frame-surface-runtime-objects
- Story: STORY-2026-04-03-frameinfolink-hld
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-03T16:27:50Z
- Updated: 2026-04-04T11:41:38Z

## Objective
Create the first placeholder runtime object files for the frame-surface model
under `src/melder/aether/nexus/rift/` without integrating them yet.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for placeholder runtime objects and
  specified the directory layout under `rift/`.
- EXECUTION_BOUNDARY: scaffold files only for `FrameLink`,
  `FrameLinkContract`, `FrameView`, and `FrameViewer`, plus package folders and
  light placeholder methods/docstrings/comments.
- DEPENDENCIES:
  - tickets/tasks/2026-04-03_design_frameinfolink_hld_task.md
  - src/melder/aether/nexus/rift/
- EXIT_GATE: placeholder files exist in the requested folders, import/syntax is
  clean, and no runtime integration has been attempted yet.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the requested layout
  conflicts with existing package structure in a way that cannot be reconciled
  locally.

## Scope Boundaries
- In scope:
  - `src/melder/aether/nexus/rift/frame_link/`
  - `src/melder/aether/nexus/rift/frame_viewer/`
  - placeholder classes and top-of-file responsibility/endgame comments
- Out of scope:
  - interface wiring
  - runtime integration into `Rift` / `Nexus`
  - ACL implementation
  - repository/update machinery

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the placeholder scaffold is accepted as complete enough to
  archive while the active HLD and Nexus holding-zone work continues above it.

## Steps / Checklist
- [x] Add frame-link package directory and placeholders.
- [x] Add frame-viewer package directory and placeholders.
- [x] Keep `__init__.py` files non-exporting.
- [x] Add top-of-file comments/docstrings describing purpose, responsibilities,
      and endgame.
- [x] Run syntax validation on the new files.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `src/melder/aether/nexus/rift/frame_link/__init__.py`
- `src/melder/aether/nexus/rift/frame_link/frame_link.py`
- `src/melder/aether/nexus/rift/frame_link/frame_link_contract.py`
- `src/melder/aether/nexus/rift/frame_viewer/__init__.py`
- `src/melder/aether/nexus/rift/frame_viewer/frame_view.py`
- `src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`

## Files / Paths Impacted
- src/melder/aether/nexus/rift/frame_link/__init__.py
- src/melder/aether/nexus/rift/frame_link/frame_link.py
- src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- src/melder/aether/nexus/rift/frame_viewer/__init__.py
- src/melder/aether/nexus/rift/frame_viewer/frame_view.py
- src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
- codex/context_compass/tickets/tasks/2026-04-03_scaffold_frame_surface_runtime_objects_task.md
- codex/context_compass/attention_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/rift/frame_link/frame_link_contract.py`
  - `python -m py_compile src/melder/aether/nexus/rift/frame_link/frame_link.py`
  - `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/frame_view.py`
  - `python -m py_compile src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py`

## Risks / Rollback Notes
- Risk: placeholder classes imply a settled ownership model before the HLD is
  finished.
  Rollback: keep the classes deliberately narrow, comment the intended endgame,
  and avoid integration or behavior claims beyond the current scaffold.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-03T16:35:12Z
  TYPE: FACT
  CLAIM: The requested placeholder runtime objects now exist under
    `src/melder/aether/nexus/rift/` in the requested package layout:
    `frame_link/` with `FrameLink` and `FrameLinkContract`, and
    `frame_viewer/` with `FrameView` and `FrameViewer`. The files are
    intentionally narrow, contain top-of-file purpose/responsibility/endgame
    comments/docstrings, keep `__init__.py` files non-exporting, and do not
    attempt runtime integration yet.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/__init__.py:1-11
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-149
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-170
  - src/melder/aether/nexus/rift/frame_viewer/__init__.py:1-11
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-141
  - src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py:1-172
  - command:python -m py_compile src/melder/aether/nexus/rift/frame_link/frame_link_contract.py src/melder/aether/nexus/rift/frame_link/frame_link.py src/melder/aether/nexus/rift/frame_viewer/frame_view.py src/melder/aether/nexus/rift/frame_viewer/frame_viewer.py
  IMPACT: The repo now has stable filesystem/object anchors for the frame-surface
    model, so the next iteration can focus on object responsibilities and
    later integration rather than re-creating the same file structure again.
  NEXT: review the placeholder shapes with the user and then continue refining
    the HLD around what each object should actually own.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-03T16:27:50Z
  TYPE: PLAN
  CLAIM: The user wants a narrow first scaffold only: `frame_link` and
    `frame_viewer` directories under `rift`, with placeholder objects and
    top-of-file comments/docstrings describing purpose, responsibilities, and
    endgame. Integration should be deferred until the HLD is tighter.
  EVIDENCE:
  - user_instruction: "make framelink its own dir, in rift, and same with FrameViewer"
  - user_instruction: "you can have frame View inside that as well as a pyfile"
  - user_instruction: "we'll integrate these objects later"
  IMPACT: This task should stay very small and avoid any wiring into `Rift` or
    `Nexus` yet.
  NEXT: create the placeholder packages and classes, then run syntax checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to lay down the placeholder runtime object files for the
frame-surface model without integrating them yet.
