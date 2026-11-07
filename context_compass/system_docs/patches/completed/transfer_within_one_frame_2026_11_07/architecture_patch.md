# architecture_patch

## Metadata
- Patch ID: transfer_within_one_frame_2026_11_07
- Status: completed (merged into src_architecture and src_components 2026-11-07; moved to patches/completed/)
- Owner: Mark (owner); written by melder_0 (synaptic_python_developer)
- Created: 2026-11-07T16:45:35Z
- Updated: 2026-11-07T16:45:35Z

## Patch Scope and Non-Goals
- Objective: `Conduit.transfer_spell_ownership` refuses a target conduit in another aetheric frame, as `link` refuses
  one - the owner, chat 2026-11-07: "they shouldn't be able to transfer between frames thats an illegal operation",
  "because you cannot link between frames either". Measured by T3 part (b): a cross-frame transfer gave the target
  Book two active spells at one address (DUPLICATE_SPELL_NAME on meld), left the source frame's address claim naming
  the moved spell (no Book there could bind the address again), and let a later bind in the target frame register a
  second active spell.
- Non-goals: cross-frame stewardship by any other route; the transfer's behaviour inside one frame; links.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Conduit (public transfer verb) | modify | refuse before the TRANSFER_OWNERSHIP transaction opens when the frames differ | none |
| Ownership Transfer (C2, ConduitWard and Contracts) | modify (doc) | its contract names the one-frame rule | Conduit |

## Interface and Boundary Deltas
- Interface delta 1 (Breaking): `transfer_spell_ownership` raises RuntimeError "Cannot transfer spell ownership
  across different AethericFrames: <source> != <target>. ..." when the target conduit's aetheric frame is not this
  conduit's; nothing starts (no transaction, no preflight footprint, no move).

## Cross-Component Invariants
- Invariant 1: a spell's stewardship, links and contracts stay inside one aetheric frame, so one active spell per
  address per frame holds through every transfer (with the 0.2.8273 notch rule and the frame-wide claim).

## Migration and Rollout Order
1. The check in `Conduit.transfer_spell_ownership` (after the dynamic-mode check, before the transaction), docstring.
2. Regression tests (both duplicate shapes; nothing moved on refusal); the T3(b) probe re-run.
3. Release note (Breaking), notch; src_architecture (transfer sequence, failure modes) and src_components (Ownership
   Transfer) with their indexes and the graph descriptor of conduit.py; the rebuild on the owner's word (held).

## Rollback Strategy
- Rollback trigger: the owner wants cross-frame transfers back.
- Rollback steps: revert the check, its tests and doc lines.
- Post-rollback verification: the T3(b) probe shows P08c/P08d ADMITTED again.

## Validation Expectations and Evidence Plan
- Validation item 1: a cross-frame transfer raises the RuntimeError and leaves both frames as they were (source Book,
  claims, target Book, melds); same-frame transfers unchanged (their existing tests pass).
- Evidence source 1: context_compass/artifacts/duplicate_address_paths_20261107/runs/ (re-run after the fix).

## Ticket Coverage Map
- Epic: EPIC-2026-11-07-spellframe_hides_the_concrete_class
- Story: none
- Tasks: TASK-2026-11-07-spellframe_ambiguity_validation_check (part (b))

## Unknowns and Decision Requests
- UNKNOWN: none for the code path (only caller of `ConduitWard._transfer_spell_ownership` is this verb).
- DECISION_REQUEST: none (the owner's ruling above). No code_description_patch: one guard before the transaction.

## Context / Handoff Summary
- What changed: nothing yet.
- What remains: rollout 1-3.
- Next entrypoint: `Conduit.transfer_spell_ownership`.
