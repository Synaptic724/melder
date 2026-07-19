# Task: remove spellbook and conduit binder factories
- Completed: 2026-05-20T08:58:57Z
- Summary: Closed after removing the Spellbook and Conduit binder factories, migrating callers to explicit top-level `SpellBinder(...)`, and validating the full suite (`8143 passed, 2 skipped, 5 xfailed, 1 warning`).

## Metadata
- Task ID: TASK-2026-05-20-remove-spellbook-and-conduit-binder-factories
- Story: none
- Epic: none
- Status: done
- Owner: codex
- Agent Name: refactor_0
- Priority: p1
- Created: 2026-05-20T08:34:32Z
- Updated: 2026-05-20T08:58:57Z

## Objective
Remove `Spellbook.create_binder()` and `Conduit.create_binder()` so fluent
binding is instantiated explicitly through top-level `SpellBinder`, while
preserving the existing binder finalize-reset behavior.

## Ticket Contract
- ENTRY_GATE: this task is routed on `attention_board.md`, patch artifacts are
  linked, and the first implementation note is recorded before code edits.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/aether/spellbook/spellbinder.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/utilities/interfaces/ispellbook.py`
  - `src/melder/utilities/interfaces/iconduit.py`
  - direct callers/tests of `create_binder()`
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/2026-05-19_investigate_bind_cycle_and_dependency_surface_task.md`
  - `codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/architecture_patch.md`
  - `codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_spellbook.md`
  - `codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_conduit.md`
  - `codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_spellbinder.md`
  - `codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_package_root.md`
- EXIT_GATE: factory surfaces are removed, callers instantiate `SpellBinder`
  directly, finalize-reset behavior is preserved, and the focused/full tests
  for the affected callers are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if removing the factories forces
  a larger `Bind` / `Spellbook.bind(...)` commit-surface redesign than agreed.

## Scope Boundaries
- In scope:
  - remove Spellbook binder factory
  - remove Conduit binder proxy
  - keep top-level `SpellBinder` export path
  - update callers/tests to instantiate `SpellBinder(...)` directly
  - preserve current `finalize() -> _reset_current()` reuse contract
- Out of scope:
  - changing `SpellBinder` to hold `Bind` instead of `Spellbook`
  - changing `Bind` ownership/commit semantics
  - unrelated spellbook or conduit refactors

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user selected the top-level `SpellBinder` strategy and
  approved removing the factory surfaces.

## Steps / Checklist
- [ ] Create patch-lane artifacts and map them to code slices.
- [ ] Remove `Spellbook.create_binder()` and its interface surface.
- [ ] Remove `Conduit.create_binder()` and its interface surface.
- [ ] Update direct callers/tests to instantiate `SpellBinder(...)` explicitly.
- [ ] Preserve and verify binder reset behavior after `finalize()`.
- [ ] Validate the affected suite.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- removed binder factory surfaces
- direct top-level `SpellBinder` caller path
- preserved binder finalize-reset behavior

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-20_remove_spellbook_and_conduit_binder_factories_task.md`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/artifact_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\spellbook\test_spellbinder.py`
  - `.\.venv_new\Scripts\python.exe -m pytest -q <direct spellbook/conduit fluent caller rings>`
  - `.\.venv_new\Scripts\python.exe -m pytest -q`

