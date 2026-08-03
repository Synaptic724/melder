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
2. ~~STORY-2026-07-31-subsystem-transactional-survey complete (all three).~~
   **CLEARED 2026-08-02T19:35:00Z** (bootstrap_0). All three surveys delivered:
   crystallizer, nexus, MR - each with six questions answered against source,
   concrete scope keys and modes, and two CONFLICT findings apiece. Read the
   cross-subsystem note at the end of the MR survey before starting wiring: the
   plane subsumes crystallizer's global gate and Nexus's block/drain/refresh
   choreography, but it does NOT subsume MR's one-way lock order, so wiring MR
   is an addition on top of a hand-maintained invariant rather than a migration.
   Also read the `ix` correction on the crystallizer survey - the first version
   of that survey asserted `ix` meant escalation and refused it everywhere; it is
   the PARENT-SCOPE marker, and it is earned in both Nexus and MR.
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

## Aether Integration Recipe (measured 2026-08-01, do not guess this)

CONSTRUCTION ORDER in `Aether.__init__` today:
  `_crystallizer` (aether.py:167) -> `_aether_utility_system` (:174) ->
  `_load_gate` (:187) -> `_mutation_research = None` (:192, LAZY) ->
  `_nexus` (:193)
The owner's constraint is that the plane is built IMMEDIATELY, FIRST, after
Aether itself. That means it goes BEFORE `_crystallizer` at :167 - earlier than
`_load_gate` sits today - because the crystallizer is one of the three
subsystems that will eventually claim against it.

CLEANUP ORDER in `Aether.cleanup` today:
  `_load_gate` (:241) -> `_crystallizer` (:245) -> `_mutation_research` (:247)
  -> `_nexus` (:253) -> `_aether_utility_system` (:255) -> dels (:258-265)
The plane must be cleaned LAST among these, mirroring its
first-constructed position, so any subsystem still releasing claims during its
own teardown finds a live plane rather than a dead one.

*** THE TEST-ISOLATION CONSEQUENCE, AND IT IS FREE IF DONE RIGHT ***
`Aether._reset_singleton_for_tests()` (aether.py:286) CALLS `cleanup()` before
clearing `_instance` / `_initialized`. Therefore: if the plane is constructed in
`__init__` AND cleaned in `cleanup()`, every existing test that already calls
`Aether._reset_singleton_for_tests()` gets plane isolation automatically, with
no test changes anywhere in the suite.
If the cleanup line is FORGOTTEN, claims LEAK ACROSS TEST CASES and the
symptom will be later tests timing out on scopes held by earlier ones - a
confusing, order-dependent failure that will look like a plane bug rather than
a wiring omission. Add the cleanup line in the same commit as the construction
line, never after.

TWO TEST PATTERNS EXIST; USE THE RIGHT ONE:
1. PLAIN FIXTURE + CLEANUP GUARD - for directly constructed, non-singleton
   components. This is what `test_scope_acquisition.py` does for the embargo
   manager, orchestrator, and mediator, and it is what the plane's OWN existing
   tests already do. No singleton reset needed, because nothing touches a
   singleton.
2. `fresh_singletons` AUTOUSE FIXTURE - required the moment a test touches
   Aether. The canonical shape (206 call sites of
   `_reset_singleton_for_tests()` across the suite):
       AetherUtilitySystem._reset_singleton_for_tests()
       Nexus._reset_singleton_for_tests()
       Aether._reset_singleton_for_tests()
       aether = Aether()
       Spellbook._aether = aether
       Conduit._aether = aether
       StaticFrameViewer._aether = aether
       yield
       Nexus._reset_singleton_for_tests()
       Aether._reset_singleton_for_tests()
   Note the REBIND step: `Spellbook`, `Conduit`, and `StaticFrameViewer` cache
   the aether at CLASS level, so resetting the singleton without rebinding
   leaves them pointing at a dead instance. Any wiring test must do the same.

## Applicable Anti-Patterns
- [ ] No wiring before the surveys land.
- [ ] No removing a working protection ahead of its replacement being proven.
- [ ] No implementation before patch docs exist and are ticket-linked.

## Context / Handoff Summary
Deliberately blocked. Do not start this because the core looks finished - the
open questions are the real gate.
