# component_patch_ownership_transfer

## Metadata
- Patch ID: transfer_within_one_frame_2026_11_07
- Component: Conduit.transfer_spell_ownership and Subcomponent: Ownership Transfer
- Status: completed (merged into src_architecture and src_components 2026-11-07; moved to patches/completed/)
- Owner: Mark (owner); written by melder_0 (synaptic_python_developer)
- Created: 2026-11-07T16:45:35Z
- Updated: 2026-11-07T16:45:35Z

## Component Purpose and Boundary
- Current boundary: the public verb checks a cleaned conduit, a normal conduit, the frame posture and dynamic mode,
  then opens TRANSFER_OWNERSHIP and hands the move to `ConduitWard._transfer_spell_ownership`.
  EVIDENCE: src/melder/aether/conduit/conduit.py:4285-4396
- Target boundary: the same, plus one check - the target conduit's aetheric frame equals this conduit's - before the
  transaction opens, mirroring `ConduitWard._link` (src/melder/aether/conduit/conduit_ward/conduit_ward.py:801-814).

## Before/After Behavior Summary
- Before: a transfer to a root of another frame ran; the target Book could hold two active spells at one address,
  the source frame's claim kept naming the moved spell, and the target frame never claimed the address.
- After: RuntimeError "Cannot transfer spell ownership across different AethericFrames: <source> != <target>. ..."
  with the remedy (bind the spell in the target frame's Spellbook), logged at ERROR; nothing starts.

## Interface Deltas
- Inputs: none. Outputs: none. Error semantics: the new RuntimeError above (link's wording, extended with a remedy).

## State and Lifecycle Deltas
- Owned state changes: none. Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: the cross-frame refusal. Removed: the cross-frame duplicate and the stale source claim.

## Dependency and Ordering Constraints
1. The check runs after the existing posture and dynamic checks and before `_build_transfer_transaction_metadata`,
   whose preflight would otherwise run against a foreign frame.
2. Reads `_aetheric_frame_name` on both conduits as `_link` does; no lock (frame names are fixed at construction).

## Validation Expectations
- Test/validation item 1: integration tests - both duplicate shapes across frames refused, both frames unchanged;
  a target frame not serving the address refused too (P08d).
- Evidence target 1: the T3(b) probe rows P08c/P08d read REFUSED.

## Unknowns and Open Decisions
- UNKNOWN: none. DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet. Remaining risks: none known.
- Next entrypoint: `Conduit.transfer_spell_ownership`.
