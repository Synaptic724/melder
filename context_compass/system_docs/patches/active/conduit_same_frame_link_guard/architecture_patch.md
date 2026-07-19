# architecture_patch

## Metadata
- Patch ID: conduit_same_frame_link_guard
- Status: draft
- Owner: codex
- Created: 2026-03-28T15:43:01Z
- Updated: 2026-03-28T15:43:01Z

## Patch Scope and Non-Goals
- Objective:
  Enforce the runtime invariant that peer conduit contracts may only be created
  between conduits that belong to the same `AethericFrame`.
- Non-goals:
  - redesigning conduit frames or ARS topology
  - changing lesser-conduit lineage rules
  - changing sever/unlink behavior for already-existing contracts

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| conduit_ward | modify | authoritative contract-creation boundary should reject cross-frame links | none |

## Interface and Boundary Deltas
- Boundary delta 1:
  `ConduitWard._link(...)` should reject target conduits whose
  `_aetheric_frame` differs from the source conduit's `_aetheric_frame`.
- Boundary delta 2:
  Cross-frame peer contracts are treated as invalid runtime topology rather
  than a policy-level ARS option.

## Cross-Component Invariants
- Invariant 1:
  Peer conduit links are same-frame only.
- Invariant 2:
  Existing conduit-local `_aetheric_frame` identity is sufficient for the
  runtime guard; `Aether` lookup is not required for the basic equality check.
- Invariant 3:
  `sever_link(...)` remains available for existing contracts and should not add
  a same-frame precondition.

## Migration and Rollout Order
1. Document the invariant in patch artifacts.
2. Add the same-frame guard in `ConduitWard._link(...)`.
3. Add one focused regression test.

## Rollback Strategy
- Rollback trigger:
  The invariant proves incompatible with an already-intended cross-frame
  contract design.
- Rollback steps:
  1. Remove the guard from `_link(...)`.
  2. Remove or rewrite the regression test.
  3. Replace the invariant with an explicit documented cross-frame policy.
- Post-rollback verification:
  Runtime and tests agree on whether cross-frame peer links are legal.

## Validation Expectations and Evidence Plan
- Validation item 1:
  `_link(...)` raises on different frame names.
- Evidence source 1:
  `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- Validation item 2:
  Unit test fails without the guard and passes with it.
- Evidence source 2:
  `tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py`

## Ticket Coverage Map
- Story:
  STORY-2026-03-16-aethericrift-system-bootstrap
- Tasks:
  - TASK-2026-03-28-investigate-conduit-same-frame-link-guard
  - TASK-2026-03-28-implement-conduit-same-frame-link-guard

## Unknowns and Decision Requests
- UNKNOWN:
  Whether any higher-level design actually intends cross-frame conduit peer
  contracts in the future.
- DECISION_REQUEST:
  None for the current narrow invariant change.

## Context / Handoff Summary
- What changed:
  The patch formalizes a same-frame-only runtime invariant for peer conduit
  contracts.
- What remains:
  Any future cross-frame contract design would need an explicit architectural
  decision instead of relying on implicit runtime permissiveness.
- Next entrypoint:
  `component_patch_conduit_ward.md`
