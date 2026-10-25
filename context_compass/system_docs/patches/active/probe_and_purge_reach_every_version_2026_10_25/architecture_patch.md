# architecture_patch

## Metadata
- Patch ID: probe_and_purge_reach_every_version_2026_10_25
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T03:03:37Z
- Updated: 2026-10-25T03:03:37Z
- Ticket: STORY-2026-10-25-probe_and_purge_reach_every_version (standalone; the owner's go, chat 2026-10-25)

## Patch Scope and Non-Goals
- Objective: `Conduit.purge(spell_id=...)`, `Conduit.has_live_creation(spell=<spell_id>)`,
  `Conduit.describe_live_creation_status(spell=<spell_id>)` and `SpellSpace.purge(spell_id=...)` - on a root, a
  lesser and a SpellSpace's door - resolve a spell_id to the exact version the conduit can see: its Book's own
  version, active or parked, or a borrowed copy, active or parked. They then act on that version's entries in the
  store the door authorizes, exactly as for an active version (R1-R4 of the story). A `unique` version with no
  owner store is refused by purge with a RuntimeError naming it (R6), where an AttributeError escaped.
- Non-goals: every door that builds or hands out an object stays active-only (`meld`, `meld_existing_spell`,
  `managed_spell_meld`, `SpellSpace.meld`, the Rift rooms' melds; R5). Every selector other than a spell_id - a
  name, a class, spellframe and binding name, an instance - keeps meld's discovery, the index's active version
  (R2; the instance limit F14 and the Spell-object selector F22 stay as they are). No new keyword
  (`has_live_creation` takes a spell_id in `spell=` today). No change to the creation stores (`creations.py`), to
  store selection or to purge authority (R3). The Rift rooms' probes are unchanged code (F18).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Meld Resolution Runtime - Meld base (`src/melder/aether/conduit/meld/meld.py`) | modify | `_resolve_visible_version_by_id` and `_resolve_probe_target`; `_resolve_purge_spell` resolves a spell_id through them | Spellbook Core's lookup |
| Meld Resolution Runtime - ConduitMeld (`conduit_meld.py`) | modify | the probe's discovery goes through `_resolve_probe_target`; `_get_purge_creations` refuses a `unique` version with no owner store | Meld base |
| Meld Resolution Runtime - SpellSpaceMeld (`spellspace_meld.py`) | modify | the probe's discovery goes through `_resolve_probe_target` | Meld base |
| Spellbook Core (`src/melder/aether/spellbook/spellbook.py`) | modify | `_find_visible_version(spell_id)`: one read of the Book's four id maps under the Book lock | none |
| Conduit Runtime (`conduit.py`) and SpellSpace (`spell_space.py`) | docstring | the purge and probe docstrings say what a spell_id reaches | the doors |

code_description_patch_meld_resolution_runtime is required: the change adds a Book-lock read on a cold path that
races a notch's map moves, and its lock order and error semantics are the contract.

## Interface and Boundary Deltas
- No signature changes and no new public symbol.
- Behaviour (visible): a spell_id of a parked version, or of a borrowed copy the lender's notch parked, is answered
  by purge and the probes where they raised KeyError "[MELD] No spell found with spell_id: <id>". purge disposes
  that version's entries in the authorized store and returns their count; the probes report that version's own
  status (`spell_id` is the version asked for).
- Error semantics: a spell_id no visible version carries raises the same KeyError, with the same text (R4).
  `ConduitMeld._get_purge_creations` raises RuntimeError "Cannot purge spell '<name>' (<id>): it has no owner
  store, so nothing was ever stored for it. Its owner stamp failed when its Book was conjured (the conjure logged
  the error). Dispose it with cleanup_spell and bind it again." for a `unique` version whose `_owner_creations` is
  None (R6).
- New internal edge: Meld calls `Spellbook._find_visible_version` (the Book a Meld already holds, `_spellbook`).

## Cross-Component Invariants
- A spell_id names one version (the owner's rule, 2026-10-17). The doors that build nothing reach it wherever the
  conduit can see it; the doors that build reach it only while it is active.
- Which store a door reads or purges, and who may purge it, come from the version's existence and owner stamp,
  exactly as for an active version; a park changes neither.
- The active path is unchanged: lock-free, the same reads in the same order (`Meld._resolve_spell_by_id`). Only a
  spell_id those reads miss takes the Book lock alone, and releases it before any store, slot or spell lock.
- Under the Book lock a version is in exactly one of the Book's four id maps: a notch's park and promotion, the
  borrowed twins, an index move, a disposal and a transfer's migration all write them under that lock. So the
  locked read never misses a version a notch is moving (F15); a lock-free read can, between two steps.
- Nothing persisted, cached, recorded or emitted changes; no cache generation or record version moves.

## Migration and Rollout Order
1. Red: the component and integration test files (done, 2026-10-25: 32 failed, 7 passed, the GIL off and on).
2. `Spellbook._find_visible_version`.
3. `Meld._resolve_visible_version_by_id` and `Meld._resolve_probe_target`; `_resolve_purge_spell` uses them.
4. ConduitMeld's and SpellSpaceMeld's `describe_live_creation_status` use `_resolve_probe_target`.
5. R6 in `ConduitMeld._get_purge_creations`.
6. Docstrings: the doors, `Conduit.purge` / `has_live_creation` / `describe_live_creation_status`, `SpellSpace.purge`.
7. Green: the two files and the related suites, the GIL off and on.
8. src_components and src_architecture with their indexes, the graph's changed sections, docs/intermediate
   (scopes, overrides), tests_components (after melder_2's turn-in), the release note.
9. The notch, the closure, the rebuild last.

## Rollback Strategy
- Rollback trigger: a supported caller relies on the KeyError for a parked spell_id, or a lock-order problem is
  found on the miss path.
- Rollback steps: revert the four source files and the docstrings; the new tests that need the reach turn red as
  the record of what was removed; revert the release-note entry.
- Post-rollback verification: the red run's 32 failures return and the 7 passing tests still pass.

## Validation Expectations and Evidence Plan
- tests/component/melder/aether/conduit/test_conduit_component_probe_and_purge_reach_every_version.py and
  tests/integration/melder/conduit/test_conduit_integration_probe_and_purge_during_notches.py green, the GIL off
  and on.
- Related suites, the GIL off and on: the purge and spellspace-creation component tests, the managed spell
  component tests, the Meld unit tests (`test_meld.py`, `test_concrete_meld_subclasses.py`), the index-link,
  notch and transfer integration tests and the Rift static-room tests.
- Windows and hosted CI: Not run until seen.

## Ticket Coverage Map
- Epic: none (standalone)
- Story: STORY-2026-10-25-probe_and_purge_reach_every_version
- Tasks: none (the story's checklist)

## Unknowns and Decision Requests
- UNKNOWN until the green run: whether a unit stub of the Book (`_SpellbookStub` in
  tests/unit/melder/aether/conduit/meld/test_concrete_meld_subclasses.py) reaches the miss path; if it does, the
  stub gains `_find_visible_version`, as it mirrors the Book surface Meld reads.
- Documented, not changed: a purge racing `cleanup_spell` of the same version is not ordered (F16, as for an
  active version); a probe or purge during an ownership transfer, between its flip and its migration, can miss the
  moving versions (KeyError), as `find_spell_by_spell_id` can.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing in src yet; the red tests are in place.
- What remains: steps 2-9 of the rollout order.
- Next entrypoint: `Spellbook._find_visible_version`, then `Meld._resolve_visible_version_by_id`.
