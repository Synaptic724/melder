# Story: Wire the AethericMediator into MR / Nexus / Crystallizer (activation-gated)

## Metadata
- Story ID: STORY-2026-07-31-aetheric-mediator-wiring
- Epic ID: EPIC-2026-07-31-aetheric-mediator-subsystem
- Status: blocked
- Owner: cowork
- Agent Name: UNASSIGNED
- Priority: p2
- Created: 2026-07-31T23:00:41Z
- Updated: 2026-07-31T23:00:41Z

## Problem / Opportunity
Wiring is where the blast radius lives - three working subsystems. It does not
start until the plane is proven standalone and the surveys are in.

## BLOCKED ON
1. STORY-2026-07-31-aetheric-mediator-core complete (plane proven standalone).
2. STORY-2026-07-31-subsystem-transactional-survey complete (all three).
3. Owner decision on epic open question 1: does the top plane claim FRAME scope
   keys, or only subsystem keys?
4. Owner decision on epic open question 2: do inner frame transactions JOIN the
   top session, or stay siblings?

## Ticket Contract
- ENTRY_GATE: all four blockers cleared.
- EXECUTION_BOUNDARY: wiring only, activation-gated - a subsystem participates
  ONLY when enabled and active.
- EXIT_GATE: each wired subsystem proves isolation without regressing its
  existing protection.
- FAILURE_ESCALATION: this is SYSTEM-IMPACTING - patch_framework_gating.md
  applies, so architecture + component patch docs are required BEFORE any edit.

## Non-Goals
- Removing existing protections before the plane demonstrably replaces them.
  LoadGate is RE-EXPRESSED as a world-scope exclusive claim, never deleted first.

## Applicable Anti-Patterns
- [ ] No wiring before the surveys land.
- [ ] No removing a working protection ahead of its replacement being proven.
- [ ] No implementation before patch docs exist and are ticket-linked.

## Context / Handoff Summary
Deliberately blocked. Do not start this because the core looks finished - the
open questions are the real gate.
