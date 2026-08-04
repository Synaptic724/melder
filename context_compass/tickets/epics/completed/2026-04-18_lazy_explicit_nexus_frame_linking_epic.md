# Epic: Lazy Explicit Nexus Frame Linking
- Completed: 2026-04-19T16:54:36Z
- Summary: Closed during the 2026-04-19 cleanup pass after downstream lazy-linking and single-space implementation landed.

## Metadata
- Epic ID: EPIC-2026-04-18-lazy-explicit-nexus-frame-linking
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T12:41:23Z
- Updated: 2026-04-19T16:54:36Z
- Target Window: 2026-04
- Related Program/Initiative: Rift runtime finishing pass

## Problem / Opportunity
`Nexus.create_rift(...)` still seeds `Rift` with Nexus-frame/default-frame
state up front and `Nexus.add_rift(...)` still eagerly attaches/realizes
Nexus frames during Rift registration. That conflicts with the intended model:

- bare Rift first
- no internal frame attachment by default
- explicit later frame request/link only
- topology policy (`single`, `indexed`, `one_per_workspace`) applied at request time

## MRP Alignment (Most Reasonable Product)
The MRP is not a full future frame-linking system.

It is:
- remove eager frame/default state from `Rift`
- stop eager Nexus-frame realization during Rift creation/registration
- make Nexus-frame realization lazy and explicit
- leave later richer link/open APIs for follow-on work

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected to removing eager/default frame
  behavior and wants this staged before implementation.
- EXECUTION_BOUNDARY: investigate and then refactor eager Rift/Nexus
  frame/default attachment into lazy explicit linking only.
- DEPENDENCIES:
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/configuration/nexus_configuration.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/nexus_frame_record.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
- EXIT_GATE: the eager Nexus-frame/default model is replaced by lazy explicit
  linking and the focused validation ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if detaching eager/default state
  requires a broader target-opening or space-contract redesign than this lane
  intends to cover.

## Goals (Outcomes)
- Make `Rift` creation frame-free.
- Move Nexus-frame realization to explicit request paths only.
- Remove Rift-owned default Nexus-frame/default target-frame state.
- Keep topology policy on `Nexus`, but apply it only at explicit request time.

## Non-Goals (Explicit Exclusions)
- full target-opening redesign onto `RiftSpace`
- event-system replacement
- future local-frame/conduit hosting implementation

## Scope Boundaries
- In scope:
  - eager Nexus-frame attachment/removal logic
  - Rift constructor state for Nexus/target defaults
  - direct viewer/metadata paths that rely on default target frame
  - direct unit-test assumptions
- Out of scope:
  - final explicit link/open API design for spaces
  - broader contract ownership moves

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested an epic and planning pass
  for removing eager/default frame behavior before implementation.

## Success Metrics
- one evidence-backed plan for lazy explicit frame linking
- no eager Nexus-frame realization on Rift creation after implementation

## Stories (Required to Complete)
- [ ] Story: investigate lazy explicit Nexus-frame linking and default-state removal

## Notes
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: PLAN
  CLAIM: The next frame-lifecycle lane is to separate Rift existence from
    Nexus-frame realization. Right now a Rift comes into existence already
    seeded with Nexus/default frame state and gets eagerly attached to Nexus
    frames during registration, which is exactly the behavior the user wants to
    remove.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:691-706
  - src/melder/aether/nexus/nexus.py:736-755
  - src/melder/aether/nexus/nexus.py:2757-2783
  - user_instruction: "nexus never build a frame ever unless requested"
  IMPACT: We need a bounded refactor that kills eager attachment without
    pretending the rest of the future frame-link design is already built.
  NEXT: complete the investigation story/task, then propose the exact no-backward-compat implementation cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Context / Handoff Summary
This epic owns the lazy explicit Nexus-frame linking refactor: no eager frame
realization at Rift creation, topology applied only on explicit request.
