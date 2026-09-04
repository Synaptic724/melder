# Task: Add the disposal-priority configuration and fluent setter

## Metadata
- Task ID: TASK-2026-09-04-disposal-priority-configuration
- Story: STORY-2026-09-04-ordered-disposal-binding
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: review
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T22:39:54Z

## Objective
Expose `enforce_priority_disposal_methods` with default False and the fluent setter,
using the existing configuration lifecycle and making the value available before bind.

## Ticket Contract
- ENTRY_GATE: The owner selected this small slice; route here after its configuration-only
  patch gate is satisfied and record implementation-to-validation mapping before source edits.
- EXECUTION_BOUNDARY: SpellbookConfiguration schema/defaults/fluent/reload accounting and
  directly relevant tests. Product files remain untouched until this task is executed.
- DEPENDENCIES: `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`.
- EXIT_GATE: Defaults, explicit booleans, setup/freeze, and defaults-free configuration
  behave correctly; tests and current source documentation support the result.
- FAILURE_ESCALATION: Record a real lifecycle conflict; do not add scattered Bind/runtime
  fallbacks to compensate for undefined configuration state.

## Scope Boundaries
- In scope: the configuration class and focused configuration tests.
- Out of scope: binding composition, compiled disposal, Nexus API additions, publication.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Configuration-only source/tests are implemented. All 115 focused
  configuration/reload/adoption tests pass; source docstrings and patch contracts are current.

## Required Reading and Evidence
Read the discovery Configuration Change Map, then the full source file before editing.
Navigate via `src_components_index.md`, Component: Spellbook Configuration and System State.
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:114-160` (schema/init)
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:202-256` (set/clear)
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:398-481` (validation)
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:505-652` (get/default/reload)
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1049-1191` (fluent)
- `src/melder/aether/spellbook/spellbook.py:5423-5474` (supplied config adopted without validate)
- `tests/unit/melder/spellbook/configuration/test_configuration.py:408-434` (order/set-once)
- `tests/unit/melder/spellbook/configuration/test_configuration.py:501-514` (partial config)
Also read the applicable tests architecture/components before changing suite code.

## Steps / Checklist
- [x] Register the new bool in available_properties; default is False.
- [x] Handle ordinary defaults and `_OPTIONAL_PROPERTY_DEFAULTS` consistently.
- [x] Ensure a supplied configuration exposes the default before its first bind, even
      without `.with_defaults()` or validation. Establish this through configuration setup.
- [x] Preserve explicit True when defaults load. A seeded set-once value must not prevent opt-in.
- [x] Cover clear/reassembly and reload accounting; distinguish recorded values from defaults.
- [x] Add `with_enforce_priority_disposal_methods(enabled=True)` as a thin fluent wrapper.
- [x] Preserve disposal-name list order, existing missing-name policy, and configuration scope.
- [x] Update touched docstrings, run focused tests, and record results before switching tasks.

## Deliverables
- One configuration-owned flag/default and fluent setter.
- Tests covering construction paths, wrong bool types, explicit True/False, and frozen lifecycle.

## Files / Paths Impacted
- `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
- `tests/unit/melder/spellbook/configuration/test_configuration.py`
- `tests/component/melder/spellbook/test_spellbook_component_configuration_core.py`
- `tests/unit/melder/aether/test_configuration_reload_lanes.py` only for owner-side default accounting
- This task and relevant patch/component docs; generated outputs belong to the assets task.

## Validation
- Passed: 115 focused tests on Windows / Python 3.14.0 free-threaded, pytest 9.1.1.
- Runner: `.venv_new/Scripts/python.exe`; the bare 3.14t interpreter has no pytest.
- Three modified test files passed 105 cases; the existing real Spellbook configuration
  adoption/shared-config test file added 10 passing smoke cases without source/test edits there.
- Full suite, cross-platform matrix, full crystal round trips, and build-asset checks: Not run.
- Canonical document promotion and derived-asset regeneration remain with the planned docs/assets task.
- Prove default False before bind, True surviving defaults, valid explicit False,
  invalid types rejected by the documented configuration boundary, and setup/freeze behavior.
- The transport task owns complete crystal/checkpoint/Nexus verification; coordinate shared tests.

## Risks / Rollback Notes
Optional-default backfilling at validation alone is too late for pre-validation binding.
Eager initialization affects iteration and reload backfilled reporting: test both intentionally.
Do not redesign generic configuration or mirror the bool on Nexus/Crystallizer roots.

## Applicable Anti-Patterns
- [ ] No post-creation policy mutation API, new defensive private-field guards, or extra snapshots.
- [ ] No seeded idempotent default that makes the new setter unusable.

