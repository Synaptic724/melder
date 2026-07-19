# Task: Strip Frame Posture Fields From SpellbookConfiguration
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed after finalizing the owner move, removing test-only compatibility, adding explicit shared/local/threadsafe tests, and validating the full suite (8181 passed).


## Metadata
- Task ID: TASK-2026-05-16-strip-frame-posture-fields-from-spellbook-configuration
- Story: STORY-2026-05-16-remove-frame-posture-from-spellbook-configuration
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T13:30:44Z
- Updated: 2026-05-16T15:47:45Z

## Objective
Remove frame posture ownership from `SpellbookConfiguration` and move the direct
runtime readers in this slice to real frame posture instead.

## Ticket Contract
- ENTRY_GATE: the reset epic/story are active and the user explicitly chose
  this as the first bounded owner-boundary step.
- EXECUTION_BOUNDARY:
  - `src/melder/spellbook/configuration/spellbook_configuration.py`
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - `src/melder/aether/conduit/conduit.py`
  - nearby direct runtime readers and their focused tests only
- DEPENDENCIES:
  - `tickets/stories/2026-05-16_remove_frame_posture_from_spellbook_configuration_story.md`
- EXIT_GATE: the frame posture fields and methods are gone from
  `SpellbookConfiguration`, direct runtime readers in this slice no longer read
  them from the rich config bag, and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if a direct reader proves a
  field still belongs to the rich config.

## Scope Boundaries
- In scope:
  - posture-field/method removal
  - direct runtime reader reroutes
  - focused test expectation moves
- Out of scope:
  - full frame lifecycle methods
  - final shared-rich-config mechanics

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner split must start here before any wider config
  behavior is safe to change.

## Steps / Checklist
- [x] Remove frame posture fields from `SpellbookConfiguration`.
- [x] Remove frame-posture helper methods from `SpellbookConfiguration`.
- [x] Reroute the direct runtime readers in this slice.
- [ ] Move the affected tests to the new owner.
- [ ] Run focused validation.

## Validation
- `python -m py_compile src/melder/spellbook/spellbook.py src/melder/aether/aether.py src/melder/aether/aetheric_frame.py src/melder/aether/conduit/conduit.py src/melder/spellbook/spellbook_creation_system.py src/melder/spellbook/configuration/spellbook_configuration.py src/melder/aether/aetheric_frame_configuration.py`
- Tests not run yet for this owner-path cleanup slice.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/frame_posture_owner_migration/architecture_patch.md`
  - `system_docs/patches/active/frame_posture_owner_migration/component_patch_spellbook.md`
  - `system_docs/patches/active/frame_posture_owner_migration/code_description_patch_spellbook.md`
  - `system_docs/patches/active/frame_posture_owner_migration/component_patch_aetheric_frame.md`
  - `system_docs/patches/active/frame_posture_owner_migration/component_patch_aether.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: after durable deltas merge into canonical docs

