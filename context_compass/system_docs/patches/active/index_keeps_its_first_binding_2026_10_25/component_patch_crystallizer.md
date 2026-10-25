# component_patch_crystallizer

## Metadata
- Patch ID: index_keeps_its_first_binding_2026_10_25
- Component: Crystallizer Root, Persistence Record, And Module-World Surfaces (RecordVersion, GraftRunner)
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T09:13:34Z
- Updated: 2026-10-25T09:13:34Z

## Component Purpose and Boundary
- Current boundary: RecordVersion stamps every durable artifact "4.3.0" and its read gate refuses only a newer major;
  an older or unstamped record ("0.0.0") passes into the tolerance lanes. The graft's merge lane parks every recorded
  member onto the caller's live index through `bind_inactive`, whatever binding it was recorded with.
- Target boundary: RecordVersion speaks 5.0.0 and reads majors 5 and up to its own: a record of an older major,
  unstamped ones included, is refused at the gate with the reason and the remedy. The merge lane files a member bound
  another way than the merge target as a shortfall and parks the rest.

## Before/After Behavior Summary
- RecordVersion. Before: `CURRENT = "4.3.0"`; `check_readable` raised only for `recorded_major > current_major`.
  After: `CURRENT = "5.0.0"`, a class constant `OLDEST_READABLE_MAJOR = 5`, and `check_readable` also raises
  ValueError when `recorded_major < OLDEST_READABLE_MAJOR`: "<label> was written by record version <v>, older than
  the oldest this melder reads (5.0.0). Since record version 5.0.0 every version of a SpellIndex is bound the way its
  first version was, and a record made before cannot promise that, so it is not read. Record the world again with
  this melder - a new checkpoint, formation or index graft - to keep it." The four call sites
  (`PersistenceCrystal.from_cached_item`, `AssetManagementSystem`'s formation load and `fetch_index_graft`,
  `GraftRunner.__init__`) are unchanged. The class comment records major 5's reason; the module and class docstrings
  say older majors are refused.
- GraftRunner merge lane. Before: `_merge_members` hydrated each member and called `bind_inactive` onto the merge
  target with the recorded spellframe and binding name. After: before that call it computes the member's signature,
  `SpellIndex.signature_of(spellframe=<the hydrated spellframe>, spell_name=<the target's name, as Bind takes it>,
  binding_name=<the recorded binding name>)`, and when it differs from the merge target's `binding_signature` appends a
  shortfall, `{"member": <id>, "reason": "member_binding_differs_from_merge_target: '<name>' was recorded with
  <its binding>, and the merge target keeps the binding <(kind, frame_key, binding_key)>"}`, and skips the member. An
  adopted selection whose member was skipped files the existing `recorded_selection_not_grafted_not_adopted`.

## Interface Deltas
- Inputs: none changed.
- Outputs: the merge report's `shortfalls` can hold the new reason; `members_parked` counts only the members parked.
- Error semantics: the record gate's new refusal (ValueError, above); the merge lane raises nothing new.

## State and Lifecycle Deltas
- Owned state changes: none (a class constant).
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: a record of major 4 or older is refused by every reader; nothing is built from it.
- Removed failure mode: none here.
- Changed failure mode: a merge member bound another way, which `bind_inactive` now refuses, is a shortfall instead of
  an error that would end the graft part-way.

## Dependency and Ordering Constraints
1. `SpellIndex.signature_of` and `binding_signature` (component_patch_binding_pipeline).
2. The merge lane checks before `bind_inactive`, so a skipped member registers nothing.
3. The restore engine and the graft's fresh lane need no change: a record of major 5 holds one binding per index (the
   bind and staging refusals guarantee it), and the gate refuses every older one.

## Validation Expectations
- A RecordVersion unit test: `CURRENT` is "5.0.0"; a payload stamped "4.3.0", one stamped "0.9.0" and an unstamped one
  are refused with the message's reason and remedy; "5.0.0" and "5.7.0" read; "6.0.0" refused as newer.
- A graft-merge test: an index captured at (Greeter, 'english') and merged into a live index at (Greeter, 'french')
  files the shortfall for each member and parks none; merged into a live index at (Greeter, 'english') it parks them.
- The crystallizer suites: the tests pinning "4.3.0" or reading older majors move to 5.0.0.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (the owner's call 1: "invalidate all the records").

## Context / Handoff Summary
- What changed: the record version and its floor; the merge lane's per-member check.
- Remaining risks: tests that hand-build records without a stamp or with a 4.x one (counted at the suite run).
- Next entrypoint: `RecordVersion.check_readable`, then `GraftRunner._merge_members`.
