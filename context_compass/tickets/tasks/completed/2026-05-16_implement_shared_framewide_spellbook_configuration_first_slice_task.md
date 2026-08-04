# Task: Implement Shared Framewide Spellbook Configuration First Slice
- Completed: 2026-05-16T15:47:45Z
- Summary: Closed as an early mechanics slice absorbed into the completed frame-posture migration lane.


## Metadata
- Task ID: TASK-2026-05-16-implement-shared-framewide-spellbook-configuration-first-slice
- Story: STORY-2026-05-16-implement-explicit-frame-configuration-and-local-config-split
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p0
- Created: 2026-05-16T11:04:03Z
- Updated: 2026-05-16T15:47:45Z

## Objective
Land the first bounded runtime slice for the new config model:
- add `shared_framewide_spellbook_configuration` to permanent frame posture
- keep the simple `Spellbook -> bind -> conjure -> meld` default path
- make shared rich `SpellbookConfiguration` ownership explicit and frame-owned
  instead of hidden Aether adoption

## Ticket Contract
- ENTRY_GATE: the frame/local investigation lane has already identified the
  current ownership/race surfaces, and the user explicitly directed starting
  with the new frame-wide rich-config sharing boolean.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame_configuration.py`
  - `src/melder/spellbook/configuration/spellbook_configuration.py`
  - `src/melder/aether/aetheric_frame.py`
  - `src/melder/aether/aether.py`
  - `src/melder/spellbook/spellbook.py`
  - `src/melder/spellbook/spellbook_creation_system.py`
  - focused tests for frame posture and Spellbook config-adoption behavior
- DEPENDENCIES:
  - `codex/context_compass/tickets/tasks/2026-05-16_inventory_frame_local_configuration_consumers_and_race_window_task.md`
  - `codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/architecture_patch.md`
  - `codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_spellbook_configuration.md`
  - `codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_aetheric_frame_configuration.md`
  - `codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_spellbook_bootstrap.md`
  - `codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/code_description_patch_spellbook_bootstrap.md`
- EXIT_GATE: the new boolean exists, first conjure can bind a permanent frame
  posture with default sharing semantics, Spellbook init respects the posture
  when deciding whether to adopt rich config from Aether, and shared rich config
  cleanup ownership is transferred to the frame instead of borrowed Spellbooks.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` only if the first slice forces a
  larger immediate migration of all frame-global fields out of
  `SpellbookConfiguration`.

## Scope Boundaries
- In scope:
  - new frame-posture boolean
  - explicit frame-owned rich config sharing semantics
  - Spellbook init/conjure adoption behavior
  - shared-config cleanup ownership
  - focused tests for this first slice
- Out of scope:
  - full frame-global field migration
  - explicit `Spellbook.configure_aetheric_frame(...)` API
  - bounded wait/timeout state machine
  - broader conduit/Nexus consumer reroutes

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the first bounded mechanics slice is implemented and the
  focused compile plus unit/component/integration validation ring is green.

## Steps / Checklist
- [ ] Add `shared_framewide_spellbook_configuration` to `AethericFrameConfiguration`.
- [ ] Add the matching authoring/default path on `SpellbookConfiguration`.
- [ ] Make `Spellbook` only adopt frame-bound rich config when the canonical
      frame posture says to share it.
- [ ] Make shared rich config frame-owned for cleanup/lifecycle purposes.
- [ ] Keep the normal default conjure path simple and automatic.
- [ ] Add focused tests for the new posture and adoption behavior.
- [x] Run focused validation.

## Deliverables
- explicit frame-posture bool for rich-config sharing
- frame-owned cleanup semantics for shared rich config
- focused passing tests

## Files / Paths Impacted
- src/melder/aether/aetheric_frame_configuration.py
- src/melder/spellbook/configuration/spellbook_configuration.py
- src/melder/aether/aetheric_frame.py
- src/melder/aether/aether.py
- src/melder/spellbook/spellbook.py
- src/melder/spellbook/spellbook_creation_system.py
- tests/unit/melder/aether/test_aetheric_frame_configuration.py
- tests/component/melder/spellbook/test_spellbook_component_configuration.py
- tests/integration/melder/spellbook/test_spellbook_integration_core.py

## Validation
- Executed:
  - `python -m py_compile src/melder/aether/aetheric_frame_configuration.py src/melder/spellbook/configuration/spellbook_configuration.py src/melder/aether/aetheric_frame.py src/melder/spellbook/spellbook.py src/melder/spellbook/spellbook_creation_system.py src/melder/utilities/interfaces/iconfiguration.py tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/integration/melder/spellbook/test_spellbook_integration_core.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/integration/melder/spellbook/test_spellbook_integration_core.py`
  - `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_nexus_frame_configuration.py`
- Result:
  - focused compile passed
  - focused runtime/config validation ring passed (`116 passed`)
  - adjacent Aether/Nexus frame-config ring passed (`160 passed`)

## Risks / Rollback Notes
- Risk: shared rich config remains Spellbook-owned and gets cleaned by the
  first borrowing Spellbook.
  Rollback: transfer ownership to the frame and make borrowing Spellbooks stop
  cleaning adopted frame-owned config.

