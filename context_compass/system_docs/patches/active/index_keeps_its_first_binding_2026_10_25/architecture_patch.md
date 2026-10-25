# architecture_patch

## Metadata
- Patch ID: index_keeps_its_first_binding_2026_10_25
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T09:13:34Z
- Updated: 2026-10-25T09:13:34Z
- Ticket: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (EPIC-2026-10-17-correctness_defects; the
  owner's go and his call 1, chat 2026-10-25)

## Patch Scope and Non-Goals
- Objective: a SpellIndex keeps the binding its first version was bound with - the kind of its spellframe (none, a
  string category, a Protocol) and the address that gives (frame key and binding key, case-insensitive) - and admits
  only a version bound the same way. `bind_inactive` and `add_to_spell_index` refuse any other version before
  anything is registered or moved, so a renamed class or a new binding name is a new spell. A notch never moves an
  index's address: it moves the address's frame claim from the outgoing version to the incoming one in one atomic
  step, before the park, and refuses an address another spell holds - another index's active version in the Book (a
  version split off with `remove_from_spell_index` while its source still serves the address) or another Book's
  spell - with nothing moved. A record made before cannot promise one binding per index, so RecordVersion goes to
  5.0.0 and every older major is refused; the creation cache goes to generation 24. A graft-merge member bound
  another way than the merge target is a per-member shortfall. (R1-R8 of the story.)
