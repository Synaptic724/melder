# Task: lay spell compiler foundation

- Completed: 2026-05-21T09:28:33Z
- Summary: Landed the additive SpellCompiler foundation surfaces, validated the focused foundation ring, and closed the temporary patch-artifact lane now that the later replacement suite is the active coverage owner.

## Metadata
- Task ID: TASK-2026-05-20-lay-spell-compiler-foundation
- Story: none
- Epic: EPIC-2026-05-20-decompose-spell-runtime-compiler-ownership
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-20T10:17:06Z
- Updated: 2026-05-21T09:28:33Z

## Objective
Add the first foundation layer for the spell decomposition lane:
introduce `SpellCompilerArtifact`, introduce `SpellCompilerSystem`, and wire
`Spell` to own the artifact without removing `SpellCrafter` behavior yet.

## Ticket Contract
- ENTRY_GATE: the spell ownership investigation is routed, the epic exists,
  the patch artifacts are linked, and the implementation mapping note is
  written before code edits.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell.py`
  - new spell-compiler foundation modules
  - directly implicated interfaces only
  - `spellbook_creation_system.py` and `meld.py` only if the foundation slice
    must expose the new system there immediately
- DEPENDENCIES:
  - tickets/tasks/2026-05-20_investigate_spell_ownership_and_decomposition_task.md
  - tickets/epics/2026-05-20_decompose_spell_runtime_compiler_ownership_epic.md
  - patch docs under `system_docs/patches/active/spell_compiler_foundation/`
- EXIT_GATE: new artifact/system classes exist, `Spell` owns the artifact, and
  no existing `SpellCrafter` behavior is removed in this slice.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the foundation slice cannot
  be wired without removing or rewriting live `SpellCrafter` behavior.

## Scope Boundaries
- In scope:
  - add `SpellCompilerArtifact`
  - add `SpellCompilerSystem`
  - add `Spell` field/init wiring for the artifact
  - mirror current `SpellCrafter` state fields into the artifact foundation
- Out of scope:
  - removing `_crafter` from `Spell`
  - deleting or hollowing out `SpellCrafter`
  - full creation-context ownership redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly selected a foundation-first slice:
  mirror the state out, do not remove behavior yet, and start the epic now.

## Steps / Checklist
- [x] Finalize patch docs and implementation mapping note.
- [x] Add `SpellCompilerArtifact`.
- [x] Add `SpellCompilerSystem`.
- [x] Wire `Spell` to own the artifact foundation.
- [x] Touch only the minimum interface/runtime surfaces needed for truthful foundation wiring.
- [x] Validate the focused foundation ring.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- new spell compiler artifact type
- new spell compiler system type
- `Spell` foundation wiring for the new artifact

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-05-20_lay_spell_compiler_foundation_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m py_compile <touched spell/compiler/interface/test files>`
  - `.\.venv_new\Scripts\python.exe -m pytest -q <focused spell/compiler rings>`

