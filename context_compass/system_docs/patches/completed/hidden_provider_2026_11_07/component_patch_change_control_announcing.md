# component_patch_change_control_announcing

## Metadata
- Patch ID: hidden_provider_2026_11_07
- Component: DevOps Control Plane announcing and watching - `ChangeControlManager._default_dirty_marker`,
  `Spellbook._add_contracted_spell` (the two announcer sites) and `SpellSystemStates._extract_collection_frame_keys`
  (the watch index)
- Status: draft
- Owner: Mark (owner); written for melder_0 (synaptic_python_developer) by its design subagent
- Created: 2026-11-07T18:01:11Z
- Updated: 2026-11-07T18:15:30Z

## Component Purpose and Boundary
- Current boundary: a committed bind, notch or link marks the collection dependents of the frame keys of its staged
  binding keys (and contract keys); a contract grant marks the copy's frame key; consumers are watched under the
  frame key of their NORMAL-collection, OVERRIDE_REQUIRED, UNRESOLVED_INPUT and AMBIGUOUS_INPUT sockets.
- Target boundary: unchanged in shape; a framed spell also announces its type key (D1 = B), and a refused consumer
  also watches its hidden candidates' address frame keys.

## Before/After Behavior Summary
- Before (measured): a consumer compiled with `greeter: English` while English was not bound stays UNRESOLVED_INPUT
  when English is then bound under Greeter or the category "greeters" (the bind announces "greeter"/"greeters"; the
  consumer watches "english"), so its melds raise UnresolvedInputError while a twin compiled after refuses. English
  bound bare under a binding name already announces "english" (a bare spell's frame key is its own name).
  EVIDENCE: change_control_manager.py:840-876 (`frame_keys` at :855); spellbook.py:3355-3360;
  spell_system_states.py:1889-1928.
- After:
  1. `_default_dirty_marker`: before its single `mark_collection_dependents_dirty` call, resolve the staged spells
     (`self._resolve_spells_for_binding_keys(self._resolve_spellbook_for_staged(staged), staged.binding_keys)`, the
     helper the structural validator already uses) and union into `frame_keys` the type key of each spell whose
     `CompilerPhase3._hidden_type_key(spell)` is not None. One call, as today (the unit test
     test_default_dirty_marker_marks_collection_and_contract_dependents asserts exactly one).
  2. `_add_contracted_spell`: beside `frame_key = spell.key[0]`, take `type_key = CompilerPhase3._hidden_type_key(spell)`
     under the Book lock; after the lock, mark `{frame_key, type_key}` (minus None) in the one existing call.
  3. `_extract_collection_frame_keys`: for an UNRESOLVED_INPUT socket also add its `hidden_frame_keys` (a refused
     consumer is re-gated when a hidden candidate's address is announced - a notch of its index announces it, as the
     S1 C1/C2 cells show for the frame's own consumer; other departure paths per the UNKNOWN below).
  4. Effect (measured with the emulation, order_b_check.py): the consumer compiled before English was bound under
     Greeter or "greeters" is gated by the bind and refused at its next meld with HIDDEN_PROVIDER, as its late twin is
     refused at bind; a bare-named English behaves so already; a bare English still wakes the consumer into NORMAL.

## Interface Deltas
- Inputs: none new.
- Outputs: more keys in the existing mark calls (one more per framed spell staged or granted).
- Error semantics: none here; a gated consumer's next meld reruns phases 1-4 (existing gate) and Phase 4 decides.

## State and Lifecycle Deltas
- Owned state changes: none (the collection-dependent index holds more keys for refused consumers).
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: a running consumer that melded by override is refused at its next meld once its class is bound
  under a frame (D2, the AMBIGUOUS precedent when a second implementation arrives).
- Removed failure mode: the LIVE != FRESH split for HIDDEN_PROVIDER on bind, notch and contract grant.
- Changed failure mode: `list[Class]` consumers are also gated by such a bind (they recompile at their next meld and
  stay empty: cost only).

## Dependency and Ordering Constraints
1. The marker runs on commit after the structural validator (which already ran phases 1-4 for new spells), so the
   staged spells resolve from the Book's lookup maps; a departed spell resolves to nothing and only its frame key is
   announced (item 3 covers a refused consumer).
2. Lands with Phase 3's `_hidden_type_key` (one predicate).
3. Departures that announce nothing today (`cleanup_spell`, S1 D1; G4) stay on the watchers epic.

## Validation Expectations
- Added: unit tests - `_default_dirty_marker` unions the type key of a framed staged spell and adds nothing for a bare
  or bare-named one, still one call; `_add_contracted_spell` marks the type key of a framed copy;
  `_extract_collection_frame_keys` adds `hidden_frame_keys` for UNRESOLVED_INPUT only.
- Added (component): the S1 file (test_conduit_component_waiting_consumer_wakes_for_its_provider.py) rewritten so each
  framed cell asserts one answer, refused - the waiting consumer at its next meld, the late twin at its bind - and the
  frame's own consumer still wakes; a refused consumer re-gated by a notch of its hidden candidate's index to a
  version of another name melds as UNRESOLVED_INPUT again (a same-named version keeps it refused).
- Rewritten (measured, option B emulation: full suite the GIL off; the 7 affected files the GIL off and on, same
  delta): 9 tests in tests/unit/melder/spellbook/test_spellbook.py - test_add_contracted_spell_updates_maps_and_notifies_when_conjured,
  test_clearing_a_peers_copies_marks_the_keys_of_the_active_copies, test_contract_marks_run_with_the_book_lock_free,
  test_contracted_copy_changes_mark_nothing_before_conjure,
  test_every_change_of_an_active_contracted_copy_marks_the_consumers_of_its_key,
  test_removing_a_parked_version_keeps_the_active_copy_of_its_index,
  test_removing_a_version_the_book_holds_no_copy_of_raises_and_keeps_the_active_copy,
  test_removing_both_versions_of_an_index_in_either_order_leaves_no_copy[active_first] and [parked_first]. Their
  `DummySpell` stub has no `.spell` (the predicate reads it through `_spell_definition_key`): the stub gains `spell`,
  and assertions on a framed copy's marks gain its type key (e.g. `dirty_calls == [{"frame", "spellname"}]`).
- Stays green by design: tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py::
  test_default_dirty_marker_marks_collection_and_contract_dependents (no spellbook resolves for its staged mutation;
  one call).
- Evidence target 1: the full suite and the S1 matrix probe re-run, the GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: the exact set of departure paths that announce a frame key (they decide when `hidden_frame_keys` fires).
- DECISION_REQUEST: none (D1 = B decided 2026-11-07).

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: extra gating load in worlds with many framed binds of classes that `list[Class]` consumers name.
- Next entrypoint: `ChangeControlManager._default_dirty_marker`.