## Risks / Rollback Notes
- Risk: broad caller churn because `create_binder()` is used across unit,
  integration, and public-api tests.
  Rollback: keep the top-level entry and restore one factory temporarily only
  if the caller migration proves larger than this bounded tranche can absorb.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/top_level_spellbinder_entry/architecture_patch.md`
  - `system_docs/patches/active/top_level_spellbinder_entry/component_patch_spellbook.md`
  - `system_docs/patches/active/top_level_spellbinder_entry/component_patch_conduit.md`
  - `system_docs/patches/active/top_level_spellbinder_entry/component_patch_spellbinder.md`
  - `system_docs/patches/active/top_level_spellbinder_entry/component_patch_package_root.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: remove patch-lane artifacts after canonical docs/code are merged and validated.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-20T08:34:32Z
  TYPE: DECISION
  CLAIM: The chosen binder cut is to remove the Spellbook and Conduit factory
    surfaces while keeping `SpellBinder` as the explicit top-level entry. The
    existing `finalize()` reset behavior already satisfies the requested reuse
    mechanic, so no new binder-reset feature is needed.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbinder.py:691-734
  - src/melder/aether/spellbook/spellbook.py:2100-2146
  - src/melder/aether/conduit/conduit.py:1744-1788
  - src/melder/utilities/interfaces/ispellbook.py:371-413
  IMPACT: This is a caller/API migration cut, not a `Bind` ownership redesign.
  NEXT: create the patch artifacts, then remove the factories and update direct callers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T08:34:32Z
  TYPE: PLAN
  CLAIM: Patch-to-implementation mapping is explicit. `architecture_patch.md`
    sets the API and ownership boundaries. `component_patch_spellbook.md` maps
    to removing `Spellbook.create_binder()` and its interface entry.
    `component_patch_conduit.md` maps to removing `Conduit.create_binder()` and
    its interface entry. `component_patch_spellbinder.md` maps to preserving
    `finalize() -> _reset_current()` unchanged while caller paths move to direct
    construction. `component_patch_package_root.md` maps to verifying the
    top-level export stays intact. The implementation pass is therefore:
    interfaces -> factories -> callers/tests -> validation.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/architecture_patch.md:1-38
  - codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_spellbook.md:1-23
  - codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_conduit.md:1-22
  - codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_spellbinder.md:1-23
  - codex/context_compass/system_docs/patches/active/top_level_spellbinder_entry/component_patch_package_root.md:1-17
  IMPACT: The engineer patch gate is satisfied and the edit order is clear.
  NEXT: remove the interface/factory surfaces, migrate direct callers, and run
    the binder/caller validation rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T08:43:31Z
  TYPE: FACT
  CLAIM: The source-level factory surfaces are removed and the direct caller
    migration is in place. `Spellbook.create_binder()` and
    `Conduit.create_binder()` are gone, direct callers now construct
    `SpellBinder(...)` explicitly, and `SpellBinder.finalize()` still resets
    staged state after a successful bind exactly as before.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:1-30
  - src/melder/aether/spellbook/spellbook.py:2098-2148
  - src/melder/aether/conduit/conduit.py:1-24
  - src/melder/aether/conduit/conduit.py:1740-1792
  - src/melder/utilities/interfaces/ispellbook.py:367-420
  - src/melder/utilities/interfaces/ispellbinder.py:7-21
  - src/melder/aether/spellbook/spellbinder.py:691-734
  IMPACT: The public entry strategy is now the explicit top-level binder path,
    not the factory methods, and the binder reset mechanic did not require new
    implementation.
  NEXT: run the full suite to catch any broader caller fallout outside the
    direct binder rings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T08:43:31Z
  TYPE: MEASURE
  CLAIM: The direct binder/caller validation ring is green and a repo search
    finds no remaining `create_binder(` call sites in `src` or `tests`.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\spellbook\\test_spellbinder.py tests\\unit\\melder\\aether\\conduit\\test_conduit_facade.py tests\\integration\\melder\\conduit\\test_conduit_integration_binder.py tests\\integration\\melder\\conduit\\test_conduit_integration_public_api.py tests\\integration\\melder\\spellbook\\test_spellbook_integration_core.py tests\\integration\\melder\\spellbook\\test_spellbook_integration_fluent.py tests\\integration\\melder\\spellbook\\test_spellbook_integration_fluent_guards.py tests\\integration\\melder\\spellbook\\test_spellbook_integration_lifecycle.py` -> `153 passed, 1 warning`
  - validation_result: `rg -n "create_binder\\(" src tests` -> no matches
  IMPACT: The explicit caller migration is complete enough to justify a full
    suite run instead of more local patching.
  NEXT: run `.\.venv_new\\Scripts\\python.exe -m pytest -q`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-20T08:44:55Z
  TYPE: MEASURE
  CLAIM: The full repo suite is green after the binder factory removal and
    caller migration. The top-level `SpellBinder(...)` path is now the only
    fluent binder entry in `src` and `tests`, and the removal did not introduce
    broader runtime fallout.
  EVIDENCE:
  - validation_result: `.\\.venv_new\\Scripts\\python.exe -m pytest -q` -> `8143 passed, 2 skipped, 5 xfailed, 1 warning`
  IMPACT: This API cut is fully validated against the full suite, not just the
    direct binder ring.
  NEXT: hand the cut back for review or choose the next bounded refactor lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Top-level `SpellBinder` strategy is implemented: Spellbook and Conduit binder
factories are removed, direct callers instantiate `SpellBinder(...)`, and the
full repo suite is green.