## Risks / Rollback Notes
- Risk: foundation wiring accidentally starts behavior migration instead of
  just setting up the new state/service surfaces.
  Rollback: keep the new classes but stop before redirecting live runtime use.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/spell_compiler_foundation/architecture_patch.md
  - system_docs/patches/active/spell_compiler_foundation/component_patch_spell.md
  - system_docs/patches/active/spell_compiler_foundation/component_patch_spell_crafter.md
  - system_docs/patches/active/spell_compiler_foundation/component_patch_spell_compiler_system.md
  - system_docs/patches/active/spell_compiler_foundation/component_patch_spellbook_creation_system.md
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: remove patch-lane artifacts after the foundation code/docs are merged and validated

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-20T10:17:06Z
  TYPE: DECISION
  CLAIM: The first implementation slice is foundation only. We will add the new
    artifact and system surfaces and wire `Spell` to own the artifact, but we
    will not remove or rewrite live `SpellCrafter` behavior in this task.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  - tickets/tasks/2026-05-20_investigate_spell_ownership_and_decomposition_task.md:121-145
  IMPACT: This keeps the first slice bounded and avoids trying to migrate the
    whole compiler/runtime path at once.
  NEXT: create the patch docs, then patch the new artifact/system foundation in
    the minimum runtime surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:22:31Z
  TYPE: MEASURE
  CLAIM: The foundation runtime compiles and the focused ring is almost green.
    The only failure is in the new foundation test helper itself:
    `_CleanableArtifact` tried to write to the read-only `Cleanable.cleaned`
    property. This is a local test-helper mistake, not a runtime foundation
    problem.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\spellbook\\spell.py src\\melder\\aether\\spellbook\\spell_crafter\\spell_compiler_artifact.py src\\melder\\aether\\spellbook\\spell_crafter\\spell_compiler_system.py src\\melder\\aether\\conduit\\meld\\meld.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py` -> `1 failed, 169 passed`
  - tests/unit/melder/spellbook/test_spell_compiler_foundation.py:55-63
  IMPACT: The foundation slice itself is stable enough to keep; only the local
    helper needs correction before rerunning the same focused ring.
  NEXT: fix `_CleanableArtifact` to track cleanup on its own field, then rerun
    the same focused validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:23:58Z
  TYPE: FACT
  CLAIM: The additive compiler foundation slice is landed. New
    `SpellCompilerArtifact` and `SpellCompilerSystem` classes exist, `Spell`
    now owns a `_compiler_artifact`, and `Meld` now owns a
    `_spell_compiler_system`. No live `SpellCrafter` behavior was removed in
    this slice.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_compiler_artifact.py:1-222
  - src/melder/aether/spellbook/spell_crafter/spell_compiler_system.py:1-74
  - src/melder/aether/spellbook/spell.py:13-13
  - src/melder/aether/spellbook/spell.py:164-171
  - src/melder/aether/spellbook/spell.py:182-205
  - src/melder/aether/spellbook/spell.py:364-367
  - src/melder/aether/spellbook/spell.py:436-448
  - src/melder/aether/spellbook/spell.py:521-524
  - src/melder/aether/conduit/meld/meld.py:28-30
  - src/melder/aether/conduit/meld/meld.py:46-55
  - src/melder/aether/conduit/meld/meld.py:136-142
  - src/melder/aether/conduit/meld/meld.py:188-190
  IMPACT: The new ownership surfaces exist, so the next slice can start moving
    real compiler state/logic without first inventing where it belongs.
  NEXT: decide the first migration inside the foundation: whether to start
    copying state between `SpellCrafter` and `SpellCompilerArtifact`, or to
    redirect one narrow runtime call path through `SpellCompilerSystem`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:23:58Z
  TYPE: MEASURE
  CLAIM: The focused foundation validation ring is green on `.venv_new` after
    fixing the local test-helper mistake.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\spellbook\\spell.py src\\melder\\aether\\spellbook\\spell_crafter\\spell_compiler_artifact.py src\\melder\\aether\\spellbook\\spell_crafter\\spell_compiler_system.py src\\melder\\aether\\conduit\\meld\\meld.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py` -> `170 passed, 1 warning`
  IMPACT: The additive foundation slice is stable enough to build the next
    decomposition step on top of it.
  NEXT: pick the first real migration step off this foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:24:31Z
  TYPE: FACT
  CLAIM: The user moved `SpellCompilerSystem` under the conduit side at
    `src/melder/aether/conduit/spell_compiler_system`. That changes the
    intended ownership namespace for the new compiler-system surface and means
    the current spell-side placement needs to be realigned before further
    foundation work continues.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next step is not new feature work; it is path/import verification
    and any required runtime/test realignment to the user-chosen location.
  NEXT: inspect the new path and the old spell-side module placement, then fix
    import fallout in the active foundation slice if needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T10:25:12Z
  TYPE: FACT
  CLAIM: The user-directed move is already consistent with the live code. The
    compiler foundation files now live under
    `src/melder/aether/conduit/spell_compiler_system/`, the older
    spell-side `spell_crafter/` package no longer contains those files, and
    current runtime/test imports already resolve from the conduit-side path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:1-1
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-1
  - src/melder/aether/spellbook/spell.py:34-35
  - src/melder/aether/conduit/meld/meld.py:30-31
  - tests/unit/melder/spellbook/test_spell_compiler_foundation.py:7-11
  IMPACT: No corrective path move is needed. Future compiler-foundation work
    should continue from the conduit-side namespace.
  NEXT: keep building on the moved conduit-side foundation path instead of the
    older spell-side location.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T10:29:02Z
  TYPE: DECISION
  CLAIM: The next bounded follow-up in the foundation slice is to give
    `SpellCompilerArtifact` its own explicit spell identity. The artifact should
    carry the owning spell's `spell_id`, and `Spell` should stamp that value
    into the artifact at construction time by default.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:27-115
  - src/melder/aether/spellbook/spell.py:364-370
  IMPACT: This keeps the artifact foundation self-identifying before any later
    migration of compiler state into it.
  NEXT: patch `SpellCompilerArtifact.__init__`, patch `Spell` construction, and
    extend the focused foundation test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T10:30:31Z
  TYPE: FACT
  CLAIM: `SpellCompilerArtifact` now carries explicit spell identity through
    `spell_id`, and `Spell` stamps that identity into the artifact at
    construction time by default.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:45-118
  - src/melder/aether/spellbook/spell.py:364-370
  - tests/unit/melder/spellbook/test_spell_compiler_foundation.py:90-97
  IMPACT: The artifact foundation is now self-identifying, which makes later
    migration of compiler-owned state into it cleaner and less implicit.
  NEXT: continue the next migration step from this identity-stamped foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T10:30:31Z
  TYPE: MEASURE
  CLAIM: The focused foundation ring stayed green after adding `spell_id` to
    `SpellCompilerArtifact` and wiring `Spell` to stamp it during
    construction.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\conduit\\spell_compiler_system\\spell_compiler_artifact.py src\\melder\\aether\\spellbook\\spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py` -> `170 passed, 1 warning`
  IMPACT: The identity stamp is safe and we still have a stable base for the
    next compiler-decomposition step.
  NEXT: choose the next bounded migration off this foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:31:52Z
  TYPE: FACT
  CLAIM: The phase result types are already concrete in the live runtime. Phase
    4 caches `SpellValidationResult`, and Phase 6 caches
    `SpellSystemValidationState`. The current `Any` annotations are stale
    holdovers, not real polymorphism requirements.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/validation/spell_validation_result.py:12-59
  - src/melder/aether/spellbook/spell_crafter/system/spell_system_validation_state.py:11-39
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:277-280
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4141-4155
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5289-5306
  IMPACT: We can tighten the new foundation artifact and the adjacent spell /
    crafter / interface surfaces to concrete result types without inventing new
    abstractions.
  NEXT: patch the artifact, `SpellCrafter`, `Spell`, and the relevant
    interfaces to use the concrete Phase 4 and Phase 6 result types.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:34:06Z
  TYPE: FACT
  CLAIM: The stale `Any` surfaces are now tightened to the real runtime
    classes. Phase 4 is typed as `Optional[SpellValidationResult]`, and Phase 6
    is typed as `Optional[SpellSystemValidationState]` across the new compiler
    artifact, `SpellCrafter`, `Spell`, and the adjacent `ISpell` /
    `ISpellCrafter` surfaces.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:12-29
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:98-103
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:83-85
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:277-280
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:634-645
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:837-845
  - src/melder/aether/spellbook/spell.py:16-18
  - src/melder/aether/spellbook/spell.py:936-955
  - src/melder/utilities/interfaces/ispell.py:20-25
  - src/melder/utilities/interfaces/ispell.py:488-505
  - src/melder/utilities/interfaces/ispellcrafter.py:6-11
  - src/melder/utilities/interfaces/ispellcrafter.py:76-85
  - src/melder/utilities/interfaces/ispellcrafter.py:254-263
  IMPACT: The foundation slice now reflects the real Phase 4 / Phase 6 result
    classes instead of leaking `Any` through the spell/compiler boundary.
  NEXT: continue the next bounded migration off this more concrete foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:34:06Z
  TYPE: MEASURE
  CLAIM: The focused foundation ring remained green after tightening the Phase
    4 / Phase 6 result types.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\conduit\\spell_compiler_system\\spell_compiler_artifact.py src\\melder\\aether\\spellbook\\spell.py src\\melder\\aether\\spellbook\\spell_crafter\\spell_crafter.py src\\melder\\utilities\\interfaces\\ispell.py src\\melder\\utilities\\interfaces\\ispellcrafter.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py` -> `170 passed, 1 warning`
  IMPACT: The concrete result typing is safe on the current foundation slice.
  NEXT: choose the next bounded migration off this foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:35:17Z
  TYPE: FACT
  CLAIM: `SpellCompilerArtifact.cleanup()` now follows the explicit owned-field
    cleanup style instead of using a generic `getattr(..., "cleanup", None)`
    helper. The cleanup path now mirrors the current `SpellCrafter` pattern:
    explicit per-field best-effort cleanup for known owned artifacts, followed
    by explicit deletion of the stored references.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:133-212
  IMPACT: The artifact cleanup path no longer pays the generic owned-code
    introspection overhead and matches the repoâ€™s stricter cleanup style.
  NEXT: continue the next bounded migration off this foundation with the
    cleanup contract now aligned to repo rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T10:35:17Z
  TYPE: MEASURE
  CLAIM: The focused foundation ring stayed green after replacing the generic
    cleanup helper with explicit per-field cleanup in `SpellCompilerArtifact`.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\conduit\\spell_compiler_system\\spell_compiler_artifact.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py` -> `170 passed, 1 warning`
  IMPACT: The cleanup-style correction is safe on the current foundation slice.
  NEXT: choose the next bounded migration off this foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:39:21Z
  TYPE: FACT
  CLAIM: One cleanup-shape mismatch still remains in
    `SpellCompilerArtifact`: the Phase 5 blueprint-map cleanup is still hiding
    behind a helper method instead of being inlined directly into `cleanup()`
    the way the current `SpellCrafter` cleanup block is structured.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:178-213
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:281-297
  IMPACT: The artifact cleanup is closer to the repo pattern, but not yet a
    literal concrete copy of the relevant `SpellCrafter` cleanup shape.
  NEXT: inline the Phase 5 blueprint-map cleanup into
    `SpellCompilerArtifact.cleanup()` and remove the leftover helper method.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T10:40:08Z
  TYPE: FACT
  CLAIM: The leftover Phase 5 blueprint-map cleanup helper is gone.
    `SpellCompilerArtifact.cleanup()` now inlines the retained blueprint-map
    cleanup directly, matching the concrete `SpellCrafter` cleanup style more
    closely instead of hiding that teardown behind another helper method.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:133-203
  IMPACT: The artifact cleanup path is now concrete end-to-end and no longer
    carries the extra helper abstraction you called out.
  NEXT: continue the next bounded migration off this foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T10:40:08Z
  TYPE: MEASURE
  CLAIM: The focused foundation ring stayed green after inlining the Phase 5
    blueprint-map cleanup and removing the helper.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\conduit\\spell_compiler_system\\spell_compiler_artifact.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py` -> `170 passed, 1 warning`
  IMPACT: The cleanup-shape correction is safe on the current foundation slice.
  NEXT: choose the next bounded migration off this foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:42:17Z
  TYPE: FACT
  CLAIM: The bigger gap is not just cleanup style, it is cleanup semantics.
    `SpellCrafter` exposes multiple top-level state-management behaviors:
    full `cleanup()`, structural-only `reset_phase_artifacts()` /
    `cleanup_phase_artifacts()`, Phase-5-and-later `clear_phase5_artifacts()`,
    and the phase5 setters that also refresh/invalidate codegen-IR state.
    `SpellCompilerArtifact` currently only has full cleanup, so it is not yet a
    real mirror of the compiler-state lifecycle surface.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:310-380
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:422-506
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1036-1069
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1498-1498
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3060-3060
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3239-3239
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:133-203
  IMPACT: If the artifact is going to become the real state owner, it needs the
    same reset/clear lifecycle entrypoints instead of only one monolithic
    teardown method.
  NEXT: mirror the top-of-file `SpellCrafter` state-management methods onto
    `SpellCompilerArtifact` and keep the focused foundation ring green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:45:02Z
  TYPE: FACT
  CLAIM: `SpellCompilerArtifact` now mirrors the top-level `SpellCrafter`
    state-management surface much more closely. It now exposes:
    - `reset_phase_artifacts()`
    - `cleanup_phase_artifacts()`
    - `clear_phase5_artifacts()`
    - `set_root_blueprint_phase5(...)`
    - `set_spell_system_index_phase5(...)`
    - owned phase2_5 / phase8_11 IR refresh-reset helpers
    and the full cleanup path stays explicit with no `getattr(...)` helper.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:133-326
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:310-380
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:422-506
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1036-1069
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1498-1498
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3239-3239
  IMPACT: The artifact is no longer just a bag of mirrored fields; it now has
    the same broad lifecycle entrypoints the eventual compiler-state owner will
    need.
  NEXT: choose the next bounded migration step that routes live state through
    the artifact instead of only mirroring it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T10:45:02Z
  TYPE: MEASURE
  CLAIM: The focused foundation ring stayed green after adding the mirrored
    reset/clear lifecycle surface to `SpellCompilerArtifact`.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m py_compile src\\melder\\aether\\conduit\\spell_compiler_system\\spell_compiler_artifact.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py`
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py` -> `170 passed, 1 warning`
  IMPACT: The mirrored lifecycle surface is stable on the current foundation
    slice.
  NEXT: choose the next bounded migration off this foundation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T11:17:25Z
  TYPE: DECISION
  CLAIM: The user confirmed that `SpellCompilerArtifact` should remain a
    spell-owned state/cleanup container in this slice. The extra non-cleanup
    artifact methods copied from `SpellCrafter` are out of scope here and are
    not part of the live runtime wiring, so this step will cut that surface
    back to cleanup/lifecycle-only behavior.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:238-496
  - src/melder/aether/spellbook/spell.py:375-376
  - src/melder/aether/spellbook/spell.py:458-460
  - codex/context_compass/system_docs/patches/active/spell_compiler_foundation/component_patch_spell_crafter.md:14-20
  IMPACT: This keeps the artifact foundation narrow and prevents the
    foundation slice from hardening a fake phase-manager API before the real
    migration is approved.
  NEXT: remove the unused non-cleanup artifact methods and leave only the
    cleanup/lifecycle surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T11:17:25Z
  TYPE: FACT
  CLAIM: The current compiler-side code is still only a foundation stub.
    `spell_compiler.py` is effectively empty, `SpellCompilerSystem` is still a
    minimal spellbook holder that imports `SpellCrafter`, and the real
    behavior still lives on the large non-init `SpellCrafter` surface. A
    truthful static port therefore needs the artifact to carry the borrowed
    spell-scoped refs that the `SpellCrafter` methods already read.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-1
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-56
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:145-305
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:589-645
  IMPACT: The first truthful migration slice is not just copying text into
    `SpellCompiler`; it also requires wiring the artifact to hold the
    spell-scoped borrowed refs that those static methods will read.
  NEXT: port the non-init `SpellCrafter` methods into a static
    `SpellCompiler`, and add the borrowed state fields the port requires on
    `SpellCompilerArtifact`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T12:04:22Z
  TYPE: PLAN
  CLAIM: The user redirected the investigation to `SpellIndex` ownership
    state. The immediate question is whether `_owner_spellbook` should become a
    narrow `_owner_spellbook_id` field and whether `_owner_spell` is actually
    required, or whether both are just historical broad references that can be
    cut down safely.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  - src/melder/aether/spellbook/bind/spell_index.py:67-71
  IMPACT: This decides whether we can simplify the owner model before more
    compiler-state migration continues.
  NEXT: inventory every runtime use of `_owner_spellbook` and `_owner_spell`,
    then classify which callers truly need ids versus live object references.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T12:05:25Z
  TYPE: FACT
  CLAIM: The traced owner chain is concrete. `Spellbook.bind(...)` attaches the
    live owner references onto `SpellIndex` before
    `SpellSystemStates.register_index(...)` runs, so `SpellSystemStates` does
    not need `ISpell` to discover owner spellbook identity. But
    `SpellIndex.update(...)` still uses the live owner spellbook object for
    callback-driven spell-id map maintenance, and it still uses `_owner_spell`
    as the exact spell instance passed into that callback. So
    `_owner_spellbook_id` alone is not enough for the current runtime, while
    `_owner_spell` looks more removable with a narrower follow-up refactor.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2879-2881
  - src/melder/aether/spellbook/spellbook.py:2900-2908
  - src/melder/aether/spellbook/spellbook.py:2924-2927
  - src/melder/aether/spellbook/bind/spell_index.py:149-150
  - src/melder/aether/spellbook/bind/spell_index.py:191-196
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:763-765
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1297-1305
  IMPACT: If we want to remove `ISpell` from `SpellSystemStates`, that looks
    like a clean seam cut. If we also want to replace `_owner_spellbook` with
    `_owner_spellbook_id` and remove `_owner_spell`, that is a second,
    deeper ownership refactor because version-update propagation currently
    still depends on live owner objects.
  NEXT: choose whether to do only the `SpellSystemStates` seam cut first, or
    also refactor `SpellIndex.update(...)` / Spellbook id-map maintenance so
    the live owner references can shrink.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T12:08:24Z
  TYPE: FACT
  CLAIM: `_owner_spell` on `SpellIndex` looks removable with a contained
    refactor. The runtime search shows it is only used in
    `SpellIndex.update(...)` to pass the exact spell object into
    `Spellbook._update_owned_spell_id(...)`, and in transfer-of-ownership to
    assert/rewrite owner consistency. There are no broader runtime consumers.
    That means the persistent `_owner_spell` back-reference is not a deep
    ownership requirement; it is a convenience field that can be eliminated if
    the owned spell-id update path resolves the live spell from Spellbook's own
    maps instead.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/spell_index.py:149-150
  - src/melder/aether/spellbook/bind/spell_index.py:193-196
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:764-765
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1298-1304
  - tests/unit/melder/spellbook/bind/test_spell_index.py:465-477
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:3673-3689
  IMPACT: `_owner_spell` is the cleaner field to kill first. It is not needed
    by `SpellSystemStates`, and removing it does not require redefining
    owner-spellbook identity; it only requires tightening the spell-id update
    path and transfer consistency checks.
  NEXT: if approved, refactor `SpellIndex.update(...)`,
    `Spellbook._update_owned_spell_id(...)`, and the transfer ownership checks
    so `_owner_spell` can be removed entirely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T12:19:14Z
  TYPE: DECISION
  CLAIM: This edit slice will be intentionally narrow. We proved the real issue
    in `SpellSystemStates` is owner spellbook identity lookup, so this pass
    will switch that lookup from `spell -> spellbook -> _id` to
    `spell_index -> _owner_spellbook -> _id` without widening the blast radius
    into interface/test signature churn yet.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  - src/melder/aether/spellbook/spellbook.py:2881-2881
  - src/melder/aether/spellbook/spellbook.py:2924-2927
  - src/melder/aether/spellbook/bind/spell_index.py:191-196
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:284-292
  IMPACT: This updates the proven dependency without dragging interface and
    test-surface signature changes into the same tranche.
  NEXT: patch `SpellSystemStates.register_index(...)` to resolve owner
    spellbook id from `spell_index`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T14:20:52Z
  TYPE: FACT
  CLAIM: The target decomposition namespace exists but is still empty:
    `src/melder/aether/conduit/spell_compiler_system/phases/` currently has no
    phase modules. That means the next migration map has to be derived from the
    live `SpellCrafter` surface rather than from any existing compiler-phase
    split.
  EVIDENCE:
  - filesystem_inventory: src/melder/aether/conduit/spell_compiler_system/phases
  IMPACT: We cannot route work into pre-existing phase classes yet. The first
    investigation step is to identify which `SpellCrafter` methods are pure
    phase operations versus spell-owned state/lifecycle methods.
  NEXT: read the live spell/compiler files and classify the first truthful
    static-cut boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T14:21:10Z
  TYPE: FACT
  CLAIM: The current compiler split is still only structural scaffolding.
    `SpellCompiler` is effectively empty, `SpellCompilerSystem` still directly
    creates `SpellCrafter`, `SpellCompilerArtifact` already owns most of the
    Phase 1-11 state fields plus cleanup/reset helpers, and `Spell` still
    routes its phase facade methods through `_ensure_crafter()` into the live
    `SpellCrafter`. So the truthful next migration is not another state split;
    it is rerouting phase behavior out of `SpellCrafter` into static
    compiler-phase surfaces that mutate the artifact in place.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-55
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-58
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:1-344
  - src/melder/aether/spellbook/spell.py:1-550
  - src/melder/aether/spellbook/spell.py:900-1150
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1-700
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4100-4300
  IMPACT: If we keep moving only fields, `SpellCrafter` remains the real
    compiler and the new compiler namespace stays fake. The next truthful cut
    is method migration by phase group, with `Spell` staying as a facade while
    the behavior moves under compiler-owned static surfaces.
  NEXT: produce the migration map: which `SpellCrafter` methods stay spell-
    owned lifecycle helpers, which become artifact methods, and which should be
    ported into phase-specific static compiler classes first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:21:28Z
  TYPE: FACT
  CLAIM: A pure `run(artifact)` phase API is not possible yet with the current
    artifact shape. The live `SpellCrafter` phase methods do not just read
    phase outputs; they read and mutate borrowed runtime state through
    `self._spell`, `self._spell._spellbook`, `self._spell_system_states`, and
    spell-owned write-back surfaces like `_add_build_details(...)`,
    `resolution_complete`, and execution-plan metrics. So if the target is
    static phase classes that consume only `SpellCompilerArtifact`, the
    artifact has to absorb those borrowed init/runtime references first.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1-700
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4100-4300
  - src/melder/aether/spellbook/spell.py:1-550
  - src/melder/aether/spellbook/spell.py:900-1150
  IMPACT: Without this borrowed-state move, the migration will either keep
    hidden `Spell` / `Spellbook` dependencies inside every static phase entry
    point or force a fake compiler facade that still relies on `SpellCrafter`.
  NEXT: define the borrowed-state expansion for `SpellCompilerArtifact`, then
    port the structural phases against that expanded artifact contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-20T14:20:52Z
  TYPE: DECISION
  CLAIM: The user has frozen the current lane to a mechanical static-phase
    extraction only. Each extracted phase surface must live under
    `src/melder/aether/conduit/spell_compiler_system/phases/` as
    `compiler_phase_<n>.py`, mutate `SpellCompilerArtifact` in place, and take
    explicit runtime collaborators as params when needed. The extraction may
    repoint or expand params only; it may not rewrite behavior, add validation,
    add defensive programming, or add `artifact/spell is None` guards.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: This removes ambiguity about the migration shape and blocks any
    "cleanup while moving" behavior drift.
  NEXT: harden the epic to this exact contract and finish the phase-by-phase
    extraction map.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:24:59Z
  TYPE: PLAN
  CLAIM: The first truthful extraction order is phase-aligned and asymmetrical.
    Phases 1-4 should move first because they already fit the static
    `compiler_phase_<n>.py` model most cleanly: they mainly consume explicit
    collaborators and write back into the artifact/spell surface. Phases 5-12
    should follow only after that pattern is established, because they depend
    on broader spellbook-visible iteration, cross-spell artifact attachment,
    change-control wiring, execution-plan metrics, and the compiled executor
    caches.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1-700
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3000-3400
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4100-4300
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5200-5235
  - src/melder/aether/spellbook/spell.py:900-1150
  - src/melder/aether/spellbook/spell.py:1450-1538
  IMPACT: The next implementation tranche should not try to move all twelve
    phases at once. The first safe extraction is structural phases 1-4, then
    rooted/system phases 5-7, then plan/executor phases 8-12.
  NEXT: produce the concrete phase-module mapping and collaborator signatures
    for the structural tranche first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:26:48Z
  TYPE: DECISION
  CLAIM: The next tranche is now explicit implementation, but still only for
    the extraction surface. We will create the static
    `compiler_phase_<n>.py` modules under
    `src/melder/aether/conduit/spell_compiler_system/phases/`, keep the phase
    classes slot-only with no `__init__`, move the live phase behavior behind
    those explicit static entrypoints, and stop before runtime wiring.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The current work can now touch code, but only within the frozen
    extraction contract. Any cutover or semantic rewrite remains out of scope.
  NEXT: identify the exact files to touch for the phase-module surface and add
    the static classes without changing runtime behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:31:35Z
  TYPE: FACT
  CLAIM: The first extraction surface is now present in code. The
    `spell_compiler_system/phases/` namespace now contains the twelve
    `compiler_phase_<n>.py` modules, each exposing a slot-only static class
    with no `__init__`, and `SpellCompiler` is now the thin static facade that
    delegates into those phase classes. This tranche did not wire runtime
    callers over and did not rewrite the underlying phase behavior; the phase
    classes currently forward mechanically into the canonical `SpellCrafter`
    phase methods.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-277
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:1-61
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_6.py:1-61
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:1-61
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_8.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_9.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_10.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:1-75
  IMPACT: The compiler namespace now has explicit phase surfaces for later
    wiring, and the next migration decision is whether to begin replacing the
    mechanical delegation with direct extracted logic phase by phase.
  NEXT: stop at the extraction boundary and let the next approved tranche pick
    whether to wire the facade or start replacing delegation with direct phase
    logic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:38:13Z
  TYPE: DECISION
  CLAIM: The user rejected the fake wrapper approach and narrowed the next
    implementation slice to phase 1 only. This tranche must replace
    `compiler_phase_1.py` with a direct mechanical port of
    `SpellCrafter.run_phase_requirements(...)`; later phases remain untouched
    until phase 1 is real.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next code change is sharply bounded. No more facade work; the
    new surface must stop referencing `SpellCrafter` as the executor for phase
    1.
  NEXT: read the exact phase-1 method body and port it directly into the
    phase-1 module.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:39:18Z
  TYPE: FACT
  CLAIM: Phase 1 is now the first real direct port. `compiler_phase_1.py` no
    longer references `SpellCrafter`; it now runs the requirements-finder logic
    directly, preserves the current cancellation/cache behavior, and writes the
    retained requirements into `SpellCompilerArtifact._requirements`. The
    `SpellCompiler` phase-1 facade was updated to pass the artifact explicitly.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-49
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-83
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3653-3693
  IMPACT: The extraction is no longer purely facade-level. We now have one
    real compiler phase that uses the new model instead of bouncing back into
    `SpellCrafter`.
  NEXT: stop at the phase-1 boundary and let the next approved tranche choose
    whether to port phase 2 next or widen the compiler facade changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:40:30Z
  TYPE: FACT
  CLAIM: The shared phase-helper module currently has no implementation.
    `src/melder/aether/conduit/spell_compiler_system/phases/utility.py` is
    empty, so the phase extraction does not yet have a canonical compiler-side
    home for generic helpers like cancellation throws.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/utility.py:1-1
  IMPACT: If we want the extracted phases to stop inlining the same generic
    helper logic, we need to establish that helper surface now instead of
    growing ad hoc copies phase by phase.
  NEXT: add the slot-only compiler phase utility surface there and repoint
    phase 1 to use it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-20T14:46:34Z
  TYPE: FACT
  CLAIM: Phase 2 is now the second real direct port. `compiler_phase_2.py` no
    longer references `SpellCrafter`; it now enforces the same phase-1
    requirements precondition, preserves the same current-spell-id runtime
    error, builds the `SpellSymbolicDependency` rows directly from
    `artifact._requirements.parameters`, and stores the resulting
    `SpellSymbolicGraph` on `artifact._symbolic_graph`. The `SpellCompiler`
    phase-2 facade was updated to pass the artifact explicitly.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-113
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-95
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3698-3787
  IMPACT: The extraction now has two real phases on the new model instead of
    only wrapper surfaces, and phase 3 is the next boundary where the
    broader helper/dependency pressure starts to increase materially.
  NEXT: stop at the phase-2 boundary and let the next approved tranche decide
    whether to port phase 3 next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:52:45Z
  TYPE: FACT
  CLAIM: The direct ports for phases 1 and 2 kept the logic but trimmed too
    much of the original explanatory surface. The extracted modules need the
    original method-level docstrings and inline comments copied over as part of
    the migration so the compiler-side phase surfaces do not lose contract and
    rationale detail during the move.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next correction is documentation-only inside the already ported
    phase modules; logic stays unchanged.
  NEXT: restore the phase-1 and phase-2 docstrings/comments from the
    `SpellCrafter` source into the extracted phase modules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T14:55:41Z
  TYPE: FACT
  CLAIM: Phase 2 is still behaviorally incomplete even after the direct port,
    because the current extracted module dropped the final
    `_capture_phase2_5_codegen_ir()` call. That helper is part of the real
    phase-2 behavior surface: it exports normalized phase2_5 metadata into the
    spell-scoped codegen IR payload and updates the deterministic
    `signatures.phase2_5` entry. So phase 2 is not done until the minimum IR
    helper stack needed by that call is ported or relocated to the new model.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1497-1578
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3698-3787
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-113
  IMPACT: Saying phase 2 is complete right now would be false. The immediate
    follow-on is not phase 3; it is the minimum helper migration needed to make
    the phase-2 codegen-IR export behavior real.
  NEXT: port the minimum `_capture_phase2_5_codegen_ir()` support surface into
    the new compiler model, then add the missing call back into phase 2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:02:23Z
  TYPE: FACT
  CLAIM: The missing phase-2 IR export behavior is now ported into the new
    compiler model. `SharedCompilerExecutions` now owns the direct
    `_capture_phase2_5_codegen_ir()` equivalent plus its exact helper stack:
    codegen-IR container creation, deterministic signature-part serialization,
    and signature hashing. `compiler_phase_2.py` now calls that shared helper
    after writing the symbolic graph, so the phase-2 port once again performs
    the structural IR export that the original `SpellCrafter` method performed.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/shared_compiler_executions.py:1-232
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-115
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1420-1578
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3698-3787
  IMPACT: Phase 2 is no longer missing one of its real side effects, and the
    new shared helper surface is now the compiler-side home for later phase2_5
    structural IR refresh calls from phases 3-5.
  NEXT: stop at the phase-2-complete boundary and let the next approved tranche
    decide whether to port phase 3 next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:10:26Z
  TYPE: FACT
  CLAIM: `SharedCompilerExecutions.capture_phase2_5_codegen_ir(...)` is no
    longer using fake phase-5 row placeholders. It now directly owns the
    missing `_socket_row_sort_key(...)`, `_build_phase5_socket_rows(...)`, and
    `_build_phase5_dag_edge_rows(...)` behavior from `SpellCrafter`, and the
    helper now rebuilds those rows itself when a root blueprint is present.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/shared_compiler_executions.py:1-341
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1806-1899
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1497-1578
  IMPACT: The shared phase2_5 IR exporter is now much closer to a faithful
    full copy, not just a phase-2-only partial.
  NEXT: keep using this helper as the shared structural IR exporter when phase
    3 and phase 5 are ported.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:22:33Z
  TYPE: FACT
  CLAIM: Phases 3, 4, and 5 are no longer fake wrappers. Their phase modules
    now directly contain the moved behavior instead of delegating back into
    `SpellCrafter`. Phase 3 now owns the local-frame/DAG build helpers and
    writes the resolution frame into the artifact. Phase 4 now owns the direct
    validation flow and structural-state update logic with explicit validator
    and SpellSystemStates params. Phase 5 now owns the rooted-blueprint,
    system-index, local-scope, and change-control hook setup behavior, with
    phase-5 artifact writes routed through compiler-side helper methods instead
    of the old `SpellCrafter` setter surface.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:1-385
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-151
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:1-347
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-164
  IMPACT: The extracted compiler surface is now materially real through phase
    5, but it still needs parity review instead of optimistic completion
    claims. The next honest step is checking for any missing behavior before
    widening to later phases or wiring.
  NEXT: compare the new phase-3/4/5 modules against the original `SpellCrafter`
    bodies for any dropped side effects before moving on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:37:07Z
  TYPE: FACT
  CLAIM: The extracted compiler stack through phases 1-5 is now instance-
    dispatch in the compiler-owned layer. `CompilerPhaseUtility`,
    `SharedCompilerExecutions`, and compiler phases 1-5 now use normal instance
    methods instead of static methods, and `SpellCompiler` now owns reusable
    helper/phase instances and routes calls through `self` for phases 1-5.
    Later phases 6-12 remain on the older static wrapper shape for now because
    this tranche only covered the helper/shared surface plus phases 1-5.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/utility.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/shared_compiler_executions.py:1-341
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-49
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-115
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:1-393
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-151
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:1-343
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-281
  IMPACT: The compiler hot-path extraction no longer uses the repeated static
    dispatch shape for the helper/shared surface and phases 1-5. The next step
    is parity review of those moved bodies before widening further.
  NEXT: compare the moved phase-3/4/5 bodies against the original
    `SpellCrafter` methods for any remaining dropped side effects or helper
    gaps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:40:08Z
  TYPE: DECISION
  CLAIM: â€œWire up phases 1-5â€ is now being treated as compiler-owned wiring,
    not full runtime cutover. The immediate meaning is: `SpellCompilerSystem`
    should own one instantiated `SpellCompiler` and expose the phase-1..5
    delegation path using each spellâ€™s `SpellCompilerArtifact`, the owned
    validator, the spellbook, and SpellSystemStates. This tranche still does
    not repoint existing runtime callers away from `SpellCrafter`; it only
    makes the compiler-owned execution path real and complete through phase 5.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The current code change is tightly bounded to
    `spell_compiler_system.py` and does not mix in broader cutover work.
  NEXT: patch `SpellCompilerSystem` to own one `SpellCompiler` and add phase-1
    through phase-5 delegation methods over spell + artifact + collaborators.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:41:02Z
  TYPE: FACT
  CLAIM: The compiler-owned wiring path is now real through phase 5.
    `SpellCompilerSystem` now owns one instantiated `SpellCompiler` and one
    instantiated `SpellValidationSystem`, and it exposes phase-1 through
    phase-5 delegation methods that execute against each spellâ€™s
    `SpellCompilerArtifact` plus the explicit collaborators those phases now
    require (`Spellbook`, `SpellSystemStates`, validator, and conduit id where
    applicable). This still stops short of repointing live runtime callers away
    from `SpellCrafter`, but the compiler-owned execution path itself is now
    complete through phase 5.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-170
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-281
  IMPACT: The next work is no longer â€œmake the compiler path exist.â€ It is
    parity review and later cutover decisions on top of an actual compiler-
    owned path.
  NEXT: verify parity of the moved phases and then decide whether to continue
    with later phases or start repointing callers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:45:39Z
  TYPE: FACT
  CLAIM: The current `SpellCompiler` public surface now has method-level
    docstrings for the routing path it already exposes. The enriched docstrings
    now describe the in-place artifact mutation model, the explicit
    collaborator-routing story for phases 1-5, and the narrower â€œcurrent
    surface onlyâ€ contract for phases 6-12 and phase-12 helper entrypoints.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-431
  IMPACT: The compiler-owned facade is no longer under-documented at the
    method surface it currently exposes.
  NEXT: continue parity review of the moved phase bodies instead of spending
    more time on the facade doc surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:50:11Z
  TYPE: FACT
  CLAIM: Phase 2 had a real mechanical defect after the static-to-instance
    conversion: the method signature was still missing `self`, it was still
    calling the utility/helper surfaces like static methods, and it was still
    missing a few original explanatory comment lines from `SpellCrafter`
    (`Versioned identity from SpellIndex`, `Shapes like IGNORE...`, and
    `Map shape -> symbolic metadata`). That defect is now corrected in the
    phase-2 module itself.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-118
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3698-3787
  IMPACT: Phase 2 is now back on the intended instance-dispatch shape and much
    closer to a faithful body-level copy instead of a partially converted
    hybrid.
  NEXT: keep checking the moved phase bodies for the same kind of instance-
    conversion drift before widening further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:56:47Z
  TYPE: DECISION
  CLAIM: The compiler dispatch split is now fixed by contract: the two helper
    surfaces `utility.py` and `shared_compiler_executions.py` stay static, and
    phases `1-5` become real instance classes that call those static helpers
    directly. `SpellCompiler` should instantiate only the phase classes, not
    the helper classes.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next code pass is a dispatch-shape normalization only. It should
    remove the mixed helper-instance pattern and align phases `1-5` plus
    `SpellCompiler` to the new split.
  NEXT: inspect the current phase/compiler files and normalize them to the
    static-helper plus instance-phase model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:08:04Z
  TYPE: MEASURE
  CLAIM: The live mypyc benchmark overturns the earlier pure-Python-only
    assumption for helper dispatch. Under pure Python, repeated static helper
    dispatch is the slow bucket (`1.332x` vs own methods), but under mypyc
    compilation the static helper and module-function paths are actually the
    winners (`0.923x` and `0.922x` vs own methods), while caching helper
    callables on worker attrs becomes catastrophically worse (`21.212x` and
    `21.307x`). So the compiler-phase design should not optimize against static
    helpers if the deployed path is mypyc; the real thing to avoid there is
    caching helper callables on instance attributes.
  EVIDENCE:
  - tests/experimentation/mypyc/checking_speeds_static_vs_not.py:1-229
  - validation_result: `.\\.venv_new\\Scripts\\python.exe tests\\experimentation\\mypyc\\checking_speeds_static_vs_not.py`
  IMPACT: This materially changes the dispatch decision for the compiler-phase
    stack. Static helper surfaces are acceptable under mypyc, and the earlier
    â€œmake everything instance-dispatch because static is slowerâ€ direction is
    no longer supported by the stronger benchmark.
  NEXT: treat the mypyc benchmark as the controlling performance evidence when
    deciding whether compiler helpers/phases should remain static or instance
    based.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:12:00Z
  TYPE: DECISION
  CLAIM: The next extraction tranche is phases 6 and 7 only. The dispatch
    split is now fixed: shared helpers stay static, while the real phase
    surfaces remain normal classes. This tranche therefore ports the current
    phase-6 and phase-7 `SpellCrafter` bodies into `compiler_phase_6.py` and
    `compiler_phase_7.py`, then upgrades `SpellCompiler` and
    `SpellCompilerSystem` to route those phases through instantiated phase
    objects.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The work is tightly bounded again and does not mix in later-phase
    extraction or runtime cutover.
  NEXT: read the exact phase-6 and phase-7 source bodies and port only those.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:18:20Z
  TYPE: FACT
  CLAIM: The phase-6 and phase-7 source surfaces are now fully mapped. Phase 6
    is the heavier port: it includes both the main system-validation path and
    the local-system-validation path, plus the local visibility-gap diagnostic
    helpers and the repeated system-validation strategy set. Phase 7 is
    comparatively smaller and is mostly the `ensure_change_control_ready(...)`
    wiring split plus the local variant. That means phase 6 is the real weight
    inside this tranche, not phase 7.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5180-5600
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_6.py:1-40
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:1-40
  IMPACT: The port order inside the tranche should be phase 6 first, then
    phase 7, because phase 6 owns most of the missing real behavior.
  NEXT: replace phase-6 and phase-7 wrappers with direct ports and then wire
    `SpellCompiler` / `SpellCompilerSystem` to the new instance-based surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:21:09Z
  TYPE: FACT
  CLAIM: Phases 6 and 7 are now direct ports and the compiler-owned execution
    path is wired through them. `compiler_phase_6.py` now owns the main
    system-validation path, the local-system-validation path, the local
    visibility-gap diagnostic helpers, and the full strategy set instead of
    delegating back into `SpellCrafter`. `compiler_phase_7.py` now owns the
    frame-wide and local change-control wiring paths. `SpellCompiler` now owns
    instantiated phase-6 and phase-7 objects and `SpellCompilerSystem` now
    delegates phase 6/7 through the compiler-owned path. The one concrete
    syntax-risk found during the port (`IndexDependencySanityStrategy` split
    across lines) was fixed immediately.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_6.py:1-375
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:1-125
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-351
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-234
  IMPACT: The compiler-owned direct-port surface is now real through phase 7.
    The next work is parity review and later-phase extraction, not phase-6/7
    existence work.
  NEXT: verify body-level parity of phases 6-7 against `SpellCrafter` before
    widening to later phases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:26:21Z
  TYPE: FACT
  CLAIM: The phase-6/7 parity review found and corrected two real behavior
    drifts. First, phase 7 had stopped enforcing the original â€œPhase 5 root
    blueprint map is requiredâ€ failure shape and would have fallen through to a
    worse `NoneType` failure; it now restores the explicit required-blueprint
    check. Second, the phase-7 revalidator closures had drifted from the
    original live-crafter revalidation path to the broader spell facade; they
    now require and call the live crafter again like the original
    implementation. The one phase-6 syntax-risk found during the initial port
    (`IndexDependencySanityStrategy` split across lines) was already corrected.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:1-149
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5611-5705
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_6.py:1-375
  IMPACT: The specific parity gaps identified in the first review pass are now
    closed, so phases 6-7 are materially closer to a faithful direct port than
    they were one pass ago.
  NEXT: if we want more confidence before moving on, the next step is
    validation or a second narrower review pass over docstrings/comments only;
    otherwise we can continue to later phases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:33:43Z
  TYPE: FACT
  CLAIM: The first-pass parity review for phases `1-5` is complete. No new
    behavior drift was found in phases `1`, `2`, or `4` beyond the already
    fixed issues from earlier tranche work. The real behavior gaps found in the
    review were:
    - phase `3` had dropped `spell_id` and `dependency_key` from the local
      `SpellSocketDescriptor` build path
    - phase `5` had drifted its dirty-root revalidator closures from the
      original live-crafter path to the broader spell facade path
    Those gaps are now corrected in the current extracted phase files.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-69
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-170
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:1-417
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-151
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:1-523
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3640-4770
  IMPACT: The `1-5` extraction surface is materially cleaner now. The next
    work is no longer â€œreview 1-5 again,â€ it is either validation or later
    phase extraction.
  NEXT: move on to the next approved phase tranche or run validation if we want
    runtime proof before widening.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:32:41Z
  TYPE: DECISION
  CLAIM: The next implementation tranche is phase 8 only. The work remains
    phase-local and mechanical: replace the current phase-8 wrapper with a
    direct port of `SpellCrafter.run_phase_occurrence_plan(...)`, keep shared
    helpers static, keep the phase as a normal class, and stop once phase 8 is
    on the compiler-owned path.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The scope is tightly bounded again and does not mix in phase 9+ or
    broader runtime cutover.
  NEXT: read the exact phase-8 body and current wrapper, then port only phase
    8.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:36:30Z
  TYPE: FACT
  CLAIM: Phase 8 is not a single isolated method body. The outer
    `run_phase_occurrence_plan(...)` flow depends on a phase-8-specific helper
    cluster: fast-key generation, input-signature generation, the required
    phase-5 blueprint getter, and the phase8_11 dirty-bit mark path. Those are
    phase-local concerns, not generic shared-helper concerns, so they need to
    move with phase 8 instead of being pushed into `SharedCompilerExecutions`.
  EVIDENCE:
  - src/melder/aether\spellbook\spell_crafter\spell_crafter.py:4700-4960
  IMPACT: The phase-8 tranche has a slightly wider helper surface than the
    outer method alone, but it is still phase-local and remains bounded.
  NEXT: read the exact phase-8 helper bodies and port that phase-local cluster
    together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:36:44Z
  TYPE: FACT
  CLAIM: Phase 8 is now a direct port and is wired through the compiler-owned
    path. `compiler_phase_8.py` now owns the occurrence-plan outer body plus
    its phase-local helper cluster: required phase-5 blueprint access, the
    phase-8 fast-key builder, the phase-8 input-signature builder, the
    schema-value freezer used by that signature path, and the phase8_11 dirty
    mark path. `SpellCompiler` now owns an instantiated phase-8 object and
    `SpellCompilerSystem` now delegates the phase-8 call through the
    compiler-owned path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_8.py:1-211
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-366
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-249
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4700-4960
  IMPACT: Phase 8 is no longer just a wrapper and the compiler-owned path now
    reaches through the first later-plan phase instead of stopping at the
    structural/compiler-validation boundary.
  NEXT: stop at the phase-8 boundary and decide whether phase 9 is the next
    tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:39:00Z
  TYPE: DECISION
  CLAIM: The next implementation tranche is phase 9 only. The work remains
    phase-local and mechanical: replace the current phase-9 wrapper with a
    direct port of `SpellCrafter.run_phase_injection_plan(...)`, bring over its
    phase-local helper dependency if needed, wire `SpellCompiler` and
    `SpellCompilerSystem` through that phase, and stop there.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The scope is tight again and does not mix in phase 10+ or broader
    cutover work.
  NEXT: read the exact phase-9 body and current wrapper, then port only phase
    9.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:39:02Z
  TYPE: FACT
  CLAIM: Phase 9 is now a direct port and is wired through the compiler-owned
    path. `compiler_phase_9.py` now owns the phase-local helper cluster it
    actually needs: required phase-8 occurrence-plan access, phase-9 input
    signature reuse, and the phase8_11 dirty-bit mark path. `SpellCompiler`
    now owns an instantiated phase-9 object and `SpellCompilerSystem` now
    delegates the phase-9 call through that compiler-owned path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_9.py:1-98
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-374
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-264
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4767-4834
  IMPACT: The compiler-owned direct-port surface now reaches through the second
    later-plan phase instead of stopping at occurrence-plan compilation.
  NEXT: stop at the phase-9 boundary and decide whether phase 10 is the next
    tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:43:17Z
  TYPE: FACT
  CLAIM: The phase-9 parity/doc review did not find a concrete behavior drift
    in the moved phase body, but it did find that the extracted helper and
    method surface was too thin compared to the original `SpellCrafter`
    documentation/comments. The phase-9 file now carries the missing helper
    purpose text and the missing comment around deterministic input-signature
    reuse before the builder path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_9.py:1-107
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4767-4834
  IMPACT: Phase 9 is now in a better parity state both behaviorally and at the
    local documentation/comment surface.
  NEXT: move on to phase 10 when ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:45:30Z
  TYPE: DECISION
  CLAIM: The next implementation tranche is phase 10 only. The work stays
    phase-local and mechanical: replace the current phase-10 wrapper with a
    direct port of `SpellCrafter.run_phase_patch_maps(...)`, bring over the
    local phase-10 input-signature helper it depends on, wire `SpellCompiler`
    and `SpellCompilerSystem` through that phase, and stop there.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The scope is tight again and does not mix in phase 11+ or broader
    runtime cutover work.
  NEXT: read the exact phase-10 body and current wrapper, then port only phase
    10.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:48:28Z
  TYPE: FACT
  CLAIM: The remaining `@staticmethod` decorators were stripped out of the
    phase-stack files under `spell_compiler_system/phases/`. That means the
    helper surface plus phases 1-5 are no longer pretending to be instance
    dispatch while still carrying static-method decorators. The code now
    matches the current â€œreal classes, no explicit init required on the phase
    classes themselvesâ€ direction more honestly.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-48
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-114
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:1-392
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-150
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:1-342
  - src/melder/aether/conduit/spell_compiler_system/phases/utility.py:1-39
  - src/melder/aether/conduit/spell_compiler_system/phases/shared_compiler_executions.py:1-340
  IMPACT: The phase-stack dispatch shape is now internally consistent for the
    classes already converted away from static dispatch.
  NEXT: continue the parity review / later-phase conversion work from this
    corrected dispatch baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:29:43Z
  TYPE: FACT
  CLAIM: The supplied benchmark does not measure â€œall classes versus all static
    codeâ€ in the abstract. It measures specific call shapes. The slow path is
    the repeated `StaticHelper.a(...)` style dispatch, while module-level
    functions and instance-owned methods are much closer to the baseline. That
    means the follow-on design decision should be framed as â€œavoid repeated
    static helper dispatch in the hot path,â€ not as a vague â€œclasses are
    fasterâ€ claim.
  EVIDENCE:
  - tests/experimentation/static_versus_normal.py:1-229
  - user_benchmark_report: current chat benchmark table on 2026-05-20
  IMPACT: The benchmark still supports moving away from static phase/helper
    dispatch, but the reason needs to stay exact so we do not overgeneralize
    the result.
  NEXT: run the benchmark file unchanged and compare the live output to the
    pasted table before changing the compiler dispatch model further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:35:05Z
  TYPE: MEASURE
  CLAIM: The live benchmark run under `.venv_new` confirms the same high-level
    shape as the pasted table. The expensive path is repeated static helper
    dispatch (`delegates to static helper class` at `1.329x` vs baseline), while
    module-level calls (`0.991x`) and direct instance-owned methods (`1.000x`)
    sit near each other. Caching static functions on instance attrs narrows the
    gap (`1.004x`), but plain repeated `StaticHelper.a(...)` dispatch is the
    clearly slower path in this benchmark.
  EVIDENCE:
  - tests/experimentation/static_versus_normal.py:1-229
  - validation_result: `.\\.venv_new\\Scripts\\python.exe tests\\experimentation\\static_versus_normal.py`
  IMPACT: This supports moving the compiler-phase stack away from repeated
    static helper dispatch, but it still does not justify broad overclaims like
    â€œall classes are faster.â€ The precise conclusion is narrower: avoid the
    repeated static helper call shape in the hot path.
  NEXT: use this benchmark as the evidence anchor when converting the
    compiler-phase stack from static dispatch to real instance dispatch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:24:55Z
  TYPE: DECISION
  CLAIM: The benchmark the user supplied changes the extraction contract for
    the compiler stack itself: the phase classes, the compiler facade, and the
    shared helper surfaces should stop using static dispatch and become real
    instantiated classes instead. This tranche is therefore converting the
    extracted compiler stack away from static methods while preserving the
    already-ported phase logic and keeping runtime wiring out of scope.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The current implementation pass touches the compiler facade and all
    extracted phase/helper classes, but it is still mechanical. No algorithm or
    behavior changes are permitted in the conversion.
  NEXT: patch the compiler/helper/phase stack into real instance-based classes
    and stop once that conversion is complete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T15:00:09Z
  TYPE: DECISION
  CLAIM: The shared helper surface is being renamed and made explicit under the
    phases namespace. Instead of continuing with the vague `utility.py`
    direction, this tranche adds a slot-only `SharedCompilerExecutions` class
    under `spell_compiler_system/phases/` and repoints the already ported phase
    modules to use it for shared execution helpers.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: Shared phase behavior now has a named compiler-side home that can
    absorb later shared execution helpers like structural IR export.
  NEXT: add `SharedCompilerExecutions` and repoint phase 1 and phase 2 to it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:45:05Z
  TYPE: FACT
  CLAIM: Phase 10 is now a direct port and is wired through the compiler-owned
    path. `compiler_phase_10.py` now owns the phase-local helper cluster it
    actually needs: required phase-5 root blueprint access, the phase-10 patch
    map input-signature helper, and the phase8_11 dirty-bit mark path. It also
    owns the outer patch-map build path over `PatchMapBuilder`. `SpellCompiler`
    now owns an instantiated phase-10 object and `SpellCompilerSystem` now
    delegates the phase-10 call through that compiler-owned path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_10.py:1-104
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-379
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-279
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4843-4913
  IMPACT: The compiler-owned direct-port surface now reaches through patch-map
    compilation instead of stopping at the injection-plan boundary.
  NEXT: stop at the phase-10 boundary and decide whether phase 11 is the next
    tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:49:50Z
  TYPE: DECISION
  CLAIM: The next implementation tranche is phase 11 only. This phase is
    materially larger than phase 9 or 10 because the outer
    `run_phase_execution_plan(...)` path depends on a true phase-local helper
    cluster: no-overrides input-signature generation, spell/injection
    signature-row builders, execution-plan metric caching, variant building,
    and the immediate no-overrides executor compile handoff. The tranche stays
    phase-local anyway: port that cluster with phase 11, wire `SpellCompiler`
    and `SpellCompilerSystem` through it, and stop there.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: Phase 11 is still bounded, but it is not just one outer method body.
    I need the actual helper cluster that the outer build path depends on.
  NEXT: read the exact phase-11 helper cluster and port only phase 11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T17:02:36Z
  TYPE: FACT
  CLAIM: Phase 11 is now a direct port and it now stops at the approved
    `11 -> 12` artifact boundary instead of immediately compiling phase 12.
    `compiler_phase_11.py` now owns the execution-plan outer body plus its
    phase-local helper cluster: no-overrides input-signature generation,
    spell/injection signature-row builders, fast-transient schema/signature
    helpers, execution-plan metric caching, and execution-plan variant
    building. It also now writes the approved phase-11/12 artifact handoff
    fields:
    - `_phase11_no_overrides_plan_signature`
    - `_phase11_no_overrides_transient_schema`
    and invalidates the cached phase-12 executor when the compile-affecting
    signature changes. `SpellCompiler` and `SpellCompilerSystem` now route
    phase 11 through that compiler-owned path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:1-371
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-390
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-294
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:2338-3155
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4997-5250
  IMPACT: The compiler-owned direct-port surface now reaches through execution
    plan assembly and has the explicit artifact-side handoff needed for a later
    clean phase-12 port.
  NEXT: stop at the phase-11 boundary and decide whether phase 12 is the next
    tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T17:06:00Z
  TYPE: DECISION
  CLAIM: The next implementation tranche is phase 12 only. The boundary is now
    explicit from the prior phase-11 work: phase 11 already stores the compile
    handoff fields on the artifact, so phase 12 now needs to consume that
    artifact state and own executor compilation/caching directly. This tranche
    ports the current phase-12 helper surface, wires `SpellCompiler` and
    `SpellCompilerSystem` through it, and stops there.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The work is tightly bounded and does not widen into later validation
    or cutover work.
  NEXT: read the exact phase-12 helper bodies and current wrapper, then port
    only phase 12.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T17:06:35Z
  TYPE: FACT
  CLAIM: Phase 12 is now a direct port and is wired through the compiler-owned
    path. `compiler_phase_12.py` now owns the no-overrides executor compile
    surface directly instead of delegating back into `SpellCrafter`, and it now
    consumes the artifact-held phase-11/12 handoff state:
    - `_phase11_no_overrides_plan_signature`
    - `_phase11_no_overrides_transient_schema`
    as the compile-from-plan source of truth. `SpellCompiler` now owns an
    instantiated phase-12 object and `SpellCompilerSystem` now exposes the
    no-overrides compile calls through that compiler-owned path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:1-190
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:1-403
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-326
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3077-3189
  IMPACT: The compiler-owned direct-port surface now reaches through phase 12,
    and the `11 -> 12` boundary is explicit on the artifact instead of being
    hidden inside phase 11â€™s old immediate compile call.
  NEXT: the next work is parity review of phases 8-12 or a runtime cutover
    decision, not more existence work for the compiler path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T17:14:30Z
  TYPE: FACT
  CLAIM: The first concrete `11/12` wiring gap is in phase 12â€™s top-level
    `compile_no_overrides_executor(...)` path. After the approved phase-11
    split, phase 11 now stores the compile handoff state on the artifact, but
    phase 12â€™s top-level entry still starts from the old `codegen_ir` payload
    path instead of preferring the artifact-held no-overrides plan handoff.
    That means the new explicit `11 -> 12` boundary is not fully honored yet.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:1-371
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:1-190
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:3077-3189
  IMPACT: The new artifact-side phase-11 handoff exists, but the main phase-12
    entrypoint does not fully consume it yet.
  NEXT: patch phase 12 so `compile_no_overrides_executor(...)` prefers the
    artifact-held no-overrides plan handoff before falling back to payload
    compilation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T17:18:00Z
  TYPE: FACT
  CLAIM: The `11/12` parity review is now materially closed at the wiring
    boundary. Phase 12â€™s top-level compile path now prefers the artifact-held
    phase-11 no-overrides plan handoff before falling back to payload-based
    compilation, and the compiler/compiler-system entrypoints both route the
    artifact through to that phase-12 surface correctly. I did not find a
    second routing mismatch in the compiler-owned wrappers after that fix.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:1-190
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:320-352
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:318-356
  IMPACT: The explicit `11 -> 12` artifact boundary is now honored by both the
    phase code and the compiler-owned routing surfaces.
  NEXT: move to the next approved phase tranche or switch to validation if you
    want runtime proof before widening further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T17:14:42Z
  TYPE: DECISION
  CLAIM: The extracted compiler-phase surfaces now have an explicit documentation
    parity requirement: method docstrings and inline comments should match the
    original `SpellCrafter` source surface instead of being compressed
    summaries. This is a docs/comments correction tranche only; the goal is to
    raise the moved compiler-phase files to the same contract/explanation level
    as their source methods without changing behavior.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The next code pass is documentation-only over the extracted
    compiler-phase files. No behavior changes should be mixed into it.
  NEXT: patch the extracted phase files so their method docstrings and inline
    comments track the original `SpellCrafter` source more closely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:57:00Z
  TYPE: DECISION
  CLAIM: The user approved the artifact-side phase-11/12 handoff extension.
    This tranche adds the explicit phase-11 compile handoff fields to
    `SpellCompilerArtifact` so phase 11 can stop at plan assembly and phase 12
    can later consume artifact-held compile state cleanly. The approved fields
    are:
    - `_phase11_no_overrides_plan_signature`
    - `_phase11_no_overrides_transient_schema`
    and the patch also wires them into `__slots__`, `__init__`, cleanup, and
    the phase-5-and-later reset surface.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The artifact becomes a cleaner `11 -> 12` boundary without adding a
    second source of truth for normalized phase-11 payloads.
  NEXT: patch the artifact fields and their lifecycle/reset plumbing only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T16:49:30Z
  TYPE: DECISION
  CLAIM: The next implementation tranche is phase 11 only, and the docstring
    bar stays in scope for the moved surface. The work remains phase-local and
    mechanical: replace the current phase-11 wrapper with a direct port of
    `SpellCrafter.run_phase_execution_plan(...)`, bring over the phase-local
    helper cluster it actually depends on, wire `SpellCompiler` and
    `SpellCompilerSystem` through that phase, and keep the moved helper/method
    docstrings materially aligned to the source surface.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  IMPACT: The tranche stays tight and does not mix in phase 12 or broader
    runtime cutover, while still keeping documentation parity in scope for the
    moved code.
  NEXT: read the exact phase-11 body and helper cluster, then port only phase
    11 with its current contract/doc surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10- DATETIME: 2026-05-20T22:59:00Z
  TYPE: MEASURE
  CLAIM: The previously failing creation-context and meld-focused unit subset is green on the current post-seam codebase. The remaining live work is no longer inside those local builder/factory/stub seams; the next meaningful validation step is the full 	ests/unit ring.
  EVIDENCE:
  - validation: .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\meld\\creation_context\\test_creation_context_builder.py tests\\unit\\melder\\aether\\conduit\\meld\\meld_context\\test_meld_context.py tests\\unit\\melder\\aether\\conduit\\meld\\test_meld.py -> 118 passed, 1 warning
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-303
  - tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py:1-247
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1-2506
  IMPACT: We do not need more local patching in the creation-context or meld unit stubs before widening. The next failure surface should come from the broader unit ring instead of these already-fixed seams.
  NEXT: Run .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit and patch only the first current runtime/test-contract failures that remain after this green subset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10- DATETIME: 2026-05-20T23:11:00Z
  TYPE: MEASURE
  CLAIM: The current unit fallout has materially collapsed. 	ests/unit/melder/spellbook/test_spellbook.py now matches the compiler-system phase-factory seam and passes, and the dead monolithic 	ests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py surface is replaced with a smaller current-surface compiler suite that targets SpellCompiler, SpellCompilerArtifact, and SpellCompilerSystem directly. The old bound-SpellCrafter object model is no longer carried by that unit file.
  EVIDENCE:
  - validation: .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spellbook.py -> 152 passed, 1 warning
  - validation: .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_crafter\\test_spell_crafter.py tests\\unit\\melder\\spellbook\\test_spell_compiler_foundation.py -> 17 passed, 1 warning
  - tests/unit/melder/spellbook/test_spellbook.py:1-4987
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:1-313
  - tests/unit/melder/spellbook/test_spell_compiler_foundation.py:1-111
  IMPACT: The largest stale unit seam is gone, and the next meaningful signal should come from the remaining full unit ring rather than from these old compiler-surface tests.
  NEXT: Run .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit again and patch only the next current failures that remain after this compiler-test reduction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10- DATETIME: 2026-05-20T23:26:00Z
  TYPE: MEASURE
  CLAIM: The next six stale unit buckets are now aligned to current runtime surfaces. Transfer-of-ownership tests now provide spell stubs with compiler-artifact and creation-context cleanup surfaces, occurrence-plan tests use SpellCompilerSystem for Phase 8 instead of a dead bound SpellCrafter, binding-cycle strategy tests use spell.requirements, phase-invocation-count tests wrap SpellCompilerSystem, old Spell seam tests now assert the removed facades stay absent, and the fastpath file now uses artifact-based local-scope stubs and non-stale wrapper expectations.
  EVIDENCE:
  - validation: .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\conduit_ward\\transfer\\test_transfer_of_ownership.py tests\\unit\\melder\\aether\\conduit\\conduit_ward\\transfer\\test_transfer_of_ownership_contracts.py -> 134 passed, 1 warning
  - validation: .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\spell_crafter\\blueprints\\test_occurrence_plan.py tests\\unit\\melder\\spellbook\\spell_crafter\\validation\\strategies\\test_binding_resolution_cycle_strategy.py tests\\unit\\melder\\spellbook\\spellbook\\test_conjure_phase_invocation_counts.py tests\\unit\\melder\\spellbook\\test_spell.py tests\\unit\\melder\\spellbook\\test_spellbook_creation_system_resolution_fastpath.py -> 131 passed, 1 warning
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership.py:1-1574
  - tests/unit/melder/aether/conduit/conduit_ward/transfer/test_transfer_of_ownership_contracts.py:1-1517
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py:1-529
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_binding_resolution_cycle_strategy.py:1-544
  - tests/unit/melder/spellbook/spellbook/test_conjure_phase_invocation_counts.py:1-316
  - tests/unit/melder/spellbook/test_spell.py:1-1365
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1-1517
  IMPACT: The remaining full-unit signal should now be much smaller and should come from files that still have genuine stale assumptions outside these already-converted seams.
  NEXT: Run .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit again and patch only the remaining live failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T23:36:00Z
  TYPE: MEASURE
  CLAIM: The full repo test ring is green on the current post-seam runtime. Component, integration, and unit now pass together, which means the old Spell seam removal and compiler-surface test migrations hold across the combined suite rather than only in isolated rings.
  EVIDENCE:
  - validation: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests` -> `7959 passed, 2 skipped, 5 xfailed, 1 warning`
  IMPACT: The current compiler/runtime lane is no longer blocked by test fallout. The next work, if we continue, is new runtime/compiler decomposition work rather than more suite-repair churn.
  NEXT: Continue the compiler/runtime lane from a green full-suite base, or choose the next architectural cut explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T09:28:33Z
  TYPE: FACT
  CLAIM: The foundation slice is complete and no longer needs an active patch-artifact lane. The additive compiler surfaces are long-landed, the focused validation ring was green, and the later replacement suite now owns the behavioral coverage above this foundation.
  EVIDENCE:
  - validation_result: `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spell.py tests\unit\melder\spellbook\test_spell_compiler_foundation.py tests\unit\melder\aether\conduit\meld\test_meld.py` -> `170 passed, 1 warning`
  - validation_result: `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook` -> `2017 passed, 1 xfailed, 1 warning in 2.26s`
  IMPACT: The task no longer needs to stay routed on the board, and its temporary patch artifacts can be cleared under the ticket's `delete_on_close` contract.
  NEXT: close the task, remove its active artifact rows, and move it to `tickets/tasks/completed/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