- Non-goals: no replay rule for older records and no `bind_inactive(spell_index=None)` (the owner's call 1); no
  change to how a spell_id is computed or looked up; the meld naming rules (gaps 2 and 3 of the meld-identity map);
  the stuck class-annotated consumer (EPIC-2026-10-25-dependency_watchers_listen_for_names); S3 (a changed binding
  revalidates); the seam's park-before-check order for a target that is not parked
  (TASK-2026-10-16-notch_seam_checks_incoming_before_parking, backlog) - the claim moves first and is put back when
  the park or the promotion raises, so that path ends as it does today; the restore engine and the graft's fresh
  lane beyond the version gate (a record of major 5 holds one binding per index).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Binding Pipeline - SpellIndex (`src/melder/aether/spellbook/bind/spell_index.py`) | modify | keeps its binding (`binding_signature`); `signature_of`, `for_binding`, `check_admits` | none |
| Binding Pipeline - Bind (`src/melder/aether/spellbook/bind/bind.py`) | modify | builds every index with its first version's binding (`SpellIndex.for_binding`) | SpellIndex |
| AethericFrame Services (`lookup_container.py`, `aetheric_frame.py`) | modify | `LookupContainer.repoint` and `AethericFrame.repoint_lookup`: the claim's compare-and-set | none |
| Spellbook Core (`src/melder/aether/spellbook/spellbook.py`) | modify | `bind_inactive` checks before it registers; `_apply_add_to_index` checks; `_apply_notch` moves the claim first and refuses a taken address; `_apply_remove_from_index` mints with the version's binding; the dead branch of `_revert_refused_notch` goes | SpellIndex, AethericFrame Services |
| Spellbook Core - CachingSystem (`src/melder/utilities/caching_system/caching_system.py`) | modify | generation 24, "spell_index_keeps_its_binding" | none |
| Crystallizer - RecordVersion (`src/melder/crystallizer/persistence/record_version.py`) | modify | 5.0.0 and the oldest readable major (5) | none |
| Crystallizer - GraftRunner (`src/melder/crystallizer/crystal_loader_system/graft_runner.py`) | modify | the merge lane files a member bound another way as a shortfall | SpellIndex |
| Conduit Runtime (`src/melder/aether/conduit/conduit.py`) | docstring | `bind_inactive`, `notch_spell` and `add_to_spell_index` state the rule and the refusals; their examples stage an edited class under its index's binding | Spellbook Core |

code_description_patch_spellbook_core is required: the notch's claim move is a compare-and-set that decides a
refusal, `bind_inactive`'s checks move ahead of registration, and their order and error semantics are the contract.

## Interface and Boundary Deltas
- New public SpellIndex surface: `binding_signature` (read-only: `(kind, frame_key, binding_key)`, or None for an index
  built without a binding), `SpellIndex.signature_of(*, spellframe, spell_name, binding_name)`,
  `SpellIndex.for_binding(initial_id, *, spellframe, spell_name, binding_name)` and `check_admits(spell, *, verb)`.
  The constructor gains keyword-only `binding_signature=None` and `binding_text=None`, so `SpellIndex(initial_id)`
  still builds an index, one without a binding. No new verb on Conduit or Spellbook.
- New internal: `LookupContainer.repoint(key, spell_id, *, from_spell_id) -> Optional[str]` and
  `AethericFrame.repoint_lookup(key, spell_id, *, from_spell_id) -> Optional[str]`.
- Errors (Breaking): `bind_inactive` raises ValueError for a version bound another way than its index (it staged the
  version), and RuntimeError "... is not owned by this spellbook ..." for another Book's index before anything is
  registered (it raised after registering the version, which stayed parked in the Book, so a retry was refused as a
  spell_id collision); `add_to_spell_index` raises ValueError for such a version (it moved it); `notch_spell` raises
  RuntimeError "... is held by spell_id '<holder>' ..." for an address another spell holds (it took the address, or,
  for a version never compiled, refused it as a failed structural check); every reader of a record of major 4 or older
  - a cached checkpoint, a formation, an index graft - raises ValueError naming the remedy (record the world again),
  where it read it.
- Records: RecordVersion 5.0.0; no shape change. The major fences records that could hold an index under two bindings.
- Cache: generation 24; a bundle written before is cold once (the owner's call 1).

## Cross-Component Invariants
- Every version of a SpellIndex is bound the way its first version was: the same kind of spellframe and the same
  address. An index's address never moves, and every caller that names the address follows a notch.
- The kind is part of the binding: a string category spelled like a bare class's name, or the reverse, is another
  binding at the same address. Two Protocols of one name give one address and one binding, as the frame claim and
  `Spell._key` already treat them.
- One active spell per address per frame holds through a notch: the claim moves from the outgoing version to the
  incoming one by compare-and-set and never overwrites another spell's claim.
- A refusal leaves nothing behind: `bind_inactive` checks before it registers, `add_to_spell_index` before it moves,
  and the notch before it parks.
- The binding is immutable on the index, read without a lock, and kept after cleanup, like the index's id.
- No new lock and no new lock-order edge: the claim move is one call into the frame lookup's leaf lock under the Book
  lock, where the notch's unconditional update ran.

## Migration and Rollout Order
1. These patch docs, linked from the story; the mapping note (patch section -> code -> test).
2. SpellIndex and Bind; LookupContainer and AethericFrame; Spellbook Core; RecordVersion and the cache generation;
   GraftRunner; the Conduit docstrings.
3. The red tests green, the GIL off and on; then the suites, rewriting the tests that stage versions under another
   binding (169 in 35 files on 0.2.8267), the record-version tests, the UX examples that stage renamed classes and the
   README's stage -> notch -> meld example.
4. System documents (src_architecture, src_components, tests_architecture, tests_components) with their indexes, the
   graph's descriptors and assembly, the user docs, the running release note (Breaking), the next free notch.
5. Closure; the rebuild last.

## Rollback Strategy
- Rollback trigger: the owner redirects, or a suite cannot be made green without weakening a refusal.
- Rollback steps: revert the source edits, the record and cache versions, the tests and the docs. Nothing persisted
  needs migrating back; SpellIndex's new surface is additive.
- Post-rollback verification: the suites green on the reverted tree, the GIL off and on.

## Validation Expectations and Evidence Plan
- The three red files green: tests/component/melder/spellbook/test_spellbook_component_index_keeps_its_first_binding.py,
  tests/unit/melder/aether/test_lookup_container_repoint.py and
  tests/unit/melder/spellbook/bind/test_spell_index_binding_signature.py.
- New: a RecordVersion unit test (5.0.0; a record of major 4 and an unstamped one refused with the remedy; a newer
  major refused as before) and a graft-merge test (a member bound another way is a shortfall; the others park).
- The unit, component and integration suites, the GIL off and on; the UX examples that stage versions.
- Evidence: the runs of the lane's artifact folder, cited from the story's Notes.

## Ticket Coverage Map
- Epic: EPIC-2026-10-17-correctness_defects
- Story: STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (R1-R8)
- Tasks: none (a story-level lane)

## Unknowns and Decision Requests
- UNKNOWN: none blocking. Which UX examples and agent documents stage renamed classes is counted at the suite run.
- DECISION_REQUEST: none. The owner's go, the rename rule and calls 1 and 2 are recorded (the story's DECISION notes
  of 2026-10-25T08:40:04Z and 08:49:58Z).

## Context / Handoff Summary
- What changed: the S2 patch, drafted from the code on 0.2.8270 (the working tree).
- What remains: steps 2-5 of Migration and Rollout Order.
- Next entrypoint: component_patch_spellbook_core.md and code_description_patch_spellbook_core.md.