## Done Checklist
- [x] Source and tests implemented; source docstrings and scoped patch contracts are accurate.
- [x] Evidence and exact commands/results recorded; no guessed coverage numbers.
- [ ] Next dependent tasks and boards updated; owner accepts closure when appropriate.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch_index.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_spellbook_configuration.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_spellbook_configuration_index.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_spellbook_configuration.md`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_spellbook_configuration_index.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted final patch closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: priority configuration, defaults, fluent API, reload reporting
- IF_UNKNOWN: none

## Noting Behavior
Record each configuration-lifecycle finding and the next single action before another tranche.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: The new setting belongs to SpellbookConfiguration and its existing fluent API.
  EVIDENCE:
  - `context_compass/tickets/tasks/2026-09-02_ordered_spell_disposal_contract_discovery_task.md:195-320`
  IMPACT: Default availability is solved at configuration setup, not at every disposal call.
  NEXT: Consume the patch contract and inspect the complete configuration implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:24:50Z
  TYPE: PLAN
  CLAIM: Begin the approved configuration-only slice. Required architecture, component, and
    code-description patches have been read in order. They map to one source file and three
    focused test files. The existing .venv_new interpreter is Python 3.14.0 free-threaded
    (GIL disabled), with pytest 9.1.1; the bare 3.14t install has no pytest.
  EVIDENCE:
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/architecture_patch.md:18-47`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/component_patch_spellbook_configuration.md:7-45`
  - `system_docs/patches/active/ordered_disposal_priority_2026_09_04/code_description_patch_spellbook_configuration.md:7-38`
  - `.venv_new/pyvenv.cfg:1-8`
  IMPACT: Mapping: init/clear/schema/defaults -> raw/cleared/defaults-free tests; fluent setter
    -> True/False/self-return/frozen/cleaned tests; early-default reload accounting ->
    recorded/absent/preconfigured cases. Generic carrier/runtime source stays unchanged.
    Type validation remains at validate/freeze, as in current source.
  NEXT: Run the three-file baseline, then add focused regression tests and the small source edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:25:36Z
  TYPE: MEASURE
  CLAIM: Baseline passed: 84 tests across configuration unit, configuration core component,
    and configuration reload files, using .venv_new's Python 3.14.0 free-threaded interpreter.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/unit/melder/aether/test_configuration_reload_lanes.py -q -p no:cacheprovider
  - Result: 84 passed in 0.31s, exit 0.
  IMPACT: The selected existing test boundary is green before the new flag and assertions.
  NEXT: Add focused priority/default/reload regressions, then implement the configuration delta.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:29:38Z
  TYPE: MEASURE
  CLAIM: Added 21 parametrized priority cases across the three focused files. Before source
    implementation, all 21 fail on the missing property/setter or absent backfill evidence;
    84 existing cases were deselected by the priority filter.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/unit/melder/aether/test_configuration_reload_lanes.py -q -p no:cacheprovider -k priority --tb=line
  - Result: 21 failed, 84 deselected in 0.34s, exit 1 (expected red phase).
  IMPACT: The new cases require the intended default, fluent, validation, freeze, and reload
    behavior. Two existing partial-key expectations were adjusted for the eager default.
  NEXT: Implement the source delta in SpellbookConfiguration, then run all three files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:29:38Z
  TYPE: FACT
  CLAIM: Implemented the configuration delta: eager False at init/clear, registered bool,
    normal/optional defaults, a thin fluent setter, and omitted-early-default reload accounting.
    Existing type-validation timing, name-list storage, freeze guards, and consumers remain intact.
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py`
  IMPACT: Only this configuration source file and three focused test files changed in product
    scope. This exposes the policy; it does not yet apply ordering to bound Spells.
  NEXT: Run all three focused test files and inspect the source/test diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:31:36Z
  TYPE: MEASURE
  CLAIM: Focused validation passed after implementation: 105 tests in the three selected
    files (84 existing plus 21 new priority cases), using Python 3.14.0 free-threaded.
    Product-scope git diff --check passed; Git only emitted its normal LF/CRLF conversion warnings.
  EVIDENCE:
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/unit/melder/aether/test_configuration_reload_lanes.py -q -p no:cacheprovider
  - Result: 105 passed in 0.35s, exit 0.
  IMPACT: The configuration slice passes its behavioral tests. This is not full-suite,
    platform-matrix, compiler-cache, or restored-world ordering evidence.
  NEXT: Review the exact diff, update the relevant component description, and hand off this slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:39:54Z
  TYPE: MEASURE
  CLAIM: Final configuration boundary passed 115 tests in 0.42s after source/docstring review.
    All three patch indexes pass --check. Product-scope diff checking reports no whitespace errors.
    No commits, pushes, consumer edits, or source/repository asset regeneration occurred.
  EVIDENCE:
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:113-165`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:245-263`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:596-674`
  - `src/melder/aether/spellbook/configuration/spellbook_configuration.py:1128-1157`
  - Command: .venv_new/Scripts/python.exe -m pytest tests/unit/melder/spellbook/configuration/test_configuration.py tests/component/melder/spellbook/test_spellbook_component_configuration_core.py tests/component/melder/spellbook/test_spellbook_component_configuration.py tests/unit/melder/aether/test_configuration_reload_lanes.py -q -p no:cacheprovider
  - Result: 115 passed in 0.42s, exit 0.
  IMPACT: The setting exists before validation, remains selectable during assembly, and is
    correctly accounted for on reload. It is staged policy only: actual ordered binding and
    disposal remain the next tasks. Patch contracts hold the current delta until canonical
    promotion under the existing documentation/assets phase.
  NEXT: Owner review, then prepare the Bind/Spell contract and execute its separate task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implemented and in review: one configuration source file plus three test files. The new
enforce_priority_disposal_methods flag defaults False before validation and after clearing;
the fluent setter opts in with no argument, and existing validation/freeze rules apply.
Recorded True/False is preserved; an absent eager False default is reported as backfilled.
115 focused tests passed with .venv_new/Scripts/python.exe. Bind and runtime consumers are
unchanged, so the flag does not yet reorder actual disposal. No commit or push was made.
Canonical docs/graph and derived assets remain scheduled for their existing later task;
the source docstrings and active patch contracts document this slice now.
Next dependents: ordered_disposal_bind_and_spell and disposal_configuration_roundtrip tasks.