## Context / Handoff Summary
Active investigation lane for static compiler-phase extraction.
The target path is
`src/melder/aether/conduit/spell_compiler_system/phases/`.
The current contract is mechanical only:
- extract the live `SpellCrafter` phase behavior into static `compiler_phase_<n>.py` modules
- keep `SpellCompilerArtifact` as the in-place state carrier
- pass runtime collaborators explicitly when a phase needs them
- do not rewrite behavior
- do not add validation
- do not add defensive programming
- do not add `artifact/spell is None` guards
- leave later wiring for a separate approved step

- DATETIME: 2026-05-20T23:59:00Z
  TYPE: FACT
  CLAIM: The extracted compiler-phase files are still uneven on documentation parity. Phase 1 and 2 are close to source shape, but later phases still compress or omit source-level docstring detail and inline comments. The next tranche should be docs/comments only against the original SpellCrafter sections rather than further behavioral edits.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-68
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-158
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:1-392
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:1-424
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:1-479
  IMPACT: The compiler extraction exists, but the public contract surface is still inconsistent with the source documentation bar the user set. Further work should target parity, not new behavior.
  NEXT: Read the matching SpellCrafter sections and patch only provable docstring/comment drift in the extracted phase files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T00:10:00Z
  TYPE: FACT
  CLAIM: The first docs-only parity correction tranche is landed on the extracted compiler phases. The concrete drift fixed here was: stale "Static compiler phase" class text on phases 1-5, a compressed phase-3 run contract, a compressed phase-5 run contract, and the malformed duplicated docstring sections in phase 9. This tranche stayed documentation-only and did not change compiler behavior.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-62
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-152
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:1-386
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-141
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:1-417
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_9.py:1-143
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4061-4328
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4721-5002
  IMPACT: The extracted compiler-phase surface is closer to the original SpellCrafter contract/comment bar, and the worst obvious documentation drift is removed without mixing in new behavior changes.
  NEXT: If we continue this lane, do another source-backed docs/comments pass over phases 6-12 and the remaining helper surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T00:20:00Z
  TYPE: FACT
  CLAIM: Runtime SpellCrafter usage is mixed. `Spell` is the public façade and owns the lazy `SpellCrafter` plus the public phase-entry methods, but runtime still contains direct `SpellCrafter` consumers outside `Spell`: `SpellCompilerSystem.create_spell_crafter_for_spell(...)`, compiler phase-5/7 dirty-root revalidators that pull `spell._crafter` and call `run_all_phases(...)`, `Meld` direct reads of crafter-backed execution caches, and ownership-transfer paths that clear `spell._crafter` directly.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:780-805
  - src/melder/aether/spellbook/spell.py:1151-1645
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:83-95
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:540-574
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:681-715
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:141-165
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:206-230
  - src/melder/aether/conduit/meld/meld.py:1311-1359
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:758-769
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1288-1294
  IMPACT: We cannot truthfully say "all SpellCrafter actions go through Spell." Public phase entry does, but runtime still has direct state and lifecycle coupling to the crafter.
  NEXT: Answer the user with the runtime split: public façade through Spell, plus the exact direct runtime consumers that still bypass the façade.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T00:28:00Z
  TYPE: FACT
  CLAIM: The next question is whether `SpellbookCreationSystem` uses `SpellCrafter` directly or only through `Spell` phase façades. This needs direct file evidence because the broader runtime picture already showed mixed usage outside `Spell`, but `SpellbookCreationSystem` itself had not been verified yet in this pass.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1-1
  IMPACT: We need to separate global runtime statements from component-specific truth so we do not overgeneralize the earlier answer.
  NEXT: Read `spellbook_creation_system.py` for direct `SpellCrafter` references and phase-call routing shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-21T00:40:00Z
  TYPE: DECISION
  CLAIM: The next additive slice is narrowed to `SpellCompilerSystem` only. The user removed the earlier front-facing methods there and removed spellbook from its initializer, so the work now is to copy the current `Spell` phase façade surface into `SpellCompilerSystem` like-for-like, but with explicit `spellbook` and `spell` call-time inputs instead of spellbook-affined instance state. No deletions or caller cutover are in scope in this slice.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: This keeps the change bounded to one file and one additive API surface while preserving current runtime behavior elsewhere.
  NEXT: Read the current `spell_compiler_system.py` surface, then patch in the copied phase façade methods with docstrings/comments preserved.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T00:52:00Z
  TYPE: FACT
  CLAIM: `SpellCompilerSystem` now has the additive front-facing phase façade copied from `Spell`, but reworked for the new stateless contract: each façade method now takes `spellbook` and `spell` explicitly, delegates into the existing compiler-owned phase pipeline, and preserves the richer docstring/comment contract instead of landing a skimmed surface. This slice also corrected the now-stale class/init/cleanup docs after spellbook was removed from the initializer. No methods were removed from `Spell` in this slice.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-509
  IMPACT: The compiler system now has a real additive public phase surface we can start wiring callers onto later, without forcing cutover or deleting the existing `Spell` façade first.
  NEXT: If we continue, the next step is caller cutover planning: identify which runtime callers should move from `Spell` façade to `SpellCompilerSystem` first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:00:00Z
  TYPE: PLAN
  CLAIM: The next slice is wiring only, and it is intentionally capped at two methods. The immediate target is the `SpellCompilerSystem` -> `SpellCompiler` -> extracted phase surface chain for phases 1 and 2 only. The goal is to verify that the front methods call the actual extracted phase objects correctly and match current `SpellCrafter` behavior names/signatures before widening to later phases.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:1-509
  IMPACT: This keeps the next cut reviewable and avoids rushing a broad front-door wiring pass across all phases.
  NEXT: Read `spell_compiler.py`, compare phase-1/2 delegation against the extracted phase modules, then patch only those two methods if they drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:08:00Z
  TYPE: FACT
  CLAIM: For phases 1 and 2, the first real wiring gap is not direct `_crafter` or `spell._spellbook` reach-through inside the phase logic. Those two phase bodies are already spell-local. The gap is that the explicit `spellbook` input currently stops at the `SpellCompilerSystem` façade instead of being threaded through the lower `SpellCompiler` and compiler-phase surfaces, which leaves the front-door contract inconsistent.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:97-151
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:106-158
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-62
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-152
  IMPACT: Even though phases 1 and 2 do not need spellbook today, the lower compiler surface should still accept the explicit call-time context so the front-door contract is uniform and later phases do not backslide into hidden reach-through.
  NEXT: Patch only phases 1 and 2 so `spellbook` is threaded from `SpellCompilerSystem` through `SpellCompiler` into the extracted phase surfaces, without widening the slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:14:00Z
  TYPE: FACT
  CLAIM: The phase-1/2 front wiring slice is now corrected. `SpellCompilerSystem` no longer stops the explicit `spellbook` input at its own façade for these two methods: phase 1 and phase 2 now thread `spellbook` from `SpellCompilerSystem` through `SpellCompiler` into `CompilerPhase1` and `CompilerPhase2`. The phase bodies still remain spell-local and do not read spellbook yet, but the front-door contract is now consistent and no hidden `spell._spellbook` / `_crafter` reach-through is involved in phases 1 and 2.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:97-151
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:106-158
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-74
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-166
  IMPACT: The first two front-facing compiler-system methods now carry the explicit context contract end-to-end, which is the prerequisite for later caller cutover and for removing spellbook affinity from Spell over time.
  NEXT: If we continue slowly, inspect phase 3 next because that is the first method that actually needs spellbook/system-state context in the lower layers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:20:00Z
  TYPE: FACT
  CLAIM: The next two-method wiring slice is complete. Phase 3 already had the correct explicit front-door shape and needed no code change: `SpellCompilerSystem -> SpellCompiler -> CompilerPhase3` already carried `spellbook` and `spell_system_states` end-to-end. Phase 4 was the lagging one, and it now matches the same explicit front-door contract: `spellbook` is threaded from `SpellCompilerSystem` through `SpellCompiler` into `CompilerPhase4` instead of stopping at the system façade.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:157-213
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:178-243
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:673-757
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-163
  IMPACT: Phases 1-4 now all carry the explicit front-door compiler-system context end-to-end. Phase 3/4 no longer have a front-door contract mismatch against the stateless compiler-system direction.
  NEXT: If we continue slowly, inspect phases 5 and 6 next because phase 5 is the first one with real runtime callback / root revalidation coupling and phase 6 depends on the phase-5 artifact boundary.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:26:00Z
  TYPE: FACT
  CLAIM: The prior phase-1/2 wiring pass overreached by forcing `spellbook` through phases that do not consume it. That created a false dependency and weakened the compiler-system contract. The correct rule is explicit real dependencies only: phases 1 and 2 stay spell-local, and `spellbook` begins at the first phase that actually needs it.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:97-151
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:106-158
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_1.py:1-74
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_2.py:1-166
  IMPACT: Leaving the fake dependency in place would make the front API noisier and less truthful. The correction is to remove `spellbook` from phase-1/2 signatures again and keep explicit context only from the first phase that actually needs it.
  NEXT: Patch only phases 1 and 2 front/compiler/phase signatures and docstrings to remove the false `spellbook` dependency.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:34:00Z
  TYPE: FACT
  CLAIM: Phase 3 and Phase 4 do not have the same dependency shape. Phase 3 genuinely needs `spellbook` and `spell_system_states` in the lower compiler surfaces because it resolves candidates against live spellbook state. Phase 4 does not: its lower compiler surface only consumes `spell`, `artifact`, `spell_validator`, and `spell_system_states`. Keeping `spellbook` threaded below the front façade in phase 4 would be another false dependency.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_3.py:673-757
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-163
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:178-243
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:157-213
  IMPACT: Phase 3 can stay as-is, but phase 4 needs the same correction we already made for phases 1 and 2: keep spellbook at the front façade only and remove it from the lower compiler surface.
  NEXT: Patch only phase 4 lower signatures/calls, then verify phases 5 and 6 still reflect real dependencies only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:38:00Z
  TYPE: FACT
  CLAIM: Phase 4 now matches the same contract rule as phases 1 and 2: `spellbook` remains at the `SpellCompilerSystem` front façade but is no longer threaded into the lower `SpellCompiler` and `CompilerPhase4` surfaces because the phase body does not consume it. By contrast, phases 5 and 6 already have real lower-surface spellbook use, so they do not need the same correction. Phase 5 uses spellbook for visibility, ownership, frame-name lookup, change-control rebuild/upsert, and dirty-root callback resolution; phase 6 uses spellbook for spell lookup and scoped validation propagation.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:189-213
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:224-243
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_4.py:1-157
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:266-418
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_6.py:258-389
  IMPACT: Phases 1, 2, and 4 are now stripped back to real lower-surface dependencies only, while phases 3, 5, and 6 still truthfully carry spellbook/state because their bodies actually use them.
  NEXT: If we continue, the next real review target is phases 7-12 for the same dependency-truth check before any caller cutover.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:48:00Z
  TYPE: FACT
  CLAIM: The real body-level spellbook/signature correction in phases 1-6 was phase 5, not phase 6. Phase 5â€™s dirty-root revalidation callbacks no longer jump back through `SpellCrafter.run_all_phases(...)`; they now instantiate a local `SpellCompilerSystem` and re-run compilation through the compiler-system front façade with explicit `spellbook` + `spell` + `conduit_id`. Phase 6 already used the explicit spellbook/system-state signature honestly and needed no body change.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:537-576
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:684-724
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_6.py:258-389
  IMPACT: In the 1-6 range, the last remaining runtime path that still re-entered through the spell-owned crafter on a spellbook-sensitive callback has been moved to the compiler-system front API. That makes the phase-5 revalidation bridge consistent with the explicit spellbook/spell call contract.
  NEXT: If we continue, the next equivalent cleanup target is phase 7, because it has the same dirty-root / change-control callback shape phase 5 had before this fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T01:54:00Z
  TYPE: FACT
  CLAIM: Phase 7 now matches phase 5 at the body level. The change-control dirty-root revalidation callbacks no longer pull `spell._crafter` and jump back through `SpellCrafter.run_all_phases(...)`; both the frame-wide and local phase-7 callbacks now instantiate a local `SpellCompilerSystem` and re-enter through the compiler-system front façade with explicit `spellbook`, `spell`, and `conduit_id` inputs.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:90-191
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:192-266
  IMPACT: The same compiler-system front-door rule now holds for the change-control revalidation bridge. In the 1-7 range, the remaining obvious spellbook/crafter callback leak has been removed from phase 7 as well.
  NEXT: If we continue, inspect phases 8-12 for any remaining hidden spellbook or spell-owned-crafter reach-through in the lower bodies before caller cutover.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:02:00Z
  TYPE: PLAN
  CLAIM: The next review target is phase 8, but its dependency shape may already be honest: the extracted phase-8 body previously showed explicit `spellbook` and `spell_system_states` inputs rather than hidden `spell._spellbook` or `_crafter` reach-through. This slice should verify that exact point and only patch code if a real lower-body leak still exists.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_8.py:1-339
  IMPACT: This prevents another fake change. If phase 8 is already clean, we should say so and move to the next actual problem instead of churning signatures or comments.
  NEXT: Verify phase-8 lower-body dependency use against the extracted code already read, then patch only if a hidden reach-through exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:08:00Z
  TYPE: FACT
  CLAIM: Phase 9 does not need a lower-body dependency cleanup. Its extracted body is already honest: it consumes only `spell`, `artifact`, and `cancel_event`, and it does not reach through `spell._spellbook`, `spell._crafter`, or `SpellCrafter.run_all_phases(...)`. The front/compiler/lower split is already truthful for this phase.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_9.py:1-143
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:587-620
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:466-494
  IMPACT: There is no real body-level work to do on phase 9. Changing it anyway would just create churn and risk. The next worthwhile dependency-truth check should move on to the next phase that still has a hidden lower-body reach-through.
  NEXT: Inspect phase 10 next, then phase 11, and keep skipping phases that are already dependency-honest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:14:00Z
  TYPE: FACT
  CLAIM: Phase 10 does not need a lower-body dependency cleanup. Its extracted body already consumes only `spell`, `artifact`, and `cancel_event`, and it does not reach through `spell._spellbook`, `spell._crafter`, or `SpellCrafter.run_all_phases(...)`. The phase-10 front/compiler/lower split is already truthful.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_10.py:1-145
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:622-655
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:496-524
  IMPACT: There is no real body-level work to do on phase 10. Touching it anyway would be churn, not progress. The next worthwhile dependency-truth check should move to phase 11 or 12.
  NEXT: Inspect phase 11 next, then phase 12, and keep skipping phases that are already dependency-honest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:22:00Z
  TYPE: FACT
  CLAIM: Phase 11 does not need a lower-body dependency cleanup. It already uses the explicit `spellbook` input honestly for plan compilation and handoff storage. Phase 12 does need one real body-level correction: the payload compile path still reaches through `spell._spellbook._spell_id_pool` instead of consuming explicit spellbook context. The next slice is phase-12-only and should thread `spellbook` down only where that payload compile path actually needs it.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:1-479
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:1-190
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:657-747
  IMPACT: Phase 11 is already dependency-honest, but phase 12 still has one hidden lower-body spellbook reach-through. Fixing that closes the next real leak without inventing changes elsewhere.
  NEXT: Patch only phase 12 so the payload compile path takes explicit spellbook input instead of reading `spell._spellbook`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:30:00Z
  TYPE: FACT
  CLAIM: `SpellCompilerSystem` currently has no phase-12 front-facing methods. In this lane, phase-12 dependency cleanup therefore applies to the lower compiler surfaces only (`SpellCompiler` and `CompilerPhase12`). Before stopping, we need to verify whether any live callers exist for those compile helpers, because the explicit spellbook signature change must not strand a current call path.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:741-829
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:1-190
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:657-747
  IMPACT: If there are no live callers, the lower-surface phase-12 fix is self-contained. If there are callers, they need the same explicit spellbook correction in the same slice.
  NEXT: Search the repo for live phase-12 compile-helper call sites and patch only those if they exist.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:36:00Z
  TYPE: FACT
  CLAIM: Phase 12 is now corrected at the lower-surface dependency boundary, and the change is self-contained. `CompilerPhase12` no longer reaches through `spell._spellbook._spell_id_pool` in the payload compile path; it now takes explicit `spellbook` input for the top-level compile path and the payload compile helper. `SpellCompiler` was updated to thread that explicit spellbook input down. There are currently no live repo callers into those `SpellCompiler` phase-12 compile helpers, and `SpellCompilerSystem` still does not expose phase-12 front methods, so no additional caller patch was required in this slice.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:1-236
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:697-804
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:741-829
  - repo_search: `rg -n "compile_phase12_no_overrides_executor|compile_no_overrides_executor_from_payload|compile_no_overrides_executor_from_plan" src tests`
  IMPACT: Phase 11 remains dependency-honest with no code change needed, and the next real lower-body spellbook reach-through in the extracted compiler path is no longer phase 12. The remaining work is now about front-method exposure/caller cutover or later-phase/runtime cleanup, not this payload-compile leak.
  NEXT: If we continue, decide whether to expose phase-12 front methods on `SpellCompilerSystem` or move to caller cutover planning for the already-exposed phase fronts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:48:00Z
  TYPE: DECISION
  CLAIM: The front-facing compiler-system path should preserve pre-split semantics for execution readiness without collapsing phase 11 and 12 back together internally. The implementation choice is to extend `run_phase_execution_plan(...)` so it runs phase 11 and then phase 12 executor compilation through the explicit artifact handoff. `run_all_phases(...)` inherits that behavior automatically by continuing to end at `run_phase_execution_plan(...)`.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:657-804
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:741-829
  IMPACT: Callers keep one coherent execution-ready front method while the internal phase-11/12 split remains explicit and reusable.
  NEXT: Patch only the compiler and compiler-system execution front methods plus their docstrings/comments to reflect the new front-door behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:54:00Z
  TYPE: FACT
  CLAIM: The front-facing execution path is now extended to support the phase-11/12 split correctly. `SpellCompiler.run_phase_execution_plan(...)` still runs only the phase-11 builder surface directly, but it now immediately calls the phase-12 no-overrides executor compile helper through the explicit artifact handoff. `SpellCompilerSystem.run_phase_execution_plan(...)` inherits that behavior, and `run_all_phases(...)` documentation is now updated to include phase 12 in the front-door execution contract without collapsing the internal split back together.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:657-691
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:526-561
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:741-789
  IMPACT: Front callers now get execution-ready behavior again from the compiler-system execution-plan path, while the internal phase-11/12 separation remains explicit and reusable.
  NEXT: If we continue, the next question is caller cutover: which runtime fronts should switch from `Spell` / `SpellCrafter` paths to `SpellCompilerSystem` first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:44:00Z
  TYPE: FACT
  CLAIM: The first phase-surface inventory command was incomplete because the Windows wildcard path was wrong, so the initial comparison would have undercounted extracted methods. The phase inventory must be rerun against the whole `phases/` directory before we can truthfully state the missing SpellCrafter surface.
  EVIDENCE:
  - validation_result: `rg -n "^\\s+def\\s+" src/melder/aether/conduit/spell_compiler_system/phases/*.py ...` failed with os error 123
  IMPACT: Any gap report before the corrected inventory would be unsafe. We need the real extracted method list first.
  NEXT: Re-run the method inventory against the whole `phases/` directory and compare that list to `spell_crafter.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T02:52:00Z
  TYPE: FACT
  CLAIM: A raw method-surface comparison shows that `SpellCrafter` still has a significant surface not represented in `phases/`, `utility.py`, and `shared_compiler_executions.py`, but the gap splits into three categories rather than one: (1) expected non-phase surface such as lifecycle cleanup, property accessors, and front façade runners; (2) helper methods that were already migrated under different names or into `SpellCompilerArtifact`; and (3) real extracted-surface gaps that still do not exist in the compiler-phase/helper stack at all. The real missing extracted helpers include the phase8_11 IR row builders/capture helpers and `_try_build_execution_plan_variant_from_base(...)`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py method inventory via `rg -n "^\\s+def\\s+"`
  - src/melder/aether/conduit/spell_compiler_system/phases method inventory via `rg -n "^\\s+def\\s+" src/melder/aether/conduit/spell_compiler_system/phases`
  IMPACT: We should not treat every missing method as a bug. The next sensible step is to separate intentional owner moves (artifact/front façade) from actual unported compiler helper gaps before we do more code movement.
  NEXT: Report the method-gap categories explicitly to the user, with the real missing helper list called out separately from intentional non-phase methods.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:02:00Z
  TYPE: FACT
  CLAIM: The missing helper cluster breaks down cleanly by dependency graph. The occurrence/injection/patch/phase11 row builders are all only depended on by `_capture_phase8_11_codegen_ir`, and `_capture_phase8_11_codegen_ir_if_dirty` is only depended on by the `codegen_ir` property. That makes the whole `phase8_11` export chain a coherent shared cross-phase capability rather than a random bag of helpers. `_reset_phase2_5_codegen_ir` is separate and only depends on artifact/IR state, while `_try_build_execution_plan_variant_from_base(...)` is phase-11-specific and is not used by the current runtime path at all.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:948-965
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:1930-3059
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:243-248
  - repo_search: `rg -n "_capture_phase8_11_codegen_ir_if_dirty|_capture_phase8_11_codegen_ir|_reset_phase2_5_codegen_ir|_build_occurrence_graph_rows|_build_occurrence_instance_key_rows|_build_occurrence_canonical_rows|_build_occurrence_contract_override_rows|_build_occurrence_contract_override_spell_rows|_build_injection_instance_rows|_build_override_target_rows|_build_mutation_target_rows|_build_phase11_step_ir_row|_build_phase11_variant_ir_payload|_try_build_execution_plan_variant_from_base" src tests`
  IMPACT: We now know what actually needs a new home before deleting `SpellCrafter`: the shared `phase8_11` export chain, the `phase2_5` reset helper, and possibly the unused phase-11 variant-derivation helper if we want parity completeness.
  NEXT: Report the exact dependency ownership map to the user so we can decide whether to port the shared export chain next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:14:00Z
  TYPE: FACT
  CLAIM: The missing shared `phase8_11` export chain is now present on `SharedCompilerExecutions`, and the live system consumer is rerouted onto it. `CreationContextBuilder` no longer reads `spell._crafter` for no-overrides executor, override patch map, root blueprint, or `codegen_ir`; it now reads those from `spell._compiler_artifact`, and it flushes pending `phase8_11` IR through `SharedCompilerExecutions.capture_phase8_11_codegen_ir_if_dirty(...)` before consuming payloads. The artifact reset path also now clears stale `phase2_5` export through the new shared reset helper.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/shared_compiler_executions.py:1-1338
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-271
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:259-281
  IMPACT: The concrete helper gap that blocked a clean future `SpellCrafter` removal is materially reduced: the shared export surface now exists, and the live builder no longer depends on `crafter.codegen_ir` or other crafter-backed compiler artifacts for these paths.
  NEXT: If we continue, the next useful check is whether any remaining runtime code still reads compiler artifacts from `SpellCrafter` instead of `SpellCompilerArtifact`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:22:00Z
  TYPE: DECISION
  CLAIM: The prior builder reroute overcommitted to artifact-only reads in the middle of an active fork. The correct fork-safe behavior is preference, not replacement: `CreationContextBuilder` should prefer compiler-artifact state when present, but fall back to `SpellCrafter` state when the artifact side has not been populated yet. This keeps the new path live without breaking the old path mid-fork.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-271
  IMPACT: The runtime can keep moving forward on compiler-artifact migration without requiring an all-at-once cutover of every producer in the same fork.
  NEXT: Patch only `CreationContextBuilder` so artifact-backed reads are preferred and `SpellCrafter` reads remain as fallback when artifact data is absent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:30:00Z
  TYPE: PLAN
  CLAIM: The next slice is a pure usage audit and cleanup for the newly added shared helper surface. The question is not whether the helper methods exist anymore, but whether the 12 phase files are actually calling them instead of keeping duplicated local implementations. This slice should patch only the phases still bypassing the shared surface.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: This prevents us from leaving dead shared helpers in place while the phases continue to use stale private copies.
  NEXT: Search phase call sites for the new shared-helper methods, then patch only the phases that still duplicate or bypass them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:26:00Z
  TYPE: FACT
  CLAIM: The shared helper surface is now actually used by the extracted phases rather than just existing on disk. Phase 8 now routes schema freezing through `SharedCompilerExecutions.freeze_phase11_schema_value(...)`. Phase 11 now routes transient schema/signature construction plus phase-11/12 step/signature helper work through the shared static helper surface. Phase 12 now flushes pending shared `phase8_11` IR before reading payload fallback. The remaining duplicated dirty-bit setters in phases 8/9/10/11 are not part of the newly added shared cluster and were left alone.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_8.py:83-83
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:61-61
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:107-133
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:158-210
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:386-389
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:558-558
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_12.py:78-80
  IMPACT: The newly added shared `phase8_11` helper cluster is no longer decorative. The extracted compiler phases now consume it in the real runtime paths that need it.
  NEXT: If we continue, the next sensible audit is for any remaining runtime reads of compiler state off `SpellCrafter` that should now prefer compiler artifact/shared helper state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:36:00Z
  TYPE: FACT
  CLAIM: Post-scan, the new shared helper cluster is live where it needed to be, but three follow-up items remain. (1) `CreationContextBuilder` still has intentional fallback reads through `spell._crafter` when artifact-backed compiler state is absent in the fork. (2) `Meld` still reads `spell._crafter.root_blueprint_phase5` directly for root-vs-spell validity decisions. (3) `CompilerPhase5._get_required_crafter_from_spell(...)` still exists in the file as a dead leftover even though the phase-5 revalidation callbacks were moved to `SpellCompilerSystem`.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:71-71
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:172-175
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:196-199
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:216-219
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:265-269
  - src/melder/aether/conduit/meld/meld.py:1311-1352
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:56-74
  IMPACT: The shared helper migration is materially in place, but `SpellCrafter` is not yet fully removable. The remaining work is not the shared helper cluster anymore; it is the residual runtime reach-throughs and dead leftovers.
  NEXT: If we continue, decide whether to remove the dead phase-5 helper first or audit/reroute the remaining `Meld` crafter reads next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:44:00Z
  TYPE: DECISION
  CLAIM: The next additive surface on `SpellCompilerSystem` is the semantic spell-scoped artifact management API. The reasonable front-facing methods are the old `SpellCrafter` lifecycle operations that express caller intent rather than internal implementation detail: `reset_phase_artifacts(spell)`, `cleanup_phase_artifacts(spell)`, and `clear_phase5_artifacts(spell)`. Internal helpers like `_cleanup_phase_artifacts_locked`, `_cleanup_execution_plans_phase11`, and raw IR reset helpers stay internal.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_artifact.py:259-389
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:421-505
  IMPACT: The compiler system gets a real spell-management surface without exposing artifact internals or pretending it owns final spell teardown.
  NEXT: Patch only `spell_compiler_system.py` to add the three semantic artifact-management methods with full docstrings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:44:00Z
  TYPE: FACT
  CLAIM: The unused-parameter scan is a mixed bag. There are three categories: (1) intentionally uniform front-façade params on `SpellCompilerSystem` that are accepted for API shape even when the lower phase does not need them yet; (2) real dead params in lower phase bodies where the implementation never consumed the copied argument; and (3) cancellation placeholders where the method signature was copied through but the body never calls the cancellation helper. These should not be treated as one single cleanup action.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:93-169
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:349-530
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_6.py:308-371
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:52-274
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_8.py:399-466
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_9.py:102-175
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_10.py:104-182
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_11.py:796-805
  IMPACT: We should decide these by contract, not by lint purity. Some should stay for front-surface uniformity, some should be removed, and some should start honoring cancellation instead of pretending to.
  NEXT: Explain the list to the user by category and call out which ones are acceptable now versus which ones are actual code drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T03:58:00Z
  TYPE: DECISION
  CLAIM: The next slice is strict dead-parameter removal. The user explicitly rejected keeping unused parameters for API shape alone, so this pass will remove every verified unused parameter from the compiler-system front methods and lower phase bodies, then update direct callers/docstrings in the same slice. No behavior additions and no validation run are in scope.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - prior unused-param audit note in this task
  IMPACT: The compiler front/phase surfaces stop carrying fake parameters that do no work and only add call/maintenance overhead.
  NEXT: Patch the verified unused-param list and the corresponding same-slice callers/docstrings only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T04:08:00Z
  TYPE: FACT
  CLAIM: The next question is whether the old `SpellCrafter` actually used `cancel_event` in the phases where we removed it from the new compiler path. This needs direct body evidence from `spell_crafter.py` before we decide whether those removals preserved behavior or accidentally dropped real cancellation semantics.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5560-5820
  IMPACT: If old `SpellCrafter` used `cancel_event` in those phase bodies, removing it in the new path would be a behavior regression rather than dead-param cleanup.
  NEXT: Read the old phase 7-11 bodies and answer phase-by-phase whether `cancel_event` was actually consumed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T04:18:00Z
  TYPE: FACT
  CLAIM: Strict parity is still off for the local Phase 5 path. In old `SpellCrafter`, `run_phase_root_blueprints_local(...)` stops at local snapshot/index/blueprint attachment plus cache refresh. It does not perform local change-control upsert or revalidator registration in that method. In the split system, `CompilerPhase5.run_local(...)` still performs `change_control_manager.upsert_component_of(...)` and local revalidator registration, while `CompilerPhase7.run_local(...)` also owns local change-control wiring. So the split currently has extra local Phase-5 side effects relative to old SpellCrafter.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4522-4592
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:587-724
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_7.py:197-274
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:308-341
  IMPACT: Local Phase 5 and local Phase 7 are not cleanly separated yet in the split path. If you want strict old-surface parity, the local change-control upsert/revalidator block should live only in phase 7 local, not in phase 5 local.
  NEXT: Tell the user plainly that the split still has this mismatch and that `SpellCompilerSystem.run_phase_root_blueprints_local(...)` currently inherits the extra phase-5 local side effects because it delegates straight to `CompilerPhase5.run_local(...)`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T04:20:00Z
  TYPE: PLAN
  CLAIM: The next slice is an explicit method-usage inventory script, because the user wants direct evidence of who uses SpellCrafter methods and who uses Spell's crafter façade methods. The deliverable is a PowerShell script plus a generated report over `src` and `tests`, not a code refactor.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: This turns the question into a repeatable inventory instead of another ad hoc grep summary.
  NEXT: Create the PowerShell usage-report script under `workspace/agent/scripts`, run it once, and summarize the report.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T04:36:00Z
  TYPE: DECISION
  CLAIM: For phase 5, the default path is frame-wide and the local path is the less-common meld revalidation lane. The phase surface should say that explicitly. This slice renames the frame-wide method to `run_frame_wide(...)`, keeps `run_local(...)`, and repoints the compiler front to the explicit frame-wide name without widening into phases 6-7 yet.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4222-4521
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4522-4592
  IMPACT: Phase 5 stops hiding the primary scope behind a generic `run(...)` name and the split aligns better to conjure vs meld usage.
  NEXT: Patch compiler_phase_5 plus the compiler/compiler-system call sites for the new `run_frame_wide(...)` name only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T04:30:00Z
  TYPE: DECISION
  CLAIM: Phase 5 naming is being made explicit now: the default path is frame-wide and the local path is the less-common meld revalidation lane. This slice renames the default phase-5 method from `run(...)` to `run_frame_wide(...)`, keeps `run_local(...)`, and repoints the compiler and compiler-system call sites to the explicit frame-wide name only.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4222-4521
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:4522-4592
  IMPACT: The primary foundational phase-5 path stops hiding behind a generic `run(...)` name, which reduces the chance of local/frame-wide confusion in later work.
  NEXT: Patch compiler_phase_5 plus compiler/compiler-system call sites for the new `run_frame_wide(...)` name only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T04:54:00Z
  TYPE: FACT
  CLAIM: The phase-5 split is now aligned to the old SpellCrafter contract shape: the frame-wide path is explicitly named `run_frame_wide(...)`, the local path remains `run_local(...)`, and the extra local change-control side effects were removed from phase-5 local so that local phase-5 now stops at local compute + artifact/cache refresh just like old `run_phase_root_blueprints_local(...)`.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:450-589
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:591-679
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:289-382
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:260-341
  IMPACT: Phase 5 now has the same two-path shape as old SpellCrafter: default frame-wide foundational compile and separate local meld revalidation compile, without mixing local phase-7 behavior back into local phase-5.
  NEXT: This slice is complete. The next meaningful work is to apply the same explicit frame-wide/local naming cleanup to phases 6 and 7 if you want the split to be equally unambiguous there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T05:08:00Z
  TYPE: DECISION
  CLAIM: Phase 6 is getting the same naming split as phase 5. The default path is frame-wide and the local path is the less-common meld revalidation lane, so the phase surface should say that explicitly. This slice renames the default phase-6 method to `run_frame_wide(...)`, keeps `run_local(...)`, and repoints compiler/compiler-system call sites to the explicit frame-wide name only.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5237-5314
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5315-5569
  IMPACT: Phase 6 stops hiding the primary scope behind a generic `run(...)` name, and the split aligns better to conjure/systemwide versus meld/local usage.
  NEXT: Patch compiler_phase_6 plus the compiler/compiler-system call sites for the new `run_frame_wide(...)` name only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T05:20:00Z
  TYPE: PLAN
  CLAIM: The current slice is strict parity review for phase 6 only. The work is old frame-wide phase-6 body versus split frame-wide phase-6 body, and old local phase-6 body versus split local phase-6 body. Any patch from this point should only remove or move concrete drift in phase 6.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: This keeps the next change bounded to the exact old/new phase-6 parity question instead of widening into architecture or caller cutover again.
  NEXT: Compare the two old/new phase-6 blocks directly and patch only if the split still has behavior drift.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T05:34:00Z
  TYPE: DECISION
  CLAIM: The last naming cleanup in this lane is phase 7. Just like phase 5 and phase 6, the default path is frame-wide and the local path is the less-common meld revalidation lane, so the phase surface should say that explicitly. This slice renames the default phase-7 method to `run_frame_wide(...)`, keeps `run_local(...)`, and repoints only the compiler/compiler-system frame-wide call chain.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5570-5585
  - src/melder/aether/spellbook/spell_crafter/spell_crafter.py:5586-5705
  IMPACT: Phase 7 becomes consistent with the explicit frame-wide/local naming scheme already applied to phases 5 and 6.
  NEXT: Patch compiler_phase_7 plus the compiler/compiler-system frame-wide call sites for the new `run_frame_wide(...)` name only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T06:02:00Z
  TYPE: FACT
  CLAIM: `SpellbookCreationSystem` is now wired to `SpellCompilerSystem` for its phase-running paths instead of calling the `Spell` / `SpellCrafter` phase façade directly. The per-spell structural factories, frame-wide conduit foundational/plan runners, target-local foundational/plan runners, and post-conjure structural rerun path now execute compiler-system methods with explicit `spellbook` / `spell` / `conduit_id` arguments. A final search over `spellbook_creation_system.py` found no remaining `spell.run_phase_*`, `target_spell.run_phase_*`, or `spell.run_structural_phases(...)` callsites in that file.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:739-842
  - src/melder/aether/spellbook/spellbook_creation_system.py:892-910
  - src/melder/aether/spellbook/spellbook_creation_system.py:1075-1166
  - src/melder/aether/spellbook/spellbook_creation_system.py:1259-1300
  - src/melder/aether/spellbook/spellbook_creation_system.py:1490-1647
  - repo_search: `rg -n "spell\.run_phase_|target_spell\.run_phase_|lead_spell\.run_phase_|spell\.run_structural_phases|run_all_phases\(" src/melder/aether/spellbook/spellbook_creation_system.py`
  IMPACT: The conjure-side and target-local resolution orchestration in `SpellbookCreationSystem` now runs through the compiler-system front API instead of the old `Spell` façade, which is the first real caller cutover in runtime code.
  NEXT: If we continue, the next meaningful runtime cutover target is `Meld`, because it still contains direct `SpellCrafter` reads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T06:20:00Z
  TYPE: DECISION
  CLAIM: The next runtime cutover slice is `Meld` only. `Meld` already owns a `SpellCompilerSystem`, so the immediate work is to replace the two direct `spell._crafter` reads used for root-vs-spell validity decisions with compiler-artifact/compiler-system-backed state. No broader revalidation redesign is in scope in this pass.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:146-147
  - src/melder/aether/conduit/meld/meld.py:1311-1352
  IMPACT: This removes the first remaining direct `SpellCrafter` runtime read from `Meld` without widening into unrelated meld paths.
  NEXT: Patch only the two root-blueprint reads in `Meld` to stop depending on `spell._crafter`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T06:34:00Z
  TYPE: FACT
  CLAIM: `Meld` is now using `SpellCompilerSystem` for the two root-vs-spell validity decisions that previously read `spell._crafter.root_blueprint_phase5` directly. A new semantic helper `SpellCompilerSystem.is_current_spell_phase5_root(spell)` was added, and `Meld` now calls that helper in both `_mark_resolution_unvalidated(...)` and `_get_resolution_validity(...)`.
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:724-757
  - src/melder/aether/conduit/meld/meld.py:1303-1323
  - src/melder/aether/conduit/meld/meld.py:1340-1350
  IMPACT: The first remaining direct `SpellCrafter` runtime read inside `Meld` is gone. Root-vs-spell validity routing now goes through the compiler-system surface owned by `Meld` instead of the spell-owned crafter.
  NEXT: If we continue, the next meaningful runtime cut is to finish `SpellbookCreationSystem` compiler-system cutover end-to-end or audit the remaining explicit `spell._crafter` fallback reads in `CreationContextBuilder`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T06:44:00Z
  TYPE: PLAN
  CLAIM: The next runtime surface to check is the CreationContext builder/factory pair. We already cut `Meld` off two direct crafter reads, so the question now is whether the remaining compiler-state reach-through is isolated to `CreationContextBuilder` fallback reads or whether `CreationContextFactory` also still depends on old `SpellCrafter` ownership. This needs direct file evidence before any more cutover work.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: This decides whether the next cut is builder-only or builder+factory.
  NEXT: Read `creation_context_factory.py` and compare its dependency shape to the already-known builder fallback reads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T06:58:00Z
  TYPE: DECISION
  CLAIM: The next runtime migration slice is `CreationContextBuilder` only, and this time it is not a fork-safe preference path. The user explicitly wants that builder migrated to the new compiler system, so the remaining `_crafter` fallback reads in the builder are being removed and the builder will rely on compiler-artifact/shared state only.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:65-71
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:170-175
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:193-199
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:213-219
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:258-269
  IMPACT: `CreationContextBuilder` will stop depending on `SpellCrafter` fallback state and become a pure compiler-artifact/shared-execution consumer.
  NEXT: Patch only `creation_context_builder.py` to remove the `_crafter` fallback reads and tighten the docstrings/messages to compiler-artifact wording.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T07:02:00Z
  TYPE: FACT
  CLAIM: `CreationContextBuilder` is now migrated off `SpellCrafter` fallback state. The builder no longer reads `spell._crafter` for execution-plan, phase-12 executor, override patch map, or codegen/root-blueprint payload fallback. It now treats the spell-owned compiler artifact plus shared `phase8_11` export as the sole compiler-state source.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-271
  - repo_search: `rg -n "_crafter" src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
  IMPACT: The builder is no longer part of the remaining `SpellCrafter` dependency surface. The remaining runtime `SpellCrafter` reads are elsewhere, not in the creation-context build path.
  NEXT: If we continue, the next meaningful runtime cut is to audit the remaining explicit `spell._crafter` reads outside tests and remove or replace them case-by-case.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-21T07:14:00Z
  TYPE: DECISION
  CLAIM: The next slice is the hard removal of `SpellCrafter` from `Spell` and the deletion of `_crafter` as a runtime field. This is not a cosmetic cleanup; it means removing the spell-owned lazy crafter bridge, the old spell phase façade delegation path, and any remaining `src` runtime references that still assume `SpellCrafter` exists. The immediate step is a tight `src`-only usage inventory so the deletion boundary is exact.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-21
  IMPACT: We avoid another half-cut refactor by identifying the full runtime deletion surface before touching code.
  NEXT: Search `src` for `_crafter`, `_ensure_crafter`, and direct `SpellCrafter` construction/use sites, then cut only that exact runtime surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:13:56Z
  TYPE: FACT
  CLAIM: The requested _crafter removal is not a Spell-only edit anymore. Current src runtime still depends on the spell-owned crafter seam in three places outside spell.py: ownership transfer explicitly writes spell_obj._crafter = None, split phase 5 still reads spell._crafter, and Meld still invokes spell.run_structural_phases() through the old Spell façade. So the safe deletion boundary is Spell plus the remaining runtime dependents that still assume the old seam exists.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:198-198
  - src/melder/aether/spellbook/spell.py:780-805
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:758-758
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1288-1288
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:72-72
  - src/melder/aether/conduit/meld/meld.py:712-712
  IMPACT: Blindly deleting _crafter from Spell would leave live runtime callers broken even though SpellbookCreationSystem, Meld validity checks, and CreationContextBuilder were already migrated.
  NEXT: Read the exact spell.py, ispell.py, 	ransfer_of_ownership.py, compiler_phase_5.py, and meld.py seams once, then patch the deletion cut in one pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:18:28Z
  TYPE: FACT
  CLAIM: The current structural-phase failure is a direct compiler-system wiring bug in Phase 4. SpellbookCreationSystem reaches SpellCompilerSystem.run_phase_validation(...), but that front method still forwards arguments in the old order into SpellCompiler.run_phase_validation(...). The lower compiler surface now expects (spell, artifact, spell_validator, spell_system_states, cancel_event), while the front method is still calling it as (spellbook, spell, artifact, spell_validator, spell_system_states, cancel_event=...). That makes spell_system_states land in the cancel_event slot and then also supplies cancel_event by keyword, producing the exact multiple values for argument 'cancel_event' failure.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1937-1947
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:219-257
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler.py:247-281
  IMPACT: Structural conjure currently dies in phase 4 before any later compiler removal work matters. This is a local front-to-compiler signature mismatch, not a deeper runtime regression.
  NEXT: Patch only SpellCompilerSystem.run_phase_validation(...) to match the lower compiler signature, then stop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:19:11Z
  TYPE: FACT
  CLAIM: The current conjure failure is a stale constructor call in Meld.__init__. SpellCompilerSystem is now stateless and takes no constructor arguments, but Meld still instantiates it as SpellCompilerSystem(spellbook), so conduit creation dies before any meld/runtime behavior begins.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:146-147
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:35-53
  IMPACT: Root conduit creation fails during Meld construction, which blocks every conjure path regardless of phase correctness.
  NEXT: Patch only Meld.__init__ to construct SpellCompilerSystem() with no arguments.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:22:42Z
  TYPE: FACT
  CLAIM: The new integration failures are stale convenience-method wiring inside SpellCompilerSystem, not deeper runtime regressions. un_structural_phases(...) still calls un_phase_requirements(spellbook, spell, cancel_event=...) and un_phase_symbolic_graph(spellbook, spell, cancel_event=...) even though those front methods were slimmed to (spell, cancel_event=...). The same old-wide call shape is also still present in un_all_phases(...).
  EVIDENCE:
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:804-856
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:859-953
  - src/melder/aether/conduit/spell_compiler_system/spell_compiler_system.py:93-161
  IMPACT: Post-conjure structural reruns and any un_all_phases(...) path will keep failing with multiple values for argument 'cancel_event' until the convenience layer matches the narrowed front signatures.
  NEXT: Patch only SpellCompilerSystem.run_structural_phases(...) and un_all_phases(...) to use the current front-method signatures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:26:03Z
  TYPE: DECISION
  CLAIM: The active lane is now the actual Spell seam removal slice. We are removing _crafter and _ensure_crafter from Spell, switching Spell's public read/phase surface to compiler-artifact and SpellCompilerSystem, and then updating only the runtime/test callers that still reach through that seam. No unrelated Spell attributes are being changed.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  - src/melder/aether/spellbook/spell.py:198-198
  - src/melder/aether/spellbook/spell.py:370-372
  - src/melder/aether/spellbook/spell.py:780-805
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:871-918
  IMPACT: This is the first non-additive removal cut in the lane. Spell stops being the last runtime owner of SpellCrafter, and tests/runtime have to move to explicit compiler-system or explicit SpellCrafter construction where that old object is still under direct test.
  NEXT: Patch spell.py and the minimum runtime/interface seams first, then update the direct _crafter/_ensure_crafter tests to the new contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:40:55Z
  TYPE: FACT
  CLAIM: The hard Spell seam removal is now in the runtime code. Spell no longer owns _crafter, no longer exposes _ensure_crafter, and no longer carries the old phase-running surface. The surviving read-only spell phase state (equirements, symbolic_graph, esolution_frame, alidation_result_phase4, alidation_result_phase6, alidated, is_broken) is now sourced directly from the spell-owned compiler artifact instead of a spell-owned crafter object. Runtime callers that still depended on the removed seam were patched in place: Meld now reruns structural phases through its owned SpellCompilerSystem, ownership transfer now clears compiler-artifact + creation-context state instead of nulling _crafter, and the dead _crafter helper was removed from split phase 5.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:1-1486
  - src/melder/utilities/interfaces/ispell.py:90-526
  - src/melder/aether/conduit/meld/meld.py:704-721
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:748-770
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1280-1293
  - src/melder/aether/conduit/spell_compiler_system/phases/compiler_phase_5.py:44-90
  IMPACT: Runtime code is now aligned to the “Spell does not own SpellCrafter” contract. Remaining fallout is concentrated in tests that still call removed Spell phase methods or still assert on _crafter directly.
  NEXT: Rewrite the old Spell-surface tests to use either direct SpellCrafter construction where that class is explicitly under test or SpellCompilerSystem where the behavior being tested is really the migrated runtime/compiler path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:45:10Z
  TYPE: FACT
  CLAIM: The linked test fallout splits into two buckets. Bucket 1 is unit stubs that still model the old SpellbookCreationSystem call contracts: phase factory monkeypatches still take (spellbook, scheduler, conduit_id) instead of (spellbook, scheduler, compiler_system, conduit_id), cleanup tests still expect spell.crafter.cleanup_phase_artifacts(), and post-conjure tests still hand in fake spells that only expose un_structural_phases(). Bucket 2 is the explicit SpellCrafter integration file, which still drives removed Spell methods (un_phase_*, un_all_phases, _ensure_crafter, _crafter) instead of constructing SpellCrafter directly now that the Spell seam is gone.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:206-236
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:671-698
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:784-867
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:911-939
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:1-120
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:150-190
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:820-990
  IMPACT: These failures are test-contract drift caused by the hard Spell seam removal, not fresh runtime behavior bugs. The test files need to be updated to the new explicit boundaries.
  NEXT: Patch only the linked unit fastpath file and the linked integration spell-crafter file to match the removed Spell seam; leave broader old-surface test sweeps for later failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:50:18Z
  TYPE: FACT
  CLAIM: The first linked test rewrite tranche is in. The unit fastpath file now matches the current SpellbookCreationSystem contracts: conduit phase-factory stubs accept the extra compiler_system arg, cleanup tests monkeypatch SpellCompilerSystem.cleanup_phase_artifacts(...) instead of expecting spell.crafter, post-conjure structural tests monkeypatch SpellCompilerSystem.run_structural_phases(...) instead of handing fake spells the old Spell.run_structural_phases() seam, _register_target_single_phase(...) is asserted through its current rgs= contract, and the wrapper tests now monkeypatch 4-arg phase factory signatures. In the linked SpellCrafter integration file, the specific failing tests now construct and drive SpellCrafter directly through _make_crafter(...), _run_structural_phases_via_crafter(...), and _run_all_phases_via_crafter(...) instead of the removed Spell seam.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1-1385
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:1-990
  IMPACT: The linked failures are now aligned to the hard Spell seam removal. Remaining fallout, if any, will be other tests in the old SpellCrafter-focused files that still call removed Spell methods or assert on _crafter directly.
  NEXT: Stop here until the next failing traceback identifies the next stale old-Spell test surface to rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:52:09Z
  TYPE: FACT
  CLAIM: The latest failure batch splits cleanly into runtime fallout and test-contract fallout. Runtime-wise, structural Phase 4 still has at least one hidden _crafter read somewhere in the validation path, because fresh spellbook.conjure(...) now dies during alidation with AttributeError: 'Spell' object has no attribute '_crafter' before any conduit-runtime assertions run. Test-wise, the unit fastpath file still models the old SpellbookCreationSystem helper contracts and old cleanup seam, so it keeps failing on stale factory signatures and old spell.crafter expectations.
  EVIDENCE:
  - user_traceback: tests/component/melder/aether/conduit/test_conduit_component_creations.py phase alidation failures on 2026-05-20
  - user_traceback: tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py failures on 2026-05-20
  IMPACT: We need to remove the remaining runtime _crafter read before broad conduit/conjure tests can pass, then finish rewriting the linked unit fastpath file to the new helper contracts.
  NEXT: Search src for the remaining non-Spell _crafter runtime reads, patch the active runtime path first, then continue the linked unit test rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:52:42Z
  TYPE: FACT
  CLAIM: The live Phase 4 _crafter read is in BindingResolutionCycleStrategy.validate(...). The strategy iterates spellbook._spell_id_pool, grabs spell_instance._crafter, and reads crafter.requirements to build the binding-key graph. After the hard Spell seam removal, that becomes the first structural-phase runtime failure during conjure. This read should use the surviving spell read surface (spell_instance.requirements) instead of the deleted private field.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:72-103
  IMPACT: Structural validation cannot finish for any new conjure path until this strategy stops reading _crafter.
  NEXT: Patch this strategy to read requirements from spell_instance.requirements and keep the rest of the cycle-detection logic unchanged.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:53:26Z
  TYPE: FACT
  CLAIM: The remaining live runtime _crafter read outside the SpellCrafter package is now gone. BindingResolutionCycleStrategy.validate(...) used to pull spell_instance._crafter.requirements while building its binding-key graph during Phase 4 validation; it now reads the surviving spell surface (spell_instance.requirements) instead. A follow-up search over src outside spell_crafter/** found no remaining direct _crafter reads, _crafter = None writes, or _ensure_crafter(...) calls.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:72-98
  - repo_search: g -n '\._crafter\b|_crafter = None|_ensure_crafter\(' src --glob '!src/melder/aether/spellbook/spell_crafter/**'
  IMPACT: Fresh conjure/structural validation no longer depends on the deleted Spell _crafter field. The next failures, if any, should move to different seams.
  NEXT: Wait for the next failure batch and patch the new seam instead of continuing blind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T21:58:32Z
  TYPE: FACT
  CLAIM: The latest linked slice is patched in both runtime and tests. Runtime: BindingResolutionCycleStrategy.validate(...) no longer reads spell_instance._crafter; it now uses spell_instance.requirements, which is the surviving artifact-backed read surface after the hard Spell seam cut. Test-side: the linked component 	est_spellbook_component_spell_crafter.py no longer calls removed Spell phase methods or _ensure_crafter() / _crafter. It now uses local helper functions built on SpellCompilerSystem for phase execution and reads compiler-artifact fields directly for assertions.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:72-98
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1-1810
  IMPACT: Fresh conjure/validation should no longer die on the deleted _crafter field, and the linked component file is now aligned to the post-Spell compiler-system contract instead of the removed old seam.
  NEXT: Wait for the next failing traceback and patch that exact seam instead of widening into unrelated test files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T22:12:45Z
  TYPE: FACT
  CLAIM: The linked unit/component test fallout is now patched to the hard post-Spell seam contract. The unit fastpath file now matches the current SpellbookCreationSystem helper signatures and compiler-system cleanup/structural rerun behavior. The component 	est_spellbook_component_spell_crafter.py file no longer drives the removed Spell phase methods or private _crafter seam; it now uses local helper functions built on SpellCompilerSystem and asserts against compiler-artifact state instead.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:1-1385
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1-1825
  IMPACT: The next rerun should move off the deleted Spell seam in these linked files. Remaining failures, if any, should expose the next stale boundary instead of repeating the same removed-method/_crafter contract.
  NEXT: Wait for the next failing traceback and patch that exact boundary only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T22:13:40Z
  TYPE: PLAN
  CLAIM: The next bounded slice is import-path cleanup for tests that still import SpellCrafter from the dead melder.aether.spellbook.spell_compiler.spell_crafter path. This slice only updates those explicit import lines first, then runs the affected tests to surface the next concrete fallout.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-20
  NEXT: Replace the dead import path with the live melder.aether.spellbook.spell_crafter.spell_crafter path in the matching test files, then run the affected test subset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T22:14:14Z
  TYPE: FACT
  CLAIM: The dead SpellCrafter import path has been rewritten in the six affected test files. The immediate validation blocker is environmental: bare pytest is not on PATH in this workspace, so the next step is to run the same six-file subset through the repo-local pytest executable instead of the shell alias.
  EVIDENCE:
  - repo_search: exact import matches in six test files
  - shell_error: pytest command not found in workspace shell
  IMPACT: The import-path cleanup is in, but we need the concrete local pytest path to surface the next real failures.
  NEXT: Detect the repo-local pytest executable and rerun the same six-file subset.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T22:21:09Z
  TYPE: FACT
  CLAIM: The next failure batch is current-surface drift, not old-surface restoration. Runtime: _collect_target_resolution_scope(...) in SpellbookCreationSystem still called removed Spell local-scope methods instead of reading current compiler-artifact scope. Test-side: 	est_conduit_component_meld_gating.py still calls removed spell.run_all_phases(...), 	est_conduit_component_resolution_validation.py still wraps SpellCrafter instead of the current compiler front surface, and 	est_conduit_component_meld_overrides.py still uses a helper that runs removed Spell phase methods.
  EVIDENCE:
  - user_traceback: tests/component/melder/aether/conduit/test_conduit_component_meld_gating.py on 2026-05-20
  - user_traceback: tests/component/melder/aether/conduit/test_conduit_component_resolution_validation.py on 2026-05-20
  - user_traceback: tests/component/melder/aether/conduit/test_conduit_component_spell_contracts.py on 2026-05-20
  - user_traceback: tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py on 2026-05-20
  IMPACT: The runtime seam now needs one direct artifact-based scope reader, and the linked conduit component tests need to be rewritten to the current compiler-system surface instead of the removed Spell phase façade.
  NEXT: Patch the runtime scope collector first, then patch the three linked component test seams only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T22:53:26Z
  TYPE: MEASURE
  CLAIM: The hard Spell seam removal now holds against both the component and integration rings after moving the stale test surfaces to SpellCompilerSystem / compiler-artifact helpers and removing the last live _crafter runtime read outside the spell_crafter package.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1568-1588
  - src/melder/aether/spellbook/spell_crafter/validation/strategies/binding_resolution_cycle_strategy.py:72-98
  - tests/component/melder/spellbook/compiler_test_helpers.py:1-160
  - tests/integration/melder/spellbook/test_spellbook_integration_post_conjure_bind_snapshot.py:1-460
  - tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py:1-2140
  - tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py:1-1050
  - validation: .[0m\.venv_new\Scripts\python.exe -m pytest -q tests/component
  - validation: .[0m\.venv_new\Scripts\python.exe -m pytest -q tests/integration
  IMPACT: The runtime no longer depends on Spell._crafter, and the component/integration suites are aligned to the compiler-system/artifact surfaces instead of the removed old Spell phase façade.
  NEXT: If we continue, the remaining meaningful validation ring is unit tests, or we can proceed with the next runtime deletion/rename tranche from a green component+integration base.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
