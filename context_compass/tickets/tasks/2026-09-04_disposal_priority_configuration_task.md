# Task: Add the disposal-priority configuration and fluent setter

## Metadata
- Task ID: TASK-2026-09-04-disposal-priority-configuration
- Story: STORY-2026-09-04-ordered-disposal-binding
- Story Ticket: `tickets/stories/2026-09-04_ordered_disposal_binding_story.md`
- Epic Ticket: `tickets/epics/2026-09-02_ordered_live_spell_disposal_epic.md`
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-04T21:17:27Z
- Updated: 2026-09-04T21:17:27Z

## Objective
Expose `enforce_priority_disposal_methods` with default False and the fluent setter,
using the existing configuration lifecycle and making the value available before bind.

## Ticket Contract
- ENTRY_GATE: Route here after the patch-contract task; read its configuration/binding
  contract and record implementation-to-validation mapping before source edits.
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
- from_state: draft
- to_state: ready
- transition_reason: Owner selected the flag name/default and requested implementation tasks.

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
- [ ] Register the new bool in available_properties; default is False.
- [ ] Handle ordinary defaults and `_OPTIONAL_PROPERTY_DEFAULTS` consistently.
- [ ] Ensure a supplied configuration exposes the default before its first bind, even
      without `.with_defaults()` or validation. Establish this through configuration setup.
- [ ] Preserve explicit True when defaults load. A seeded set-once value must not prevent opt-in.
- [ ] Cover clear/reassembly and reload accounting; distinguish recorded values from defaults.
- [ ] Add `with_enforce_priority_disposal_methods(enabled=True)` as a thin fluent wrapper.
- [ ] Preserve disposal-name list order, existing missing-name policy, and configuration scope.
- [ ] Update touched docstrings, run focused tests, and record results before switching tasks.

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
- Not run; ticket only. Use a verified Python 3.14 interpreter, not the default 3.13.
- Run the focused configuration unit/component tests after changes.
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
- [ ] Source and tests implemented; documentation is accurate.
- [ ] Evidence and exact commands/results recorded; no guessed coverage numbers.
- [ ] Next dependent tasks and boards updated; owner accepts closure when appropriate.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false at ticket creation
- ARTIFACT_PATHS: none yet; link the actual configuration/binding patch before implementation
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

## Context / Handoff Summary
Default False means Spell methods first; True means configured book methods first. This task
adds the setting only. Binding and downstream consumers are separate. No code has been changed.
Next dependents: ordered_disposal_bind_and_spell and disposal_configuration_roundtrip tasks.

