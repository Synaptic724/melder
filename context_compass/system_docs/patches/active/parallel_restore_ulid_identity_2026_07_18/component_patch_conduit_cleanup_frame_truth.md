# Component Patch: Conduit cleanup frame-truth hardening (S4 REOPEN delta)

Lane: parallel_restore_ulid_identity_2026_07_18. Ticket: STORY-2026-07-18-loadplan-phase-compiler.

## Before
- _cleanup_normal_conduit step 4 wraps THREE verbs in ONE try/except (conduit.py:758-765):
  spell unregistration from Aether, root-conduit removal from the frame, and the Nexus
  frame-record push. A failure in the FIRST verb (e.g. the owning spellbook already
  cleaned: its _spells was del'd -> AttributeError) skips _remove_root_conduit() entirely
  while the except swallows the error - the frame's root-conduit registry retains a
  CLEANED husk (and the name mapping stays poisoned in _conduit_ids_by_name).

## After
- Step 4 splits into three INDEPENDENT try/except blocks, frame removal FIRST:
  1. _remove_root_conduit() - frame truth is never hostage to sibling-verb state.
  2. spellbook._unregister_conduit_spells_from_aether(id) - guarded alone.
  3. _publish_frame_record_to_nexus() - guarded alone.
- Ordering safety (source-verified): _remove_spells_from_aether operates on the frame's
  SPELL registry keyed by conduit_id (aether.py:1606-1628 ->
  frame.unregister_conduit_spells) and never consults frame._conduits, so removing the
  root-conduit registration first cannot break spell unregistration; the Nexus push reads
  frame state and correctly publishes the post-removal record either way.

## Interface Deltas
- None. Private teardown body only; failure lanes keep logging per verb.

## State / Failure Deltas
- A conduit cleaned after its spellbook now ALWAYS leaves frame._conduits and the
  name map; the spell-registry verb may still log its own failure without collateral.

## Dependency / Ordering
- Complements the scheduler quiesce (code_description_patch_phase_scheduler_quiesce.md):
  quiesce removes the engine-lane producer of the book-before-conduit ordering; this
  split protects every OTHER lane that can clean a book before its conduit.

## Validation Expectations
- Component row: clean the spellbook FIRST, then conduit.cleanup(); the frame registry
  and name map are empty, the conduit reads cleaned, no husk remains.
