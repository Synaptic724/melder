# Task: Delete Package Init Files Under Core Dirs

## Metadata
- Task ID: TASK-2026-05-05-delete-package-init-files-under-core-dirs
- Story:
- Epic:
- Status: in_progress
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-05T00:20:18Z
- Updated: 2026-05-05T00:20:18Z

## Objective
Delete every `__init__.py` file under:
- `src/melder/aether`
- `src/melder/crystallizer`
- `src/melder/spellbook`
- `src/melder/utilities`

## Ticket Contract
- ENTRY_GATE: the user explicitly requested deleting all `__init__.py` files
  under the four core namespace trees.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/**/__init__.py`
  - `src/melder/crystallizer/**/__init__.py`
  - `src/melder/spellbook/**/__init__.py`
  - `src/melder/utilities/**/__init__.py`
  - focused import/test validation after the delete
- DEPENDENCIES:
  - current namespace-package import surface
  - current interfaces split lane
- EXIT_GATE: all targeted `__init__.py` files are removed and focused import
  validation proves the namespace-package posture still loads.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if a non-empty deleted file
  proves to have been carrying behavior that breaks the requested namespace
  package move.

## Scope Boundaries
- In scope:
  - deletion of targeted `__init__.py` files only
  - focused validation after deletion
- Out of scope:
  - broader package refactors
  - rewriting imports unrelated to fallout from the deletion
  - top-level `src/melder/__init__.py`

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested deleting the core
  namespace-package markers.

## Steps / Checklist
- [ ] Delete the targeted `__init__.py` files.
- [ ] Run focused import and consumer validation.
- [ ] Record any fallout from non-empty package routers that were removed.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- namespace-package-style core trees without nested `__init__.py` markers
- focused validation result

## Files / Paths Impacted
- src/melder/aether/**/__init__.py
- src/melder/crystallizer/**/__init__.py
- src/melder/spellbook/**/__init__.py
- src/melder/utilities/**/__init__.py

## Validation
- Not run.
- Recommended commands:
  - import smoke across `melder.aether`, `melder.spellbook`, `melder.crystallizer`, and `melder.utilities`
  - focused unit rings already used by the interfaces/crystallizer lanes

## Risks / Rollback Notes
- Risk: several targeted files are not empty package markers today, so this can
  remove export-router behavior in addition to the package marker itself.
  Rollback: restore only the specific package files that prove to carry required
  behavior after the validation ring shows concrete fallout.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-05T00:20:18Z
  TYPE: FACT
  CLAIM: The requested delete set is large and not purely empty markers. There
    are `100` targeted `__init__.py` files under the four requested trees, and
    a non-trivial subset are non-empty package routers today, including
    package-level routing under the Nexus, Rift, frame-descriptor, interfaces,
    and AI-support areas.
  EVIDENCE:
  - filesystem_inventory: targeted init scan under `src/melder/aether`, `src/melder/crystallizer`, `src/melder/spellbook`, and `src/melder/utilities`
  - targeted_count: `100`
  - nonempty_examples:
    - `src/melder/aether/nexus/__init__.py`
    - `src/melder/aether/nexus/rift/frame_link/__init__.py`
    - `src/melder/aether/nexus/rift/frame_viewer/__init__.py`
    - `src/melder/aether/nexus/rift/rift_space/memory_system/__init__.py`
    - `src/melder/utilities/ai_native_support_tools/__init__.py`
  IMPACT: This is still a valid delete tranche because you explicitly asked for
    it, but the post-delete validation matters because we are removing some
    active package wiring, not just empty markers.
  NEXT: delete the full targeted set and run focused import/consumer
    validation immediately afterward.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the namespace-package delete tranche across the four core trees.
