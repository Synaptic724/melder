# Architecture Patch: mutation_research_accessor_doors_2026_07_12

## Metadata
- Patch ID: mutation_research_accessor_doors_2026_07_12
- Status: active
- Owner ruling: 2026-07-12 session (mutation_0 lane) - explicit reversal of the
  2026-07-06 "conduits and frames carry no mutation dimension" ruling, narrowed to
  Spellbook and Conduit only.
- Ticket: tickets/tasks/2026-07-12_mutation_research_accessor_doors_task.md

## Objective
Give Spellbook and Conduit a borrowed reference to the Aether-hosted MutationResearch
world root, bound at init exactly like the `_crystallizer` emit reference, exposed
through one read-only public property per class, and deleted in cleanup.

## Non-Goals
- No MR verb forwarding on either door (the Rift rooms remain the mediated agent
  surface; the 34/21 command split is untouched).
- No frame-level MR surface (AethericFrame keeps zero mutation dimension).
- No change to the record model: bind/bind_inactive/notch auto-record seams keep
  their non-constructing peek and their "research never gates a bind" contract.
- No change to MR root lifecycle verbs, ResearchSet semantics, or the crystallizer
  MR twin / restore build stage.

## Changed Components
- Spellbook Core (Binding and Conjure): +1 owned-slot borrowed reference,
  +1 public property, +2 cleanup touch points.
- Conduit Runtime (Normal and Lesser): +1 owned-slot borrowed reference,
  +1 public property (returns at the site of the deleted 2026-07-11 door),
  +1 cleanup touch point.

## Invariants (unchanged)
- MR is WORLD-scoped: the doors return the one Aether-hosted root; nothing becomes
  conduit- or spellbook-scoped. Docstrings must state this explicitly.
- Single-residence invariant, journal semantics, and room ACL mediation unchanged.
- Frames carry no MR dimension.
- Lock order stays one-way (spellbook -> root -> set -> child); the doors add no
  lock acquisition beyond the existing Aether lazy-build lock at first bind.

## Invariants (new)
- The bound reference is BORROWED: neither class cleans the MR root; cleanup deletes
  only the local reference (crystallizer parity).
- Doors are read-only object handoff; liveness/activation enforcement stays on the
  root's own verbs (check_cleaned / activation gates).

## Interface Deltas
- Spellbook.mutation_research -> MutationResearch (new public read-only property).
- Conduit.mutation_research -> MutationResearch (new public read-only property).
- Behavior delta R1: first Spellbook() construction now builds the (inactive) MR root
  via Aether.mutation_research; previously deferred to first explicit root access.
- Behavior delta R2: a cleaned MR root under a live Aether now fails Spellbook()
  construction with RuntimeError (existing aether accessor contract, surfaced earlier).

## Migration Order
1. Spellbook deltas (slot, import, bind, property, cleanup).
2. Conduit deltas (slot, import, bind-from-spellbook, property, cleanup).
3. Source NOTE update at the old conduit door site (update, never delete).
4. Unit tests.
5. Canonical doc sync (src_components.md, src_architecture.md).

## Rollback
Revert the two source files and the test file; revert doc deltas. No record shape,
persisted artifact, or configuration schema changes exist in this patch.

## Ticket Coverage Matrix
| Delta | Ticket step |
| --- | --- |
| Spellbook door + cleanup | Implement Spellbook deltas |
| Conduit door + cleanup | Implement Conduit deltas |
| NOTE reversal record | Update conduit.py NOTE |
| Contract tests | Write unit tests |
| C-doc sync | Sync src_components.md / src_architecture.md |
