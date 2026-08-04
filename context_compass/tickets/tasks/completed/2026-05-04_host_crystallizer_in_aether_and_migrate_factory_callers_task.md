# Task: Host Crystallizer In Aether And Migrate Factory Callers
- Completed: 2026-05-10T00:06:36Z
- Summary: Closed after Crystallizer was hosted in Aether like Nexus and the
  direct crystal-construction callers were moved onto the factory seam.

## Metadata
- Task ID: TASK-2026-05-04-host-crystallizer-in-aether-and-migrate-factory-callers
- Story:
- Epic: EPIC-2026-05-04-implement-crystallizer-configuration-and-activation
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-04T22:44:22Z
- Updated: 2026-05-10T00:06:36Z

## Objective
Move the crystallizer root to the same hosted-singleton posture as Nexus:
- `Aether` privately hosts the singleton
- the hosted root starts unconfigured and inactive
- direct caller/test construction shifts toward `Crystallizer.create_spell_crystal(...)`

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the follow-on cleanup after the
  first configuration/singleton slice and required the hosted-root posture to
  match Nexus via Aether.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aether.py`
  - `src/melder/crystallizer/crystallizer.py`
  - direct `SpellCrystal(...)` test callers that should move to the root
    factory seam
  - focused Aether/crystallizer tests for the new hosted-root behavior
- DEPENDENCIES:
  - `tickets/tasks/2026-05-04_implement_crystallizer_configuration_and_singleton_task.md`
  - `src/melder/aether/nexus/nexus.py`
  - `tests/unit/melder/aether/test_aether.py`
  - `tests/unit/melder/crystallizer/test_crystallizer.py`
- EXIT_GATE: Aether hosts a private crystallizer singleton in the same
  configured-but-disabled style as Nexus, and the main test/caller surfaces
  use `Crystallizer.create_spell_crystal(...)` instead of constructing
  `SpellCrystal` directly.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if matching the Nexus hosting
  pattern requires a wider public-interface redesign than this bounded slice
  can safely own.

## Scope Boundaries
- In scope:
  - Aether-hosted crystallizer boot and cleanup
  - crystallizer first-init behavior aligned with hosted-singleton semantics
  - migration of the direct spell-crystal test callers to the crystallizer
    factory surface where appropriate
  - focused unit/component/integration test updates for that seam
- Out of scope:
  - full loader implementation
  - removal of `SpellCrystal.__init__` as an internal seam
  - broader crystallizer identity redesign

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the hosted-root and factory-call migration slice is
  implemented, validated, and ready for user review.

## Steps / Checklist
- [x] Patch `Aether` to host `Crystallizer` like it hosts `Nexus`.
- [x] Align `Crystallizer` first-init behavior with the hosted-root posture.
- [x] Move direct test/caller seams toward `create_spell_crystal(...)`.
- [x] Add or update focused tests for the hosted-root behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Aether-hosted crystallizer root
- factory-oriented spell-crystal caller/test seam
- focused validation for the hosted-root lifecycle

## Files / Paths Impacted
- src/melder/aether/aether.py
- src/melder/crystallizer/crystallizer.py
- tests/unit/melder/aether/test_aether.py
- tests/unit/melder/crystallizer/test_crystallizer.py
- tests/unit/melder/crystallizer/test_spell_crystal.py
- tests/component/melder/crystallizer/test_spell_crystal_component.py
- tests/integration/melder/crystallizer/test_spell_crystal_integration.py

## Validation
- Executed:
  - `python -m py_compile src/melder/aether/aether.py src/melder/crystallizer/crystallizer.py tests/unit/melder/aether/test_aether.py tests/unit/melder/crystallizer/test_crystallizer.py tests/unit/melder/crystallizer/test_spell_crystal.py tests/component/melder/crystallizer/test_spell_crystal_component.py tests/integration/melder/crystallizer/test_spell_crystal_integration.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_aether.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_crystallizer.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/crystallizer/test_spell_crystal.py`
  - `python -m pytest -q -p no:cacheprovider tests/component/melder/crystallizer/test_spell_crystal_component.py`
  - `python -m pytest -q -p no:cacheprovider tests/integration/melder/crystallizer/test_spell_crystal_integration.py`
- Result:
  - compile validation passed
  - `test_aether.py` passed (`126 passed`)
  - `test_crystallizer.py` passed (`7 passed`)
  - `test_spell_crystal.py` passed (`92 passed`)
  - component spell-crystal ring passed (`40 passed`)
  - integration spell-crystal ring passed (`80 passed`)

## Risks / Rollback Notes
- Risk: forcing Nexus-style first-time Aether hosting on `Crystallizer` may
  make some low-level tests too rigid.
  Rollback: keep the hosted-root lifecycle in Aether while retaining a narrow
  internal construction seam for direct isolated tests if evidence proves that
  boundary is necessary.

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
- DATETIME: 2026-05-04T22:44:22Z
  TYPE: PLAN
  CLAIM: The first crystallizer slice landed as a standalone singleton root,
    but the repo's actual hosting pattern is stronger than that: `Aether`
    eagerly creates private hosted roots like `Nexus` and tears them down on
    singleton cleanup. The direct `SpellCrystal(...)` call surface is now
    basically limited to tests, so the next bounded cleanup is to host
    `Crystallizer` the same way and move those tests toward
    `create_spell_crystal(...)`.
  EVIDENCE:
  - src/melder/aether/aether.py:72-79
  - src/melder/aether/aether.py:123-123
  - src/melder/crystallizer/crystallizer.py:277-280
  - tests/unit/melder/aether/test_aether.py:378-400
  - tests/unit/melder/crystallizer/test_spell_crystal.py:48-67
  IMPACT: This keeps the crystallizer root aligned with the live runtime's
    singleton-hosting model and narrows the remaining direct constructor seam.
  NEXT: patch the hosted-root lifecycle first, then migrate the test/caller
    seam and validate the new behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-04T22:52:11Z
  TYPE: MEASURE
  CLAIM: The hosted-root slice is landed and green. `Aether` now privately
    hosts `Crystallizer` the same way it hosts `Nexus`, the hosted root starts
    unconfigured and inactive, first-time crystallizer bootstrap now requires
    the Aether host just like Nexus, direct spell-crystal test callers were
    moved to `Crystallizer.create_spell_crystal(...)`, and the matching
    architecture and component docs now acknowledge the hosted crystallizer
    root in the Aether boot/ownership story.
  EVIDENCE:
  - src/melder/aether/aether.py:1-346
  - src/melder/crystallizer/crystallizer.py:1-312
  - tests/unit/melder/aether/test_aether.py:1-413
  - tests/unit/melder/crystallizer/test_crystallizer.py:1-133
  - tests/unit/melder/crystallizer/test_spell_crystal.py:1-263
  - tests/component/melder/crystallizer/test_spell_crystal_component.py:1-115
  - tests/integration/melder/crystallizer/test_spell_crystal_integration.py:1-187
  - codex/context_compass/system_docs/src_architecture.md:385-456
  - codex/context_compass/system_docs/src_components.md:397-427
  IMPACT: The crystallizer root now follows the live runtime's actual hosting
    grammar, and the public construction seam is cleaner because callers/tests
    are no longer leaning on direct `SpellCrystal(...)` construction by
    default.
  NEXT: decide whether the remaining low-level `SpellCrystal.__init__(..., user_source_root_paths=...)`
    seam should stay as an internal constructor seam or collapse into a
    smaller internal classification context later.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the follow-on cleanup after the first crystallizer
configuration/root slice: host the root in Aether like Nexus and move the
direct spell-crystal test seam toward the crystallizer factory.
