# architecture_patch

## Metadata
- Patch ID: meld_by_spell_index_id_2026_11_28
- Status: implemented at 0.2.8317; merged into src_architecture, src_components, tests_components and the
  source graph
- Owner: Mark (owner); executor melder_0 (synaptic_python_developer)
- Created: 2026-11-28T19:00:37Z
- Updated: 2026-11-28T19:55:00Z

## Patch Scope and Non-Goals
- Objective: a meld may name its target by spell index id. `Conduit.meld`, `SpellSpace.meld` and
  `Conduit.managed_spell_meld` take a keyword-only `spell_index_id=` beside `spell_id=`. The Spellbook that owns the
  index resolves it - index id -> SpellIndex -> `selected_spell_id` - and the meld continues in the existing spell_id
  lane, so a meld by index id builds the version the index has active and follows a notch. A spell_id meld that
  misses a version the conduit's Book can see parked says so and names that version's index id. The meld forms that
  exist keep their speed (the owner's constraint, 2026-11-28).
- Non-goals: refusing or removing `spell_id=`; the Rift rooms' `meld` command and `meld_existing_spell`; purge, the
  live-creation probes and the version verbs (they keep spell_ids); any lookup through SpellSystemStates (the owner,
  2026-11-28: the Spellbook is the resource).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Conduit Runtime (Normal and Lesser) | modify | `meld` and `managed_spell_meld` take `spell_index_id=` | Spellbook Core |
| Creations and SpellSpace | modify | `SpellSpace.meld` takes `spell_index_id=` | Spellbook Core |
| Spellbook Core (Binding and Conjure) | modify | an index-id map beside `_spells` and one resolver | none |
| Ownership Transfer (subcomponent) | modify | its direct writes of both Books' `_spells` keep the map | Spellbook Core |
| Meld Resolution Runtime | modify | the spell_id miss text names a parked version's index | Spellbook Core |

## Interface and Boundary Deltas
- Boundary delta: `Conduit.meld(..., spell_index_id=None)`, `SpellSpace.meld(..., spell_index_id=None)` and
  `Conduit.managed_spell_meld(..., spell_index_id=None)`; `spell_index_id` excludes `spell`, `spell_id`,
  `spellframe` and `binding_name` (ValueError), must be a str (TypeError), and an id no index of the conduit's Book -
  owned or borrowed - carries raises KeyError naming it.
- Interface delta: `Spellbook._selected_spell_id_for_index_id(spell_index_id) -> str` (internal) and the owned
  map `Spellbook._spell_indexes_by_id: dict[str, SpellIndex]`, the local twin of `_contracted_indexes`.
- The KeyError a spell_id meld raises keeps its first words, "[MELD] No spell found with spell_id: <id>", and gains a
  sentence when the id is a version the Book can see parked.

## Cross-Component Invariants
- `_spell_indexes_by_id` holds exactly the ids of `_spells`' keys: every writer of `_spells` - seven Spellbook methods
  and four ownership-transfer sites - writes the map in the same locked section.
- A meld by index id builds what a meld by the index's selected spell_id builds, through the same door lane, warm
  doors included.
- The existing meld forms run the same code as before but for one `is not None` test of the new keyword at each
  door's entry.

## Migration and Rollout Order
1. The Spellbook map, its writers, its cleanup and the resolver.
2. The three doors and the miss text.
3. Tests, timings, docs, release note, notch, rebuild.

## Rollback Strategy
- Rollback trigger: a regression in a suite or a measurable warm-meld slowdown.
- Rollback steps: revert the commit; nothing persisted, cached or recorded changes shape.
- Post-rollback verification: the suites the diff reached pass again.

## Validation Expectations and Evidence Plan
- Failing-first component tests: by index id, the active version; after a notch, the incoming version; a borrowed
  index; the argument refusals; an unknown index id; the parked spell_id miss text; the map in step after bind,
  notch, cleanup_spell, a refused late bind, the index moves, a transfer and teardown; automatic and dynamic.
- Warm-meld timings of the existing forms before and after, the GIL off.
- Evidence source: Notes of TASK-2026-11-28-meld_by_spell_index_id (#346).

## Ticket Coverage Map
- Epic: EPIC-2026-10-17-correctness_defects (#209), item C8
- Story: none
- Tasks: TASK-2026-11-28-meld_by_spell_index_id (#346)

## Unknowns and Decision Requests
- Settled 2026-11-28: every test that checks the spell_id miss text matches its first words (five files), so the
  longer text keeps them passing.
- DECISION_REQUEST: none open.

## Context / Handoff Summary
- What changed: implemented at 0.2.8317 as specified, with these refinements (#346's Notes): one argument
  check for the three doors (`Meld._check_spell_index_id_call`, allocation-free for a well-formed call); the
  Book's KeyError built by `Spellbook._unknown_spell_index_id_error`, which names an index holding only parked
  versions; the parked spell_id miss gives one of three remedies (meld by index id, notch the version active,
  or the lender's notch back for a granted copy). The invariant that the existing forms run the same code
  but for one test holds for the code, not the cost: the keyword's default fill made each warm automatic
  meld 6 to 11 ns slower (A/B against 0.2.8316), which the owner accepted on 2026-11-28; the SPEED NOTE in
  `Conduit.meld` and `SpellSpace.meld` records a `specialized_meld` split that would win it back. Found in
  passing and left for #209: C9, a borrower cannot meld a lender's notched version the lender never melded.
  The deltas are merged into src_architecture, src_components, tests_components and the source graph.
- What remains: nothing in this patch; C9 waits on #209.
- Next entrypoint: none (completed).
