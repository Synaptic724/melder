# Task: Resolve ordered book and per-spell disposal names at bind

## Metadata
- Task ID: TASK-2026-09-04-ordered-disposal-bind-and-spell
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
Each new Spell receives one ordered list composed from its own names and the book's names,
using the configured priority. Hash that same sequence and retain it directly on Spell.

## Ticket Contract
- ENTRY_GATE: Configuration task is verified, patch contract is read/mapped, and board routes here.
- EXECUTION_BOUNDARY: Spellbook bind/bind_inactive, Bind matching/fingerprinting, Spell metadata,
  existing conjure metadata expectation, and focused bind/Spell tests.
- DEPENDENCIES:
  `tickets/tasks/2026-09-04_disposal_priority_configuration_task.md`
  `tickets/tasks/2026-09-04_ordered_disposal_patch_contract_task.md`
- EXIT_GATE: Both priority values, independent binds, missing/duplicate names, list ownership,
  and ordered SHA behavior are verified through real supported binding paths.
- FAILURE_ESCALATION: Record an actual registration/identity conflict; do not silently change
  index semantics, remove disposal from SHA, or move matching to conjure.

## Scope Boundaries
- In scope: the three binding/Spell files plus necessary existing integrity expectations/tests.
- Out of scope: compiler rewrite, disposal mutation after creation, new matching families.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner selected list composition and requested a bounded binding task.

## Required Reading and Evidence
Use the component index's Spellbook Core and Binding Pipeline slices, then the graph index
for selected files. Read source completely before editing; ranges below are entry anchors.
- `src/melder/aether/spellbook/spellbook.py:4754-4970` (inactive bind)
- `src/melder/aether/spellbook/spellbook.py:5030-5304` (active bind)
- `src/melder/aether/spellbook/spellbook.py:6539-6561` (existing frozenset expectation)
- `src/melder/aether/spellbook/bind/bind.py:229-485` (forwarding/matching/Spell construction)
- `src/melder/aether/spellbook/bind/bind.py:489-633` (inspector and SHA)
- `src/melder/aether/spellbook/spell.py:287-603` (storage and cleanup)
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:67-132`
- `src/melder/aether/spellbook/spellbinder.py:641-661` (existing passthrough)
- `src/melder/aether/spellbook/spellbinder.py:826-870` (finalize forwarding)

## Composition Contract
- False/default: walk explicit Spell names, then configured book names.
- True: walk book names first in configuration order, then Spell names.
- Retain only names in the existing class profile; keep their first occurrence.
- Use list membership for the small result. No additional set or per-instance reflection.
- Empty or omitted Spell names leave book names applicable. Both empty yields an empty list.
- Matching and has_disposal_methods are established once at Spell creation.
- Spell stores the resolved list directly; no defensive copy or extra setter is required.

## Steps / Checklist
- [ ] Forward both inputs and priority through active and inactive bind paths.
- [ ] Remove/retire the first-bind candidate latch and its relevant init/cleanup/slot wiring.
- [ ] Compose/filter once in Bind; use that same result for SHA and Spell construction.
- [ ] Replace Spell's frozenset disposal storage with direct list storage.
- [ ] Retire the obsolete frozenset-specific conjure expectation without adding private-mutation guards.
- [ ] Preserve inspector parity using the same resolved ordered inputs.
- [ ] Update focused tests and docstrings; record evidence before consumer work starts.

## Deliverables
- Independent ordered disposal metadata for every bound Spell and consistent bind identity.
- Real bind tests for both priority modes and fluent SpellBinder passthrough.

## Files / Paths Impacted
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/bind/bind.py`
- `src/melder/aether/spellbook/spell.py`
- Existing tests under `tests/unit/melder/spellbook/bind/` and relevant Spell unit tests.
- `tests/component/melder/spellbook/test_spellbook_component_spellbook.py`
- `tests/component/melder/spellbook/test_spellbook_component_bind.py`
- Focused new order/hash regression test if existing modules cannot host it clearly.

## Validation
- Not run; ticket only. Discover a supported Python 3.14 executable before importing Melder.
- Book [flush, close], Spell [close, stop, flush]: False -> [close, stop, flush];
  True -> [flush, close, stop]. Test missing names and duplicates in either group.
- Bind two different Spells with distinct explicit names; the first must not configure the second.
- Verify class-profile behavior remains unchanged for non-class and inherited-only cases.
- Run a real bind in fresh supported processes with different PYTHONHASHSEED values using
  a stable source-defined class. Earlier discovery tested only a generic hash pattern.
- Test that reordering the final names affects SHA and changing only unmatched names does not.

## Risks / Rollback Notes
Fingerprints intentionally reflect execution order. Do not promise historical hash stability
for unordered inputs or add compatibility shims without a concrete requirement.

## Applicable Anti-Patterns
- [ ] No configuration override-only model or default-True assumption.
- [ ] No new getter/probe/locking scheme; no runtime policy mutation support.

## Done Checklist
- [ ] Binding changes and focused tests complete; source evidence and results recorded.
- [ ] Phase 2 dependencies updated; owner acceptance precedes final closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false at ticket creation
- ARTIFACT_PATHS: none yet; consume actual producer/code-description patch outputs first
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: accepted program closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: source selection, ordered matching, Spell ownership, SHA
- IF_UNKNOWN: none

## Noting Behavior
Record tactical findings with evidence and one NEXT action; keep settled policy unchanged.

## Notes
- DATETIME: 2026-09-04T21:17:27Z
  TYPE: PLAN
  CLAIM: Current first-bind latching and frozenset storage are the producer corrections.
  EVIDENCE:
  - `src/melder/aether/spellbook/spellbook.py:5136-5159`
  - `src/melder/aether/spellbook/bind/bind.py:396-475`
  - `src/melder/aether/spellbook/spell.py:434-435`
  IMPACT: Downstream tasks can consume one resolved list and its established presence flag.
  NEXT: After configuration verification, read the full binding implementations and patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
No implementation yet. The policy is combined lists, False default, first occurrence wins.
Both active/inactive paths matter. Final-list mutations after creation are not supported work.
Next: `tickets/tasks/2026-09-04_ordered_disposal_compiler_propagation_task.md`.
