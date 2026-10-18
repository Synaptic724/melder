# Component patch: Spellbook - one managed version of a class per index (part B; managed_settings_spell_id_2026_10_17)

## Metadata
- Patch ID: managed_settings_spell_id_2026_10_17
- Component: Spellbook Core (`bind_inactive`, `_apply_add_to_index`, the spell_id collision error) and
  ReleaseManagedSpell (`_resolve_pool`'s docstring)
- Status: draft; for the talk after part A (owner, 2026-10-18); lands after melder_1 releases spellbook.py
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T00:10:00Z
- Updated: 2026-10-18T00:42:22Z

## Component Purpose and Boundary
- Current boundary: an index may hold versions under different binding signatures (owner, 2026-10-17); nothing stops
  two managed versions of one class object in one index when their address or disposal list differs, and each keeps
  its own pool, so a release with no filter goes to the active version's pool and can strand the other's count.
- Target boundary: `bind_inactive` and `add_to_spell_index` refuse a managed version whose class object already backs
  another managed version of the target index. Different classes - the versions an agent iterates through - and
  non-managed versions are untouched.

## Before/After Behavior Summary
- Before: Worker managed at ('workers', 'worker') active and Worker managed at ('workers', 'worker_b') staged on its
  index: two pools; after a notch a release misroutes as S6's Q2 does.
- After: the staging (or the move) raises before anything is registered or moved; the remedy names the two choices -
  bind the class at its own index, or change the settings of the existing spell (`cleanup_spell`, then `bind`).

## Interface Deltas
- Error semantics: RuntimeError, as the seams' other refusals, naming the class, both spell_ids and the remedy.
  Placement - before Bind registers the staged version in `bind_inactive`, and inside `_apply_add_to_index`'s
  checks before anything moves for an index move - is UNKNOWN until both are re-read on melder_1's released tree.
- The collision error ("Spell ID collision detected. ...") adds one sentence: managed settings are not part of the
  spell_id; to change them, `cleanup_spell` the spell and bind it again.
- `ReleaseManagedSpell._resolve_pool`'s docstring stops listing "two versions of one index" among the ambiguous cases
  it resolves; the active-version preference stays for pools of one class in two roots after a no-move transfer.

## State and Lifecycle Deltas
- None: a refusal changes nothing.

## Failure Mode Deltas
- New failure mode: the refusal above (**Breaking change** for code that stages one managed class twice in an index).
- Removed failure mode: the residual misroute.

## Dependency and Ordering Constraints
1. After part A (the settings already out of the spell_id) and after melder_1's release of spellbook.py.
2. Rebases on S1's and S2's fixes if they land first in the same seams:
   - STORY-2026-10-17-staged_version_releases_active_signature
   - STORY-2026-10-17-notch_moves_signature_by_incoming_key_only

## Validation Expectations
- Integration: staging and moving a second managed version of one class into an index refused with the Book, index,
  frame claims and pools unchanged; a version of another class staged as before; non-managed staging unchanged.
- Probe: probe_managed_release_routing Q2 adapted to the residual (another binding name) refused.

## Unknowns and Open Decisions
- UNKNOWN: the exact placement in `bind_inactive` (read at implementation, on melder_1's released tree).
- DECISION_REQUEST (owner): this refusal at all (recommended), or accept the residual.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: the seams are also S1's and S2's; whichever lands second rebases.
- Next entrypoint: `src/melder/aether/spellbook/spellbook.py:Spellbook.bind_inactive`.