## Applicable Anti-Patterns
- [ ] No hidden reintroduction of unconditional rich-config sharing.
- [ ] No implementation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No partial ownership fix that leaves shared config cleanup ambiguous.

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
  - system_docs/patches/active/shared_framewide_spellbook_configuration_policy/architecture_patch.md
  - system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_spellbook_configuration.md
  - system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_aetheric_frame_configuration.md
  - system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_spellbook_bootstrap.md
  - system_docs/patches/active/shared_framewide_spellbook_configuration_policy/code_description_patch_spellbook_bootstrap.md
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: task closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-16T11:04:03Z
  TYPE: PLAN
  CLAIM: The first bounded implementation slice should not try to complete the
    whole frame/local split. The smallest high-signal cut is to make rich
    Spellbook-config sharing explicit and posture-owned through one permanent
    frame boolean, while preserving the simple default conjure path.
  EVIDENCE:
  - user_instruction: "what if we have another configuration item in the aetheric_frame_configuration"
  - user_instruction: "shared_framewide_spellbook_configuration"
  - user_instruction: "when conjure is used it will automatically create a default configuration"
  IMPACT: We can land a useful ownership improvement now without forcing the
    whole frame-global field migration in the same patch.
  NEXT: create the patch docs, wire the boolean through the frame/config path,
    and fix shared-config cleanup ownership in the same pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-16T11:04:03Z
  TYPE: DECISION
  CLAIM: Shared rich `SpellbookConfiguration` is now explicitly dual-gated. The frame posture bool (`shared_framewide_spellbook_configuration`) enables the feature, but shared rich config is only actually used when the user also intentionally provides a `SpellbookConfiguration` object for that shared framewide role. Spellbook init still runs normally; it only adopts frame-shared rich config when both conditions are true: the frame posture says shared mode is enabled, and the frame already has an explicit shared rich config object. Otherwise each Spellbook keeps or creates its own local rich config.
  EVIDENCE:
  - user_instruction: "if the aetheric_frame has that bool turned on, it then returns the configuration from the shared system otherwise conjure builds it by default or the user makes it"
  - user_instruction: "if the user enables that feature and feeds in a SpellbookConfiguration object then thats the only time we use that"
  IMPACT: The first slice must not silently promote a local Spellbook config into shared frame state just because the bool is true. Shared rich config is opt-in and explicit; the bool alone only permits the path.
  NEXT: patch init/conjure ownership rules so frame posture lock-in and shared rich-config adoption follow this dual-gate contract exactly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T11:04:03Z
  TYPE: PLAN
  CLAIM: Patch-artifact consumption for the first slice is complete and mapped.
    `architecture_patch.md` narrows the slice to posture-owned optional rich
    config sharing. `component_patch_spellbook_configuration.md` adds the new
    authoring/default path. `component_patch_aetheric_frame_configuration.md`
    carries the permanent frame-posture bool. `component_patch_spellbook_bootstrap.md`
    and `code_description_patch_spellbook_bootstrap.md` define the ownership
    and control-flow changes in Spellbook init/conjure/cleanup. Focused
    validation stays on frame-posture unit tests plus Spellbook
    component/integration adoption behavior.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/architecture_patch.md:1-56
  - codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_spellbook_configuration.md:1-28
  - codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_aetheric_frame_configuration.md:1-26
  - codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/component_patch_spellbook_bootstrap.md:1-32
  - codex/context_compass/system_docs/patches/active/shared_framewide_spellbook_configuration_policy/code_description_patch_spellbook_bootstrap.md:1-23
  IMPACT: The patch-framework gate is satisfied for this first implementation
    slice, so runtime edits can stay inside the documented boundaries.
  NEXT: update the patch docs to the final dual-gate/default-false semantics,
    then patch runtime files and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-16T12:22:59Z
  TYPE: MEASURE
  CLAIM: The first bounded mechanics slice is landed and green. `AethericFrameConfiguration`
    now carries `shared_framewide_spellbook_configuration` with default `False`,
    `SpellbookConfiguration` can author that posture through defaults and a
    fluent setter, `Spellbook` only adopts frame-owned rich config when the
    canonical frame posture permits it, shared rich config is no longer cleaned
    by borrowing Spellbooks, and conjure now binds frame posture before any
    optional shared rich-config bind so a conflicting posture cannot leave a
    stray rich config in Aether.
  EVIDENCE:
  - src/melder/aether/aetheric_frame_configuration.py:13-261
  - src/melder/spellbook/configuration/spellbook_configuration.py:13-820
  - src/melder/aether/aetheric_frame.py:88-126
  - src/melder/spellbook/spellbook.py:99-103
  - src/melder/spellbook/spellbook.py:188-193
  - src/melder/spellbook/spellbook.py:2889-2945
  - src/melder/spellbook/spellbook.py:2950-2977
  - src/melder/spellbook/spellbook.py:3146-3248
  - src/melder/spellbook/spellbook_creation_system.py:222-225
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:29-198
  - tests/unit/melder/spellbook/configuration/test_configuration.py:8-222
  - tests/component/melder/spellbook/test_spellbook_component_configuration.py:31-357
  - tests/integration/melder/spellbook/test_spellbook_integration_core.py:233-334
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/integration/melder/spellbook/test_spellbook_integration_core.py` -> `116 passed`
  - validation_result:
    `python -m pytest -q -p no:cacheprovider tests/unit/melder/aether/test_aether.py tests/unit/melder/aether/test_nexus_frame_configuration.py` -> `160 passed`
  IMPACT: The runtime now has an explicit first-class mechanic for optional
    frame-owned rich Spellbook config without forcing that mode on default
    users, and the cleanup/ordering bug in the old hidden-sharing path is gone.
  NEXT: return this first slice for review, then move the actual frame-global
    posture attributes over in the next refactor cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first bounded implementation slice for the explicit
frame/local config refactor.