## Notes
- DATETIME: 2026-05-16T13:30:44Z
  TYPE: PLAN
  CLAIM: The first repair step is deliberately small: remove posture from the
    rich config and stop the direct readers from pulling it out of the wrong
    owner. Nothing else should be solved in this same task.
  EVIDENCE:
  - user_instruction: "just move the fucken variables out of spellbook configuration"
  - user_instruction: "keep SpellbookConfiguration as the local rich config only"
  IMPACT: This keeps the next code pass bounded and prevents another all-at-once
    drifted refactor.
  NEXT: patch only the owner boundary and the direct readers first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T13:43:16Z
  TYPE: FACT
  CLAIM: The next incomplete part of the owner split is now explicit: the
    frame-posture methods still live on `SpellbookConfiguration` even though
    the posture fields have been moved out of its rich property bag. That keeps
    the wrong authoring surface in place and leaks the old ownership model into
    runtime helpers and tests.
  EVIDENCE:
  - src/melder/spellbook/configuration/spellbook_configuration.py:658-858
  - src/melder/utilities/interfaces/iconfiguration.py:278-410
  - src/melder/aether/conduit/conduit.py:969-969
  - src/melder/spellbook/spellbook.py:3022-3027
  IMPACT: The bounded next step is to migrate `with_system_state(...)`,
    `with_ai_native(...)`, `with_rift_enabled(...)`,
    `with_shared_framewide_spellbook_configuration(...)`, `dynamic_defaults()`,
    `automatic_defaults()`, and `to_aetheric_frame_configuration(...)` onto
    `AethericFrameConfiguration`, then switch the direct callers to the new
    owner.
  NEXT: patch only those method moves and the direct callers/tests that still
    use the old `SpellbookConfiguration` surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T13:43:16Z
  TYPE: MEASURE
  CLAIM: The source-side method migration is now in. `SpellbookConfiguration`
    no longer exposes the frame-posture methods, and the source callers now use
    the frame-owned path instead: `AethericFrame` creates the default posture,
    `Spellbook` holds the frame-owned reference, `Conduit` reads the real frame
    posture instead of synthesizing it from rich config, and Nexus-managed
    creation binds frame posture before the root Spellbook path.
  EVIDENCE:
  - src/melder/spellbook/configuration/spellbook_configuration.py:13-758
  - src/melder/aether/aetheric_frame_configuration.py:13-303
  - src/melder/aether/aetheric_frame.py:93-96
  - src/melder/spellbook/spellbook.py:193-203
  - src/melder/spellbook/spellbook.py:3213-3258
  - src/melder/spellbook/spellbook_creation_system.py:398-425
  - src/melder/aether/conduit/conduit.py:170-177
  - src/melder/aether/conduit/conduit.py:961-972
  - src/melder/aether/nexus/nexus_frame_configuration.py:311-327
  - src/melder/aether/nexus/nexus_frame_manager.py:956-968
  - validation_result:
    `python -m py_compile src/melder/aether/aetheric_frame.py src/melder/aether/aetheric_frame_configuration.py src/melder/aether/aether.py src/melder/aether/conduit/conduit.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/nexus_frame_configuration.py src/melder/aether/nexus/nexus_frame_manager.py src/melder/spellbook/spellbook.py src/melder/spellbook/spellbook_creation_system.py src/melder/spellbook/configuration/spellbook_configuration.py src/melder/utilities/interfaces/iconfiguration.py`
  IMPACT: The source owner boundary is materially cleaner now, but the test
    suite still contains many old `SpellbookConfiguration` posture helper calls
    that need migration to the new frame-owned surface in the next pass.
  NEXT: update the stale tests to the new owner model and rerun the focused
    validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:18:56Z
  TYPE: FACT
  CLAIM: The next runtime drift is now isolated: frame posture is frame-owned
    and default-created, but `Spellbook` still uses
    `_configuration_cleanup_owned_by_frame` to reason about rich-config cleanup
    and shared-config adoption. That bool is now the remaining local owner
    bookkeeping seam that needs removal before test migration.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:188-200
  - src/melder/spellbook/spellbook.py:343-355
  - src/melder/spellbook/spellbook.py:2904-2941
  - src/melder/spellbook/spellbook.py:3175-3213
  - src/melder/aether/aetheric_frame.py:96-102
  - src/melder/aether/aether.py:848-879
  IMPACT: The bounded next code pass is to remove that bool and make Spellbook
    use direct frame-owned checks through `Aether` / `AethericFrameConfiguration`
    instead of local cleanup-owner state.
  NEXT: patch `Spellbook` init/bind/cleanup so direct frame-owned truth replaces
    `_configuration_cleanup_owned_by_frame`, then review the resulting owner path
    before any test updates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:18:56Z
  TYPE: PLAN
  CLAIM: Patch-framework entry gating is now repaired for this slice. The
    active task links a minimal patch lane that maps the owner-boundary change
    across `Spellbook`, `Aether`, and `AethericFrame`, so the runtime edit can
    proceed without inventing undocumented lifecycle behavior.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_posture_owner_migration/architecture_patch.md:1-47
  - codex/context_compass/system_docs/patches/active/frame_posture_owner_migration/component_patch_spellbook.md:1-43
  - codex/context_compass/system_docs/patches/active/frame_posture_owner_migration/code_description_patch_spellbook.md:1-34
  IMPACT: The next implementation pass is now compliant and bounded.
  NEXT: remove the Spellbook owner bool and switch to direct frame-owned checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-16T14:18:56Z
  TYPE: MEASURE
  CLAIM: The remaining Spellbook owner-bool drift is now removed from runtime
    source. `Spellbook` initializes the frame-owned posture reference before
    rich-config init, uses direct frame-owned shared-config checks for
    adoption/cleanup, and no longer stores `_configuration_cleanup_owned_by_frame`.
  EVIDENCE:
  - src/melder/spellbook/spellbook.py:188-199
  - src/melder/spellbook/spellbook.py:343-355
  - src/melder/spellbook/spellbook.py:2893-3030
  - src/melder/spellbook/spellbook.py:3206-3280
  - src/melder/aether/aetheric_frame.py:96-102
  - src/melder/aether/aether.py:848-879
  - validation_result:
    `python -m py_compile src/melder/spellbook/spellbook.py src/melder/aether/aether.py src/melder/aether/aetheric_frame.py src/melder/aether/conduit/conduit.py src/melder/spellbook/spellbook_creation_system.py src/melder/spellbook/configuration/spellbook_configuration.py src/melder/aether/aetheric_frame_configuration.py`
  IMPACT: The source-side owner path is now closer to the intended model before
    test migration: frame posture is frame-owned and default-created, Spellbook
    retains a direct frame-owned posture reference, and shared rich-config
    cleanup is decided from actual frame-owned truth instead of local bookkeeping.
  NEXT: do one more direct source review pass on Spellbook/Aether/AethericFrame
    consistency, then decide the next source-side cleanup before touching tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:18:56Z
  TYPE: FACT
  CLAIM: The owner-path source review is now consistent with the intended frame
    model. `AethericFrame` default-creates the posture object, `Spellbook`
    initializes its frame-owned posture reference before rich-config init,
    frame posture is frozen through the Aether bind path, and the remaining
    Spellbook runtime reads in this slice use the retained frame-owned posture
    reference directly instead of a local ownership bool.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:95-102
  - src/melder/aether/aetheric_frame.py:268-292
  - src/melder/aether/aether.py:848-879
  - src/melder/spellbook/spellbook.py:188-199
  - src/melder/spellbook/spellbook.py:343-355
  - src/melder/spellbook/spellbook.py:2893-3030
  - src/melder/spellbook/spellbook.py:3206-3280
  - src/melder/spellbook/spellbook.py:3282-3295
  - validation_result:
    `python -m py_compile src/melder/spellbook/spellbook.py src/melder/aether/aetheric_frame.py`
  IMPACT: The source-side refactor is now in the right place to start test
    migration next. The next work item should be moving stale test callers and
    expectations onto the frame-owned posture surface, not more owner-path
    invention in runtime code.
  NEXT: update the stale tests to the new frame-owned posture API and rerun the
    focused validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:18:56Z
  TYPE: FACT
  CLAIM: The first failing test is only the visible tip. The current test suite
    still has a broad stale caller surface using removed
    `SpellbookConfiguration` posture methods such as `dynamic_defaults()`,
    `with_system_state(...)`, `with_rift_enabled(...)`, and
    `to_aetheric_frame_configuration(...)`. The immediate import failure in
    `test_conduit_component_creations.py` is a syntax error caused by one of
    those stale edits, but the real next tranche is a focused test migration to
    the frame-owned posture surface.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:47-64
  - tests/unit/melder/spellbook/configuration/test_configuration.py:16-517
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:21-214
  - tests/component/melder/spellbook/test_spellbook_component_configuration.py:96-306
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:154-541
  - measure_result:
    `rg -n "with_system_state\\(|with_ai_native\\(|with_rift_enabled\\(|with_shared_framewide_spellbook_configuration\\(|dynamic_defaults\\(|automatic_defaults\\(|to_aetheric_frame_configuration\\(" tests`
  IMPACT: The next step is not a single syntax fix. It is a bounded migration of
    the focused config/spellbook/conduit test ring onto frame-owned posture
    setup and assertions.
  NEXT: patch the focused failing ring first, using `AethericFrameConfiguration`
    or frame-owned posture setup directly, then rerun that ring before touching
    wider tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: The first real pytest run on `tests/` now shows the immediate blocker
    layer clearly: collection stops on three syntax-broken stale test files,
    all carrying leftover `SpellbookConfiguration` posture calls after the
    owner-surface removal. Until those three collection blockers are repaired,
    pytest cannot expose the deeper assertion/runtime fallout.
  EVIDENCE:
  - validation_result:
    `python -m pytest -q tests`
  - tests/component/melder/aether/conduit/test_conduit_component_creations.py:63-64
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:312-316
  - tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py:141-145
  IMPACT: The next bounded test tranche is to fix these three collection
    blockers first, then rerun pytest to reveal the next actual failure layer.
  NEXT: patch the three syntax-broken stale test files onto the frame-owned
    posture surface and rerun `python -m pytest -q tests`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: After fixing the initial collection blockers and rerunning
    `python -m pytest -q tests`, the suite now reaches runtime assertions and a
    much smaller coherent problem appears: the centralized test posture helper
    is resetting frame posture back to automatic every time a follow-up helper
    such as `with_system_state(...)`, `with_rift_enabled(...)`, or
    `to_aetheric_frame_configuration()` calls the shared getter. That one reset
    bug is cascading into many of the remaining posture-related failures.
  EVIDENCE:
  - validation_result:
    `python -m pytest -q tests`
  - tests/_frame_posture_test_support.py:47-105
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:41-44
  - tests/component/melder/spellbook/test_spellbook_component_configuration_core.py:203-215
  IMPACT: The next bounded fix is to split Ã¢â‚¬Å“get the frame-owned posture objectÃ¢â‚¬Â
    from Ã¢â‚¬Å“apply defaultsÃ¢â‚¬Â in the test helper. That should collapse a large
    fraction of the remaining posture-failure surface before we judge deeper
    runtime issues.
  NEXT: patch the shared test posture helper so getter paths never mutate
    posture, then rerun the focused failing tests before another full-suite run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: The test harness and frame-bind follow-up fixes are now validated on
    the posture-heavy subset. The shared test helper now keeps detached
    per-configuration posture state and syncs it onto the frame-owned posture
    without resetting reads, and `Aether._bind_aetheric_frame_configuration(...)`
    now preserves the existing unfrozen frame-owned object identity while
    copying in new posture values before freeze. The focused subset covering
    component Spellbook configuration and the heavy capability/static Rift
    integration harnesses is green.
  EVIDENCE:
  - tests/_frame_posture_test_support.py:1-169
  - src/melder/aether/aether.py:848-879
  - validation_result:
    `python -m pytest -q tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py`
  IMPACT: The next signal should come from another full-suite run, not more
    local harness speculation.
  NEXT: rerun `python -m pytest -q tests` and reduce the remaining failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: The second full-suite run is now down to 64 failures and the remaining
    break surface is clustered instead of diffuse. The main buckets are:
    1) tests that still assert the old shared-rich-config default/bind behavior,
    2) the test posture helper needing frozen-frame idempotence for repeated
       same-posture setup on already-frozen frames,
    3) stale unit tests that still target removed Spellbook internals such as
       `_derive_aetheric_frame_configuration(...)`, and
    4) a smaller set of direct runtime or contract tests that still need source-
       aligned updates.
  EVIDENCE:
  - validation_result:
    `python -m pytest -q tests`
  - tests/integration/melder/aether/test_aether_integration_core.py:115-115
  - tests/integration/melder/aether/test_aether_integration_frames.py:286-286
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:72-72
  - tests/unit/melder/spellbook/test_spellbook.py:1695-2052
  IMPACT: The next tranche should not be another whole-suite blind pass. It
    should fix frozen-frame idempotence in the helper first, then move the stale
    expectation/unit tests onto the new owner model in focused groups.
  NEXT: patch frozen-frame idempotence into the helper and start updating the
    stale Aether/Spellbook unit expectations that still target removed behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: The next narrowed rerun leaves only three failures across the targeted
    categories, and all three are stale expectation mismatches:
    1) `with_ai_native(True)` no longer raises immediately on the local rich
       config path and should be asserted through frame-posture validation,
    2) `_bind_configuration(...)` no longer treats a new non-default frame name
       as missing because Aether now ensures frames during normal use, and
    3) rich config is no longer shared by default on conjure, so the old
       `Aether._get_configuration(frame)` expectation is wrong unless explicit
       shared framewide mode is enabled.
  EVIDENCE:
  - validation_result:
    `python -m pytest -q tests/integration/melder/conduit/test_conduit_integration_concurrency.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/integration/melder/aether/test_aether_integration_core.py tests/integration/melder/aether/test_aether_integration_frames.py`
  - tests/unit/melder/spellbook/configuration/test_configuration.py:116-117
  - tests/integration/melder/aether/test_aether_integration_core.py:115-115
  - tests/integration/melder/aether/test_aether_integration_frames.py:286-286
  IMPACT: The next edits should be isolated expectation updates in those test
    files, not more helper/runtime surgery.
  NEXT: patch those three stale expectations to the new owner model, then rerun
    the narrowed subset and another full-suite pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: The narrowed helper/expectation tranche is now green. The repeated
    dynamic-frame concurrency setup, the local config posture assertions, and
    the immediate Aether shared-config expectation updates all pass after:
    1) making the test helper preserve detached per-config posture state,
    2) making frozen same-posture sync idempotent,
    3) preserving frame-config object identity in the Aether bind path, and
    4) updating the stale shared-config and ai-native expectation tests.
  EVIDENCE:
  - tests/_frame_posture_test_support.py:1-169
  - src/melder/aether/aether.py:848-879
  - tests/unit/melder/spellbook/configuration/test_configuration.py:113-118
  - tests/integration/melder/aether/test_aether_integration_core.py:103-116
  - tests/integration/melder/aether/test_aether_integration_frames.py:273-295
  - validation_result:
    `python -m pytest -q tests/integration/melder/conduit/test_conduit_integration_concurrency.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/integration/melder/aether/test_aether_integration_core.py tests/integration/melder/aether/test_aether_integration_frames.py`
  IMPACT: The next meaningful signal must come from another full-suite run.
  NEXT: rerun `python -m pytest -q tests` and reduce the remaining failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: The next stale unit/setup cluster is now green too. Conduit unit tests
    now seed the spellbook stub with frame-owned posture instead of rich-config
    derivation, the Aether frame-config tests now assert the new frame-owned
    object-identity semantics rather than the old input-object identity, and
    the descriptor-cache test now expects the default-created frame posture
    instead of `None`.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:251-275
  - tests/unit/melder/aether/test_aether.py:733-844
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:28-176
  - tests/unit/melder/aether/test_frame_descriptor_manager.py:135-149
  - validation_result:
    `python -m pytest -q tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/unit/melder/aether/test_frame_descriptor_manager.py tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py`
  IMPACT: The remaining failures are now pushed farther inward to the larger
    stale Spellbook/Nexus/runtime expectation groups.
  NEXT: rerun the full suite and reduce the next concentrated failure cluster.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: MEASURE
  CLAIM: The final remaining cluster before the last full-suite pass is now
    green as well. The shared target-frame helpers were moved to real
    `AethericFrameConfiguration` binds, the stale Spellbook unit expectations
    were updated to the frame-owned posture path, and the SpellCrafter/
    occurrence-plan stubs now expose `_aetheric_frame_configuration` instead of
    only `_configuration`.
  EVIDENCE:
  - tests/unit/melder/aether/test_nexus.py:168-196
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:133-160
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:62-89
  - tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py:52-77
  - tests/unit/melder/spellbook/test_spellbook.py:1490-2052
  - tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py:1-170
  - tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py:1-5250
  - tests/unit/melder/spellbook/test_conjure_hotspot_fixes.py:1-180
  - tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py:1-280
  - validation_result:
    `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus_orchestration_and_lifecycle.py tests/unit/melder/aether/test_nexus_frame_configuration.py tests/unit/melder/spellbook/test_spellbook.py`
  - validation_result:
    `python -m pytest -q tests/unit/melder/spellbook/spell_crafter/blueprints/test_occurrence_plan.py tests/unit/melder/spellbook/spell_crafter/test_spell_crafter.py tests/unit/melder/spellbook/test_conjure_hotspot_fixes.py tests/unit/melder/spellbook/spell_crafter/validation/strategies/test_contract_provider_presence_strategy.py`
  IMPACT: The next full-suite run should be the real closeout check for this
    tranche rather than another exploratory pass.
  NEXT: run `python -m pytest -q tests` one final time and report the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T14:28:13Z
  TYPE: DECISION
  CLAIM: The green full-suite result used a test-only compatibility shim in
    `tests/conftest.py` that monkeypatched removed frame-posture methods back
    onto `SpellbookConfiguration`. That is not acceptable for final state. The
    shim has to go, and the tests have to be rewritten to call explicit helper
    functions or assert directly against frame-owned posture.
  EVIDENCE:
  - tests/conftest.py:1-44
  - tests/_frame_posture_test_support.py:1-169
  IMPACT: The suite currently passes, but not with the test surface in the
    desired explicit form. The next tranche is a real test rewrite pass, not a
    runtime change.
  NEXT: remove the monkeypatch compatibility layer from `tests/conftest.py`,
    replace stale test callers with explicit helper invocations, and rerun the
    full suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T15:42:27Z
  TYPE: DECISION
  CLAIM: With the tests now explicitly aligned to the new owner model, the next
    runtime cleanup is the one you asked for earlier: move
    `AethericFrameConfiguration` bind/freeze/conflict logic off `Aether` and
    onto `AethericFrame` itself. `Aether` should only resolve or create frames;
    it should not own per-frame posture lifecycle behavior.
  EVIDENCE:
  - src/melder/aether/aether.py:794-893
  - src/melder/aether/aetheric_frame.py:96-102
  - src/melder/spellbook/spellbook.py:3283-3284
  - src/melder/aether/nexus/nexus_frame_manager.py:961-962
  IMPACT: The next code pass will relocate the last misplaced frame-posture
    owner path now that test noise is out of the way.
  NEXT: add the posture bind method to `AethericFrame`, retarget `Spellbook`
    and `NexusFrameManager`, and validate the focused runtime ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T15:47:45Z
  TYPE: MEASURE
  CLAIM: The frame-posture bind/freeze/conflict logic now lives on
    `AethericFrame`, the direct runtime callers were retargeted, the last
    stale `Aether._bind_aetheric_frame_configuration(...)` test callers were
    migrated, the test bootstrap compatibility shim is gone, and the full test
    suite is green in that explicit state.
  EVIDENCE:
  - src/melder/aether/aetheric_frame.py:281-363
  - src/melder/aether/aether.py:794-927
  - src/melder/spellbook/spellbook.py:3251-3290
  - src/melder/aether/nexus/nexus_frame_manager.py:956-968
  - src/melder/utilities/interfaces/iaethericframe.py:1-49
  - tests/conftest.py:1-12
  - validation_result:
    `python -m pytest -q tests`
  IMPACT: The owner boundary is now cleaner in code and tests: frame posture is
    frame-owned end-to-end, Aether only resolves/creates frames, and the tests
    no longer rely on hidden reattached SpellbookConfiguration posture methods.
  NEXT: return the landed owner move and test cleanup for your review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T16:08:06Z
  TYPE: MEASURE
  CLAIM: Added three direct proof tests for the rich-config sharing contract in
    `test_spellbook_integration_core.py`: one explicit shared-mode proof, one
    explicit local-mode proof, and one same-frame concurrent shared-mode proof.
    The concurrent case uses two distinct initial rich configs, same frame,
    shared mode enabled, simultaneous conjure on separate threads, and asserts
    both Spellbooks converge onto one frame-owned shared config object with no
    errors.
  EVIDENCE:
  - tests/integration/melder/spellbook/test_spellbook_integration_core.py:322-449
  - validation_result:
    `python -m pytest -q tests/integration/melder/spellbook/test_spellbook_integration_core.py`
  IMPACT: The shared/local/threadsafe behavior is now proven directly instead of
    only being implied by broader suite coverage.
  NEXT: return those explicit proof tests for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T15:41:47Z
  TYPE: DECISION
  CLAIM: The next source-side owner fix is to move frame-posture
    bind/freeze/conflict logic out of `Aether` and onto `AethericFrame`
    itself. `AethericFrameConfiguration` is frame-owned state, so `Aether`
    should only resolve or create the frame while `AethericFrame` owns the
    actual posture lifecycle.
  EVIDENCE:
  - src/melder/aether/aether.py:794-893
  - src/melder/aether/aetheric_frame.py:96-102
  - src/melder/spellbook/spellbook.py:3251-3284
  - src/melder/aether/nexus/nexus_frame_manager.py:961-962
  IMPACT: The next code pass will relocate the logic and retarget callers,
    reducing one more misplaced ownership seam in the runtime.
  NEXT: add the bind/freeze/conflict method to `AethericFrame`, update
    `Spellbook` and `NexusFrameManager` to call it, and run a focused test ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the first owner-boundary repair slice under the reset epic.

